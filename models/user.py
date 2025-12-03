# models/user.py
import os
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Read database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    @staticmethod
    def create_user(username, password):
        db = SessionLocal()
        if db.query(User).filter_by(username=username).first():
            db.close()
            return None, "Username already exists"
        user = User(username=username, password=password)
        db.add(user)
        db.commit()
        db.refresh(user)
        db.close()
        return user, None

    @staticmethod
    def authenticate(username, password):
        db = SessionLocal()
        user = db.query(User).filter_by(username=username, password=password).first()
        db.close()
        return user
