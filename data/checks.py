from datetime import datetime


def check_courier(courier):
    try:
        if len(list(courier.values())) == 4 and courier["id"] and courier["regions"] and courier[
            "working_hours"] and courier["courier_type"]:
            if not check_id(courier["id"]):
                return False
            if not check_courier_regions(courier["regions"]):
                return False
            if not check_hours(courier["working_hours"]):
                return False
            if not check_courier_type(courier["courier_type"]):
                return False
            return True
    except Exception:
        pass
    return False


def check_order(order):
    try:
        if len(list(order.values())) == 4 and order["order_id"] and order["region"] and order[
            "delivery_hours"] and order["weight"]:
            if not check_id(order["order_id"]):
                return False
            if not check_order_region(order["region"]):
                return False
            if not check_weight(order["weight"]):
                return False
            if not check_hours(order["delivery_hours"]):
                return False
            return True
    except Exception:
        pass
    return False


def check_intersection(list1, list2):
    list1 = [[datetime.strptime(i.split("-")[0], "%H:%M"), datetime.strptime(i.split("-")[1], "%H:%M")] for i in list1]
    list2 = [[datetime.strptime(i.split("-")[0], "%H:%M"), datetime.strptime(i.split("-")[1], "%H:%M")] for i in list2]
    for start1, finish1 in list1:
        for start2, finish2 in list2:
            if start2.time() < finish1.time() and start1.time() < finish2.time():
                return True
    return False


def check_regions(list1, region):
    if set(list1) & {region}:
        return True
    return False


def check_id(id):
    if id.__class__.__name__ != 'int':
        return False
    return True


def check_courier_type(type):
    if type not in ['foot', 'bike', 'car']:
        return False
    return True


def check_hours(hours):
    if hours.__class__.__name__ != "list":
        return False
    for h in hours:
        if h.__class__.__name__ != "str":
            return False
        if not (h[0].isdigit() and h[1].isdigit() and h[2] == ':' and h[3].isdigit() and h[4].isdigit() and h[
            5] == '-' and h[6].isdigit() and h[7].isdigit() and h[8] == ':' and h[9].isdigit() and h[
                    10].isdigit()) or len(h) != 11:
            return False
    return True


def check_courier_regions(regions):
    if regions.__class__.__name__ != "list":
        return False
    for el in regions:
        if el.__class__.__name__ != 'int':
            return False
    return True


def check_weight(weight):
    if weight.__class__.__name__ != 'float' and weight.__class__.__name__ != 'int':
        return False
    return True


def check_order_region(region):
    if region.__class__.__name__ != 'int':
        return False
    return True

