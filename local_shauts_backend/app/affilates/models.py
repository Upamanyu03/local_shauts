from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Date,
    func,
)
from app import db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base: declarative_base = db.Model

class Affilate(Base):
    __tablename__ = 'affilate'
    affilate_id = Column(Integer, primary_key=True)
    affilate_name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    mobile_number = Column(String, nullable=False)
    address = Column(String, nullable=False)
    affilate_logo = Column(String, nullable=True)
    date = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), default=func.now())

    users = relationship('User', back_populates='affilate')

