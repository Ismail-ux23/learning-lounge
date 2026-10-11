import subprocess
import sys

import pytest

from app.ai.schemas import QuestionData
from app.extensions import db
from app.models import Attempt, Course, Module, Question, Topic
from app.services.seed import seed_database
from data.curriculum import LESSONS
from data.question_bank import bank_entries

ENTRIES = list(bank_entries())


@pytest.mark.parametrize("key,title,content", ENTRIES, ids=[q[0] for q in ENTRIES])
def test_bank_content_and_executable_answers(key, title, content):
    QuestionData.model_validate(content)
    assert title in {lesson[1] for lesson in LESSONS}
    if content["category"] == "concept":
        return
    # Only checked-in authored programs run here; learner code uses Judge0.
    result = subprocess.run(
        [sys.executable, "-c", content["code"]],
        capture_output=True,
        text=True,
        timeout=5,
    )
    if content["category"] == "output":
        assert result.returncode == 0, result.stderr
        assert result.stdout.rstrip("\n") == content["options"][content["correct"]]
    else:
        assert result.returncode != 0
        assert (
            result.stderr.splitlines()[-1].split(":", 1)[0] == content["expected_error"]
        )


def test_reseed_upgrades_existing_course_without_resetting_edits(app):
    with app.app_context():
        course = Course.query.filter_by(slug="python-foundations").one()
        original_id = course.id
        # Simulate the old course: remove the new bank only, leaving legacy rows.
        from hashlib import sha256

        fingerprints = [
            sha256(f"python-foundations:{key}".encode()).hexdigest()
            for key, _, _ in ENTRIES
        ]
        Question.query.filter(Question.fingerprint.in_(fingerprints)).delete(
            synchronize_session=False
        )
        db.session.commit()
        legacy_count = Question.query.count()
        seed_database()
        assert Course.query.one().id == original_id
        assert Question.query.count() == legacy_count + len(ENTRIES)
        edited = Question.query.filter(Question.fingerprint.in_(fingerprints)).first()
        edited.state = "draft"
        edited.content = {
            **edited.content,
            "explanation": "Administrator revised this explanation.",
        }
        db.session.commit()
        edited_id = edited.id
        seed_database()
        assert Question.query.count() == legacy_count + len(ENTRIES)
        edited = db.session.get(Question, edited_id)
        assert edited.state == "draft"
        assert (
            edited.content["explanation"] == "Administrator revised this explanation."
        )


@pytest.mark.parametrize(
    "categories", [["concept"], ["output"], ["concept", "output", "error"]]
)
@pytest.mark.parametrize("count", [29, 30])
def test_seeded_course_final_covers_syllabus_and_scores(
    learner, app, categories, count
):
    response = learner.post(
        "/api/v1/attempts",
        json={
            "course_id": 1,
            "mode": "final",
            "categories": categories,
            "count": count,
        },
    )
    assert response.status_code == 201, response.json
    attempt_id = response.json["data"]["id"]
    public = learner.post(f"/api/v1/attempts/{attempt_id}/begin").json["data"]
    assert len(public["questions"]) == count
    assert all("correct" not in q for q in public["questions"])
    with app.app_context():
        attempt = db.session.get(Attempt, attempt_id)
        expected = {
            t.id for t in Topic.query.join(Module).filter(Module.course_id == 1)
        }
        assert {q.topic_id for q in attempt.questions} == expected
        assert len({q.question_id for q in attempt.questions}) == count
        assert {q.snapshot["category"] for q in attempt.questions} == set(categories)
        answers = [(q.id, str(q.snapshot["correct"])) for q in attempt.questions]
    for question_id, answer in answers:
        saved = learner.post(
            f"/api/v1/attempts/{attempt_id}/answers",
            json={
                "question_id": question_id,
                "answer": answer,
            },
        )
        assert saved.status_code == 200
    assert learner.post(f"/api/v1/attempts/{attempt_id}/submit").status_code == 200
    with app.app_context():
        attempt = db.session.get(Attempt, attempt_id)
        assert attempt.status == "complete"
        assert attempt.earned == attempt.total


def test_upgrade_rejects_ambiguous_topic_without_partial_question_additions(app):
    from hashlib import sha256

    with app.app_context():
        fingerprints = [
            sha256(f"python-foundations:{key}".encode()).hexdigest()
            for key, _, _ in ENTRIES
        ]
        Question.query.filter(Question.fingerprint.in_(fingerprints)).delete(
            synchronize_session=False
        )
        topic = Topic.query.filter_by(title=LESSONS[-1][1]).one()
        topic.title = "Administrator renamed the final topic"
        db.session.commit()
        before = Question.query.count()
        with pytest.raises(ValueError, match="expected one syllabus topic"):
            seed_database()
        assert Question.query.count() == before
