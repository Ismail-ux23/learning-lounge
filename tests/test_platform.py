from datetime import timedelta
import pytest
from app.extensions import db
from app.models import *
from app.services.assessment import sweep_expired
from app.ai.schemas import QuestionData

def prepare(client,mode='exam'):
    r=client.post('/api/v1/attempts',json={'course_id':1,'mode':mode,'categories':['concept','error','output'],'count':6})
    assert r.status_code==201,r.json
    return r.json['data']['id']
def test_registration_enrollment_and_lessons(learner,app):
    assert learner.post('/courses/1/enroll').status_code==302
    assert learner.post('/lessons/1').status_code==200
    assert learner.get('/lessons/1').status_code==200
    with app.app_context():
        assert Enrollment.query.count()==1
        assert Progress.query.count()==1
        assert Lesson.query.count()==29
    for url in ['/','/courses','/courses/python-foundations','/dashboard','/profile','/practice','/history','/mistakes','/roadmap']:
        assert learner.get(url).status_code==200,url

def test_deadline_autosave_snapshot_and_private_answers(learner,app):
    id=prepare(learner)
    data=learner.get('/api/v1/attempts/'+id).json['data']
    assert data['expires_at'] is None
    a=learner.post('/api/v1/attempts/'+id+'/begin').json['data']
    assert learner.post('/api/v1/attempts/'+id+'/begin').json['data']['expires_at']==a['expires_at']
    assert learner.get('/api/v1/attempts/'+id).json['data']['expires_at']==a['expires_at']
    for q in a['questions']:
        assert not {'correct','tests','reference','explanation'}&q.keys()
    q=a['questions'][0]
    assert learner.post('/api/v1/attempts/'+id+'/answers',json={'question_id':q['id'],'answer':'2','flagged':True}).status_code==200
    assert learner.get('/api/v1/attempts/'+id).json['data']['questions'][0]['answer']=='2'
    with app.app_context():
        old=db.session.get(Attempt,id).questions[0].snapshot['explanation']
        source=db.session.get(Question,db.session.get(Attempt,id).questions[0].question_id)
        source.content={**source.content,'explanation':'changed later'};db.session.commit()
        assert db.session.get(Attempt,id).questions[0].snapshot['explanation']==old

def test_idempotent_submission_certificate_and_revocation(learner,app):
    id=prepare(learner);learner.post('/api/v1/attempts/'+id+'/begin')
    with app.app_context(): answers=[(q.id,str(q.snapshot['correct'])) for q in db.session.get(Attempt,id).questions]
    for q,answer in answers: learner.post('/api/v1/attempts/'+id+'/answers',json={'question_id':q,'answer':answer})
    for _ in range(2): assert learner.post('/api/v1/attempts/'+id+'/submit').status_code==200
    with app.app_context():
        a=db.session.get(Attempt,id);assert a.status=='complete';assert a.earned==a.total
        assert Certificate.query.count()==1;c=Certificate.query.one();cid=c.id
    assert learner.get('/results/'+id).status_code==200
    pdf=learner.get('/certificates/'+cid+'/download');assert pdf.data.startswith(b'%PDF')
    assert b'learner@example.com' not in learner.get('/verify/'+cid).data
    with app.app_context(): db.session.get(Certificate,cid).status='revoked';db.session.commit()
    assert b'Revoked' in learner.get('/verify/'+cid).data
    assert learner.get('/certificates/'+cid+'/download').status_code==404

def test_expiry_without_browser_and_late_answers(learner,app):
    id=prepare(learner);learner.post('/api/v1/attempts/'+id+'/begin')
    with app.app_context():
        a=db.session.get(Attempt,id);a.expires_at=now()-timedelta(seconds=1);qid=a.questions[0].id;db.session.commit();sweep_expired()
        assert db.session.get(Attempt,id).status=='complete'
    assert learner.post('/api/v1/attempts/'+id+'/answers',json={'question_id':qid,'answer':'0'}).status_code==409

def test_ownership_and_admin(learner,app):
    id=prepare(learner)
    other=app.test_client();other.post('/register',data={'name':'Another Learner','email':'other@example.com','password':'another long password'})
    assert other.get('/api/v1/attempts/'+id).status_code==404
    assert other.post('/api/v1/attempts/'+id+'/submit').status_code==404
    assert learner.get('/admin/').status_code==403

def test_another_course_without_source_changes(learner,app):
    with app.app_context(): User.query.first().role='admin';db.session.commit()
    import json
    rules={'weights':{'concept':1,'error':2,'output':2,'code':5},'seconds':{'concept':45,'error':90,'output':60,'code':240},'pass':70}
    r=learner.post('/admin/courses/new/edit',data={'title':'SQL Essentials','slug':'sql','status':'published','rules':json.dumps(rules)})
    assert r.status_code==302
    assert b'SQL Essentials' in learner.get('/courses/sql').data
    for path in ['/admin/','/admin/courses','/admin/questions','/admin/users','/admin/courses/1/edit']:
        assert learner.get(path).status_code==200,path

def test_invalid_ai_question_rejected():
    with pytest.raises(ValueError): QuestionData(prompt='An invalid test question',category='concept',options=['x','x','y','z'],correct=0,explanation='Explanation with enough words')

