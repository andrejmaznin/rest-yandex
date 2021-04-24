from flask import jsonify, request
from flask_restful import Resource, abort
from werkzeug.security import generate_password_hash
from data.checks import *
from data import db_session
from data.orders import Order
from data.couriers import Courier
from data.payments import Payment
import json
from sqlalchemy import *
from datetime import datetime

courier_types = {"foot": 10,
                 "bike": 15, "car": 50}
courier_types2 = {1: "foot",
                  2: "bike", 3: "car"}


def abort_if_order_not_found(order_id):
    session = db_session.create_session()
    orders = session.query(Order).get(order_id)
    if not orders:
        abort(400)


def abort_if_courier_not_found(courier_id):
    session = db_session.create_session()
    orders = session.query(Courier).get(courier_id)
    if not orders:
        abort(400)


class OrdersListResource(Resource):
    def post(self):
        req = request.get_json()
        valid_ids = []
        invalid_ids = []
        session = db_session.create_session()

        orders_list = req["data"]
        for i in orders_list:
            if check_order(i):
                order = Order(
                    order_id=i['order_id'],
                    weight=i['weight'],
                    region=i['region'],
                    delivery_hours=i['delivery_hours'])
                session.add(order)
                valid_ids.append(i["order_id"])
            else:
                invalid_ids.append(i["order_id"])

        session.commit()

        if not invalid_ids:
            response = {"orders": [{"id": i} for i in valid_ids]}
            response = jsonify(response)
            response.status_code = 201
            return response
        response = {"validation_error": {"orders": [{"id": i} for i in invalid_ids]}}
        response = jsonify(response)
        response.status_code = 400
        return response


class OrdersAssignResource(Resource):
    def post(self):
        req = request.get_json()
        if not check_id(req["courier_id"]):
            response = {"validation_error": {"couriers": {'courier_id': req["courier_id"]}}}
            response = jsonify(response)
            response.status_code = 400
            return response
        for el in req.keys():
            if el != "courier_id":
                response = {"validation_error": {"couriers": {'wrong_data': el}}}
                response = jsonify(response)
                response.status_code = 400
                return response

        session = db_session.create_session()
        courier = session.query(Courier).get(req["courier_id"]).as_dict()

        weight_courier = session.query(Order).filter_by(courier_id=req["courier_id"]).all()
        weight_courier = sum([i.as_dict()["weight"] for i in weight_courier])
        free_weight = courier_types[courier_types2[int(courier["courier_type"])]] - weight_courier

        courier_times = courier["working_hours"]
        orders = [i.as_dict() for i in
                  session.query(Order).filter(and_(Order.courier_id == None, Order.completed == False)).all()]
        orders = list(filter(lambda a: check_regions(courier["regions"], a["region"]) and
                                       check_intersection(courier_times, a["delivery_hours"]), orders))
        ids = []
        for i in orders:
            if free_weight >= i["weight"]:
                free_weight -= i["weight"]
                new_order = i
                new_order["courier_id"] = req["courier_id"]
                session.query(Order).filter_by(order_id=i["order_id"]).update(new_order)
                ids.append(i["order_id"])
        response = {"orders": [{"id": i} for i in ids], "assign_time": datetime.strftime(datetime.now(),
                                                                                         "%Y-%m-%dT%H:%M:%S." + str(
                                                                                             datetime.now().microsecond)[
                                                                                                                :2] + "Z")}
        response = jsonify(response)
        response.status_code = 200
        session.commit()

        return response


class OrdersCompleteResource(Resource):
    def post(self):
        req = request.get_json()
        for el in req.keys():
            if el not in ['courier_id', 'order_id', 'complete_time']:
                response = {"validation_error": {"couriers": {'wrong_data': el}}}
                response = jsonify(response)
                response.status_code = 400
                return response
        if not check_id(req['courier_id']):
            response = {"validation_error": {"couriers": {'courier_id': req['courier_id']}}}
            response = jsonify(response)
            response.status_code = 400
            return response
        if not check_id(req['order_id']):
            response = {"validation_error": {"couriers": {'order_id': req['order_id']}}}
            response = jsonify(response)
            response.status_code = 400
            return response

        abort_if_courier_not_found(req["courier_id"])
        abort_if_order_not_found(req["order_id"])
        session = db_session.create_session()
        courier = session.query(Courier).get(req["courier_id"]).as_dict()
        if session.query(Order).get(req["order_id"]).as_dict()["courier_id"] != req["courier_id"]:
            response = jsonify()
            response.status_code = 400
            return response
        order = session.query(Order).filter(Order.order_id == req["order_id"]).first()
        courier = session.query(Courier).filter(Courier.id == order.courier_id).first()
        payment_sum = int(order.weight) * (4 - int(courier.courier_type)) * 10
        payment = Payment(order_id=order.order_id, courier_id=courier.id, sum=payment_sum)
        session.add(payment)
        session.commit()
        session.query(Order).filter_by(order_id=req["order_id"]).update({"completed": True, "courier_id": None})
        response = {"order_id": req["order_id"]}
        response = jsonify(response)
        response.status_code = 200
        session.commit()
        return response


def order_complete(order_id):
    session = db_session.create_session()
    order = session.query(Order).filter(Order.order_id == order_id).first()
    courier = session.query(Courier).filter(Courier.id == order.courier_id).first()
    payment_sum = int(order.weight) * (4 - int(courier.courier_type)) * 10
    payment = Payment(order_id=order.order_id, courier_id=courier.id, sum=payment_sum)
    session.add(payment)
    session.commit()
    session.query(Order).filter_by(order_id=order_id).update({"completed": True, "courier_id": None})
    session.commit()


def assign(courier_id):
    session = db_session.create_session()
    courier = session.query(Courier).get(courier_id).as_dict()

    weight_courier = session.query(Order).filter_by(courier_id=courier_id).all()
    weight_courier = sum([i.as_dict()["weight"] for i in weight_courier])
    free_weight = courier_types[courier_types2[int(courier["courier_type"])]] - weight_courier

    courier_times = courier["working_hours"]
    orders = [i.as_dict() for i in
              session.query(Order).filter(and_(Order.courier_id == None, Order.completed == False)).all()]
    orders = list(filter(lambda a: check_regions(courier["regions"], a["region"]) and
                                   check_intersection(courier_times, a["delivery_hours"]), orders))
    ids = []
    for i in orders:
        if free_weight >= i["weight"]:
            free_weight -= i["weight"]
            new_order = i
            new_order["courier_id"] = courier_id
            session.query(Order).filter_by(order_id=i["order_id"]).update(new_order)
            ids.append(i["order_id"])
    session.commit()


def list_of_completed_orders():
    session = db_session.create_session()
    orders = session.query(Order).filter(Order.completed == True).all()
    return orders


def list_of_new_orders():
    session = db_session.create_session()
    orders = session.query(Order).filter(Order.completed == False, Order.courier_id == None).all()
    return orders
