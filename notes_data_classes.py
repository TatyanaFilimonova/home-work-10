from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from datetime import date
import time
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
import re
from SQL_alchemy_classes import *
from sqlalchemy import create_engine, or_, update, delete
from  flask import Flask, redirect, url_for
from flask import request
from LRU_cache import *

class Notebook(ABC):

    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def get_all_notes(self):
        pass

    @abstractmethod
    def get_notes(self, key):
        pass

    @abstractmethod
    def get_note_by_id(self, id):
        pass


    @abstractmethod
    def update_note(self, note, new_note):
        pass

    @abstractmethod
    def insert_note(self, note):
        pass

    @abstractmethod
    def delete_note(self, id):
        pass

class Mongo_notebook(Notebook):

    def __init__(self, notes_db = None, counter_db = None):
        self.notes = []
        self.notes_db = notes_db
        self.counter_db = counter_db

    @LRU_cache(1)
    def get_all_notes(self):
        self.notes = []
        try:
            result = self.notes_db.find({}).sort('note_id')
            for res in result:
                self.notes.append(Mongo_note(res))
            return self.notes    
        except Exception as e:
            raise e
        
    @LRU_cache(10)
    def get_notes(self, key):
        self.notes = []
        rgx = re.compile(f'.*{key}.*', re.IGNORECASE)
        result = self.notes_db.find({'$or':[{'keywords':rgx},{'text':rgx}]})
        for res in result:
            self.notes.append(Mongo_note(res))
        return self.notes
    
    @LRU_cache(10)
    def get_note_by_id(self, id):
        result = self.notes_db.find_one({'note_id':int(id)})
        if result!=None:
            return Mongo_note(result)
        else:
            print(f"Result is {result}, id = {id}, type ID = {type(id)}")
        return None

    @LRU_cache_invalidate('get_notes', 'get_all_notes', 'get_note_by_id')
    def update_note(self, id, request):
        try:
            kw = request.form.get('Keywords')
            kw = [k.strip() for k in kw.split(',')]
            self.notes_db.replace_one({'note_id':int(id)},
                                   {'note_id':int(id),
                                    'created_at': datetime.today(),
                                    'keywords': request.form.get('Keywords'),
                                    'text': request.form.get('Text')
                                   } 
                               )
            return 0
        except Exception as e:
            return e
        
    @LRU_cache_invalidate('get_notes', 'get_all_notes')
    def insert_note(self, request):
        try:        
            counter = self.counter_db.find_one({"counter_name": 'note_id'},{'value':1})['value']
            self.counter_db.replace_one(
                          { "counter_name": 'note_id' },
                          { "counter_name": 'note_id',
                            "value": counter+1}
                             )  
            self.notes_db.insert_one({
            'note_id': (counter+1),
            'keywords': request.form.get('Keywords'),
            'text': request.form.get('Text'),
            'created_at': datetime.today(),    
            })
            return 0
        except Exception as e:
            return e
        
    @LRU_cache_invalidate('get_notes', 'get_all_notes', 'get_note_by_id')
    def delete_note(self, id):
        try:
            self.notes_db.delete_one({'note_id':int(id)})
            return 0
        except Exception as e:
            return e


class PostgreSQL_notebook(Notebook):

    def __init__(self, session = None):
        self.session = session
        
    @LRU_cache(1)
    def get_all_notes(self):
        self.notes= []
        result = self.session.query(
            Note_.note_id, Note_.keywords, Text.text, Note_.created_at
            ).join(Text).order_by(Note_.note_id)
        for r in result:
            self.notes.append(Postgres_note(r))
        return self.notes    

    @LRU_cache(10)
    def get_notes(self, key):
        self.notes= []
        result = self.session.query(
                    Note_.note_id, Note_.keywords, Text.text, Note_.created_at
                    ).join(Text).filter(
                        or_(func.lower(Note_.keywords).like(func.lower(f"%{key}%")
                        ), func.lower(Text.text).like(func.lower(f"%{key}%"))))
        for r in result:
            self.notes.append(Postgres_note(r))
        return self.notes    
    
    @LRU_cache(10)
    def get_note_by_id(self, id):
        result = self.session.query(
                    Note_.note_id, Note_.keywords, Text.text, Note_.created_at
                    ).join(Text).filter(Note_.note_id == id)
        return Postgres_note(result[0])

    @LRU_cache_invalidate('get_notes', 'get_all_notes', 'get_note_by_id')
    def update_note(self, id, request):
        try:
            keywords = request.form.get('Keywords')
            text = request.form.get('Text')
            self.session.execute(update(Note_, values={Note_.keywords: keywords}).filter(Note_.note_id == id))
            self.session.execute(update(Text, values={Text.text: text}).filter(Text.note_id == id))
            self.session.commit()
            return 0
        except Exception as e:
            self.session.rollback()
            return e
        
    @LRU_cache_invalidate('get_notes', 'get_all_notes')
    def insert_note(self, request):
        try:        
            keywords = request.form.get('Keywords')
            text = request.form.get('Text')
            note = Note_(keywords = keywords, created_at = date.today())
            self.session.add(note)
            self.session.commit()
            text=Text(note_id = note.note_id, text = text)
            self.session.add(text)
            self.session.commit()
            return 0
        except Exception as e:
            self.session.rollback()
            return e

    @LRU_cache_invalidate('get_notes', 'get_all_notes', 'get_note_by_id')
    def delete_note(self, id):
        try:
            stmt = delete(Note_).where(Note_.note_id == id)
            self.session.execute(stmt)    
            self.session.commit()
            return 0
        except Exception as e:
            self.session.rollback()
            return e


class Note_abstract(ABC):

    @abstractmethod
    def __init__(self):
        self.note_id = None
        self.text = None
        self.created_at = None
        self.keywords = None
        
class Mongo_note(Note_abstract):

    def __init__(self, json):
        self.note_id = json['note_id']
        self.keywords =','.join(json['keywords'])
        self.created_at = json['created_at']
        self.text = json['text']

class Postgres_note(Note_abstract):

    def __init__(self, note):
        self.note_id = note.note_id
        self.created_at = note.created_at
        self.keywords=note.keywords
        self.text = note.text
                
        

      
