from flask import jsonify, request
from flask_restful import Resource, abort
from werkzeug.security import generate_password_hash
from data.checks import *
from data import db_session
from data.orders import Order
from data.couriers import Courier
import json
from sqlalchemy import *
from datetime import datetime

courier_types = {"foot": 10,
                 "bike": 15, "car": 50}


def abort_if_order_not_found(order_id):
    session = db_session.create_session()
    orders = session.query(Order).get(order_id)
    if not orders:
        abort(400)


def abort_if_courier_not_found(order_id):
    session = db_session.create_session()
    orders = session.query(Courier).get(order_id)
    if not orders:
        abort(400)


class OrdersResource(Resource):
    def patch(self, id):
        abort_if_order_not_found(id)
        req = request.get_json()
        print(req)
        session = db_session.create_session()
        session.query(Order).filter_by(order_id=id).update(req)
        response = session.query(Order).get(id).as_dict()
        session.commit()
        response = jsonify(response)
        response.status_code = 200
        return response


class OrdersListResource(Resource):
    def post(self):
        req = request.get_json()
        print(request.base_url)
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

        session = db_session.create_session()
        courier = session.query(Courier).get(req["courier_id"]).as_dict()

        weight_courier = session.query(Order).filter_by(courier_id=req["courier_id"]).all()
        weight_courier = sum([i.as_dict()["weight"] for i in weight_courier])
        free_weight = courier_types[courier["courier_type"]] - weight_courier

        courier_times = courier["working_hours"]
        orders = [i.as_dict() for i in
                  session.query(Order).filter(and_(Order.courier_id == None, Order.completed == False)).all()]
        orders = list(filter(lambda a: check_regions(courier["regions"], a["region"]) and
                                       check_intersection(courier_times, a["delivery_hours"]), orders))
        print(orders)
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
        abort_if_courier_not_found(req["courier_id"])
        abort_if_order_not_found(req["order_id"])
        session = db_session.create_session()
        courier = session.query(Courier).get(req["courier_id"]).as_dict()
        if session.query(Order).get(req["order_id"]).as_dict()["courier_id"] != req["courier_id"]:
            response = jsonify()
            response.status_code = 400
            return response
        session.query(Order).filter_by(order_id=req["order_id"]).update({"completed": True, "courier_id": None})
        response = {"order_id": req["order_id"]}
        response = jsonify(response)
        response.status_code = 200
        session.commit()
        return response


def complete(order_id):
    session = db_session.create_session()
    session.query(Order).filter_by(order_id=order_id).update({"completed": True, "courier_id": None})
    session.commit()


def assign(courier_id):
    session = db_session.create_session()
    courier = session.query(Courier).get(courier_id).as_dict()

    weight_courier = session.query(Order).filter_by(courier_id=courier_id).all()
    weight_courier = sum([i.as_dict()["weight"] for i in weight_courier])
    free_weight = courier_types[courier["courier_type"]] - weight_courier

    courier_times = courier["working_hours"]
    orders = [i.as_dict() for i in
              session.query(Order).filter(and_(Order.courier_id == None, Order.completed == False)).all()]
    orders = list(filter(lambda a: check_regions(courier["regions"], a["region"]) and
                                   check_intersection(courier_times, a["delivery_hours"]), orders))
    print(orders)
    ids = []
    for i in orders:
        if free_weight >= i["weight"]:
            free_weight -= i["weight"]
            new_order = i
            new_order["courier_id"] = courier_id
            session.query(Order).filter_by(order_id=i["order_id"]).update(new_order)
            ids.append(i["order_id"])
    session.commit()
