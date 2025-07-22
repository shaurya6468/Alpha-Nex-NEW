from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, PasswordField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class SignupForm(FlaskForm):
    """User registration form with validation"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', 
                                   validators=[DataRequired(), EqualTo('password')])
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class LoginForm(FlaskForm):
    """User authentication form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class UploadForm(FlaskForm):
    file = FileField('File', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'mp4', 'mp3', 'wav', 'txt', 'py', 'js', 'html', 'css', 'jpg', 'png'], 
                   'Allowed file types: PDF, Video (MP4), Audio (MP3, WAV), Text, Code, Images')
    ])
    description = TextAreaField('Description', validators=[DataRequired(), Length(min=10, max=1000)])
    category = SelectField('Category', validators=[DataRequired()], choices=[
        ('video', 'Video'),
        ('audio', 'Audio'), 
        ('document', 'Document/PDF'),
        ('code', 'Code'),
        ('text', 'Text'),
        ('image', 'Image')
    ])
    ai_consent = BooleanField(
        'I agree that this content belongs to me, does not violate any rules, and can be used by AI companies for training',
        validators=[DataRequired()]
    )

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', validators=[DataRequired()], choices=[
        ('good', 'Good - High quality content'),
        ('bad', 'Bad - Poor quality or inappropriate')
    ])
    description = TextAreaField('Review Description', 
                              validators=[DataRequired(), Length(min=20, max=500)],
                              render_kw={"placeholder": "Explain your rating in detail..."})

class KYCForm(FlaskForm):
    document = FileField('ID Document (Passport/License)', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images and PDF only')
    ])
    selfie = FileField('Selfie Photo', validators=[
        FileRequired(), 
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only')
    ])

class WithdrawalForm(FlaskForm):
    amount_xp = IntegerField('XP Amount', validators=[DataRequired()])
    payment_method = SelectField('Payment Method', validators=[DataRequired()], choices=[
        ('paypal', 'PayPal'),
        ('bank', 'Bank Transfer'),
        ('crypto', 'Cryptocurrency')
    ])
    payment_details = TextAreaField('Payment Details', validators=[DataRequired()])
