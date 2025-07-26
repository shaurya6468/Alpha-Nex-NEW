from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class UploadForm(FlaskForm):
    file = FileField('File', validators=[FileRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=500)])
    category = SelectField('Category', choices=[
        ('documents', 'Documents'),
        ('code', 'Code'),
        ('images', 'Images'),
        ('audio', 'Audio'),
        ('text', 'Text Files'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    submit = SubmitField('Upload File')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        ('good', 'Good Quality'),
        ('bad', 'Poor Quality')
    ], validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[Length(max=500)])
    submit = SubmitField('Submit Review')