from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField, RadioField, SelectMultipleField
from wtforms.validators import DataRequired, Length , Email, EqualTo, ValidationError
from flask_login import login_user,current_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, SelectField, RadioField, SelectMultipleField
from wtforms.validators import DataRequired, Length , Email, EqualTo, ValidationError

class LoginForm(FlaskForm):
    voter_id = StringField('Voter ID',validators=[DataRequired()] )
    password = PasswordField('Password',validators=[DataRequired()] )
    submit = SubmitField('Sign In')
    email = StringField('Email',
                         validators=[DataRequired(), Email()] )

