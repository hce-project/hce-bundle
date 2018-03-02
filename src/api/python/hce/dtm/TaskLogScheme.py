'''
@package: dtm
@author igor
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from TaskLog import TaskLog

##ORM mapper for TaskLog class(log of finished tasks)
#
Base = declarative_base()
class TaskLogScheme(Base):  # pylint: disable-all
  __tablename__ = "task_log_scheme"
  __table_args__ = {'mysql_engine': 'MyISAM'}
  id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)
  pId = sqlalchemy.Column(sqlalchemy.BigInteger, unique=False, index=True)
  nodeName = sqlalchemy.Column(sqlalchemy.String, unique=False, index=True)
  cDate = sqlalchemy.Column(sqlalchemy.DateTime, unique=False, index=True)
  sDate = sqlalchemy.Column(sqlalchemy.DateTime, unique=False, index=True)
  rDate = sqlalchemy.Column(sqlalchemy.DateTime, unique=False, index=True)
  fDate = sqlalchemy.Column(sqlalchemy.DateTime, unique=False, index=True)
  pTime = sqlalchemy.Column(sqlalchemy.BigInteger, unique=False, index=True)
  pTimeMax = sqlalchemy.Column(sqlalchemy.BigInteger, unique=False, index=False)
  state = sqlalchemy.Column(sqlalchemy.Integer, unique=False, index=False)
  uRRAM = sqlalchemy.Column(sqlalchemy.BigInteger, unique=False, index=False)
  uVRAM = sqlalchemy.Column(sqlalchemy.BigInteger, unique=False, index=False)
  uCPU = sqlalchemy.Column(sqlalchemy.Integer, unique=False, index=False)
  uThreads = sqlalchemy.Column(sqlalchemy.Integer, unique=False, index=False)
  tries = sqlalchemy.Column(sqlalchemy.Integer, unique=False, index=False)
  host = sqlalchemy.Column(sqlalchemy.String, unique=False, index=True)
  port = sqlalchemy.Column(sqlalchemy.String, unique=False, index=True)
  deleteTaskId = sqlalchemy.Column(sqlalchemy.Integer, unique=False, index=False, server_default="0")
  autoCleanupFields = sqlalchemy.Column(sqlalchemy.String, unique=False, index=False, server_default="")
  type = sqlalchemy.Column(sqlalchemy.Integer, unique=False, index=True, server_default="0")
  name = sqlalchemy.Column(sqlalchemy.String, unique=False, index=True, server_default="")


  ##constructor
  #creates and sets all attributes from taskLog object instance
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
