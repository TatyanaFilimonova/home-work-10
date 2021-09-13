from pymongo import MongoClient
from bson.objectid import ObjectId
import random
from faker import Faker
fake = Faker()
import re
import os

MONGO_DB = os.environ.get('MONGOBD_HOST', "localhost")
client = MongoClient('mongodb://'+MONGO_DB+':27017/')
db = client.contact_book
contact_db = db.contact
counter_db = db.counter
note_db=db.note
 
from datetime import datetime, date, timedelta



def insert_users():
    contacts= []
    contacts_counter = {
                    "counter_name"  : "contact_id",
                    "value" : 0
                        }
    counter_db.insert_one(contacts_counter)
    try:
        for i in range(1000):
            counter_db.replace_one(
                          { "counter_name": 'contact_id' },
                          { "counter_name": 'contact_id',
                            "value": i}  )
            contact = {
                "contact_id": i,
                "name" : fake.first_name()+" "+fake.last_name(),
                "birthday": datetime.combine(fake.date_of_birth(tzinfo=None, minimum_age=18, maximum_age=73), datetime.min.time()), 
                "created_at": datetime.today(),
                "email": fake.company_email(),
                "phone": [fake.msisdn() for i in range(random.randrange(0,3,1))],
                "address": {
                            "zip":fake.postcode(), 
                            "country": fake.country(),
                            "region": "",
                            "city": fake.city(),
                            "street": fake.street_name(),
                            "house": fake.building_number(),
                            "apartment": random.randrange(1,100,1),
                             }
                }
            contacts.append(contact)             
        contact_db.insert_many(contacts)
        for element in contact_db.find({"contact_id": 10}).limit(10):
            print(element)
    except Exception as e:
        print(e)

def insert_notes():
    notes_counter = {
                    "counter_name"  : "note_id",
                    "value" : 0
                        }
    counter_db.insert_one(notes_counter)
    notes = []
    try:
        for i in range(1000):
            text = fake.text(max_nb_chars=250)
            note = {'note_id': i,
                    'text': text, 
                    'keywords': [word for word in text.split(" ")[0:random.randrange(2,5,1)]],
                    'created_at': datetime.today()
                    }
            notes.append(note)
            counter_db.replace_one(
                          { "counter_name": 'note_id' },
                          { "counter_name": 'note_id',
                            "value": i}
                             )        
                    
        note_db.insert_many(notes)            
                
    except Exception as e:
        print(e)

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
        
        
def get_birthdays(period):
    contacts = []
    max_id = counter_db.find_one({"counter_name": 'contact_id'},{'value':1})['value']
    contacts = []
    counter = 0
    while True:
        contact = contact_db.find_one({"contact_id":counter})
        counter+=1
        birthday = contact['birthday']
        d = datetime(birthday.year, 1,1,0)
        d1 = datetime(datetime.today().year, 1,1,0)
        delta = d1-d
        birthday_this_year = birthday+delta
        temp_contact = Contact(contact)
        if birthday_this_year >= datetime.today() and  birthday_this_year<=datetime.today()+timedelta(days = period):
            temp_contact.celebrate = birthday_this_year.date()
            contacts.append(temp_contact)
        print(temp_contact.contact_id," ", max_id," ", type(temp_contact.contact_id), " ", type(max_id))    
        if temp_contact.contact_id == max_id:
            break
    return contacts  

if __name__ == '__main__':                          
    #contact_db.drop_indexes()
    #note_db.drop_indexes()
    #rgx = re.compile('.* .*', re.IGNORECASE)
    #counter_db.delete_many({})
    #contact_db.delete_many({})
    #note_db.delete_many({})
    #insert_users()
    #insert_notes()
    #res = contact_db.index_information()
    #result = contact_db.create_index([('contact_id', 1)], unique = True) 
    #print(result)
    #result = note_db.create_index([('note_id', 1)], unique = True) 
    #print(result)
    #start_date = date.today()
    #print(d)
    #period = request.form.get('Period')
    #get_birthdays(10)

    '''res = contact_db.aggregate([{
                                 "$match": {"$expr":
                                       {'$eq': [{'$substr': [{"$dateToString":{"format": "%d.%m.%Y", "date": "$birthday"}}, 0 ,5]},'29.03']}
                                           } 
                                           
                                 }
                               ])

    res1 = contact_db.aggregate([{
                                 "$match": {"$expr":
                                       {'$in': [{'$substr': [{"$dateToString":{"format": "%d.%m.%Y", "date": "$birthday"}}, 0 ,5]},
                                                [(date_).strftime("%d.%m.%Y")[0:5] for date_ in date+i for i in range(0,period)]]}
                                           } 
                                           
                                 }
                               ])'''
    
    dates = [datetime.today+timedelta(days = i) for i in range(2)]
    print  (dates)
       

    
    #res = contact_db.find({{'$dateToString':{'format':"%Y-%m-%d", date:"$birthday"}}:" "})
    #res =contact_db.find_one({{'$dateToString':{'date': datetime.now()}} : str(datetime.today())})
    for r in res1:
        print(r)
    
    #for res in contact_db.find({}).sort("birthday"):
    #print(res)
    #    $lt: ISODate("2010-05-01T00:00:00.000Z")})
    #print(res, type(res)==type(""))
    #print([elem for elem in counter_db.find({"counter_name":"note_id"})])
    #print([elem for elem in contact_db.find({}).limit(1)])
