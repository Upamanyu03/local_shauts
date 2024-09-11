from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
    Date
)
from app import db
from sqlalchemy.ext.declarative import declarative_base

Base: declarative_base = db.Model

class DemoRegistration(Base):
    __tablename__: str = "demo_registration"
    id = Column(Integer, primary_key=True)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=False)
    phone = Column(Integer, nullable=False)
    state = Column(String, nullable=True)
    demo_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=db.func.now())
    deleted_at = Column(DateTime(timezone=True), default=func.now())