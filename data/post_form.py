from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, StringField, TextAreaField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    text = TextAreaField('Текст:', validators=[DataRequired()])
    submit = SubmitField('Опубликовать')
