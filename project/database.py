from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from project.config import settings
import databases
import psycopg2
from psycopg2.extras import RealDictCursor
import time



SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:silash@localhost/firsttimeapi'

#later added by me
database = databases.Database(SQLALCHEMY_DATABASE_URL)

#---------------------------------------------

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




# while True:
#    try:
#        conn = psycopg2.connect(host='localhost', database='firsttimeapi', user='postgres', password='silash',
#                                cursor_factory=RealDictCursor)
#       cursor = conn.cursor()
#        print("database is connected")
#        break
#    except Exception as error:
#        print("connecting to database failed")
#        print("Error:", error)
#        #time.sleep(2)
