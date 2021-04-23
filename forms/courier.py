from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, ValidationError
from wtforms.validators import DataRequired

class CheckWeight(object):
    def __init__(self):
        self.message = "Массу заказа необхимо указать числом"

    def __call__(self, form, field):
        try:
            weight = float(field.data)
        except ValueError:
            raise ValidationError(self.message)
        if weight > 50:
            raise ValidationError("Масса заказа не может превышать 50 кг.")


class MainForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired()])
    region = SelectField('Район', choices=[(1, 'Левобережный район'), (2, 'Правобережный'), (3, 'Орджоникидзовский')],
                         coerce=int)
    type = SelectField('Способ передвижения', choices=[(1, 'Пешком'), (2, 'Велосипед'), (3, 'Автомобиль')], coerce=int)
    start_hour = SelectField('Начало рабочих часов', choices=[str(hour) for hour in range(24)], coerce=int)
    finish_hour = SelectField('Конец рабочих часов', choices=[str(hour) for hour in range(24)], coerce=int)
    submit = SubmitField('Зарегистрироваться')


class LoginForm(MainForm):
    username = StringField('Логин', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class ChangeForm(MainForm):
    submit = SubmitField('Изменить')


class SignInForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
