from  flask import Flask, redirect, url_for
from jinja2 import Template
from flask import request
from datetime import datetime, timedelta
from datetime import date
import time
import math
import re
import json
from neural_code import *
import os
from mongo_to_flask import *
from LRU_cache import *
from pymongo import MongoClient
from bson.objectid import ObjectId

import warnings 
warnings.filterwarnings('ignore')

app = Flask(__name__)

#####routes section############################

@app.route('/hello_', methods=['GET', 'POST'])
def hello_():
   return redirect('/bot-command')   

def validate_contact_data(request, form_dict):
    for key in form_dict.keys():
        if  re.search("^Hint", request.form.get(key)):
            form_dict[key]['value'] = ""
        else:
            form_dict[key]['value'] = request.form.get(key)
        res_tuple = form_dict[key]['checker'](form_dict[key]['value'])
        form_dict[key]['valid']  = res_tuple[0]
        form_dict[key]['error_message'] =res_tuple[1]
        form_dict[key]['value']= res_tuple[2]
    return form_dict

def Name_checker(name):
    error_message  = ""
    valid = True
    if len(name)>50:
        error_message  = "Max len of Name is 50 char"
        valid = False
    return valid, error_message, name    
        
def Birthday_checker(birthday):
    error_message  = ""
    valid = True
    if re.search('\d{2}\.\d{2}\.\d{4}', birthday) == None:
        error_message  = "Use dd.mm.yyyy format"
        valid = False
    else:
        birthday = datetime.strptime(birthday, '%d.%m.%Y')
    return valid, error_message, birthday

def Phone_checker(phones):
    error_message  = ""
    valid = True
    for phone in phones.split(","):
        if re.search('\+{0,1}\d{9,13}', phone.strip()) == None:
            error_message  = """Phone should have format: '[+] XXXXXXXXXXXX' (9-12 digits), phones separated by ','"""
            valid = False
    return valid, error_message, phones

def ZIP_checker(zip):
    error_message  = ""
    valid = True
    if len(zip)>10:
        error_message  = "Max len of ZIP is 10 char"
        valid = False
    return valid, error_message, zip

def Country_checker(Country):
    error_message  = ""
    valid = True
    if len(Country)>50:
        error_message  = "Max len of Country is 50 char"
        valid = False
    return valid, error_message, Country

def Region_checker(Region):
    error_message  = ""
    valid = True
    if len(Region)>50:
        error_message  = "Max len of Region is 50 char"
        valid = False
    return valid, error_message, Region

def City_checker(City):
    error_message  = ""
    valid = True
    if len(City)>40:
        error_message  = "Max len of City is 40 char"
        valid = False
    return valid, error_message, City

def Street_checker(Street):
    error_message  = ""
    valid = True
    if len(Street)>50:
        error_message  = "Max len of Street is 50 char"
        valid = False
    return valid, error_message, Street

def House_checker(House):
    error_message  = ""
    valid = True
    if len(House)>5:
        error_message  = "Max len of House is 5 char"
        valid = False
    return valid, error_message, House

def Apartment_checker(Apartment):
    error_message  = ""
    valid = True
    if len(Apartment)>5:
        error_message  = "Max len of House is 5 char"
        valid = False
    return valid, error_message, Apartment

def Email_checker(email):
    error_message  = ""
    valid = True
    if re.search('[a-zA-Z0-9\.\-\_]+@[a-zA-Z0-9\-\_\.]+\.[a-z]{2,4}', email) == None:
        error_message  = "Email should have format: 'name@domain.[domains.]high_level_domain'"
        valid = False
    return valid, error_message, email

