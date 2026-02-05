from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from datetime import datetime
from .database import Base

class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    data = Column(Text, nullable=False)
    map_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    llm_name = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
class User(Base):
    __tablename__="admins"
    id=Column(Integer,primary_key=True,index=True)
    email=Column(String,nullable=False)
    password=Column(String,nullable=False)

class Question(Base):
    __tablename__="user_questions"
    id=Column(Integer,primary_key=True,index=True)
    question=Column(String,nullable=False)

class Answer(Base):
    __tablename__='answers'
    id=Column(Integer,primary_key=True,index=True)
    answer=Column(String,nullable=False)

class Images(Base):
    __tablename__='images'
    id=Column(Integer,primary_key=True,index=True)
    image=Column(String)
