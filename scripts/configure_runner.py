"""Operator-only: approve an installed Judge0 language after inspecting its isolation."""
import argparse
from app import create_app
from app.extensions import db
from app.models import ExecutionProfile,Course
parser=argparse.ArgumentParser()
parser.add_argument('--language-id',type=int,required=True)
parser.add_argument('--version',required=True)
parser.add_argument('--name',required=True)
parser.add_argument('--course',required=True)
args=parser.parse_args()
with create_app().app_context():
    course=Course.query.filter_by(slug=args.course).first_or_404()
    p=ExecutionProfile(name=args.name,language_id=args.language_id,version=args.version,enabled=True)
    db.session.add(p);db.session.flush();course.profile_id=p.id;db.session.commit()
    print(f'Execution profile {p.id} configured. Validate reference solutions before approving coding questions.')
