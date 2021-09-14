#global packages
from  flask import Flask, redirect, url_for
from jinja2 import Template
from flask import request
import time
import re
import os
import warnings 
warnings.filterwarnings('ignore')

#local packages
from neural_code import *
from LRU_cache import *
from db_mongo import MONGO_DB, db, contact_db, counter_db, note_db
from db_postgres import session
from contacts_data_classes import *
from notes_data_classes import *
from validate import *


app = Flask(__name__)
contact_book = None 
note_book = None
command_history = {"command":"response"}

#####routes section############################

#Choose the DB engine (mongo or postgres)
@app.before_request
def before_request():
   global contact_book
   global note_book
   if (contact_book == None or note_book == None) and request.endpoint!= 'start_page':
        return redirect('/login')



@app.route('/hello_', methods=['GET', 'POST'])
def hello_():
   return redirect('/bot-command')   


@app.route('/add_contact', methods=['GET', 'POST'])
def add_contact():
    form_dict = form_dict_temp
    if request.method == 'POST':
        form_dict = validate_contact_data(request, form_dict)
        valid_list = [element['valid'] for element in form_dict.values()]
        if False not in  valid_list:
            res = contact_book.insert_contact(Form_dict_contact(form_dict))
            if res == 0:
               return render_template('html/add_user/OK.html')
            else:
               return html_error(res)
        else:
            pass
    return render_template('html/add_user/add_user.html', form_dict = form_dict)
  

    
@app.route('/edit_contact', methods=['GET', 'POST'])
def edit_contact():
    results = []
    if request.method == 'POST':
        keywords = clean_search_str(request.form.get('Keywords'))
        for k in [keyword for keyword in keywords.strip().split(" ")]:
            results.extend(contact_book.get_contacts(k))
        return render_template('html/edit_user/user_found.html', result = results)   
    else:
        return render_template('html/find_user/find_user.html')           
        

@app.route('/edit_contact/<id>', methods=['GET', 'POST'])
def edit_contact_(id):
   form_dict = form_dict_temp
   if request.method == 'POST':
      form_dict = validate_contact_data(request, form_dict)
      valid_list = [element['valid'] for element in form_dict.values()]
      if False not in  valid_list:
         res= contact_book.update_contact(id, Form_dict_contact(form_dict))   
         if res == 0:
            return render_template('html/edit_user/OK.html')
         else:
               return html_error(res)
      else:
            return render_template('html/edit_user/edit_user.html', form_dict = form_dict)

   else:
      contact = contact_book.get_contact_details(id)
      form_dict["Name"]["value"]= contact.name
      form_dict["Birthday"]["value"] = contact.birthday
      form_dict["Email"]["value"] = contact.email
      form_dict["Phone"]["value"] =  ", ".join([ph for ph in contact.phone])   
      form_dict["ZIP"]["value"] = contact.zip
      form_dict["Country"]["value"] = contact.country
      form_dict["Region"]["value"] = contact.region
      form_dict["City"]["value"] = contact.city
      form_dict["Street"]["value"] = contact.street
      form_dict["House"]["value"] = contact.house
      form_dict["Apartment"]["value"] = contact.apartment
      return render_template('html/edit_user/edit_user.html', form_dict = form_dict)

@app.route('/find_contact', methods=['GET', 'POST'])
def find_contact():
   results = []
   if request.method == 'POST':
      keywords = clean_search_str(request.form.get('Keywords'))
      for k in [keyword for keyword in keywords.strip().split(" ")]:
         for res in contact_book.get_contacts(k):
            if res not in results:
               results.append(res)
      return render_template('html/find_user/user_found.html', result = results)    
   else:
      return render_template('html/find_user/find_user.html')

        
@app.route('/find_notes', methods=['GET', 'POST'])
def find_notes():
   results = []
   if request.method == 'POST':
      keywords = clean_search_str(request.form.get('Keywords'))
      for k in [keyword.strip() for keyword in keywords.split(",")]:
         for res in note_book.get_notes(k):
            if res not in results:
               results.append(res)
      return render_template('html/find_note/find_notes_found.html', result = results)   
   else:
      return render_template('html/find_note/find_notes_search.html')
       

@app.route('/show_all_contacts', methods=['GET', 'POST'])
def show_all_contacts():
   if request.method == 'POST':
      return redirect('/bot-command')
   else:
      result = contact_book.get_all_contacts()
      return render_template('html/all_contacts/all_contacts.html', result = result) 
        

@app.route('/contact_detail/<id>', methods=['GET', 'POST'])
def contact_detail(id):
   contact = contact_book.get_contact_details(id)
   return render_template('html/user_details/user_details.html',
                            contact = contact,
                            phone = contact.phone,
                            email = contact.email,
                            address = contact,
                            url='/find_contact')  
     
         
