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

import collections
from threading import Lock
import sqlalchemy
from sqlalchemy.sql import select
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import reflection

from sqlalchemy import text

import Constants as CONSTANTS  # pylint: disable=W0403
import app.Utils as Utils

# Logger initialization
logger = Utils.MPLogger().getLogger()

# instantiate global database object
lock = Lock()


# #Common use wrapper class to interact with the ORM databases
# Provide CRUD interface (create, read, update, delete) entries
#
class DBI(object):

  MANDATORY_DBS = ["ee_responses_table", "resources_table", "scheduler_task_scheme", "task_back_log_scheme",
                   "task_log_scheme", "tasks_data_table"]

  # #constructor
  # initialize fields
  #
  # @param config_dic dict object instance from config section
  #
  def __init__(self, config_dic):
    # db_name = config_dic["db_name"]
    engineString = "mysql+mysqldb://%s:%s@%s"
    engineString = engineString % (config_dic["db_user"], config_dic["db_pass"], config_dic["db_host"])
    if "db_port" in config_dic:
      engineString += ':' + str(config_dic["db_port"])
    engineString += '/' + config_dic["db_name"]

    # self.engine = create_engine("mysql+mysqldb://hce:hce12345@localhost:3306/dtm")
    self.engine = create_engine(engineString)
    self.checkTables()
    Session = sessionmaker(bind=self.engine)
    self.session = Session()

    self.errorCode = CONSTANTS.DBI_SUCCESS_CODE
    self.errorMessage = CONSTANTS.DBI_SUCCESS_MSG


  # #checkTables
  # checkTables checks present of mandatory table in db
  #
  def checkTables(self):
    try:
      insp = reflection.Inspector.from_engine(self.engine)
      avlTables = insp.get_table_names()
      for dbTable in self.MANDATORY_DBS:
        if dbTable not in avlTables:
          raise Exception(">>> %s table not present in database" % dbTable)
    except Exception as err:
      self.errorCode = CONSTANTS.DBI_COMMON_ERROR_CODE
      self.errorMessage = CONSTANTS.DBI_COMMON_ERROR_MSG + ": " + err.message
      raise DBIErr(self.getErrorCode(), self.getErrorMsg())


  # #get error code
  # return error code last performed action (e.g. insert, update, etc.)
  #
  # @return error code last performed action (e.g. insert, update, etc.)
  #
  def getErrorCode(self):
    return self.errorCode


  # #get error message
  # return error message last performed action (e.g. insert, update, etc.)
  #
  # @return error message last performed action (e.g. insert, update, etc.)
  #
  def getErrorMsg(self):
    return self.errorMessage


  # #insert
  # insert objects into the database
  #
  # @param tasks - list of objects (not mandatory the same type) for insertion
  # @return the same list of objects
  # @error can be checked by the getError() method
  #
  def insert(self, tasks):
    with lock:
      self.errorCode = CONSTANTS.DBI_SUCCESS_CODE

      taskList = []
      if isinstance(tasks, collections.Iterable):
        taskList = tasks
      else:
        taskList.append(tasks)

      # boolean flag exist faults
      hasFaults = False

      for task in taskList:
        try:
          self.session.add(task)
          self.session.commit()
        except sqlalchemy.exc.SQLAlchemyError, err:
          logger.info("tasks: %s, type: %s", str(tasks), str(type(tasks)))
          self.errorMessage = CONSTANTS.DBI_INSERT_ERROR_MSG + ": " + str(err)
          self.session.rollback()
          hasFaults = True
        except Exception, err:
          logger.info("tasks: %s, type: %s", str(tasks), str(type(tasks)))
          self.errorMessage = CONSTANTS.DBI_INSERT_ERROR_MSG + ": " + str(err)
          hasFaults = True

      if hasFaults:
        self.errorCode = CONSTANTS.DBI_INSERT_ERROR_CODE
        raise DBIErr(self.getErrorCode(), self.getErrorMsg())

      return tasks


  # #fetch
  # fetch objects from the database
  #
  # @param obj - list of objects (not mandatory the same type) for fetching
  # @param clause - sql clause for fetching the object from table
  # @return list of fetched objects
  # @error can be checked by the getError() method
  #
  def fetch(self, obj, clause):
    with lock:
      self.errorCode = CONSTANTS.DBI_SUCCESS_CODE
      fetched = []
      try:
        rows = self.session.query(type(obj)).filter(text(clause)).all()
        if len(rows):
          fetched = rows
      # Firstly, we check if exception was thrown by the DBI itself
      # If so we rollback DB
      except sqlalchemy.exc.SQLAlchemyError as err:
        self.session.rollback()
        self.errorCode = CONSTANTS.DBI_FETCH_ERROR_CODE
        self.errorMessage = CONSTANTS.DBI_FETCH_ERROR_MSG + ": " + str(err)
        raise DBIErr(self.getErrorCode(), self.getErrorMsg())
      except Exception as err:
        self.errorCode = CONSTANTS.DBI_FETCH_ERROR_CODE
        self.errorMessage = CONSTANTS.DBI_FETCH_ERROR_MSG + ": " + str(err)
        raise DBIErr(self.getErrorCode(), self.getErrorMsg())

      return fetched


  # #sql
  # fetch objects from the database
  #
  # @param obj - list of objects (not mandatory the same type) for fetching
  # @param clause - sql clause for fetching the object from table
  # @return list of fetched objects
  # @error can be checked by the getError() method
  #
  def sql(self, obj, clause):
    with lock:
      self.errorCode = CONSTANTS.DBI_SUCCESS_CODE
      fetched = []
      try:
        rows = self.session.query(type(obj)).from_statement(text(clause)).all()
        if len(rows):
          fetched = rows
      # Firstly, we check if exception was thrown by the DBI itself
      # If so we rollback DB
      except sqlalchemy.exc.SQLAlchemyError as err:
        self.session.rollback()
        self.errorCode = CONSTANTS.DBI_SQL_ERROR_CODE
        self.errorMessage = CONSTANTS.DBI_SQL_ERROR_MSG + ": " + str(err) + ", clause:\n" + str(clause)
        raise DBIErr(self.getErrorCode(), self.getErrorMsg())
      except Exception as err:
        self.errorCode = CONSTANTS.DBI_SQL_ERROR_CODE
        self.errorMessage = CONSTANTS.DBI_SQL_ERROR_MSG + ": " + str(err) + ", clause:\n" + str(clause)
        raise DBIErr(self.getErrorCode(), self.getErrorMsg())

      return fetched


