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
