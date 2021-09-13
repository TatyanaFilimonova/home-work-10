from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from datetime import date
import time
import os
from db import MONGO_DB, db, contact_db, counter_db, note_db
from pymongo import MongoClient
from bson.objectid import ObjectId
import re
from SQL_alchemy_classes import *
from sqlalchemy import create_engine, or_, update, delete

class Contactbook(ABC):

    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def get_all_contacts(self):
        pass

    @abstractmethod
    def get_contacts(self, keys):
        pass

    @abstractmethod
    def get_contact_details(self, id):
        pass

    @abstractmethod
    def get_birthday(self, period):
        pass

    @abstractmethod
    def update_contact(self, contact, new_contact):
        pass

    @abstractmethod
    def insert_contact(self, contact):
        pass

    @abstractmethod
    def delete_contact(self, id):
        pass

class Mongo_contact_book(Contactbook):

    def __init__(self, contact_db = None, counter_db = None):
        self.contacts = []
        self.contact_db = contact_db
        self.counter_db = counter_db

    def get_all_contacts(self):
        self.contacts = []
        try:
            result = self.contact_db.find({})
            for res in result:
                self.contacts.append(Mongo_contact(res))
            return self.contacts    
        except Exception as e:
            raise e

    def get_contacts(self, keys):
        self.contacts = []
        try:
            rgx = re.compile(f'.*{keys}.*', re.IGNORECASE)
            result = self.contact_db.find({'$or': [{'name':rgx}, {'phone':rgx}]})
            for res in result:
                self.contacts.append(Mongo_contact(res))
            return self.contacts
        except Exception as e:
            raise e

    def get_contact_details(self, id):
        res = self.contact_db.find_one({'contact_id':int(id)})
        if res!= None:
            contact = Mongo_contact(res)
            return contact
        else:
            return res    

    def get_birthday(self, period):
        self.contacts = []
        result= self.contact_db.aggregate([{
                                 "$match":
                                 {"$expr":
                                       {'$in':
                                         [{'$substr':
                                           [{"$dateToString":
                                             {"format": "%d.%m.%Y", "date": "$birthday"}}, 0 ,5]},
                                               [(datetime.today()+timedelta(days =  i)).strftime("%d.%m.%Y")[0:5] for i in range(0,period)]]}
                                           } 
                                           
                                 }
                               ])
        for r in result:
            contact_ = Mongo_contact(r)
            contact_.celebrate = contact_.birthday[0:5]
            self.contacts.append(contact_)
            datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
            self.contacts = sorted(self.contacts, key = lambda x: datetime.strptime(x.birthday[0:6]+str(datetime.today().year),'%d.%m.%Y'))
        return self.contacts 


    def update_contact(self, id, contact):
        try:
            self.contact_db.replace_one(
                {'contact_id':int(id)},
                {'contact_id':int(id),
                 'name': contact.name,
                 'birthday': contact.birthday,
                 'created_at': contact.created_at,
                 'phone': contact.phone,
                  'email': contact.email,
                  'address':
                     {'zip': contact.zip,
                      'country': contact.country,
                      'region': contact.region,
                      'city': contact.city,
                      'street': contact.street,
                      'house': contact.house,
                      'apartment':contact.apartment
                      }
                 }
                )
            return 0     
        except Exception as e:
            return e

    def insert_contact(self, contact):
        try:
            counter = self.counter_db.find_one({"counter_name": 'contact_id'},{'value':1})['value']
            self.counter_db.replace_one(
                          { "counter_name": 'contact_id' },
                          { "counter_name": 'contact_id',
                            "value": counter+1}
                             )  
            self.contact_db.insert_one(
                {'contact_id': counter+1,
                 'name': contact.name,
                 'birthday': contact.birthday,
                 'created_at': contact.created_at,
                 'phone': contact.phone,
                 'email': contact.email,
                 'address':
                     {'zip': contact.zip,
                      'country': contact.country,
                      'region': contact.region,
                      'city': contact.city,
                      'street': contact.street,
                      'house': contact.house,
                      'apartment':contact.apartment
                      }
                 })
            return 0  
        except Exception as e:
            return "Some problem"

    def delete_contact(self, id):
        try:
            self.contact_db.delete_one({'contact_id':int(id)})
            return 0
        except Exception as e:
            return e


