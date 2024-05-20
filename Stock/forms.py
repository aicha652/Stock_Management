from collections.abc import Sequence
from typing import Mapping
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_admin.contrib.sqla.fields import QuerySelectField
from wtforms import StringField, PasswordField, SelectField, validators, ValidationError, SubmitField, IntegerField, DateField, HiddenField, TextAreaField
from wtforms.validators import Email, DataRequired, EqualTo
from flask_wtf.file import FileAllowed, FileField
from .models import User
from .tools import verify_pass


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             id='pwd_create',
                             validators=[DataRequired(),
                                         EqualTo('confirm',
                                                 message='incorrect password')])
    confirm = PasswordField("Repeat Password", validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired(),
                                             validators.Length(min=10,
                                                               message='Phone should be 10 characters')])
    
    submit = SubmitField("Register")

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username already Exists.")
    
    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("Email already registred!")
        

class AddProducts(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    price = StringField("Price", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    quantity = IntegerField("Quantity", [validators.NumberRange(min=1, max=10000)])
    image_1 = FileField("Image", validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'svg', 'gif'])])
    