from fastapi import FastAPI
from project import models
from project.database import engine
from project.routers import user, auth
from project.config import settings
from project.otp import routerotp
from project.database import database

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

#app.include_router(googleapi.router)
app.include_router(routerotp.router) #for otp

app.include_router(user.router)
app.include_router(auth.router)

@app.on_event('startup')
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
