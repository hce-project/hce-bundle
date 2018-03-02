"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dtm
@file dbi.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


from sqlalchemy.sql import select
from sqlalchemy import delete
import sqlalchemy 
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy import schema, types
from sqlalchemy.pool import StaticPool
from sqlalchemy.pool import SingletonThreadPool
from sqlalchemy.orm import sessionmaker


##Common use wrapper class to interact with the ORM databases
#Provide CRUD interface (create, read, update, delete) entries
#
class DBI(object):


  ##constructor
  #initialize fields
  #
  #@param config_dic dict object instance from config section
  #
  def __init__(self, config_dic):
    db_name = config_dic["db_name"]
    """
    db_name - database name
    Examples:
    db_name=sqlite://               # in memory
    db_name=sqlite:///:memory:      # in memory
    db_name=sqlite:///del.db        # relative path to file
    db_name=sqlite:////tmp/del.db   # absolute path to file
    """
    
    engine = create_engine('sqlite:///:memory:', echo=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    self.session = Session()
    
    self.errorCode = 0
    self.errorMessage = "Ok"


  ##get error code
  #return error code last performed action (e.g. insert, update, etc.)
  #
  #@return error code last performed action (e.g. insert, update, etc.)
  #
  def getErrorCode(self):
    return self.errorCode 


  ##get error message
  #return error message last performed action (e.g. insert, update, etc.)
  #
  #@return error message last performed action (e.g. insert, update, etc.)
  #
  def getErrorMsg(self):
    return self.errorMessage


  ##insert
  #insert objects into the database
  #
  #@param tasks - list of objects (not mandatory the same type) for insertion
  #@return the same list of objects
  #@error can be checked by the getError() method
  #
  def insert(self, task):
    self.errorCode = 0
    self.session.add(task)
    #try:
    self.session.commit()
    #except:
      #db.session.rollback()
      #self.errorCode = CONSTANTS.DBI_INSERT_ERROR_CODE
      #self.errorMessage  = CONSTANTS.DBI_INSERT_ERROR_MSG
    return task


  ##fetch
  #fetch objects from the database
  #
  #@param obj - list of objects (not mandatory the same type) for fetching
  #@param clause - sql clause for fetching the object from table
  #@return list of fetched objects
  #@error can be checked by the getError() method
  #
  def fetch(self, obj, clause):
    self.errorCode = 0
    fetched = []
    try:
      fetched.append(db.session.query(type(obj)).filter(clause).first())
      #fetched.append(db.session.query(type(obj)).from_statement(clause).first())
    except:
      db.session.rollback()
      self.errorCode = 1
      self.errorMessage  = "Fetch error"
    return fetched


  ##sql
  #fetch objects from the database
  #
  #@param obj - list of objects (not mandatory the same type) for fetching
  #@param clause - sql clause for fetching the object from table
  #@return list of fetched objects
  #@error can be checked by the getError() method
  #
  def sql(self, obj, clause):
    self.errorCode = 0
    fetched = []
    try:
      fetched.append(db.session.query(type(obj)).from_statement(clause).first())
    except:
      db.session.rollback()
      self.errorCode = 2 
      self.errorMessage  = "sql error"
    return fetched


  ##fetchAll
  #fetch all objects from the database
  #
  #@param tasks - object type for fetching
  #@return list of fetched objects
  #@error can be checked by the getError() method
  #
  def fetchAll(self, tasks):
    self.errorCode = 0
    fetched = []
    try:
      conn = db.engine.connect()
      if hasattr(tasks, "__len__"):
        for task in tasks:
          fetched.append(conn.execute(select([type(task)])).fetchall())
      else:
        fetched.append(conn.execute(select([type(tasks)])).fetchall())
    except:
      db.session.rollback()
      self.errorCode = 3
      self.errorMessage  = "fetch all error"
    return fetched


  ##update
  #update objects in the database
  #
  #@param tasks - list of objects (not mandatory the same type) for updating
  #@param clause - sql clause for updating the object in the table
  #@return list of updated objects
  #@error can be checked by the getError() method
  #
  def update(self, obj, clause):
    self.errorCode = 0
    updated = []
    try:
      updated_task = db.session.query(type(obj)).filter(clause).first()
      if updated_task:
        attributes = [attr for attr in dir(obj) if not attr.startswith('__') and not attr.startswith('_') and getattr(obj,attr)]
        for attr in attributes:
          setattr(updated_task, attr, getattr(obj, attr))
          updated.append(updated_task)
      db.session.commit()
    except:
      db.session.rollback()
      self.errorCode = 4
      self.errorMessage  = "update error"
    return updated


  ##insertOnUpdate
  #insert new object or update object if exists in the table
  #@param tasks - list of objects (not mandatory the same type) for updating
  #@param clause - (deprecated) sql clause for updating the object in the table
  #@return list of updated objects
  #@error can be checked by the getError() method
  #
  def insertOnUpdate(self, tasks, clause):
    self.errorCode = 0
    try:
      if hasattr(tasks, "__len__"):
        for task in tasks:
          db.session.merge(task)
      else:
        db.session.merge(tasks)
      db.session.commit()
    except:
      db.session.rollback()
      self.errorCode = 5
      self.errorMessage  = "insert on update error"
    return tasks


  ##delete
  #delete objects from the database
  #@param obj- list of objects (not mandatory the same type) for deleting
  #@param clause - sql clause for deleting the object from the table
  #@return list of deleted objects
  #@error can be checked by the getError() method
  #
  def delete(self, obj, clause):
    self.errorCode = 0
    deleted = []
    try:
      deleted_task = db.session.query(type(obj)).filter(clause).first()
      if deleted_task:
        deleted.append(deleted_task)
        db.session.delete(deleted_task)
      db.session.commit()
    except:
      db.session.rollback()
      self.errorCode = 6
      self.errorMessage  = "delete error"
    return deleted


  ##deleteAll
  #delete all objects from the database
  #@param tasks - object type for deleting
  #@return list of deleted objects
  #@error can be checked by the getError() method
  #
  def deleteAll(self, tasks):
    deleted = []
    self.errorCode = 0
    try:
      conn = db.engine.connect()
      if hasattr(tasks, "__len__"):
        for task in tasks:
          conn.execute(type(task).delete())
      else:
        #conn.execute(type(tasks).delete())
        #db.session.query(delete(tasks))
        #db.session.delete(tasks)
        ress = db.session.query(tasks).filter(tasks.UThreads=="").first()
        #ress = conn.execute(select([type(tasks)])).fetchall()
        for res in ress:
          db.session.delete(res)
      db.session.commit()
    except:
      db.session.rollback()
      self.errorCode = 7
      self.errorMessage  = "delete all error"
    return deleted







from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String

##Class describes structures of  task item used in TaskDataManager module
#
class TasksDataTable(Base):
  __tablename__ = "tasks_data_table"
  tableid = Column(Integer, primary_key=True)
  id = Column(Integer, unique=True, index=True)
  data = Column(String, unique=False, index=False)
  
  
  
  
  
  
  
if __name__ == '__main__':
  tdt = TasksDataTable()
  conf = {'db_name':'memory'}
  db = DBI(conf)
  tdt.id = 11
  db.insert(tdt)
  for instance in db.session.query(TasksDataTable).order_by(TasksDataTable.id): 
    print instance.id, instance.data