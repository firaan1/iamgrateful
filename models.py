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
    id = Column(Integer, primary_key=True, autoincrement=True)
    happiness = Column(Integer)
    date = Column(DateTime, default = datetime.now())
    things = relationship('Thing', secondary = 'memory_thing_link')
    def __repr__(self):
        return '<Memory %s>' % {self.date}

class Thing(Base):
    __tablename__ = 'thing'
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text)
    def __repr__(self):
        return '<Item %s>' % {self.text}

class MemoryThingLink(Base):
    __tablename__ = 'memory_thing_link'
    memory_id = Column(Integer, ForeignKey('memory.id'), primary_key=True)
    thing_id = Column(Integer, ForeignKey('thing.id'), primary_key=True)

# if __name__ == '__main__':
# connection
engine = create_engine(DATABASE, echo = DEBUG)
session_factory = sessionmaker(bind = engine)
session = session_factory()
# initialize database
if not os.path.exists('db.sqlite3'):
    Base.metadata.create_all(engine)
    