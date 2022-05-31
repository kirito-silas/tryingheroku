from fastapi import APIRouter, HTTPException, status
from project import schemas
from project.otp import otp, crud, otpUtil, foremail
import uuid
from project.routers import user

router = APIRouter(prefix="/registration/otp", tags=['OTPs'])



@router.post("/send")
async def send_otp(type: otp.OTPType, request: schemas.CreateOTP):
    #schemas.CreateOTP.recipient_id = schemas.CreateUsers.email
    #request.recipient_id = schemas.CreateUsers.email
    otp_blocks = await crud.find_otp_block(request.recipient_id)
    if otp_blocks:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sorry, this phone will be blocked in 5 min")

    #generate and save in py_otps table
    otp_code = otpUtil.random(6)
    session_id = str(uuid.uuid1())
    await crud.save_otp(request, session_id, otp_code)
    foremail.sendemail(request.recipient_id, otp_code)
    return {"recipient_id": request.recipient_id,
            "session_id": session_id,
            "otp_code": otp_code}

@router.post("/verify")
async def send_verify(request: schemas.VerifyOTP):
    otp_blocks = await crud.find_otp_block(request.recipient_id)
    if otp_blocks:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sorry, this phone will be blocked in 5 min")

    #check otp lifespan
    lifetime_result = await crud.find_otp_lifetime(request)
    if not lifetime_result:
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
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Failed")

        #throw exception
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The OTP code you've entered is incorrect.")

    #disable OTP when success verified
    await crud.disable_otp_code(lifetime_result)
    #add user
    #user.create_user()




    return {
        "status_code": status.HTTP_200_OK,
        "detail": "OTP verified successfully"
    }