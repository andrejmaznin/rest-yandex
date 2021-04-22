from flask import Flask, request
from data import db_session, couriers_resourses, orders_resourses
from data.couriers import Courier
from data.orders import Order
from data.orders_resourses import *
from flask_restful import reqparse, abort, Api, Resource
from flask import render_template, redirect
from forms.courier import LoginForm, ChangeForm, SignInForm
from forms.order import MakeOrderForm
import hashlib
from requests import post, patch
from datetime import datetime
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


def set_password(password):
    return str(hashlib.md5(password.encode('utf-8')).hexdigest())


TYPES = {1: "foot", 2: "bike", 3: "car"}
USER_TYPES = {'1': "Пешком", '2': "На велосипеде", '3': "На машине"}
REGIONS = {1: 'Левобережный район', 2: 'Правобережный', 3: 'Орджоникидзовский'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

# тестовые данные
# user = {'username': 'Иван Иванов', 'regions': [1], 'hashed_password': '*как бы хэш*', 'working_hours': ['11:00-13:00']}
test = [{'weight': '234', 'region': '1', 'completed': False, 'delivery_hours': ['11:00-13:00', '14:00-15:00']},
        {'weight': '234', 'region': '2', 'completed': True, 'delivery_hours': ['11:00-13:00']},
        {'weight': '234', 'region': '3', 'completed': True, 'delivery_hours': ['11:00-13:00']}]

db_session.global_init("couriers")
api.add_resource(couriers_resourses.CouriersListResource, '/couriers')  # для списка объектов
api.add_resource(couriers_resourses.CouriersResource, '/couriers/<int:id_c>')
api.add_resource(orders_resourses.OrdersListResource, '/orders')  # для списка объектов
api.add_resource(orders_resourses.OrdersAssignResource, '/orders/assign')  # для списка объектов
api.add_resource(orders_resourses.OrdersCompleteResource, '/orders/complete')
api.add_resource(orders_resourses.OrdersResource, "/order/patch")

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Courier).filter(Courier.id == user_id).first()


@app.route('/')
@app.route('/main')
def main_page():
    return render_template('main.html', orders=test, user=current_user, regions=REGIONS)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = SignInForm()
    if request.method == "POST":
        if form.validate_on_submit():
            session = db_session.create_session()
            user_check = session.query(Courier).filter(Courier.login == form.username.data).first()
            if user_check and user_check.hashed_password == set_password(form.password.data):
                login_user(user_check, remember=True)
                return redirect('/profile')
            return render_template('sign_in.html', user=current_user, message="Неправильный логин или пароль",
                                   form=form)
        return render_template('sign_in.html', form=form, user=current_user, message='')
    elif request.method == "GET":
        return render_template('sign_in.html', form=form, user=current_user, message='')


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
            courier = session.query(Courier).filter(Courier.login == form.username.data).first()
            login_user(courier)
            return redirect('/profile')
        return render_template('sign_up.html', user=current_user, form=form)
    elif request.method == "GET":
        return render_template('sign_up.html', user=current_user, form=form)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    session = db_session.create_session()
    orders = session.query(Order).filter(Order.courier_id == current_user.id)
    return render_template('profile.html', user=current_user, orders=orders, regions=REGIONS, user_types=USER_TYPES)


@app.route('/order', methods=['GET', 'POST'])
def order():
    form = MakeOrderForm()
    if request.method == "POST":
        if form.validate_on_submit():
            session = db_session.create_session()
            courier = Order(weight=form.weight.data, region=form.region.data,
                            delivery_hours=[
                                f"{form.start_delivery_hour.data}:00-{form.finish_delivery_hour.data}:00"])
            session.add(courier)
            session.commit()
            return redirect('/main')
        return render_template('order.html', user=current_user, form=form)
    elif request.method == "GET":
        return render_template('order.html', user=current_user, form=form)


@app.route('/change_profile', methods=['GET', 'POST'])
@login_required
def change_profile():
    form = ChangeForm()
    if request.method == "POST":
        if form.validate_on_submit():
            session = db_session.create_session()
            session.query(Courier).filter(Courier.id == current_user.id).update({
                "courier_type": form.type.data, "regions": [form.region.data],
                "working_hours": [f"{form.start_hour.data}:00-{form.finish_hour.data}:00"],
                "hashed_password": set_password(form.password.data)})
            session.commit()
            return redirect('/profile')
        print('qqqqqq')
        return render_template('change_profile.html', user=current_user, form=form)
    elif request.method == "GET":
        return render_template('change_profile.html', user=current_user, form=form)


@app.route('/orders_patch/<int:courier_id>')
@login_required
def assign_order(courier_id):
    assign(courier_id)
    return redirect('/profile')


@app.route('/order_complete/<int:order_id>')
@login_required
def complete_order(order_id):
    complete(order_id)
    return redirect('/profile')


@app.route('/exit')
@login_required
def exit():
    logout_user()
    return redirect('/main')


if __name__ == '__main__':
    app.run()
