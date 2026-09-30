import pytest
from app import create_app
from app.extensions import db
from app.services.seed import seed_database
@pytest.fixture
def app(tmp_path):
    app=create_app({'TESTING':True,'SECRET_KEY':'test-key','SQLALCHEMY_DATABASE_URI':'sqlite:///'+str(tmp_path/'test.db'),'WTF_CSRF_ENABLED':False,'RATELIMIT_ENABLED':False})
    with app.app_context(): db.create_all();seed_database()
    yield app
    with app.app_context(): db.session.remove();db.drop_all()
@pytest.fixture
def client(app): return app.test_client()
@pytest.fixture
def learner(client):
    response=client.post('/register',data={'name':'Test Learner','email':'learner@example.com','password':'long secure passphrase'})
    assert response.status_code==302
    return client
