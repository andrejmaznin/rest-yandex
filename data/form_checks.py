from .db_session import create_session
from .users import User


def check_uniqe_login(login):
    session = create_session()
    if session.query(User).filter(User.login == login).first():
        return False
    return True


def check_times(time1, time2):
    if time1 >= time2:
        return False
    return True