form_dict_temp = {"Name":{
                           "value": "Hint: Input first and second name in one row",
                           "valid": True,
                           "checker": Name_checker,
                           "error_message":""
                         },
                  "Birthday":
                        {
                           "value":"Hint: Use dd.mm.yyyy format",
                           "valid": True,
                           "checker": Birthday_checker,
                           "error_message":""
                        },
                 "Email":
                        {
                           "value":"Hint: Use user@domain format",
                           "valid": True,
                           "checker": Email_checker,
                           "error_message":""
                        },
                 "Phone":
                        {
                           "value":"Hint: Use + or digits only, phones separate by ','",
                           "valid": True,
                           "checker": Phone_checker,
                           "error_message":""
                        },    
                 "ZIP":
                        {
                           "value":"Hint: Up to 10 char",
                           "valid": True,
                           "checker": ZIP_checker,
                           "error_message":""
                        },
                 "Country":
                        {
                           "value":"Hint: Up to 50 char",
                           "valid": True,
                           "checker": Country_checker,
                           "error_message":""
                        },
                 "Region":
                        {
                           "value":"Hint: Up to 50 char",
                           "valid": True,
                           "checker": Region_checker,
                           "error_message":""
                        },
                 "City":
                        {
                           "value":"Hint: Up to 40 char",
                           "valid": True,
                           "checker": City_checker,
                           "error_message":""
                        },
                 "Street":
                        {
                           "value":"Hint: Up to 50 char",
                           "valid": True,
                           "checker": Street_checker,
                           "error_message":""
                        },
                 "House":
                        {
                           "value":"",
                           "valid": True,
                           "checker": House_checker,
                           "error_message":""
                        },
                 "Apartment":
                        {
                           "value":"",
                           "valid": True,
                           "checker": Apartment_checker,
                           "error_message":""
                        },
                }

@app.route('/add_contact', methods=['GET', 'POST'])
def add_contact():
    form_dict = form_dict_temp
    if request.method == 'POST':
        form_dict = validate_contact_data(request, form_dict)
        valid_list = [element['valid'] for element in form_dict.values()]
        if False not in  valid_list:
            res = insert_contact(form_dict)
            if res == 0:
               return f'''<h3>Contact successfully saved</h2>
                       <p></p> 
                       <p align = 'center'><a href="./add_contact">Add one more contact</a></p>
                       <p></p>
                       <p align = 'center'><a href="./bot-command">Return to BOT embrace</a></p>                 
                       '''
            else:
               return html_error(res)
        else:
            pass
    try:  
       with open('html/add_user/add_user.html', 'r') as file:
          t = Template(file.read())
          return t.render(form_dict = form_dict)
    except:
       return html_error(e)

    
@app.route('/edit_contact', methods=['GET', 'POST'])
def edit_contact():
    results = []
    if request.method == 'POST':
        keywords = clean_search_str(request.form.get('Keywords'))
        for k in [keyword for keyword in keywords.strip().split(" ")]:
            results.extend(contact_query(k))
        try:
            with open('html/edit_user/user_found.html', 'r') as file:
                 t = Template(file.read())
                 return t.render(result = results)
        except Exception as e:
             return html_error(e)  
    else:    
        try:
            with open('html/find_user/find_user.html', 'r') as file:
                t = Template(file.read())
                return t.render()
        except Exception as e:
                 return html_error(e)

@app.route('/edit_contact/<id>', methods=['GET', 'POST'])
def edit_contact_(id):
     form_dict = form_dict_temp
     if request.method == 'POST':
        form_dict = validate_contact_data(request, form_dict)
        valid_list = [element['valid'] for element in form_dict.values()]
        if False not in  valid_list:
            res= update_contact_details(form_dict, id)   
            if res == 0:
               return f'''<h3 align = 'center'>Contact successfully saved with ID = {id}</h2>
                           <p></p> 
                           <p align = 'center'><a href="/edit_contact">Edit one more contact</a></p>
                           <p></p>
                           <p align = 'center'><a href="/bot-command">Return to BOT embrace</a></p>
                           '''
            else:
               return html_error(res)
        else:
             with open('html/edit_user/edit_user.html', 'r') as file:
                 t = Template(file.read())
                 return t.render(form_dict = form_dict)
     else:
         contact = get_contact_details(id)
         bd = str(contact.birthday).split("-")   
         form_dict["Name"]["value"]= contact.name
         form_dict["Birthday"]["value"] = str(contact.birthday)
         form_dict["Email"]["value"] = contact.email
         form_dict["Phone"]["value"] =  ", ".join([ph for ph in contact.phone])   
         form_dict["ZIP"]["value"] = contact.zip
         form_dict["Country"]["value"] = contact.country
         form_dict["Region"]["value"] = contact.region
         form_dict["City"]["value"] = contact.city
         form_dict["Street"]["value"] = contact.street
         form_dict["House"]["value"] = contact.house
         form_dict["Apartment"]["value"] = contact.apartment
         with open('html/edit_user/edit_user.html', 'r') as file:
             t = Template(file.read())
             return t.render(form_dict = form_dict)