def test_runner_outage_is_pending_and_partial_credit(learner,app,monkeypatch):
    from app.services.assessment import assemble,begin,submit,grade
    from app.services.runner import RunnerUnavailable
    import app.services.assessment as service
    with app.app_context():
        p=ExecutionProfile(name='Test only',language_id=999,version='Python 3.14',enabled=True);db.session.add(p);db.session.flush()
        c=db.session.get(Course,1);c.profile_id=p.id;q=Question.query.filter_by(category='code').one();q.state='approved';db.session.commit();app.config['JUDGE0_URL']='http://test.invalid'
        a=assemble(User.query.first(),c,'exam',['code'],1);begin(a);a.questions[0].answer='print(sum(map(int,input().split())))';db.session.commit()
        def down(*args): raise RunnerUnavailable()
        monkeypatch.setattr(service,'run',down);submit(a)
        assert a.status=='grading';assert a.questions[0].earned is None
        monkeypatch.setattr(service,'run',lambda source,t,p:{'passed':t['visible'],'status':'Accepted' if t['visible'] else 'Wrong answer'})
        grade(a);assert a.status=='complete';assert a.earned==1

def test_csrf_enabled_by_default(app):
    app.config['WTF_CSRF_ENABLED']=True
    assert app.test_client().post('/register',data={}).status_code==400

def test_final_refuses_incomplete_syllabus(learner):
    response=learner.post('/api/v1/attempts',json={'course_id':1,'mode':'final','categories':['concept'],'count':6})
    assert response.status_code==400
    assert 'every syllabus topic' in response.json['error']['message']

def test_untimed_practice_feedback_and_exam_guard(learner,app):
    response=learner.post('/api/v1/attempts',json={'course_id':1,'mode':'practice','categories':['concept'],'count':1,'timed':False})
    id=response.json['data']['id']
    data=learner.post('/api/v1/attempts/'+id+'/begin').json['data']
    assert data['expires_at'] is None
    qid=data['questions'][0]['id']
    assert learner.post('/api/v1/attempts/'+id+'/answers',json={'question_id':qid,'answer':'0'}).status_code==200
    assert learner.post('/api/v1/attempts/'+id+'/feedback',json={'question_id':qid,'hint':True}).json['data']['hints_used']==1
    assert 'explanation' in learner.post('/api/v1/attempts/'+id+'/feedback',json={'question_id':qid}).json['data']
    exam=prepare(learner);data=learner.post('/api/v1/attempts/'+exam+'/begin').json['data']
    assert learner.post('/api/v1/attempts/'+exam+'/feedback',json={'question_id':data['questions'][0]['id']}).status_code==403

def test_daily_session_reused(learner):
    first=prepare(learner,'daily');second=prepare(learner,'daily')
    assert first==second

def test_gwen_setup_state_and_exam_boundary(learner,app):
    app.config['AI_MODEL']=''
    response=learner.post('/api/v1/gwen',json={'question':'Explain variables','lesson_id':2})
    assert response.status_code==503
    assert 'configure' in response.json['error']['message'].lower() or 'set ai_model' in response.json['error']['message'].lower()
    id=prepare(learner);learner.post('/api/v1/attempts/'+id+'/begin')
    assert learner.post('/api/v1/gwen',json={'question':'Explain variables','lesson_id':2}).status_code==403

def test_gwen_citations_limited_to_published_lessons(learner,monkeypatch):
    from app.ai.schemas import GwenAnswer
    import app.ai.providers as providers
    captured=[]
    def generate(prompt,schema):
        captured.append(prompt)
        return GwenAnswer(answer='A variable names a value.',lesson_ids=[2,999999])
    monkeypatch.setattr(providers,'generate',generate)
    response=learner.post('/api/v1/gwen',json={'question':'Explain variables','lesson_id':2})
    assert response.status_code==200
    assert [x['id'] for x in response.json['data']['references']]==[2]
    assert 'hidden' not in captured[0]

def test_review_pages_and_owner_only_content(learner,app):
    for path in ['/resources','/challenges','/courses','/lessons/1','/dashboard']:
        response=learner.get(path)
        assert response.status_code==200,path
        assert b'Powered by Ismail' in response.data
        assert b'theme-toggle' in response.data
    assert b'/lessons/2' in learner.get('/lessons/1').data
    assert learner.get('/static/images/gwen/gwen.png').status_code==200
    assert learner.get('/admin/resources').status_code==403
    with app.app_context():
        User.query.first().role='admin';db.session.commit()
    for path in ['/admin/resources','/admin/categories','/admin/progress']:
        assert learner.get(path).status_code==200
    response=learner.post('/admin/resources/new/edit',data={'title':'Unsafe','description':'Test only','url':'javascript:alert(1)','category':'Test','status':'published','position':'0'})
    assert response.status_code==200
    with app.app_context(): assert Resource.query.filter_by(title='Unsafe').count()==0

def test_theme_and_artwork_contract(client):
    html=client.get('/').data.decode()
    assert 'Learn smarter.' in html
    assert '/static/images/gwen/gwen.png' in html
    assert 'crystal-orbit.svg' not in html
    assert 'theme.js' in html
    assert 'data-theme=dark' in client.get('/static/css/tokens.css').data.decode()
    assert 'prefers-reduced-motion' in client.get('/static/css/tokens.css').data.decode()
