from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func,
)
from app import db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base: declarative_base = db.Model

class Roles(Base):
    __tablename__: str = "roles"
    id = Column(Integer, primary_key=True)
    role_name = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(),onupdate=db.func.now())
    

    users = relationship('User', back_populates='roles')
