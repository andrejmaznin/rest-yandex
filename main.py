# основа приложения
from flask import Flask, request, render_template, redirect
from flask_restful import reqparse, abort, Api, Resource
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# работа с базой данных
from data import db_session

# классы таблиц базы
from data.couriers import Courier
from data.orders import Order
from data.users import User
from data.admin import Admin
from data.payments import Payment

# работа с запросами и данными для них
from data.couriers_resourses import *
from data.orders_resourses import *
from data.payments_resourses import *
from requests import post, patch
from datetime import datetime
from data.form_checks import *

# работа с формами
from forms.courier import LoginForm, ChangeForm, SignInForm
from forms.order import MakeOrderForm
from forms.admin import AdminForm

# создание хэшей данных
import hashlib

# сервер
from waitress import serve


def set_password(password):
    return str(hashlib.md5(password.encode('utf-8')).hexdigest())


TYPES = {1: "foot", 2: "bike", 3: "car"}
USER_TYPES = {'1': "Пешком", '2': "На велосипеде", '3': "На машине"}
REGIONS = {1: 'Левобережный район', 2: 'Правобережный', 3: 'Орджоникидзовский'}
ADMIN_PASSWORD = set_password('yandex')
USER_TABLE_TYPES = {'courier': Courier, 'admin': Admin}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)

db_session.global_init("couriers")
api.add_resource(CouriersListResource, '/couriers')  # для списка объектов
api.add_resource(CouriersResource, '/couriers/<int:id_c>')
api.add_resource(OrdersListResource, '/orders')  # для списка объектов
api.add_resource(OrdersAssignResource, '/orders/assign')  # для списка объектов
api.add_resource(OrdersCompleteResource, '/orders/complete')
# api.add_resource(OrdersResource, "/order/patch")

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    if user is not None:
        user_type = USER_TABLE_TYPES[user.type]
        return db_sess.query(user_type).filter(user_type.id == user.id_from_type_table).first()
    return user


@app.route('/')
@app.route('/main')
def main_page():
    return render_template('main.html', user=current_user)


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    form = SignInForm()
    if request.method == "POST":
        if form.validate_on_submit():
            session = db_session.create_session()
            user = session.query(User).filter(User.login == form.username.data).first()
            if user and user.hashed_password == set_password(form.password.data):
                login_user(user)
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
            login = form.username.data
            if check_uniqe_login(login):
                if check_times(int(form.start_hour.data), int(form.finish_hour.data)):
                    courier = Courier(courier_type=form.type.data, regions=[form.region.data],
                                      working_hours=[
                                          f"{str(form.start_hour.data).rjust(2, '0')}:00-{str(form.finish_hour.data).rjust(2, '0')}:00"],
                                      login=form.username.data)
                    session.add(courier)
                    courier = session.query(Courier).filter(Courier.login == form.username.data).first()
                    login_user(courier)
                    user = User(id_from_type_table=courier.id, hashed_password=set_password(form.password.data),
                                login=login, type='courier')
                    session.add(user)
                    session.commit()
                    login_user(user)
                    return redirect('/profile')
                return render_template('sign_up.html', user=current_user, form=form, login_message='',
                                       time_message="Такое время недопустимо.")
            return render_template('sign_up.html', user=current_user, form=form, login_message='Этот логин уже занят.',
                                   time_message='')
        return render_template('sign_up.html', user=current_user, form=form, login_message='', time_message='')
    elif request.method == "GET":
        return render_template('sign_up.html', user=current_user, form=form, login_message='', time_message='')


