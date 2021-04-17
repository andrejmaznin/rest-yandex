from flask import Flask
from data import db_session, couriers_resourses, orders_resourses
from data.couriers import Courier
from flask_restful import reqparse, abort, Api, Resource
from flask import render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

user = True

REGIONS = {'1': 'Левобережный район', '2': 'Правобережный', '3': 'Орджоникидзовский'}
test = [{'weight': '234', 'region': '1', 'completed': False, 'delivery_hours': ['11:00-13:00']},
        {'weight': '234', 'region': '2', 'completed': True, 'delivery_hours': ['11:00-13:00']},
         {'weight': '234', 'region': '3', 'completed': True, 'delivery_hours': ['11:00-13:00']}]


class LoginForm(FlaskForm):
    username = StringField('ФИО', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    region = SelectField('Район', choices=[(1, 'Левобережный район'), (2, 'Правобережный'), (3, 'Орджоникидзовский')],
                         coerce=int)
    type = SelectField('Способ передвижения', choices=[(1, 'Пешком'), (2, 'Велосипед'), (3, 'Автомобиль')], coerce=int)
    start_hour = SelectField('Начало рабочих часов', choices=[str(hour) for hour in range(1, 25)], coerce=int)
    finish_hour = SelectField('Конец рабочих часов', choices=[str(hour) for hour in range(1, 25)], coerce=int)
    submit = SubmitField('Зарегистрироваться')


class SigninForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


def main():
    db_session.global_init("couriers")
    api.add_resource(couriers_resourses.CouriersListResource, '/couriers')  # для списка объектов
    api.add_resource(couriers_resourses.CouriersResource, '/couriers/<int:id_c>')
    api.add_resource(orders_resourses.OrdersListResource, '/orders')  # для списка объектов
    api.add_resource(orders_resourses.OrdersAssignResource, '/orders/assign')  # для списка объектов
    api.add_resource(orders_resourses.OrdersCompleteResource, '/orders/complete')

    @app.route('/')
    @app.route('/main')
    def main_page():
        return render_template('main.html', orders=test, user=user, regions=REGIONS)

    @app.route('/sign_in')
    def sign_in():
        form = SigninForm()
        if form.validate_on_submit():
            return redirect('/profile')
        return render_template('sign_in.html', user=user, form=form)

    @app.route('/sign_up', methods=['GET', 'POST'])
    def sign_up():
        form = LoginForm()
        if form.validate_on_submit():
            return redirect('/profile')
        return render_template('sign_up.html', user=user, form=form)

    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        if user:
            return render_template('profile.html', user=user)
        return render_template('sign_in.html', orders=test, user=user, regions=REGIONS)

    @app.route('/order')
    def order():
        return render_template('order.html', user=user)

    @app.route('/change_profile', methods=['GET', 'PATCH'])
    def change_profile():
        form = SigninForm()

        if form.validate_on_submit():
            return redirect('/profile')
        return render_template('sign_in.html', user=user, form=form)

    app.run()


if __name__ == '__main__':
    main()
