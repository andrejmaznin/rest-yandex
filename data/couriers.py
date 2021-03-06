import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from flask_login import UserMixin


class Courier(SqlAlchemyBase, UserMixin):
    __tablename__ = 'couriers'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    courier_type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    regions = sqlalchemy.Column(sqlalchemy.ARRAY(sqlalchemy.INTEGER))
    working_hours = sqlalchemy.Column(sqlalchemy.ARRAY(sqlalchemy.TEXT))
    orders = orm.relation("Order", back_populates="courier")
    login = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