@app.route('/find_contact', methods=['GET', 'POST'])
def find_contact():
    results = []
    if request.method == 'POST':
        keywords = clean_search_str(request.form.get('Keywords'))
        for k in [keyword for keyword in keywords.strip().split(" ")]:
            results.extend(contact_query(k))
        try:
            with open('html/find_user/user_found.html', 'r') as file:
                 t = Template(file.read())
                 return t.render(result = results)
        except Exception as e:
             return html_error(e)        

    try:
        with open('html/find_user/find_user.html', 'r') as file:
            t = Template(file.read())
            return t.render()
    except Exception as e:
            return html_error(e)


def clean_search_str(keywords):
   keywords = (
     keywords.replace("+","\+")
            .replace("*", "\*")
            .replace("{", "\{")
            .replace("}", "\}")
            .replace("[", "\[")
            .replace("]", "\]")
            .replace("?", "\?")
            .replace("$", "\$")
            .replace("'\'", "\\")
             )
   return keywords
         
        
@app.route('/find_notes', methods=['GET', 'POST'])
def find_notes():
    res_list = []
    if request.method == 'POST':
        keywords = clean_search_str(request.form.get('Keywords'))
        for k in [keyword.strip() for keyword in keywords.split(",")]:
           result = find_note_query(k)
        try:
            with open('html/find_note/find_notes_found.html', 'r') as file:
                t = Template(file.read())
                return t.render(result = result)
        except Exception as e:
                 return html_error(e)
    else:    
        try:
            with open('html/find_note/find_notes_search.html', 'r') as file:
                t = Template(file.read())
                return t.render()
        except Exception as e:
                 return html_error(e)

@app.route('/show_all_contacts', methods=['GET', 'POST'])
def show_all_contacts():
    if request.method == 'POST':
        return redirect('/bot-command')
    else:
        try:
            result = get_all_contacts()
        except Exception as e:
            return html_error(e)
            
        try:
            with open('html/all_contacts/all_contacts.html', 'r') as file:
                t = Template(file.read())
                return t.render(count = 0, result = result)
        except Exception as e:
            return html_error(e)
        

def html_error(error):
    return f'''<html>
           <p><b>There was an error while your request handled</b><p>
           <p>The details of error you could find below.</p>
           <p>Please return to the BOT section and try another request</p>
           <p>{error}</p>
           <p><a href="./bot-command">Return to BOT embrace</a></p>
           </html>'''


@app.route('/contact_detail/<id>', methods=['GET', 'POST'])
def contact_detail(id):
     contact = get_contact_details(id)
     try:
         with open('html/user_details/user_details.html', 'r') as file:
             t = Template(file.read())
             return t.render(contact = contact, phone = contact.phone, email = contact.email, address = contact)
     except Exception as e:
             return html_error(e)
         
@app.route('/show_all_notes', methods=['GET', 'POST'])
def show_all_notes ():
    if request.method == 'POST':
        return redirect('/bot-command')
    else:
        result =find_note_query_all()
        try:
            with open('html/all_notes/all_notes.html', 'r') as file:
                t = Template(file.read())
                return t.render(result = result)
        except Exception as e:
             return html_error(e)
                    
            
