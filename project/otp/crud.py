from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from project import database, schemas, models
from sqlalchemy.orm import Session
# from project import database
from project.database import database


def find_otp_block(recipient_id: str):
    query = "SELECT * FROM py_otp_blocks WHERE recipient_id=:recipient_id " \
            "AND created_on >= now() at time zone  'UTC' - interval '5 minutes'"

    return database.fetch_one(query, values={"recipient_id": recipient_id})
    # return user


def save_otp(request: schemas.CreateOTP, session_id: str, otp_code: str):
    query = "INSERT INTO py_otps VALUES (nextval('otp_id_seq'), :recipient_id, :session_id, :otp_code," \
            "'1',now() at time  zone  'UTC', null, '0' )"
    return database.execute(query, values={"recipient_id": request.recipient_id, "session_id": session_id, "otp_code":otp_code})


def find_otp_lifetime(request: schemas.VerifyOTP):
    query = "SELECT * FROM py_otps WHERE  recipient_id=:recipient_id and session_id=:session_id and " \
            "created_on >=now() at time zone 'UTC' - interval '1 minutes'"
    return database.fetch_one(query, values={"recipient_id": request.recipient_id, "session_id": request.session_id})


def update_otp_failed_count(request: schemas.OTPList):
    query = "UPDATE py_otps SET otp_failed_count=otp_failed_count + 1 where recipient_id=:recipient_id " \
            "and session_id=:session_id and otp_code=:otp_code"
    return database.execute(query, values={"recipient_id": request.recipient_id, "session_id": request.session_id,
                                           "otp_code": request.otp_code})


def save_block_otp(request: schemas.OTPList):
    query = "INSERT INTO py_otp_blocks VALUES (:id, :recipient_id,now() at time zone 'UTC')"
    return database.execute(query, values={"recipient_id": request.recipient_id})


def disable_otp_code(request: schemas.OTPList):
    query = "UPDATE py_otps SET status= '9' WHERE status='1' AND recipient_id=:recipient_id" \
            " AND session_id=:session_id AND otp_code=:otp_code"
    return database.execute(query, values={"recipient_id": request.recipient_id, "session_id": request.session_id,
                                           "otp_code": request.otp_code})
