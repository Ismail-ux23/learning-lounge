import json
from collections import defaultdict
from datetime import timedelta
from zoneinfo import ZoneInfo,ZoneInfoNotFoundError
from flask import Blueprint,render_template,redirect,request,flash,abort,send_file,current_app
from flask_login import current_user,login_required
from app.extensions import db
from app.ai.providers import is_configured
from app.models import *
from app.routes.api import owned
bp=Blueprint('main',__name__)
@bp.get('/')
def home(): return render_template('home.html',courses=Course.query.filter_by(status='published').all(),ai_configured=is_configured())
@bp.get('/health')
def health():
    db.session.execute(db.text('SELECT 1')); return {'status':'ok'}
@bp.get('/courses')
def catalog(): return render_template('catalog.html',courses=Course.query.filter_by(status='published').all())
@bp.get('/courses/<slug>')
def course(slug):
    c=Course.query.filter_by(slug=slug,status='published').first_or_404()
    return render_template('course.html',course=c,enrolled=current_user.is_authenticated and Enrollment.query.filter_by(user_id=current_user.id,course_id=c.id).first())
@bp.post('/courses/<int:id>/enroll')
@login_required
def enroll(id):
    c=Course.query.filter_by(id=id,status='published').first_or_404()
    if not Enrollment.query.filter_by(user_id=current_user.id,course_id=id).first():
        db.session.add(Enrollment(user_id=current_user.id,course_id=id)); db.session.commit()
    done={p.lesson_id for p in Progress.query.filter_by(user_id=current_user.id)}
    next_lesson=next((l for m in c.modules for t in m.topics for l in t.lessons if l.status=='published' and l.id not in done),None)
    flash('You are enrolled. Your progress will be saved.')
    return redirect('/lessons/'+str(next_lesson.id) if next_lesson else '/courses/'+c.slug)
@bp.route('/lessons/<int:id>',methods=['GET','POST'])
@login_required
def lesson(id):
    lesson=Lesson.query.get_or_404(id)
    if lesson.status!='published' or lesson.topic.module.course.status!='published': abort(404)
    if request.method=='POST':
        if not Progress.query.filter_by(user_id=current_user.id,lesson_id=id).first():
            db.session.add(Progress(user_id=current_user.id,lesson_id=id)); db.session.commit()
        flash('Lesson completed. Put it into practice when you are ready.')
    ordered=[l for m in lesson.topic.module.course.modules for t in m.topics for l in t.lessons if l.status=='published']
    position=next(i for i,l in enumerate(ordered) if l.id==id)
    next_lesson=ordered[position+1] if position+1<len(ordered) else None
    return render_template('lesson.html',next_lesson=next_lesson,lesson=lesson,done=Progress.query.filter_by(user_id=current_user.id,lesson_id=id).first())
@bp.get('/dashboard')
@login_required
def dashboard():
    attempts=Attempt.query.filter_by(user_id=current_user.id).order_by(Attempt.started_at.desc()).all()
    complete=[a for a in attempts if a.status=='complete']
    dates={a.submitted_at.replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo(current_user.timezone)).date() for a in complete if a.submitted_at}
    today=now().replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo(current_user.timezone)).date()
    cursor=today if today in dates else today-timedelta(days=1); streak=0
    while cursor in dates: streak+=1; cursor-=timedelta(days=1)
    done={p.lesson_id for p in Progress.query.filter_by(user_id=current_user.id)}
    enrollments=Enrollment.query.filter_by(user_id=current_user.id).all()
    next_lesson=next((l for e in enrollments for m in e.course.modules for t in m.topics for l in t.lessons if l.status=='published' and l.id not in done),None)
    weak=AttemptQuestion.query.join(Attempt).filter(Attempt.user_id==current_user.id,Attempt.status=='complete',AttemptQuestion.earned<AttemptQuestion.points).order_by(Attempt.submitted_at.desc()).first()
    recommended=Lesson.query.filter_by(topic_id=weak.topic_id,status='published').first() if weak else None
    return render_template('dashboard.html',next_lesson=next_lesson,recommended=recommended,attempts=attempts[:8],enrollments=Enrollment.query.filter_by(user_id=current_user.id).all(),completed=Progress.query.filter_by(user_id=current_user.id).count(),certificates=Certificate.query.filter_by(user_id=current_user.id).all(),streak=streak,average=round(sum(a.earned/a.total*100 for a in complete)/len(complete)) if complete else None,trend=[round(a.earned/a.total*100) for a in reversed(complete[:10])])
