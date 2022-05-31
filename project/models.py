from sqlalchemy import Column, Integer, String, Boolean, text, ForeignKey, Sequence
from sqlalchemy.sql.expression import null
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from project.database import Base
import datetime
from datetime import datetime


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    recipient_id = Column(String, nullable=False, unique=True)
    fullname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    verified = Column(String, nullable=False, server_default= '1')


class otps(Base):
    __tablename__ = "py_otps"
    id = Column(Integer, Sequence("otp_id_seq"), primary_key=True, nullable=False)
    recipient_id = Column(String(100))
    session_id = Column(String(100))
    otp_code = Column(String(6))
    status = Column(String(1))
    created_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    updated_on = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    otp_failed_count = Column(Integer)


class otp_blocks(Base):
    __tablename__ = "py_otp_blocks"
    id = Column(Integer, Sequence("otp_id_seq"), primary_key=True, nullable=False)
    recipient_id = Column(String(100))
    created_on = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