#   # #fetchAll
#   # fetch all objects from the database
#   #
#   # @param tasks - object type for fetching
#   # @return list of fetched objects
#   # @error can be checked by the getError() method
#   #
#   def fetchAll(self, tasks):
#     with lock:
#       self.errorCode = CONSTANTS.DBI_SUCCESS_CODE
#       fetched = []
#
#
#       try:
#         conn = self.engine.connect()
#         if hasattr(tasks, "__len__"):
#           for task in tasks:
#             fetched.append(conn.execute(select([type(task)])).fetchall())
#         else:
#           fetched.append(conn.execute(select([type(tasks)])).fetchall())
#       # Firstly, we check if exception was thrown by the DBI itself
#       # If so we rollback DB
#       except sqlalchemy.exc.SQLAlchemyError as err:
#         self.session.rollback()
#         self.errorCode = CONSTANTS.DBI_FETCH_ERROR_CODE
#         self.errorMessage = CONSTANTS.DBI_FETCH_ERROR_MSG + ": " + err.message
#         raise DBIErr(self.getErrorCode(), self.getErrorMsg())
#       except Exception as err:
#         self.errorCode = CONSTANTS.DBI_FETCH_ERROR_CODE
#         self.errorMessage = CONSTANTS.DBI_FETCH_ERROR_MSG + ": " + err.message
#         raise DBIErr(self.getErrorCode(), self.getErrorMsg())
#       return fetched


  # fetch all objects from the database
  #
  # @param tasks - object type for fetching
  # @return list of fetched objects
  # @error can be checked by the getError() method
  #
  def fetchAll(self, tasks):
    with lock:
      # variable for result
      fetched = []
      self.errorCode = CONSTANTS.DBI_SUCCESS_CODE

      connection = None
      try:
        connection = self.engine.connect()

        taskList = []
        if isinstance(tasks, collections.Iterable):
          taskList = tasks
        else:
          taskList.append(tasks)

        # boolean flag exist faults
        hasFaults = False
        for task in taskList:
          try:
            fetched.append(connection.execute(select([type(task)])).fetchall())
          except sqlalchemy.exc.SQLAlchemyError, err:
            self.session.rollback()
            self.errorMessage = CONSTANTS.DBI_FETCH_ERROR_MSG + ": " + str(err)
            hasFaults = True
          except Exception, err:
            self.errorMessage = CONSTANTS.DBI_FETCH_ERROR_MSG + ": " + str(err)
            hasFaults = True

        if hasFaults:
          self.errorCode = CONSTANTS.DBI_FETCH_ERROR_CODE
          raise DBIErr(self.getErrorCode(), self.getErrorMsg())

      except DBIErr, e:
        raise e
      except Exception, e:
        raise DBIErr(CONSTANTS.DBI_FETCH_ERROR_CODE, str(e))
      finally:
        if connection is not None:
          connection.close()

      return fetched


  # #update
  # update objects in the database
  #
  # @param tasks - list of objects (not mandatory the same type) for updating
  # @param clause - sql clause for updating the object in the table
  # @return list of updated objects
  # @error can be checked by the getError() method
  #
  def update(self, obj, clause):
    with lock:
      self.errorCode = CONSTANTS.DBI_SUCCESS_CODE
      updated = []
      try:
        updated_task = self.session.query(type(obj)).filter(text(clause)).first()
        if updated_task:
          attributes = [attr for attr in dir(obj) if not attr.startswith('__') \
                        and not attr.startswith('_') and getattr(obj, attr) is not None]
          # attributes = [attr for attr in dir(obj) if not attr.startswith('__') and not attr.startswith('_')]
          for attr in attributes:
            setattr(updated_task, attr, getattr(obj, attr))
          updated.append(updated_task)
        self.session.commit()
      # Firstly, we check if exception was thrown by the DBI itself
      # If so we rollback DB
      except sqlalchemy.exc.SQLAlchemyError as err:
        self.session.rollback()
        self.errorCode = CONSTANTS.DBI_UPDATE_ERROR_CODE
        self.errorMessage = CONSTANTS.DBI_UPDATE_ERROR_MSG + ": " + str(err)
        raise DBIErr(self.getErrorCode(), self.getErrorMsg())
      except Exception as err:
        self.errorCode = CONSTANTS.DBI_UPDATE_ERROR_CODE
        self.errorMessage = CONSTANTS.DBI_UPDATE_ERROR_MSG + ": " + str(err)
        raise DBIErr(self.getErrorCode(), self.getErrorMsg())

      return updated


  # #insertOnUpdate
  # insert new object or update object if exists in the table
  # @param tasks - list of objects (not mandatory the same type) for updating
  # @param clause - (deprecated) sql clause for updating the object in the table
  # @return list of updated objects
  # @error can be checked by the getError() method
  #
  def insertOnUpdate(self, tasks, clause):  # pylint: disable=W0613
    with lock:
      self.errorCode = CONSTANTS.DBI_SUCCESS_CODE
      try:

        taskList = []
        if isinstance(tasks, collections.Iterable):
          taskList = tasks
        else:
          taskList.append(tasks)

        for task in taskList:
          self.session.merge(task)

        self.session.commit()
      # Firstly, we check if exception was thrown by the DBI itself
      # If so we rollback DB
      except sqlalchemy.exc.SQLAlchemyError as err:
        self.session.rollback()
        self.errorCode = CONSTANTS.DBI_INSERT_ERROR_CODE
        self.errorMessage = CONSTANTS.DBI_INSERT_ERROR_MSG + ": " + str(err)
        raise DBIErr(self.getErrorCode(), self.getErrorMsg())
      except Exception as err:
        self.errorCode = CONSTANTS.DBI_INSERT_ERROR_CODE
        self.errorMessage = CONSTANTS.DBI_INSERT_ERROR_MSG + ": " + str(err)
        raise DBIErr(self.getErrorCode(), self.getErrorMsg())

      return tasks


  # #delete
  # delete objects from the database
  # @param obj- list of objects (not mandatory the same type) for deleting
  # @param clause - sql clause for deleting the object from the table
  # @return list of deleted objects
  # @error can be checked by the getError() method
  #
  def delete(self, obj, clause):
    with lock:
      self.errorCode = CONSTANTS.DBI_SUCCESS_CODE
      deleted = []
      try:
        deleted_task = self.session.query(type(obj)).filter(text(clause)).first()
        if deleted_task:
          deleted.append(deleted_task)
          self.session.delete(deleted_task)
        self.session.commit()
      # Firstly, we check if exception was thrown by the DBI itself
      # If so we rollback DB
      except sqlalchemy.exc.SQLAlchemyError as err:
        self.session.rollback()
        self.errorCode = CONSTANTS.DBI_DELETE_ERROR_CODE
        self.errorMessage = CONSTANTS.DBI_DELETE_ERROR_MSG + ": " + str(err)
        raise DBIErr(self.getErrorCode(), self.getErrorMsg())
      except Exception as err:
        self.errorCode = CONSTANTS.DBI_DELETE_ERROR_CODE
        self.errorMessage = CONSTANTS.DBI_DELETE_ERROR_MSG + ": " + str(err)
        raise DBIErr(self.getErrorCode(), self.getErrorMsg())

      return deleted


