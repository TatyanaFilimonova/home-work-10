from sqlalchemy import create_engine, or_, update
from sqlalchemy.orm import sessionmaker
from SQL_alchemy_classes import *
import os

POSTGRES_DB = os.environ.get('BD_HOST', "localhost")
engine = create_engine(
"postgresql+psycopg2://postgres:1234@"+POSTGRES_DB+"/contact_book",
echo=True)
DBSession = sessionmaker(bind=engine)
Base.metadata.bind = engine
session = DBSession()
