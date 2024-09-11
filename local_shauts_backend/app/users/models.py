from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    func,
)
from app import db
import bcrypt
from sqlalchemy.orm import relationship

Base = db.Model

class User(Base):
    __tablename__ = "users"
    id  = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    affilate_id = Column(Integer, ForeignKey('affilate.affilate_id'))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    profile_pic = Column(String, nullable=False)
    details = Column(String, nullable=False)
    flag = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    roles = relationship('Roles', back_populates='users')
    affilate = relationship('Affilate', back_populates='users')



    def __init__(self, role_id, affilate_id, name, email, password, details, flag):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.affilate_id = affilate_id
        self.role_id = role_id
        self.details = details
        self.flag = flag