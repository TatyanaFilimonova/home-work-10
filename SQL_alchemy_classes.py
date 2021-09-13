from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime ,func, UniqueConstraint, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
 
Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contact'
    contact_id = Column(Integer, primary_key=True,)
    name = Column(String(50), nullable=False)
    created_at = Column(Date, server_default=func.now(), nullable=False)
    birthday =Column(Date, nullable=True)
            

class Phone_(Base):
    __tablename__ = 'phone'
    phone_id = Column(Integer, primary_key=True,)
    phone = Column(String(15), nullable= True)
    contact_id = Column(Integer,ForeignKey('contact.contact_id', onupdate="CASCADE", ondelete="CASCADE") )
    contact = relationship("Contact")
    __table_args__ = (UniqueConstraint('phone', name='up_1'),)

class Email_(Base):
    __tablename__ = 'email'
    email_id = Column(Integer, primary_key=True,)
    email = Column(String(50), nullable=True)
    contact_id = Column(Integer,ForeignKey('contact.contact_id',onupdate="CASCADE", ondelete="CASCADE" ))
    contact = relationship("Contact")
    __table_args__ = (UniqueConstraint('email', name='ue_1'),)
 

class Address_(Base):
    __tablename__ = 'address'
    address_id = Column(Integer, primary_key=True,)
    zip = Column(String(10), default = '')
    country = Column(String(50), default = '')
    region = Column(String(50), default = '')
    city = Column(String(40), default = '')
    street = Column(String(50), default = '')
    house = Column(String(5), default = '')
    apartment = Column(String(5), default = '')
    contact_id = Column(Integer,ForeignKey('contact.contact_id',onupdate="CASCADE", ondelete="CASCADE" ))
    contact = relationship("Contact")

class Note_(Base):
    __tablename__ = 'note'
    note_id = Column(Integer, primary_key=True,)
    keywords =Column(String(250))
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    

class Text(Base):
    __tablename__ = 'text'
    text_id = Column(Integer, primary_key=True,)
    text = Column(String(500))
    note_id = Column(Integer,ForeignKey('note.note_id', onupdate="CASCADE", ondelete="CASCADE" ))
    note = relationship("Note_")
    

#engine = create_engine(
#   "postgresql+psycopg2://postgres:1234@pgdb/contact_book")
    
#DBSession = sessionmaker(bind=engine)
#session = DBSession()
#Base.metadata.bind = engine