@bp.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    if request.method=='POST':
        name=request.form.get('name','').strip(); tz=request.form.get('timezone','UTC')
        if not 2<=len(name)<=100: abort(400)
        try: ZoneInfo(tz)
        except (ZoneInfoNotFoundError,ValueError): abort(400,description='Enter a valid IANA timezone, such as Asia/Karachi')
        current_user.name=name; current_user.timezone=tz; current_user.interests=request.form.get('interests','')[:1000]; db.session.commit(); flash('Profile saved.')
    return render_template('profile.html')
@bp.get('/practice')
@login_required
def setup():
    return render_template('setup.html',courses=Course.query.filter_by(status='published').all(),runner_ready=bool(current_app.config['JUDGE0_URL']),topic=request.args.get('topic',''),mode=request.args.get('mode','practice'))
@bp.get('/attempts/<id>')
@login_required
def attempt(id):
    a=owned(id)
    if a.status in ('complete','grading','evaluating'): return redirect('/results/'+a.id)
    return render_template('attempt.html',attempt=a)
@bp.get('/results/<id>')
@login_required
def results(id):
    a=owned(id)
    if a.status in ('ready','active'): return redirect('/attempts/'+id)
    groups=defaultdict(lambda:[0,0])
    for q in a.questions:
        groups[q.snapshot['category']][0]+=q.earned or 0; groups[q.snapshot['category']][1]+=q.points
    topics=defaultdict(lambda:[0,0])
    for q in a.questions:
        topics[q.snapshot['topic']][0]+=q.earned or 0; topics[q.snapshot['topic']][1]+=q.points
    correct=sum(1 for q in a.questions if q.answer and q.earned==q.points)
    unanswered=sum(1 for q in a.questions if not q.answer)
    percent=a.earned/a.total*100 if a.total else 0
    grade='A' if percent>=90 else 'B' if percent>=80 else 'C' if percent>=70 else 'Developing'
    minutes=round((a.submitted_at-a.started_at).total_seconds()/60,1) if a.submitted_at and a.started_at else 0
    return render_template('results.html',attempt=a,groups=groups,topics=topics,correct=correct,unanswered=unanswered,incorrect=len(a.questions)-correct-unanswered,grade=grade,minutes=minutes,certificate=Certificate.query.filter_by(attempt_id=id).first(),analysis=json.loads(a.analysis) if a.analysis else None)
@bp.get('/history')
@login_required
def history(): return render_template('history.html',attempts=Attempt.query.filter_by(user_id=current_user.id).order_by(Attempt.started_at.desc()).limit(100).all())
@bp.get('/mistakes')
@login_required
def mistakes():
    rows=AttemptQuestion.query.join(Attempt).filter(Attempt.user_id==current_user.id,Attempt.status=='complete',AttemptQuestion.earned<AttemptQuestion.points).order_by(Attempt.submitted_at.desc()).limit(100).all()
    return render_template('mistakes.html',questions=rows)
@bp.get('/roadmap')
@login_required
def roadmap():
    weak=db.session.query(AttemptQuestion.topic_id).join(Attempt).filter(Attempt.user_id==current_user.id,Attempt.status=='complete',AttemptQuestion.earned<AttemptQuestion.points).distinct().all()
    ids=[x[0] for x in weak]
    lessons=Lesson.query.filter(Lesson.topic_id.in_(ids),Lesson.status=='published').order_by(Lesson.position).all() if ids else Lesson.query.filter_by(status='published').order_by(Lesson.id).limit(5).all()
    return render_template('roadmap.html',lessons=lessons,weak=bool(ids))
@bp.get('/certificates/<id>/download')
@login_required
def download(id):
    c=Certificate.query.filter_by(id=id,user_id=current_user.id,status='valid').first_or_404()
    from app.services.certificates import make_pdf
    return send_file(make_pdf(c),mimetype='application/pdf',as_attachment=True,download_name='Learning-Lounge-'+id+'.pdf')
@bp.get('/verify/<id>')
def verify(id): return render_template('verify.html',certificate=Certificate.query.get_or_404(id))

@bp.get('/resources')
def resources():
    return render_template('resources.html',resources=Resource.query.filter_by(status='published').order_by(Resource.position,Resource.title).all())

@bp.get('/challenges')
def challenges():
    available=bool(current_app.config['JUDGE0_URL']) and db.session.query(Question.id).join(Course,Question.course_id==Course.id).join(ExecutionProfile,Course.profile_id==ExecutionProfile.id).filter(Question.category=='code',Question.state=='approved',Course.status=='published',ExecutionProfile.enabled.is_(True)).first() is not None
    return render_template('challenges.html',coding_available=available)
