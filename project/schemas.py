from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint

class CreateOTP(BaseModel):
    recipient_id: EmailStr

class UserOut(CreateOTP):
    id: int

    created_at: datetime

    class Config:
        orm_mode = True



class CreateUsers(CreateOTP):

    fullname: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    #email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


# --------------------------------------------------for otp---



class VerifyOTP(CreateOTP):
    session_id: str
    otp_code: str


class OTPList(VerifyOTP):
    otp_failed_count: int
    status: str

class Verifywithout(CreateOTP):
    recipient_id: str
    otp_code: str

