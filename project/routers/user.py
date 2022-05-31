from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import delete, update
from project import models, schemas, utils
from project.database import get_db
from project.otp import routerotp, otp
from starlette.responses import RedirectResponse
#-------------------------
from project.otp import otp, crud, otpUtil, foremail
import uuid
from project.database import database
#--------------------

router = APIRouter(
    prefix="/users",
    tags=['Users']
)


# --------------------------------------------------------------------------
@router.post("/", status_code=status.HTTP_201_CREATED)#, response_model=schemas.UserOut)
async def create_user(request: schemas.CreateUsers, db: Session = Depends(get_db)):
    # create otp and verify
    user = db.query(models.Users).filter(models.Users.recipient_id == request.recipient_id).first()
    if not user:

        otp_blocks = await crud.find_otp_block(request.recipient_id)
        if otp_blocks:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sorry, this phone will be blocked in 5 min")

    # generate and save in py_otps table
        otp_code = otpUtil.random(6)
        session_id = str(uuid.uuid1())
        await crud.save_otp(request, session_id, otp_code)
        foremail.sendemail(request.recipient_id, otp_code)

    #await routerotp.send_otp(user.email, user.email)


    # hashing password
        hashed_password = utils.hash(request.password)
        request.password = hashed_password

        new_user = models.Users(**request.dict())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"recipient_id": request.recipient_id,
                "session_id": session_id,
                "otp_code": otp_code}
    else:
        return {"User already exists!!"}
    #return new_user

@router.post("/verify")
async def send_verify(request: schemas.VerifyOTP, db: Session = Depends(get_db)):
    user = request.recipient_id
    #new_user = models.Users(user)




    otp_blocks = await crud.find_otp_block(request.recipient_id)
    if otp_blocks:
        b = db.query(models.Users).filter(models.Users.verified == '1').delete()
        print(b)
        db.commit()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sorry, this phone will be blocked in 5 min")

    #check otp lifespan
    lifetime_result = await crud.find_otp_lifetime(request)
    if not lifetime_result:
        b = db.query(models.Users).filter(models.Users.verified == '1').delete()
        print(b)
        db.commit()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="OTP code has expired, please request a new one")


    lifetime_result = schemas.OTPList(**lifetime_result)
    print(lifetime_result)

    #check if OTP code is already used
    if lifetime_result.status == "9":

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="OTP code has been used, please request a new one")

    #verify OTP code
    if lifetime_result.otp_code != request.otp_code:
        await crud.update_otp_failed_count(lifetime_result)
        #increment OTP failed count
        #then block otp
        if lifetime_result.otp_failed_count + 1 == 5:
            await crud.save_block_otp(lifetime_result)
            b = db.query(models.Users).filter(models.Users.verified == '1').delete()
            print(b)
            db.commit()
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Failed")
        b = db.query(models.Users).filter(models.Users.verified == '1').delete()
        print(b)
        db.commit()
        #throw exception
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The OTP code you've entered is incorrect.")

    #disable OTP when success verified

    await crud.disable_otp_code(lifetime_result)
    #add user
    #changing values
    a = db.query(models.Users).filter(models.Users.recipient_id == request.recipient_id).first()
    print(a)
    a.verified = '0'
    db.commit()




    return {
        "status_code": status.HTTP_200_OK,
        "detail": "OTP verified successfully"
    }


@router.get("/{id}", response_model=schemas.UserOut)
async def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.Users).filter(models.Users.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {id} does not exists")
    return user
