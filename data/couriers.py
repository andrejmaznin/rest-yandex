import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Courier(SqlAlchemyBase):
    __tablename__ = 'couriers'

    courier_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    courier_type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    regions = sqlalchemy.Column(sqlalchemy.ARRAY(sqlalchemy.INTEGER))
    working_hours = sqlalchemy.Column(sqlalchemy.ARRAY(sqlalchemy.TEXT))
    orders = orm.relation("Order", back_populates="courier")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
