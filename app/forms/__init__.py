from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
class LoginForm(FlaskForm):
    email=StringField('Email',validators=[DataRequired(),Email(),Length(max=254)])
    password=PasswordField('Password',validators=[DataRequired()])
    submit=SubmitField('Sign in')
class RegisterForm(LoginForm):
    name=StringField('Full name',validators=[DataRequired(),Length(min=2,max=100)])
    password=PasswordField('Password · at least 12 characters',validators=[DataRequired(),Length(min=12,max=128)])
    submit=SubmitField('Create account')
