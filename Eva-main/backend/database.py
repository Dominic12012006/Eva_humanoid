from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./eva.db"

engine = create_engine(
    "sqlite:////home/eva/Desktop/dominic/Eva-main/backend/eva.db",
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print("DATABASE IN USE:", engine.url)
Base = declarative_base()
