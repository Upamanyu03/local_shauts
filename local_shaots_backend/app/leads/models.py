from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import declarative_base
from app import db

Base: declarative_base = db.Model


class Leads(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True)
    business_name = Column(String, nullable=False, unique=True)
    contact_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    email = Column(String, nullable=False)
    bussiness_address = Column(String, nullable=False)
    service_interest = Column(Integer, nullable=False)
    lead_status = Column(Integer, nullable=False)
    notes = Column(String, nullable=False)
    assigned_affiliate = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now())
