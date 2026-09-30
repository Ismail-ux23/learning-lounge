import hashlib,secrets,smtplib
from email.message import EmailMessage
from datetime import timedelta
from flask import Blueprint,render_template,redirect,url_for,request,flash,current_app,abort
from flask_login import login_user,logout_user,login_required
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy.exc import IntegrityError
from app.extensions import db,limiter
from app.forms import LoginForm,RegisterForm
from app.models import User,ResetToken,now
bp=Blueprint('auth',__name__)
@bp.route('/register',methods=['GET','POST'])
@limiter.limit('10 per hour',methods=['POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        user=User(email=form.email.data.strip().lower(),name=form.name.data.strip(),password_hash=generate_password_hash(form.password.data))
        try: db.session.add(user); db.session.commit()
        except IntegrityError:
            db.session.rollback(); flash('That email is already registered.'); return render_template('auth.html',form=form,title='Join the lounge')
        login_user(user); return redirect(url_for('main.dashboard'))
    return render_template('auth.html',form=form,title='Join the lounge')
@bp.route('/login',methods=['GET','POST'])
@limiter.limit('10 per minute',methods=['POST'])
def login_view():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.enabled and check_password_hash(user.password_hash,form.password.data):
            login_user(user); return redirect(url_for('main.dashboard'))
        flash('Email or password is incorrect.')
    return render_template('auth.html',form=form,title='Welcome back')
@bp.post('/logout')
@login_required
def logout():
    logout_user(); return redirect('/')
@bp.route('/reset',methods=['GET','POST'])
@limiter.limit('5 per hour',methods=['POST'])
def reset_request():
    if request.method=='POST':
        user=User.query.filter_by(email=request.form.get('email','').strip().lower()).first()
        if user and current_app.config['MAIL_HOST']:
            raw=secrets.token_urlsafe(32)
            db.session.add(ResetToken(id=hashlib.sha256(raw.encode()).hexdigest(),user_id=user.id,expires=now()+timedelta(minutes=30))); db.session.commit()
            msg=EmailMessage(); msg['Subject']='Reset your Learning Lounge password'; msg['From']=current_app.config['MAIL_FROM']; msg['To']=user.email
            msg.set_content('Reset your password: '+current_app.config['PUBLIC_URL']+'/reset/'+raw)
            try:
                with smtplib.SMTP(current_app.config['MAIL_HOST'],current_app.config['MAIL_PORT'],timeout=10) as smtp: smtp.send_message(msg)
            except OSError: current_app.logger.error('Password reset delivery unavailable')
        flash('If your account exists and mail is configured, a reset link has been sent.')
    return render_template('reset.html',token=None,mail_ready=bool(current_app.config['MAIL_HOST']))
@bp.route('/reset/<token>',methods=['GET','POST'])
def reset_token(token):
    record=db.session.get(ResetToken,hashlib.sha256(token.encode()).hexdigest())
    if not record or record.used or record.expires<now(): abort(400,description='This reset link has expired or was already used.')
    if request.method=='POST':
        password=request.form.get('password','')
        if not 12<=len(password)<=128: abort(400,description='Use 12–128 characters')
        claimed=ResetToken.query.filter_by(id=record.id,used=False).filter(ResetToken.expires>now()).update({'used':True})
        if not claimed: abort(400)
        db.session.get(User,record.user_id).password_hash=generate_password_hash(password); db.session.commit()
        flash('Password updated. Sign in with your new password.'); return redirect('/login')
    return render_template('reset.html',token=token,mail_ready=True)
