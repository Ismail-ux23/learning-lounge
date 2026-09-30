import os, secrets
from pathlib import Path
import click
from flask import Flask, render_template, jsonify, request
from config import Config
from app.extensions import db, migrate, login, csrf, limiter

def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config: app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)
    if not app.config.get('SECRET_KEY'):
        if os.getenv('PRODUCTION') == '1': raise RuntimeError('SECRET_KEY is required in production')
        key = Path(app.instance_path) / 'session.key'
        if not key.exists():
            key.write_text(secrets.token_hex(32)); key.chmod(0o600)
        app.config['SECRET_KEY'] = key.read_text()
    for ext in (db, login, csrf, limiter): ext.init_app(app)
    migrate.init_app(app, db)
    from app.models import User
    @login.user_loader
    def load_user(id):
        user = db.session.get(User, int(id))
        return user if user and user.enabled else None
    login.login_view = 'auth.login_view'
    @login.unauthorized_handler
    def unauthorized():
        if request.path.startswith('/api/'):
            return jsonify(error={'message':'Please sign in again.','code':401}),401
        from flask import redirect, url_for
        return redirect(url_for('auth.login_view'))
    from app.routes import auth, main, api, admin
    for bp in (auth.bp, main.bp, api.bp, admin.bp): app.register_blueprint(bp)
    @app.context_processor
    def globals():
        from flask_login import current_user
        from app.models import Course, Module, Topic, Lesson, Enrollment, Progress
        counts=dict(db.session.query(Module.course_id,db.func.count(Lesson.id)).join(Topic,Topic.module_id==Module.id).join(Lesson,Lesson.topic_id==Topic.id).filter(Lesson.status=='published').group_by(Module.course_id).all())
        progress={};done=set()
        if current_user.is_authenticated:
            done={p.lesson_id for p in Progress.query.filter_by(user_id=current_user.id)}
            for e in Enrollment.query.filter_by(user_id=current_user.id):
                ids={l.id for m in e.course.modules for t in m.topics for l in t.lessons if l.status=='published'}
                progress[e.course_id]=round(len(ids & done)/len(ids)*100) if ids else 0
        return {'brand':app.config['PLATFORM_NAME'],'lesson_counts':counts,'course_progress':progress,'done_ids':done}
    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['X-Frame-Options']='DENY'
        response.headers['Referrer-Policy']='same-origin'
        response.headers['Cache-Control']='no-store'
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; form-action 'self'"
        return response
    @app.errorhandler(400)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(409)
    @app.errorhandler(429)
    @app.errorhandler(500)
    def error(e):
        code = getattr(e,'code',500)
        if request.path.startswith('/api/'):
            return jsonify(error={'message':getattr(e,'description','Request failed'),'code':code}),code
        return render_template('error.html',code=code,message=getattr(e,'description','Something went wrong.')),code
    @app.cli.command('seed')
    def seed():
        from app.services.seed import seed_database
        seed_database(); click.echo('Curriculum seeded.')
    @app.cli.command('create-admin')
    @click.option('--email', prompt=True)
    @click.option('--name', prompt=True)
    @click.password_option()
    def create_admin(email,name,password):
        from werkzeug.security import generate_password_hash
        if len(password)<12: raise click.ClickException('Use at least 12 characters')
        if User.query.filter_by(email=email.lower()).first(): raise click.ClickException('Email already exists')
        db.session.add(User(email=email.lower(),name=name,password_hash=generate_password_hash(password),role='admin')); db.session.commit()
    @app.cli.command('sweep')
    def sweep():
        from app.services.assessment import sweep_expired
        sweep_expired(); click.echo('Expired and pending attempts processed.')
    return app
