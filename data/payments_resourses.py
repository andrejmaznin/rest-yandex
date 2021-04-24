from data.checks import *
from data import db_session
from data.orders import Order
from data.couriers import Courier
from data.payments import Payment


def list_of_payments():  # возвращает словарь курьеров и не выплаченных им платежей
    session = db_session.create_session()
    all_payments = {}
    for courier in session.query(Courier).all():
        courier_payments = session.query(Payment).filter(Payment.courier_id == courier.id, Payment.completed == False).all()
        all_payments[courier.login] = courier_payments
    return all_payments


def payment_complete(payment_id):
    session = db_session.create_session()
    session.query(Payment).filter_by(id=payment_id).update({"completed": True})
    session.commit()
