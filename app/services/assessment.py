import copy, random
from zoneinfo import ZoneInfo
from datetime import timedelta
from flask import current_app
from app.extensions import db
from app.models import Attempt, AttemptQuestion, Question, Certificate, Topic, Module, now
from app.services.runner import run, RunnerUnavailable

def assemble(user,course,mode,categories,count,topic_id=None,difficulty='beginner',timed=True):
    if mode not in ('practice','exam','placement','daily','final'): raise ValueError('Invalid mode')
    if not 1<=count<=30: raise ValueError('Choose 1–30 questions')
    if not categories or not set(categories)<= {'concept','error','output','code'}: raise ValueError('Select valid categories')
    daily_key=None
    if mode=='daily':
        day=now().replace(tzinfo=ZoneInfo('UTC')).astimezone(ZoneInfo(user.timezone)).date().isoformat()
        daily_key=f'{user.id}:{course.id}:{day}'
        existing=Attempt.query.filter_by(daily_key=daily_key).first()
        if existing: return existing
    profile=course.profile
    if 'code' in categories and (not profile or not profile.enabled or not current_app.config['JUDGE0_URL']): raise ValueError('Coding is unavailable until an operator configures a runner')
    query=Question.query.filter_by(course_id=course.id,state='approved',difficulty=difficulty).filter(Question.category.in_(categories))
    if topic_id: query=query.filter_by(topic_id=topic_id)
    pool=query.all()
    if mode=='final':
        expected={t.id for m in course.modules for t in m.topics}
        available={q.topic_id for q in pool}
        if not expected <= available or count < len(expected):
            raise ValueError('Final assessment is not available yet: reviewed questions must cover every syllabus topic. Use practice or a regular exam meanwhile.')
    if len(pool)<count: raise ValueError(f'Only {len(pool)} reviewed questions match. Reduce the count or broaden your topics.')
    if count<len(categories): raise ValueError('Question count must cover each selected category')
    rng=random.Random(f'{course.id}:{day}') if mode=='daily' else random.SystemRandom()
    selected=[]
    for category in categories:
        matching=[q for q in pool if q.category==category]
        if not matching: raise ValueError('No reviewed questions for '+category)
        selected.append(rng.choice(matching))
    selected+=rng.sample([q for q in pool if q not in selected],count-len(selected))
    rng.shuffle(selected)
    rules=copy.deepcopy(course.rules)
    rules['timed']=bool(timed) if mode=='practice' else True
    rules.update(course_title=course.title,course_version=course.version,profile={'language_id':profile.language_id,'version':profile.version,'enabled':profile.enabled} if profile else None)
    attempt=Attempt(user_id=user.id,course_id=course.id,mode=mode,rules=rules,daily_key=daily_key)
    db.session.add(attempt); db.session.flush()
    for i,q in enumerate(selected):
        snap=copy.deepcopy(q.content); snap.update(category=q.category,version=q.version,topic=q.topic.title)
        db.session.add(AttemptQuestion(attempt_id=attempt.id,question_id=q.id,topic_id=q.topic_id,position=i,snapshot=snap,points=rules['weights'][q.category]))
    attempt.total=sum(rules['weights'][q.category] for q in selected)
    db.session.commit(); return attempt

def begin(attempt):
    if attempt.status!='ready': return attempt
    seconds=sum(attempt.rules['seconds'][q.snapshot['category']] for q in attempt.questions)
    started=now()
    Attempt.query.filter_by(id=attempt.id,status='ready').update({'status':'active','started_at':started,'expires_at':started+timedelta(seconds=seconds) if attempt.rules.get('timed',True) else None})
    db.session.commit(); db.session.refresh(attempt); return attempt

def submit(attempt):
    Attempt.query.filter_by(id=attempt.id,status='active').update({'status':'grading','submitted_at':min(now(),attempt.expires_at) if attempt.expires_at else now()})
    db.session.commit(); db.session.refresh(attempt)
    if attempt.status=='grading': grade(attempt)
    return attempt

def grade(attempt):
    # Conditional transaction claim prevents concurrent workers producing duplicate outcomes.
    claimed=Attempt.query.filter_by(id=attempt.id,status='grading').update({'status':'evaluating','grading_started':now()})
    db.session.commit()
    if not claimed: return
    pending=False
    try:
        for q in attempt.questions:
            if q.earned is not None: continue
            if not q.answer:
                q.earned=0; q.outcome={'status':'Unanswered'}
            elif q.snapshot['category']!='code':
                q.earned=q.points if q.answer==str(q.snapshot['correct']) else 0
                q.outcome={'status':'Correct' if q.earned else 'Incorrect'}
            else:
                try:
                    outcomes=[run(q.answer,t,attempt.rules['profile']) for t in q.snapshot['tests']]
                    total=sum(t['weight'] for t in q.snapshot['tests'])
                    q.earned=q.points*sum(t['weight'] for t,r in zip(q.snapshot['tests'],outcomes) if r['passed'])/total
                    q.outcome={'status':'Evaluated','tests':[{'passed':r['passed'],'status':r['status']} for r in outcomes]}
                except RunnerUnavailable:
                    pending=True; q.outcome={'status':'Pending runner evaluation'}
        attempt.earned=sum(q.earned or 0 for q in attempt.questions)
        attempt.status='grading' if pending else 'complete'
        if not pending and attempt.mode in ('exam','final') and attempt.total and attempt.earned/attempt.total*100>=attempt.rules['pass']:
            if not Certificate.query.filter_by(attempt_id=attempt.id).first():
                db.session.add(Certificate(attempt_id=attempt.id,user_id=attempt.user_id,snapshot={'name':attempt.user.name,'course':attempt.rules['course_title'],'earned':attempt.earned,'total':attempt.total,'percent':round(attempt.earned/attempt.total*100,1),'type':'Assessment achievement','platform':current_app.config['PLATFORM_NAME']}))
        db.session.commit()
    except Exception:
        db.session.rollback()
        Attempt.query.filter_by(id=attempt.id,status='evaluating').update({'status':'grading'}); db.session.commit()
        raise

def sweep_expired():
    # A generous lease recovers a process killed during grading. One attempt can
    # contain 30 x 20 tests; each runner call has a bounded poll/HTTP budget.
    Attempt.query.filter(Attempt.status=='evaluating',Attempt.grading_started<now()-timedelta(hours=4)).update({'status':'grading'})
    db.session.commit()
    for a in Attempt.query.filter(Attempt.status=='active',Attempt.expires_at<=now()).all(): submit(a)
    for a in Attempt.query.filter_by(status='grading').all(): grade(a)

def public_attempt(a):
    return {'id':a.id,'status':a.status,'server_time':now().isoformat()+'Z','expires_at':a.expires_at.isoformat()+'Z' if a.expires_at else None,'questions':[{'id':q.id,'position':q.position,'prompt':q.snapshot['prompt'],'category':q.snapshot['category'],'editor_mode':'python' if q.snapshot.get('runtime','').lower().startswith('python') else None,'code':q.snapshot.get('code',''),'options':q.snapshot.get('options',[]),'samples':[{'stdin':t['stdin'],'expected':t['expected']} for t in q.snapshot.get('tests',[]) if t.get('visible')],'answer':q.answer,'flagged':q.flagged} for q in a.questions]}
