from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy import ForeignKey

BASE = declarative_base()

class Group(BASE):
    __tablename__ = 'groups'
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    privacy = Column(String, nullable=False)
    members = Column(Integer)

class Feed(BASE):
    __tablename__ = 'feeds'
    id = Column(String, primary_key=True)
    message = Column(String, nullable=False)
    updated_time = Column(DateTime, nullable=False)

class Comment(BASE):
    __tablename__ = 'comments'
    id = Column(String, primary_key=True)
    feed_id = Column(String, ForeignKey("feeds.id"), nullable=False)
    from_id = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_time = Column(DateTime, nullable=False)
