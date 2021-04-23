from data import db_session
from data.users import User


def check_uniqe_login(login):
    session = db_session.create_session()
    if session.query(User).filter(User.login == login).first():
        return False
    return True
