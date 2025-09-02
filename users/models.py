from sqlalchemy import Column, String, Integer,Boolean,DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Role(Base):
    __tablename__="roles"
    id=Column(Integer, primary_key=True, autoincrement=True, index=True)
    name=Column(String)
    users=relationship("User", back_populates="role")
    


class User(Base):
    __tablename__="users"
    id=Column(Integer, primary_key=True, autoincrement=True, index=True)
    first_name=Column(String(40), index=True,nullable=False)
    last_name=Column(String(40), index=True,nullable=False)
    password=Column(String)
    email=Column(String, index=True, unique=True,nullable=False)
    joined=Column(DateTime, default= datetime.now)
    phone_number=Column(String, nullable=False)
    country=Column(String)
    address=Column(String,nullable=False)
    role_id=Column(ForeignKey("roles.id"), nullable=False)
    role=relationship("Role", back_populates="users")




class OTP(Base):
    __tablename__="tokens"
    id=Column(Integer, primary_key=True, autoincrement=True, index=True)
    codigo=Column(Integer())
    exp=Column(DateTime)
    used=Column(Boolean, default=False)
    user_id=Column(Integer, ForeignKey("users.id"), nullable=False)