class PostgreSQL_contact_book(Contactbook):

    def __init__(self, session = None):
        self.contacts = []
        self.session = session
        
    def get_all_contacts(self):
        self.contacts = []
        try:
            result =self.session.query(Contact.contact_id, Contact.name)
            return result
        except Exception as e:
            raise e

    def get_contacts(self, key):
        result = self.session.query(
                    Contact.contact_id, Contact.name
                    ).join(Phone_).filter(
                        or_(func.lower(Contact.name).like(func.lower(f"%{key}%")
                        ), func.lower(Phone_.phone).like(func.lower(f"%{key}%"))))
        return result

    def get_contact_details(self, id):
        contact = self.session.query(Contact.contact_id, Contact.name, Contact.birthday).filter(Contact.contact_id == id)
        phone   = self.session.query(Phone_.phone).filter(Phone_.contact_id == id)
        email   = self.session.query(Email_.email).filter(Email_.contact_id == id)
        address = self.session.query(Address_).filter(Address_.contact_id == id)
        return Postgres_contact(contact[0], phone, email[0], address[0])   

    def get_birthday(self, period):
        sql_text=f'''
                select contact_id, name,  date(birthday+(date_trunc('year', now()) - date_trunc('year', birthday)))  as celebrate from contact
                where 
                birthday+(date_trunc('year', now()) - date_trunc('year', birthday)) 
                between 
                date_trunc('day', now()) 
                and 
                date_trunc('day', now()+interval '{period} day');
                '''    
        result = self.session.execute(sql_text).fetchall()
        return result 


    def update_contact(self, id, contact):
        try:
             self.session.execute(update(Contact, values={
                 Contact.name: contact.name,
                 Contact.birthday: contact.birthday}
                             ).filter(Contact.contact_id == id))
             self.session.commit()
             stmt = delete(Phone_).where(Phone_.contact_id == id)
             self.session.execute(stmt)    
             self.session.commit()
             for ph in contact.phone:
                 phone = Phone_(contact_id=id, phone = ph)
                 self.session.add(phone)
             stmt = delete(Address_).where(Address_.contact_id == id)
             self.session.execute(stmt)
             address = Address_(zip = contact.zip,
                                country = contact.country,
                                region = contact.region,
                                city = contact.city,
                                street = contact.street,
                                house = contact.house,
                                apartment =contact.apartment, 
                                contact_id = id)
             email=Email_(email = contact.email,
                          contact_id = id)
             self.session.add(address)
             stmt = delete(Email_).where(Email_.contact_id == id)
             self.session.execute(stmt)
             self.session.commit()
             self.session.add(email)
             self.session.commit()
             return 0     
        except Exception as e:
            return e
        finally:
            self.session.rollback()
        
    def insert_contact(self, contact):
        try:
            contact_= Contact(name = contact.name,
                         created_at= date.today(),
                         birthday = contact.birthday)
            self.session.add(contact)
            self.session.commit()
        except Exception as e:
            return e
        finally:
            self.session.rollback();
        try:    
            for ph in [phone_.strip() for phone_ in contact.phone]:
                phone = Phone_(contact_id=contact_.contact_id, phone = ph)
                self.session.add(phone)
            address = Address_(zip = contact.zip,
                                country = contact.country,
                                region = contact.region,
                                city = contact.city,
                                street = contact.street,
                                house = contact.house,
                                apartment =contact.apartment, 
                                contact_id = contact_.contact_id)
            email=Email_(email = contact.email,
                         contact_id = contact_.contact_id)
            self.session.add(address)
            self.session.add(email)
            self.session.commit()
        except Exception as e:
            return e
        finally:
            self.session.rollback()
        return 0    


    def delete_contact(self, id):
        try:
            stmt = delete(Contact).where(Contact.contact_id == id)
            self.session.execute(stmt)    
            self.session.commit()
            return 0
        except Exception as e:
            self.session.rollback()
            return e



class Contact_abstract(ABC):

    @abstractmethod
    def __init__(self):
        self.name = None
        self.contact_id = None
        self.created_at = None
        self.birthday = None
        self.phone = None
        self.email = None
        self.zip = None
        self.country = None
        self.region = None
        self.city = None
        self.street = None
        self.house = None
        self.apartment = None
        self.selebrate = None

class Mongo_contact(Contact_abstract):

    def __init__(self, json):
        self.name = json['name']
        self.created_at = datetime.today()
        self.contact_id = json['contact_id']
        if json['birthday'] == "" or json['birthday'] == None:
            self.birthday =""
        else:    
            self.birthday =json['birthday'].date().strftime('%d.%m.%Y')
        self.phone = json['phone']
        self.email = json['email']
        self.zip = json['address']['zip']
        self.country = json['address']['country']
        self.region = json['address']['region']
        self.city = json['address']['city']
        self.street = json['address']['street']
        self.house = json['address']['house']
        self.apartment = json['address']['apartment']
        self.selebrate =""

class Postgres_contact(Contact_abstract):

    def __init__(self, contact, phone, email, address):
        self.contact_id = contact.contact_id
        self.name = contact.name
        self.birthday = contact.birthday.strftime('%d.%m.%Y')
        self.phone=[]
        for p in phone:
            self.phone.append(p.phone)
        self.email = email.email
        self.zip = address.zip
        self.country = address.country
        self.region =  address.region
        self.city =  address.city
        self.street = address.street
        self.house = address.house
        self.apartment = address. apartment           

        
        
class Form_dict_contact(Contact_abstract):

    def __init__(self, form_dict):
        self.contact_id = None
        self.name =  form_dict['Name']['value']
        self.birthday =  form_dict['Birthday']['value']
        self.created_at = datetime.today()
        self.phone = [phone_.strip()
                      for phone_ in form_dict['Phone']['value']
                          .split(",")
                      ]
        self.email =  form_dict['Email']['value']
        self.zip = form_dict['ZIP']['value']
        self.country = form_dict['Country']['value']
        self.region =  form_dict['Region']['value']
        self.city =  form_dict['City']['value']
        self.street = form_dict['Street']['value']
        self.house = form_dict['House']['value']
        self.apartment = form_dict['Apartment']['value']            

      
