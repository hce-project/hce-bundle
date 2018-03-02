#!/usr/bin/python

#from dbi.dbi import DBI
#from dbi.dbi import db
#from dbi.DBI import db
#import dbi.dbi as row_dbi
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy    
from sqlalchemy.sql import select
from sqlalchemy import delete
import sqlalchemy 
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy import schema, types
from sqlalchemy.pool import StaticPool
from sqlalchemy.pool import SingletonThreadPool
app = Flask(__name__)
db = SQLAlchemy(app)

class TestObj(db.Model):
  tid = db.Column(db.Integer, primary_key=True)
  id = db.Column(db.Integer, unique=True, autoincrement=False, index=True)
  val = db.Column(db.Integer, index=True)
  

def process():
  app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
  db.create_all()
  
  obj1 = TestObj()
  obj1.id = 1
  obj1.val = 10

  obj2 = TestObj()
  obj2.id = 2
  obj2.val = 20
  
  db.session.add(obj1)
  db.session.add(obj2)
  db.session.commit()

  #taskInSlotNumber = len(row_dbi.db.session.query(type(TestObj)).filter_by(rTime<rightBorderMs, state=PLANED).all())
  
  from sqlalchemy import func
  num = db.session.query(TestObj.val).group_by(TestObj.val).having(func.count(TestObj.val) < 9).all()
  print num

if __name__ == "__main__":
  process()