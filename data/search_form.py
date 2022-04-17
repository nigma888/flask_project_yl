from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, StringField, TextAreaField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    id = StringField('', validators=[DataRequired()])
    submit = SubmitField('перейти')
