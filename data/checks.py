from datetime import datetime


def check_courier(courier):
    try:
        if len(list(courier.values())) == 4 and courier["courier_id"] and courier["regions"] and courier[
            "working_hours"] and courier["courier_type"]:
            return True
    except Exception:
        pass
    return False


def check_order(order):
    try:
        if len(list(order.values())) == 4 and order["order_id"] and order["region"] and order[
            "delivery_hours"] and order["weight"]:
            return True
    except Exception:
        pass
    return False


def check_intersection(list1, list2):
    print(list2)
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


# print(check_intersection(["6:10-7:00", "19:10-20:00"], ["18:50-19:00"]))
print(check_regions([11, 12, 13, 14], 15))
