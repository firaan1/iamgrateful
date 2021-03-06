from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, Boolean
from sqlalchemy.orm import relation, sessionmaker, relationship, backref

from datetime import datetime
import os

# Database
DATABASE = 'sqlite:///db.sqlite3'
DEBUG = True

# ORM
Base = declarative_base()

# model
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    passcode = Column(Integer, nullable=False)
    question = Column(String)
    answer = Column(String)
    def __init__(self, passcode):
        self.passcode = passcode
    def __repr__(self):
        return '<User %s>' % {self.id}

class Memory(Base):
    __tablename__ = 'memory'
    # id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, primary_key = True)
    happiness = Column(Integer, default = 3)
    thing1 = Column(String, default = '')
    thing2 = Column(String, default = '')
    thing3 = Column(String, default = '')
    def __repr__(self):
        return '<Memory %s>' % {self.date}

# if __name__ == '__main__':
# connection
engine = create_engine(DATABASE, echo = DEBUG)
session_factory = sessionmaker(bind = engine)
session = session_factory()
# initialize database
if not os.path.exists('db.sqlite3'):
    Base.metadata.create_all(engine)
    