@app.route('/sign_up/admin', methods=['GET', 'POST'])
def admin_check():
    login_message = ''
    check_password_message = ''
    form = AdminForm()
    if request.method == "POST":
        if form.validate_on_submit():
            check_password = set_password(form.check_password.data) == ADMIN_PASSWORD
            uniqe_login = check_uniqe_login(form.login.data)
            if check_password and uniqe_login:
                session = db_session.create_session()
                admin = Admin(login=form.login.data)
                session.add(admin)
                session.commit()
                admin = session.query(Admin).filter(Admin.login == form.login.data).first()
                user = User(login=admin.login, id_from_type_table=admin.id, type='admin',
                            hashed_password=set_password(form.password.data))
                session.add(user)
                session.commit()
                login_user(user)
                return redirect('/profile')
            if not check_password:
                check_password_message = 'Неверный пароль доступа к регистрации.'
            if not uniqe_login:
                login_message = 'Этот логин уже занят.'
        return render_template('admin_sign_up.html', user=current_user, form=form, login_message=login_message,
                               check_password_message=check_password_message)
    elif request.method == "GET":
        return render_template('admin_sign_up.html', user=current_user, form=form, login_message=login_message,
                               check_password_message=check_password_message)


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user._get_current_object().__class__.__name__ == 'Courier':
        session = db_session.create_session()
        orders = session.query(Order).filter(Order.courier_id == current_user.id)
        payments, salary = list_of_completed_payments(current_user.id)
        return render_template('courier_profile.html', user=current_user, orders=orders, regions=REGIONS,
                               user_types=USER_TYPES, payments=payments, salary=salary)
    if current_user._get_current_object().__class__.__name__ == 'Admin':
        payments = list_of_payments()
        completed_orders = list_of_completed_orders()
        new_orders = list_of_new_orders()
        return render_template('admin_profile.html', user=current_user, payments=payments,
                               completed_orders=completed_orders, new_orders=new_orders, regions=REGIONS)
    return render_template('no_access.html', user=current_user)


@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    if current_user._get_current_object().__class__.__name__ == 'Admin':
        form = MakeOrderForm()
        if request.method == "POST":
            if form.validate_on_submit():
                if check_times(int(form.start_delivery_hour.data), int(form.finish_delivery_hour.data)):
                    session = db_session.create_session()
                    courier = Order(weight=form.weight.data, region=form.region.data, contact=form.contact.data,
                                    delivery_hours=[
                                        f"{str(form.start_delivery_hour.data).rjust(2, '0')}:00-{str(form.finish_delivery_hour.data).rjust(2, '0')}:00"])
                    session.add(courier)
                    session.commit()
                    return redirect('/profile')
                return render_template('order.html', user=current_user, form=form,
                                       time_message='Такое время недопустимо.')
            return render_template('order.html', user=current_user, form=form, time_message='')
        elif request.method == "GET":
            return render_template('order.html', user=current_user, form=form, time_message='')
    return render_template('no_access.html', user=current_user)


@app.route('/change_profile', methods=['GET', 'POST'])
@login_required
def change_profile():
    if current_user._get_current_object().__class__.__name__ == 'Courier':
        form = ChangeForm()
        if request.method == "POST":
            if form.validate_on_submit():
                if check_times(int(form.start_hour.data), int(form.finish_hour.data)):
                    session = db_session.create_session()
                    session.query(Courier).filter(Courier.id == current_user.id).update({
                        "courier_type": form.type.data, "regions": [form.region.data],
                        "working_hours": [
                            f"{str(form.start_hour.data).rjust(2, '0')}:00-{str(form.finish_hour.data).rjust(2, '0')}:00"]})
                    session.query(User).filter(User.id_from_type_table == current_user.id,
                                               User.type == 'courier').update(
                        {"hashed_password": set_password(form.password.data)})
                    session.commit()
                    return redirect('/profile')
                return render_template('change_profile.html', user=current_user, form=form,
                                       time_message='Такое время недопустимо.')
            return render_template('change_profile.html', user=current_user, form=form, time_message='')
        elif request.method == "GET":
            return render_template('change_profile.html', user=current_user, form=form, time_message='')
    return render_template('no_access.html', user=current_user)


@app.route('/orders_patch/<int:courier_id>')
@login_required
def assign_order(courier_id):
    if current_user._get_current_object().__class__.__name__ == 'Courier':
        assign(courier_id)
        return redirect('/profile')
    return render_template('no_access.html', user=current_user)


@app.route('/order_complete/<int:order_id>')
@login_required
def complete_order(order_id):
    if current_user._get_current_object().__class__.__name__ == 'Courier':
        order_complete(order_id)
        return redirect('/profile')
    return render_template('no_access.html', user=current_user)


@app.route('/pay/<int:payment_id>')
@login_required
def complete_payment(payment_id):
    if current_user._get_current_object().__class__.__name__ == 'Admin':
        payment_complete(payment_id)
        return redirect('/profile')
    return render_template('no_access.html', user=current_user)


@app.route('/exit')
@login_required
def exit():
    logout_user()
    return redirect('/main')


if __name__ == '__main__':
    # app.run(host='192.168.1.168', port=8080)
    serve(app, host='127.0.0.1', port=5000)
