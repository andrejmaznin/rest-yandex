from flask import Flask
from data import db_session, couriers_resourses, orders_resourses
from data.couriers import Courier
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)


def main():
    db_session.global_init("couriers")
    api.add_resource(couriers_resourses.CouriersListResource, '/couriers')  # для списка объектов
    api.add_resource(couriers_resourses.CouriersResource, '/couriers/<int:id_c>')
    api.add_resource(orders_resourses.OrdersListResource, '/orders')  # для списка объектов
    api.add_resource(orders_resourses.OrdersAssignResource, '/orders/assign')  # для списка объектов
    api.add_resource(orders_resourses.OrdersCompleteResource, '/orders/complete')

    app.run()


if __name__ == '__main__':
    main()
