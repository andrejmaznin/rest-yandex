from flask import jsonify, request
from flask_restful import Resource, abort
from werkzeug.security import generate_password_hash
from data.checks import *
from data import db_session
from data.couriers import Courier
from data.orders import Order
import json


def abort_if_courier_not_found(courier_id):
    session = db_session.create_session()
    couriers = session.query(Courier).get(courier_id)
    if not couriers:
        abort(400)


courier_types = {"foot": 10, "bike": 15, "car": 50}
courier_types2 = {1: "foot", 2: "bike", 3: "car"}
courier_types3 = {'1': 10, '2': 15, '3': 50}
courier_types4 = {"foot": '1', "bike": '2', "car": '3'}


class CouriersResource(Resource):
    def patch(self, id_c):
        abort_if_courier_not_found(id_c)
        req = request.get_json()
        session = db_session.create_session()

        # проверка данных
        if 'courier_type' in req:
            if not check_courier_type(req['courier_type']):
                response = {"validation_error": {"couriers": {'courier_type': req['courier_type']}}}
                response = jsonify(response)
                response.status_code = 400
                return response
        if 'regions' in req:
            if not check_courier_regions(req['regions']):
                response = {"validation_error": {"couriers": {'regions': req['regions']}}}
                response = jsonify(response)
                response.status_code = 400
                return response
        if 'working_hours' in req:
            if not check_hours(req['working_hours']):
                response = {"validation_error": {"couriers": {'working_hours': req['working_hours']}}}
                response = jsonify(response)
                response.status_code = 400
                return response
        for el in req.keys():
            if el not in ['courier_type', 'regions', 'working_hours']:
                response = {"validation_error": {"couriers": {'wrong_data': el}}}
                response = jsonify(response)
                response.status_code = 400
                return response

        session.query(Courier).filter_by(id=id_c).update(req)
        courier = session.query(Courier).get(id_c).as_dict()
        orders = [i.as_dict() for i in session.query(Order).filter_by(order_id=id_c).all()]
        weight_orders = weight = sum([i["weight"] for i in orders])
        weight_courier = courier_types3[courier["courier_type"]]
        for i in orders:
            if not check_intersection(courier["working_hours"], i["delivery_hours"]) or not check_regions(
                    courier["regions"], i["region"]):
                session.query(Order).filter_by(order_id=i["order_id"]).update({"courier_id": None})
        orders = list(sorted(orders, key=lambda a: a["weight"]))
        for i in orders:
            if weight <= weight_courier:
                break
            else:
                session.query(Order).filter_by(order_id=i["order_id"]).update({"courier_id": None})
                weight -= i["weight"]

        session.commit()
        response = session.query(Courier).get(id_c).as_dict()
        response = jsonify(response)
        response.status_code = 200

        return response


class CouriersListResource(Resource):
    def post(self):
        req = request.get_json()

        valid_ids = []
        invalid_ids = []
        session = db_session.create_session()

        couriers_list = req["data"]
        for i in couriers_list:
            if check_courier(i):
                courier = Courier(
                    id=i['id'],
                    courier_type=i['courier_type'],
                    regions=i['regions'],
                    working_hours=i['working_hours'])
                session.add(courier)
                valid_ids.append(i["id"])
            else:
                invalid_ids.append(i["id"])

        session.commit()

        if not invalid_ids:
            response = {"couriers": [{"id": i} for i in valid_ids]}
            response = jsonify(response)
            response.status_code = 201
            return response
        response = {"validation_error": {"couriers": [{"id": i} for i in invalid_ids]}}
        response = jsonify(response)
        response.status_code = 400
        return response
