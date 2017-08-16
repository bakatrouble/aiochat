from uuid import UUID, uuid4
from datetime import datetime

from pony import orm

from utils import make_password, check_password

db = orm.Database()
db.bind(provider='postgres', user='aiochat', password='aiochat', database='aiochat')


class User(db.Entity):
    id = orm.PrimaryKey(UUID, default=uuid4)
    username = orm.Required(str, unique=True)
    password = orm.Required(str)
    rooms = orm.Set('Room')
    messages = orm.Set('Message')

    def set_password(self, new_password):
        self.password = make_password(new_password)
        orm.commit()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Room(db.Entity):
    id = orm.PrimaryKey(UUID, default=uuid4)
    name = orm.Required(str, unique=True)
    creator = orm.Required(User)
    messages = orm.Set('Message')
    # active = orm.Required(bool, default=False)


class Message(db.Entity):
    id = orm.PrimaryKey(UUID, default=uuid4)
    room = orm.Required(Room)
    author = orm.Required(User)
    created = orm.Required(datetime, default=datetime.now)
    modified = orm.Optional(datetime)
    text = orm.Optional(str)
    deleted = orm.Required(bool, default=False)


db.generate_mapping(create_tables=True)