#   # #deleteAll
#   # delete all objects from the database
#   # @param tasks - object type for deleting
#   # @return list of deleted objects
#   # @error can be checked by the getError() method
#   #
#   def deleteAll(self, tasks):
#     with lock:
#       deleted = []
#       self.errorCode = CONSTANTS.DBI_SUCCESS_CODE
#       try:
#         conn = self.engine.connect()
#         if hasattr(tasks, "__len__"):
#           for task in tasks:
#             conn.execute(type(task).delete())
#         else:
#           # conn.execute(type(tasks).delete())
#           # self.session.query(delete(tasks))
#           # self.session.delete(tasks)
#           ress = self.session.query(tasks).filter(tasks.UThreads == "").first()
#           # ress = conn.execute(select([type(tasks)])).fetchall()
#           for res in ress:
#             self.session.delete(res)
#         self.session.commit()
#       # Firstly, we check if exception was thrown by the DBI itself
#       # If so we rollback DB
#       except sqlalchemy.exc.SQLAlchemyError as err:
#         self.session.rollback()
#         self.errorCode = CONSTANTS.DBI_DELETE_ERROR_CODE
#         self.errorMessage = CONSTANTS.DBI_DELETE_ERROR_MSG + ": " + err.message
#         raise DBIErr(self.getErrorCode(), self.getErrorMsg())
#       except Exception as err:
#         self.errorCode = CONSTANTS.DBI_DELETE_ERROR_CODE
#         self.errorMessage = CONSTANTS.DBI_DELETE_ERROR_MSG + ": " + err.message
#         raise DBIErr(self.getErrorCode(), self.getErrorMsg())
#       return deleted


  # delete all objects from the database
  # @param tasks - object type for deleting
  # @return list of deleted objects
  # @error can be checked by the getError() method
  #
  def deleteAll(self, tasks):
    with lock:
      deleted = []
      self.errorCode = CONSTANTS.DBI_SUCCESS_CODE
      connection = None
      try:
        connection = self.engine.connect()

        taskList = []
        if isinstance(tasks, collections.Iterable):
          taskList = tasks
        else:
          taskList.append(tasks)

        # boolean flag exist faults
        hasFaults = False
        for task in taskList:
          try:
            connection.execute(type(task).delete())
          except sqlalchemy.exc.SQLAlchemyError, err:
            self.session.rollback()
            self.errorMessage = CONSTANTS.DBI_DELETE_ERROR_MSG + ": " + str(err)
            hasFaults = True
          except Exception, err:
            self.errorMessage = CONSTANTS.DBI_DELETE_ERROR_MSG + ": " + str(err)
            hasFaults = True

        if hasFaults:
          self.errorCode = CONSTANTS.DBI_DELETE_ERROR_CODE
          raise DBIErr(self.getErrorCode(), self.getErrorMsg())

      except DBIErr, e:
        raise e
      except Exception, e:
        raise DBIErr(CONSTANTS.DBI_DELETE_ERROR_CODE, str(e))
      finally:
        if connection is not None:
          connection.close()

      return deleted


  # #sqlCustom
  # sqlCustom method makes SQL Custom request and returns result
  # @param clause - sql clause for deleting the object from the table
  # @return list of result objects
  #
  def sqlCustom(self, clause):
    with lock:
      self.errorCode = CONSTANTS.DBI_SUCCESS_CODE
      customResponse = []
      try:
        sqlText = text(clause)
        result = self.session.execute(sqlText)
        if result is not None:
          customResponse = result.fetchall()
        self.session.commit()
      # Firstly, we check if exception was thrown by the DBI itself
      # If so we rollback DB
      except sqlalchemy.exc.SQLAlchemyError as err:
        self.session.rollback()
        self.errorCode = CONSTANTS.DBI_SQL_ERROR_CODE
        self.errorMessage = CONSTANTS.DBI_SQL_ERROR_MSG + ": " + err.message
        raise DBIErr(self.getErrorCode(), self.getErrorMsg())
      except Exception as err:
        self.errorCode = CONSTANTS.DBI_SQL_ERROR_CODE
        self.errorMessage = CONSTANTS.DBI_SQL_ERROR_MSG + ": " + err.message
        raise DBIErr(self.getErrorCode(), self.getErrorMsg())

      return customResponse


  # #makeQueryFromObj
  # makeQueryFromObj static method creates and returns sqlalchemy query, based on incoming object
  # @param obj incoming object, which represent table schema
  # @param engine incoming db engine
  # @param session incoming sqlalchemy session
  # @return instance of sqlalchemy query
  #
  @staticmethod
  def makeQueryFromObj(obj, engine, session):
    ret = None
    criterions = {}
    insp = reflection.Inspector.from_engine(engine)
    localColumns = insp.get_columns(obj.__tablename__)
    for columName in [elem["name"] for elem in localColumns]:
      if columName in obj.__dict__:
        criterions[columName] = obj.__dict__[columName]
    if len(criterions) > 0:
      ret = session.query(type(obj)).filter_by(**criterions)
    return ret


# #Class is used to inform about error of DBI object
#
#
class DBIErr(Exception):

  def __init__(self, errCode, message):
    Exception.__init__(self, message)
    self.errCode = errCode