@app.route('/show_all_notes', methods=['GET', 'POST'])
def show_all_notes ():
   if request.method == 'POST':
      return redirect('/bot-command')
   else:
      result =note_book.get_all_notes()
      return render_template('html/all_notes/all_notes.html',result = result)
                            
            
@app.route('/help_', methods=['GET', 'POST'])
def help_():
   return render_template('html/help/help.html', exec_command = exec_command)
    

@app.route('/add_note', methods=['GET', 'POST'])
def add_note():
   if request.method == 'POST':
      res = note_book.insert_note(request)
      if res ==0:
         return render_template('html/add_note/OK.html') 
      else:
         return html_error(res)
   else:
      return render_template('html/add_note/add_note.html')      


@app.route('/edit_note', methods=['GET', 'POST'])
def edit_note():
   res_list = []
   if request.method == 'POST':
      keywords = clean_search_str(request.form.get('Keywords'))
      for k in [keyword.strip() for keyword in keywords.split(",")]:
         result = note_book.get_notes(k)
      return render_template('html/edit_notes/edit_notes_found.html', result = result) 
   else:    
      return render_template('html/edit_notes/edit_notes_search.html')  

        
@app.route('/save_note/<id>', methods=['GET', 'POST'])
def save_note(id):
   if request.method == 'POST':
      res = note_book.update_note(id, request) 
      if  res== 0:
         return render_template('html/edit_notes/OK.html') 
      else:
         return html_error(res) 
   else:
      result = note_book.get_note_by_id(id)
      return render_template('html/edit_notes/edit_notes_save.html', res = result)        
                    
    
@app.route('/delete_contact', methods=['GET', 'POST'])
def delete_contact():
   results = []
   if request.method == 'POST':
      keywords = clean_search_str(request.form.get('Keywords'))
      for k in [keyword for keyword in keywords.strip().split(" ")]:
         results.extend(contact_book.get_contacts(k))
         return render_template('html/delete_user/user_to_delete.html', result = results) 
   else:
      return render_template('html/find_user/find_user.html')

      
@app.route('/delete_contact/<id>', methods=['GET', 'POST'])
def contact_delete_(id):
   res = contact_book.delete_contact(id)
   if res ==0: 
      return render_template('html/delete_user/OK.html', id = id)
   else:
      return html_error(res)

          

@app.route('/delete_note', methods=['GET', 'POST'])
def delete_note():
   res_list = []
   if request.method == 'POST':
      keywords = clean_search_str(request.form.get('Keywords'))
      for k in [keyword.strip() for keyword in keywords.split(",")]:
         result = note_book.get_notes(k)
         return render_template('html/delete_note/delete_notes_found.html', result = result)  
   else:
      return render_template('html/delete_note/delete_notes_search.html') 
        

@app.route('/delete_note/<id>', methods=['GET', 'POST'])
def note_delete_(id):
   res = note_book.delete_note(id)
   if res == 0:
      return render_template('html/delete_note/OK.html' , id = id) 
   else:
      return html_error(res)                


@app.route('/sort_notes', methods=['GET', 'POST'])
def sort_notes():
   return redirect('/bot-command')


@app.route('/sort_folder', methods=['GET', 'POST'])
def sort_folder():
   return redirect('/bot-command')


def get_period(message=""):
   return render_template('html/list_birthday/find_user.html', err_message = message)
   

@app.route('/next_birthday', methods=['GET', 'POST'])
def next_birthday():
   message =""
   if request.method == 'POST':
      try:
         period = int(request.form.get('Period'))
         assert period > 0 and period < 365
      except:
         return get_period("You could use numbers only, the period should be > 0 and < 365")  
      res = contact_book.get_birthday(period)
      return render_template('html/list_birthday/user_found.html',
                                days = request.form.get('Period'),
                                result = res)
   else:
      return get_period()   
        
    
@app.route('/login', methods=['GET', 'POST'])
def start_page():
   if request.method == 'POST':
      option = request.form['db']
      global contact_book
      global note_book
      if option =='mongodb':
         note_book = Mongo_notebook(note_db, counter_db)
         contact_book = Mongo_contact_book(contact_db, counter_db)
      else:
         contact_book = PostgreSQL_contact_book(session)
         note_book = PostgreSQL_notebook(session)
      return redirect('/bot-command')     
   else:
      return render_template('html/index.html')

@app.route('/bot-command', methods=['GET', 'POST'])
def bot():
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
   else:
      return render_template('html/bot_page.html',command_history = command_history)

############## end of routes section #########################3

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


def render_template(path, **kwargs):
   try:  
      with open( path, 'r') as file:
         t = Template(file.read())
         return t.render(**kwargs)
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


def html_error(error):
   return render_template('html/error.html', error = error)
    
if __name__ == "__main__":
     app.run(debug=True)
