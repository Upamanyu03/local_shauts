from sqlalchemy import Column, Integer, String,DateTime ,func
from sqlalchemy.orm import declarative_base
from app import db

Base : declarative_base = db.Model

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    address = Column(String, nullable=False)
    contact_no = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    age = Column(String, nullable=False)
    created_at = Column(DateTime, default=True)
    updated_at = Column(DateTime, default=True)
   

