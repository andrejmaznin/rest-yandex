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


class MakeOrderForm(FlaskForm):
    weight = StringField('Вес', validators=[DataRequired(), CheckWeight()])
    region = SelectField('Район доставки    ',
                         choices=[(1, 'Левобережный район'), (2, 'Правобережный'), (3, 'Орджоникидзовский')],
                         coerce=int)
    start_delivery_hour = SelectField('Начало', choices=[str(hour) for hour in range(24)], coerce=int)
    finish_delivery_hour = SelectField('Конец', choices=[str(hour) for hour in range(24)], coerce=int)
    contact = StringField('Контактные данные', validators=[DataRequired()])
    submit = SubmitField('Сделать заказ')
