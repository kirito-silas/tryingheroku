from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from project import database, schemas, models, utils, oauth2
#from app.database import get_db


router = APIRouter(tags=['Authentication'])


@router.post('/login', response_model=schemas.Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    b = db.query(models.Users).filter(models.Users.verified == '1').delete()
    print(b)
    db.commit()
    user = db.query(models.Users).filter(models.Users.recipient_id == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    # return token
    access_token = oauth2.create_access_token(data= {"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
