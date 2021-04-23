from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, ValidationError
from wtforms.validators import DataRequired


class AdminForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль нового пользователя', validators=[DataRequired()])
    check_password = PasswordField('Пароль, предоставленный нашей компанией', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
