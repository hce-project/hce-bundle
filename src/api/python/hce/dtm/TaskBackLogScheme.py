'''
Created on Mar 6, 2014

@author: igor
'''
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import dtm.EventObjects

from TaskLog import TaskLog


# #ORM mapper for TaskLog class
#
Base = declarative_base()
class TaskBackLogScheme(Base):  # pylint: disable-all
  __tablename__ = "task_back_log_scheme"
  __table_args__ = {'mysql_engine': 'MyISAM'}
  id = sqlalchemy.Column(sqlalchemy.BigInteger, unique=True, index=True, primary_key=True, autoincrement=False)
  pId = sqlalchemy.Column(sqlalchemy.BigInteger, unique=False, index=True)
  nodeName = sqlalchemy.Column(sqlalchemy.String, unique=False, index=True)
  cDate = sqlalchemy.Column(sqlalchemy.DateTime, unique=False, index=True)
  sDate = sqlalchemy.Column(sqlalchemy.DateTime, unique=False, index=True)
  rDate = sqlalchemy.Column(sqlalchemy.DateTime, unique=False, index=True)
  fDate = sqlalchemy.Column(sqlalchemy.DateTime, unique=False, index=True)
  pTime = sqlalchemy.Column(sqlalchemy.BigInteger, unique=False, index=True)
  pTimeMax = sqlalchemy.Column(sqlalchemy.BigInteger, unique=False, index=False)
  state = sqlalchemy.Column(sqlalchemy.Integer, unique=False, index=True,
            server_default=str(dtm.EventObjects.EEResponseData.TASK_STATE_NEW_JUST_CREATED), nullable=True)
  uRRAM = sqlalchemy.Column(sqlalchemy.BigInteger, unique=False, index=False, server_default="0")
  uVRAM = sqlalchemy.Column(sqlalchemy.BigInteger, unique=False, index=False, server_default="0")
  uCPU = sqlalchemy.Column(sqlalchemy.Integer, unique=False, index=False, server_default="0")
  uThreads = sqlalchemy.Column(sqlalchemy.Integer, unique=False, index=False, server_default="0")
  tries = sqlalchemy.Column(sqlalchemy.Integer, unique=False, index=False)
  host = sqlalchemy.Column(sqlalchemy.String, unique=False, index=True, server_default="")
  port = sqlalchemy.Column(sqlalchemy.String, unique=False, index=True, server_default="")
  deleteTaskId = sqlalchemy.Column(sqlalchemy.Integer, unique=False, index=False, server_default="0")
  autoCleanupFields = sqlalchemy.Column(sqlalchemy.String, unique=False, index=False, server_default="")
  type = sqlalchemy.Column(sqlalchemy.Integer, unique=False, index=True, server_default="0")
  name = sqlalchemy.Column(sqlalchemy.String, unique=False, index=True, server_default="")


  # #constructor
  # creates and sets all attributes from taskLog object instance
  def __init__(self, taskLog):
    attributes = [attr for attr in dir(self) if not attr.startswith('__') and not attr.startswith('_')]
    for attr in attributes:
      setattr(self, attr, getattr(taskLog, attr, None))


  def _getTaskLog(self):
    taskLog = TaskLog()
    attributes = [attr for attr in dir(taskLog) if not attr.startswith('__') and not attr.startswith('_')]
    for attr in attributes:
      setattr(taskLog, attr, getattr(self, attr, None))
    return taskLog
