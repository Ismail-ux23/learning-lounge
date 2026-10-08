import pytest

from app.extensions import db
from app.models import Attempt, Course, Module, Question, Topic


@pytest.fixture
def final_course(app):
    with app.app_context():
        course = Course(title='Selection tests', slug='selection-tests', status='published')
        db.session.add(course)
        db.session.flush()
        module = Module(course_id=course.id, title='Module')
        db.session.add(module)
        db.session.flush()
        topics = [Topic(module_id=module.id, title=f'Topic {i}', position=i) for i in range(3)]
        db.session.add_all(topics)
        db.session.flush()
        # The first topic dominates the bank. Uniform random sampling can
        # omit the other two even when their reviewed questions are available.
        for index, (topic, category) in enumerate(
            [(topics[0], 'concept')] * 8
            + [(topics[1], 'concept'), (topics[1], 'output'), (topics[2], 'concept')]
        ):
            db.session.add(Question(
                course_id=course.id, topic_id=topic.id, state='approved',
                category=category, difficulty='beginner', fingerprint=f'selection-{index}',
                content={'prompt':f'Question {index}', 'options':['A', 'B', 'C', 'D'],
                         'correct':0, 'explanation':'A reviewed explanation.'},
            ))
        db.session.commit()
        return course.id, {topic.id for topic in topics}


def test_final_covers_topics_and_categories_with_minimum_slots(learner, app, final_course):
    course_id, topics = final_course
    for _ in range(12):
        response = learner.post('/api/v1/attempts', json={
            'course_id':course_id, 'mode':'final',
            'categories':['concept', 'output'], 'count':3,
        })
        assert response.status_code == 201, response.json
        with app.app_context():
            questions = db.session.get(Attempt, response.json['data']['id']).questions
            assert {q.topic_id for q in questions} == topics
            assert {q.snapshot['category'] for q in questions} == {'concept', 'output'}
            assert len({q.question_id for q in questions}) == 3


def test_final_rejects_insufficient_combined_coverage(learner, app, final_course):
    course_id, topics = final_course
    with app.app_context():
        # Make output exclusive to the first topic, which also has the only
        # error question. Three topics and three categories now need four slots.
        output = Question.query.filter_by(course_id=course_id, category='output').one()
        output.topic_id = min(topics)
        q = Question.query.filter_by(course_id=course_id, topic_id=min(topics)).first()
        q.category = 'error'
        db.session.commit()
    payload = {'course_id':course_id, 'mode':'final',
               'categories':['concept', 'error', 'output'], 'count':3}
    response = learner.post('/api/v1/attempts', json=payload)
    assert response.status_code == 400
    assert 'question count' in response.json['error']['message']
    with app.app_context():
        assert Attempt.query.filter_by(course_id=course_id).count() == 0
    response = learner.post('/api/v1/attempts', json={**payload, 'count':4})
    assert response.status_code == 201
    with app.app_context():
        questions = db.session.get(Attempt, response.json['data']['id']).questions
        assert {q.topic_id for q in questions} == topics
        assert {q.snapshot['category'] for q in questions} == set(payload['categories'])


@pytest.mark.parametrize('categories', [
    ['concept', 'concept'], 'concept', {'concept':True}, [['concept']], None, [],
])
def test_invalid_categories_are_rejected_without_creating_attempt(learner, app, categories):
    response = learner.post('/api/v1/attempts', json={
        'course_id':1, 'categories':categories, 'count':2,
    })
    assert response.status_code == 400
    with app.app_context():
        assert Attempt.query.count() == 0
