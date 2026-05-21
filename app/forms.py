from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Foydalanuvchi nomi', validators=[DataRequired()])
    password = PasswordField('Parol', validators=[DataRequired()])
    remember_me = BooleanField("Meni eslab qol")
    submit = SubmitField('Kirish')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField("To'liq ism", validators=[DataRequired(), Length(min=2, max=128)])
    username = StringField('Foydalanuvchi nomi', validators=[
        DataRequired(), Length(min=3, max=64)
    ])
    password = PasswordField('Parol', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Parolni tasdiqlang', validators=[
        DataRequired(), EqualTo('password', message='Parollar mos kelmaydi')
    ])
    submit = SubmitField("Ro'yxatdan o'tish")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Bu foydalanuvchi nomi allaqachon band.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Bu email allaqachon ishlatilgan.')


class PostForm(FlaskForm):
    image = FileField('Rasm', validators=[
        FileRequired('Rasm tanlang!'),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Faqat rasm fayllari!')
    ])
    caption = TextAreaField('Izoh', validators=[Optional(), Length(max=2200)])
    location = TextAreaField('Joylashuv', validators=[Optional(), Length(max=128)])
    submit = SubmitField('Ulashish')


class EditProfileForm(FlaskForm):
    full_name = StringField("To'liq ism", validators=[Optional(), Length(max=128)])
    username = StringField('Foydalanuvchi nomi', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    website = StringField('Veb-sayt', validators=[Optional(), Length(max=256)])
    avatar = FileField('Profil rasmi', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Faqat rasm fayllari!')
    ])
    submit = SubmitField('Saqlash')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Bu foydalanuvchi nomi allaqachon band.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Bu email allaqachon ishlatilgan.')


class CommentForm(FlaskForm):
    body = StringField('Izoh yozing...', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Yuborish')


class SearchForm(FlaskForm):
    q = StringField('Qidirish', validators=[DataRequired()])


class SupportForm(FlaskForm):
    subject = StringField('Mavzu', validators=[DataRequired(), Length(max=256)])
    message = TextAreaField('Xabar', validators=[DataRequired()])
    submit = SubmitField('Yuborish')
