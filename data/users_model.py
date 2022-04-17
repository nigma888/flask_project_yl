import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm

from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase


subscriptions = sqlalchemy.Table(
    'subscriptions',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('user', sqlalchemy.String,
                      sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('subscribe_on', sqlalchemy.String,
                      sqlalchemy.ForeignKey('users.id'))
)


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def __repr__(self):
        return f'<User> {self.id} {self.email}'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


