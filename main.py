from flask import Flask, request
from data import db_session, couriers_resourses, orders_resourses
from data.couriers import Courier
from flask_restful import reqparse, abort, Api, Resource
from flask import render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, ValidationError
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib


def set_password(password):
    return str(hashlib.md5(password.encode('utf-8')).hexdigest())


types = {1: "foot", 2: "bike", 3: "car"}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

REGIONS = {'1': 'Левобережный район', '2': 'Правобережный', '3': 'Орджоникидзовский'}

# тестовые данные
user = False
# user = {'username': 'Иван Иванов', 'regions': [1], 'hashed_password': '*как бы хэш*', 'working_hours': ['11:00-13:00']}
test = [{'weight': '234', 'region': '1', 'completed': False, 'delivery_hours': ['11:00-13:00', '14:00-15:00']},
        {'weight': '234', 'region': '2', 'completed': True, 'delivery_hours': ['11:00-13:00']},
        {'weight': '234', 'region': '3', 'completed': True, 'delivery_hours': ['11:00-13:00']}]


class CheckWeight(object):
    def __init__(self):
        self.message = "Массу заказа необхимо указать числом"

    def __call__(self, form, field):
        try:
            weight = float(field.data)
        except ValueError:
            raise ValidationError(self.message)


class MainForm(FlaskForm):
    username = StringField('ФИО', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    region = SelectField('Район', choices=[(1, 'Левобережный район'), (2, 'Правобережный'), (3, 'Орджоникидзовский')],
                         coerce=int)
    type = SelectField('Способ передвижения', choices=[(1, 'Пешком'), (2, 'Велосипед'), (3, 'Автомобиль')], coerce=int)
    start_hour = SelectField('Начало рабочих часов', choices=[str(hour) for hour in range(1, 25)], coerce=int)
    finish_hour = SelectField('Конец рабочих часов', choices=[str(hour) for hour in range(1, 25)], coerce=int)
    submit = SubmitField('Зарегистрироваться')


class LoginForm(MainForm):
    submit = SubmitField('Зарегистрироваться')


class ChangeForm(MainForm):
    submit = SubmitField('Изменить')


class SignInForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class MakeOrderForm(FlaskForm):
    weight = StringField('Вес', validators=[DataRequired(), CheckWeight()])
    region = SelectField('Район доставки    ',
                         choices=[(1, 'Левобережный район'), (2, 'Правобережный'), (3, 'Орджоникидзовский')],
                         coerce=int)
    start_delivery_hour = SelectField('Начало', choices=[str(hour) for hour in range(1, 25)], coerce=int)
    finish_delivery_hour = SelectField('Конец', choices=[str(hour) for hour in range(1, 25)], coerce=int)
    submit = SubmitField('Сделать заказ')


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

    @app.route('/sign_in', methods=['GET', 'POST'])
    def sign_in():
        form = SignInForm()
        session = db_session.create_session()
        if request.method == "POST":
            courier = session.query(Courier).filter(Courier.login == form.username.data,
                                                    Courier.hashed_password == set_password(
                                                        form.password.data)).all()
            if form.validate_on_submit() and session.query(Courier).filter(Courier.login == form.username.data,
                                                                           Courier.hashed_password == set_password(
                                                                               form.password.data)).all():
                global user
                user = courier[0].as_dict()
                return redirect('/profile')
            return render_template('sign_in.html', form=form)
        elif request.method == "GET":
            return render_template('sign_in.html', form=form)

    @app.route('/sign_up', methods=['GET', 'POST'])
    def sign_up():
        form = LoginForm()
        if request.method == "POST":
            if form.validate_on_submit():
                session = db_session.create_session()
                if session.query(Courier).filter(Courier.login == form.username.data).all():
                    return redirect('/sign_in')
                courier = Courier(courier_type=form.type.data, regions=[form.region.data],
                                  working_hours=[f"{form.start_hour.data}:00-{form.finish_hour.data}:00"],
                                  hashed_password=set_password(form.password.data), login=form.username.data)

                session.add(courier)
                session.commit()
                return redirect('/profile')
            return render_template('sign_up.html', user=user, form=form)
        elif request.method == "GET":
            return render_template('sign_up.html', user=user, form=form)

    @app.route('/profile', methods=['GET', 'POST'])
    def profile():
        if user:
            return render_template('profile.html', user=user, orders=test, regions=REGIONS)
        return redirect('/sign_in')

    @app.route('/order', methods=['GET', 'POST'])
    def order():
        form = MakeOrderForm()
        if request.method == "POST":
            if form.validate_on_submit():
                # работа с базой
                return redirect('/main')
            return render_template('order.html', user=user, form=form)
        elif request.method == "GET":
            return render_template('order.html', user=user, form=form)

    @app.route('/change_profile', methods=['GET', 'POST'])
    def change_profile():
        if user:
            form = ChangeForm()
            if request.method == "POST":
                print(1)
                if form.validate_on_submit():
                    session = db_session.create_session()
                    print(form.start_hour.data)
                    session.query(Courier).filter(Courier.courier_id == user["courier_id"]).update({
                        "courier_type": form.type.data, "regions": [form.region.data],
                        "working_hours": [f"{form.start_hour.data}:00-{form.finish_hour.data}:00"],
                        "hashed_password": set_password(form.password.data), "login": form.username.data})
                    session.commit()
                    return redirect('/profile')
                return render_template('change_profile.html', user=user, form=form)
            elif request.method == "GET":
                return render_template('change_profile.html', user=user, form=form)
        return redirect('/sign_in')

    app.run()


if __name__ == '__main__':
    main()
