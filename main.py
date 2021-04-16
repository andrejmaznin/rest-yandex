from flask import Flask
from data import db_session, couriers_resourses, orders_resourses
from data.couriers import Courier
from flask_restful import reqparse, abort, Api, Resource
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

user = False


class LoginForm(FlaskForm):
    username = StringField('ФИО', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    region = StringField('Регион', validators=[DataRequired()])
    type = SelectField('Способ передвижения', choices=[(1, 'Пешком'), (2, 'Велосипед'), (3, 'Автомобиль')], coerce=int)
    start_hour = SelectField('Начало рабочих часов', choices=[str(hour) for hour in range(1, 25)], coerce=int)
    finish_hour = SelectField('Конец рабочих часов', choices=[str(hour) for hour in range(1, 25)], coerce=int)
    submit = SubmitField('Зарегистрироваться')


def main():
    db_session.global_init("couriers")
    api.add_resource(couriers_resourses.CouriersListResource, '/couriers')  # для списка объектов
    api.add_resource(couriers_resourses.CouriersResource, '/couriers/<int:id_c>')
    api.add_resource(orders_resourses.OrdersListResource, '/orders')  # для списка объектов
    api.add_resource(orders_resourses.OrdersAssignResource, '/orders/assign')  # для списка объектов
    api.add_resource(orders_resourses.OrdersCompleteResource, '/orders/complete')

    @app.route('/')
    @app.route('/main')
    def main():
        # словарик для теста формы
        # todo: заменить чем-то нормальным
        test = {'orders': [{'weight': '234', 'region': 'ural'},
                           {'weight': '234', 'region': 'ural'},
                           {'weight': '234', 'region': 'ural'}]}

        return render_template('main.html', orders=test, user=user)

    @app.route('/sign_in')
    def sign_in():
        return render_template('sign_in.html', user=user)

    @app.route('/sign_up')
    def sign_up():
        form = LoginForm()
        return render_template('sign_up.html', user=user, form=form)

    @app.route('/profile')
    def profile():
        if user:
            return render_template('profile.html', user=user)
        return render_template('sign_in.html')

    @app.route('/order')
    def order():
        return render_template('order.html', user=user)

    app.run()


if __name__ == '__main__':
    main()
