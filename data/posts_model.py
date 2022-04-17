import datetime
import sqlalchemy
from .users_model import User
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Post(SqlAlchemyBase):
    __tablename__ = 'posts'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.Text)
    created = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    author = sqlalchemy.Column(sqlalchemy.String, sqlalchemy.ForeignKey('users.id'))
    user = orm.relation('User')