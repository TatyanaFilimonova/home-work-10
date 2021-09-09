from  flask import Flask, redirect, url_for
from jinja2 import Template
from flask import request
from datetime import datetime, timedelta, time
from datetime import date
import os
from db import MONGO_DB, db, contact_db, counter_db, note_db
from pymongo import MongoClient
from bson.objectid import ObjectId
import re


class Contact():
    def __init__(self, json):
        self.name = json['name']
        self.contact_id = json['contact_id']
        self.birthday = json['birthday'].date().strftime('%d.%m.%Y')
        #self.birthday= datetime.strptime(str(json['birthday']), '%d.%m.%Y').date()
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

        
class Note():
    def __init__(self, json):
        self.note_id = json['note_id']
        self.keywords = json['keywords']
        if type(self.keywords)!=type(''):
            self.keywords = " #".join(self.keywords)
        self.created_at = json['created_at']
        self.text = json['text']        
    
    
def find_note_query(key):
    notes = []
    rgx = re.compile(f'.*{key}.*', re.IGNORECASE)
    result = note_db.find({'$or':[{'keywords':rgx},{'text':rgx}]})
    for res in result:
        notes.append(Note(res))
    return notes


def find_note_query_id(id):
    result = note_db.find_one({'note_id':int(id)})
    if result!=None:
        return Note(result)
    else:
        print(f"Result is {result}, id = {id}, type ID = {type(id)}")
        return None

    
def find_note_query_all():
    notes = []
    result = note_db.find({})
    for res in result:
        notes.append(Note(res))
    return notes


def note_update(id, request):
    try:
        note_db.replace_one({'note_id':int(id)},
                               {'note_id':int(id),
                                'created_at': datetime.today(),
                                'keywords': request.form.get('Keywords'),
                                'text': request.form.get('Text')
                                   } 
                           )
        return 0
    except Exception as e:
        return e

    
def get_all_contacts():
    contacts = []
    try:
        result = contact_db.find({})
        for res in result:
            contacts.append(Contact(res))
        return contacts
    except Exception as e:
        raise e
        
        
def get_contact_details(id):
     res = contact_db.find_one({'contact_id':int(id)})
     if res!= None:
         contact = Contact(res)
         return contact
     else:
         return res

    
def delete_contact_by_id (id):
    try:
        contact_db.delete_one({'contact_id':int(id)})
        return 0
    except Exception as e:
        return e

    
def insert_note(request):
    try:        
        counter = counter_db.find_one({"counter_name": 'note_id'},{'value':1})['value']
        counter_db.replace_one(
                          { "counter_name": 'note_id' },
                          { "counter_name": 'note_id',
                            "value": counter+1}
                              )  
        note_db.insert_one({
            'note_id': (counter+1),
            'keywords': request.form.get('Keywords'),
            'text': request.form.get('Text'),
            'created_at': datetime.today(),    
                          })
        return 0
    except Exception as e:
        return e

    
def delete_note_id(id):
    try:
        note_db.delete_one({'note_id':int(id)})
        return 0
    except Exception as e:
        return e

    
def update_contact_details(form_dict, id):
    try:
         contact_db.replace_one(
            {'contact_id':int(id)},
            {'contact_id':int(id),
             'name': form_dict['Name']['value'],
             'birthday': form_dict['Birthday']['value'],
             'created_at':datetime.today(),
             'phone':[phone_.strip()
                      for phone_ in form_dict['Phone']['value']
                          .split(",")
                      ],
              'email': form_dict['Email']['value'],
              'address':
                 {'zip': form_dict['ZIP']['value'],
                  'country': form_dict['Country']['value'],
                  'region': form_dict['Region']['value'],
                  'city': form_dict['City']['value'],
                  'street': form_dict['Street']['value'],
                  'house': form_dict['House']['value'],
                  'apartment':form_dict['Apartment']['value']
                  }
             }
            )
         return 0     
    except Exception as e:
        return e
    

def contact_query(k):    
    contacts = []
    rgx = re.compile(f'.*{k}.*', re.IGNORECASE)
    result = contact_db.find({'$or': [{'name':rgx}, {'phone':rgx}]})
    for res in result:
        contacts.append(Contact(res))
    return contacts


def insert_contact(form_dict):
    try:
        counter = counter_db.find_one({"counter_name": 'contact_id'},{'value':1})['value']
        counter_db.replace_one(
                          { "counter_name": 'contact_id' },
                          { "counter_name": 'contact_id',
                            "value": counter+1}
                             )  
        contact_db.insert_one(
            {'contact_id': counter+1,
             'name': form_dict['Name']['value'],
             'birthday': form_dict['Birthday']['value'],
             'created_at':datetime.today(),
             'phone':[phone_.strip()
                      for phone_ in form_dict['Phone']['value']
                          .split(",")
                      ],
              'email': form_dict['Email']['value'],
              'address':
                     {'zip': form_dict['ZIP']['value'],
                      'country': form_dict['Country']['value'],
                      'region': form_dict['Region']['value'],
                      'city': form_dict['City']['value'],
                      'street': form_dict['Street']['value'],
                      'house': form_dict['House']['value'],
                      'apartment':form_dict['Apartment']['value']
                      }
            })
        return 0  
    except Exception as e:
        return e


def get_birthdays(period):
    contacts = []
    max_id = counter_db.find_one({"counter_name": 'contact_id'},{'value':1})['value']
    contacts = []
    result= contact_db.aggregate([{
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
        contact_ = Contact(r)
        contact_.celebrate = r['birthday'].date().strftime('%d.%m.%Y')[0:5]
        contacts.append(contact_)
        datetime.strptime('Jun 1 2005  1:33PM', '%b %d %Y %I:%M%p')
        contacts = sorted(contacts, key = lambda x: datetime.strptime(x.birthday[0:6]+str(datetime.today().year),'%d.%m.%Y'))
    return contacts        
