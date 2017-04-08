from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String

BASE = declarative_base()

class Group(BASE):
    __tablename__ = 'groups'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    privacy = Column(String, nullable=False)
    members = Column(Integer)