@app.route('/help_', methods=['GET', 'POST'])
def help_():
    try:
        with open('html/help/help.html', 'r') as file:
                t = Template(file.read())
                return t.render(exec_command = exec_command)
    except Exception as e:
             return html_error(e)


@app.route('/add_note', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        res = insert_note(request)
        if res ==0:
            return f'''<h3>Note successfully saved </h2>
                       <p></p> 
                       <p align = 'center'><a href="./add_note">Add one more note</a></p>
                       <p></p>
                       <p align = 'center'><a href="./bot-command">Return to BOT embrace</a></p>'''
        else:
            return html_error(res)
    with open('html/add_note/add_note.html', 'r') as file:
         t = Template(file.read())
         return t.render()


@app.route('/edit_note', methods=['GET', 'POST'])
def edit_note():
    res_list = []
    if request.method == 'POST':
        keywords = clean_search_str(request.form.get('Keywords'))
        for k in [keyword.strip() for keyword in keywords.split(",")]:
            result = find_note_query(k)
        try:
            with open('html/edit_notes/edit_notes_found.html', 'r') as file:
                t = Template(file.read())
                return t.render(result = result)
        except Exception as e:
                 return html_error(e)
    else:    
        try:
            with open('html/edit_notes/edit_notes_search.html', 'r') as file:
                t = Template(file.read())
                return t.render()
        except Exception as e:
                 return html_error(e)

@app.route('/save_note/<id>', methods=['GET', 'POST'])
def save_note(id):
    if request.method == 'POST':
        res = note_update(id, request) 
        if  res== 0:
           return f'''<h3>Note successfully updated</h2>
                   <p></p> 
                   <p align = 'center'><a href="/add-note">Add one more note</a></p>
                   <p></p>
                   <p align = 'center'><a href="/bot-command">Return to BOT embrace</a></p>                   
                   '''
        else:
            return html_error(res) 
    else:
        result =find_note_query_id(id)
        try:
            with open('html/edit_notes/edit_notes_save.html', 'r') as file:
                t = Template(file.read())
                return t.render(res = result)
        except Exception as e:
                 return html_error(e)
            
    
@app.route('/delete_contact', methods=['GET', 'POST'])
def delete_contact():
    results = []
    if request.method == 'POST':
        keywords = clean_search_str(request.form.get('Keywords'))
        for k in [keyword for keyword in keywords.strip().split(" ")]:
            results.extend(contact_query(k))
        try:
            with open('html/delete_user/user_to_delete.html', 'r') as file:
                 t = Template(file.read())
                 return t.render(result = results)
        except Exception as e:
             return html_error(e)        

    try:
        with open('html/find_user/find_user.html', 'r') as file:
            t = Template(file.read())
            return t.render()
    except Exception as e:
            return html_error(e)

@app.route('/delete_contact/<id>', methods=['GET', 'POST'])
def contact_delete_(id):
    res = delete_contact_by_id (id)
    if res ==0: 
        return f'''
               <html>
               <h2 align = 'center'> Contact ID = {id} succesfully deleted</h2>
               <p></p> 
               <p align = 'center'> <a href="/delete_contact">Delete one more contact</a></p>
               <p></p>
               <p align = 'center'><a href="/bot-command">Return to BOT embrace</a></p>
               
               </html>
               '''
    else:
        return html_error(res)

          

@app.route('/delete_note', methods=['GET', 'POST'])
def delete_note():
    res_list = []
    if request.method == 'POST':
        keywords = clean_search_str(request.form.get('Keywords'))
        for k in [keyword.strip() for keyword in keywords.split(",")]:
           result = find_note_query(k)
        try:
            with open('html/delete_note/delete_notes_found.html', 'r') as file:
                t = Template(file.read())
                return t.render(result = result)
        except Exception as e:
                 return html_error(e)
    else:    
        try:
            with open('html/delete_note/delete_notes_search.html', 'r') as file:
                t = Template(file.read())
                return t.render()
        except Exception as e:
                 return html_error(e)

@app.route('/delete_note/<id>', methods=['GET', 'POST'])
def note_delete_(id):
    res = delete_note_id(id)
    if res == 0:
        return f'''
               <html>
               <h2 align = 'center'> Note ID = {id} succesfully deleted</h2>
               <p></p> 
               <p><a href="/delete_note">Delete one more note</a></p>
               <p></p>
               <p><a href="/bot-command">Return to BOT embrace</a></p>
               </html>
               '''
    else:
        return html_error(res)                


@app.route('/sort_notes', methods=['GET', 'POST'])
def sort_notes():
   return redirect('/bot-command')


@app.route('/sort_folder', methods=['GET', 'POST'])
def sort_folder():
   return redirect('/bot-command')


def get_period(message=""):
   try:
      with open('html/list_birthday/find_user.html', 'r') as file:
         t = Template(file.read())
         return t.render(err_message = message)
   except Exception as e:
            return html_error(e)


@app.route('/next_birthday', methods=['GET', 'POST'])
def next_birthday():
   message =""
   if request.method == 'POST':
      try:
         period = int(request.form.get('Period'))
         res = get_birthdays(period)
      except:
         return get_period("You could use numbers only")  
      try:
         with open('html/list_birthday/user_found.html', 'r') as file:
            t = Template(file.read())
            return t.render(days = request.form.get('Period'), result = res)
      except Exception as e:
                return html_error(e)
   else:
      return get_period()   
        
    
exec_command = { 
    "hello": [hello_,                  "hello:              Greetings", 0], 
    "add contact":  [add_contact,      "add contact:        Add a new contact", 2], 
    "edit contact": [edit_contact,     "edit contact:       Edit the contact detail", 2], 
    "find contact": [find_contact,    "find contact:       Find the records by phone or name", 1], 
    "find notes":   [find_notes,       "find notes:         Find the notes by text or keywords", 1], 
    "show all contacts":[show_all_contacts, "show all contacts:  Print all the records of adress book, page by page", 0],
    "show all notes":[show_all_notes,  "show all_notes:     Print all the records of adress book, page by page", 0], 
    "help": [help_,                    "help:               Print a list of the available commands",0],  
    "add note": [add_note,             "add note:           Add new text note ", 0],
    "edit note": [edit_note,           "edit note:          Edit existing text note ", 0],
    "delete contact": [delete_contact, "delete contact:     Delete contact", 2], 
    "delete note": [delete_note,       "delete note:        Delete text note", 2], 
    "sort notes": [sort_notes,         "sort note:          Sort of the notes by keywords", 2], 
    "sort folder": [sort_folder,       "sort_folder:        Sort selected folder by file types", 2],
    "next birthday": [next_birthday,   "next birthday:      Let you the contats with birthdays in specified period", 2],
             }


@LRU_cache (max_len = 10)         
def listener(message):
    ints = predict_class(message)
    res = get_response(ints, intents)
    return res[1]

command_history = {"command":"response"}

@app.route('/', methods=['GET', 'POST'])
def start_page():
 return redirect('/bot-command')   

@app.route('/bot-command', methods=['GET', 'POST'])
def form_example():
    # handle the POST request
    if request.method == 'POST':
        command = request.form.get('BOT command')
        user_request_detailed = listener(command)
        redirect_to = "_".join(user_request_detailed.split(" "))
        if redirect_to == 'help':
            redirect_to+="_"
        elif redirect_to == 'hello':
            redirect_to+="_"    
        command_history[command]=user_request_detailed    
        return redirect(url_for(redirect_to))
                  

    # otherwise handle the GET request
    try:
            with open('html/bot_page.html', 'r') as file:
                t = Template(file.read())
                return t.render(command_history = command_history)
    except Exception as e:
                 return html_error(e)
   
MONGO_DB = os.environ.get('MONGOBD_HOST', "localhost")
client = MongoClient('mongodb://'+MONGO_DB+':27017/')
db = client.contact_book
contact_db = db.contact
counter_db = db.counter
note_db=db.note

if __name__ == "__main__":
     app.run(debug=True)
