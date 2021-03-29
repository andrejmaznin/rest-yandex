import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Order(SqlAlchemyBase):
    __tablename__ = 'orders'

    order_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    weight = sqlalchemy.Column(sqlalchemy.FLOAT, nullable=False)
    region = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    delivery_hours = sqlalchemy.Column(sqlalchemy.ARRAY(sqlalchemy.String), nullable=False)
    courier_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("couriers.courier_id"))
    courier = orm.relation('Courier')
    completed = sqlalchemy.Column(sqlalchemy.BOOLEAN, nullable=False, default=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
