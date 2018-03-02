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
from SchedulerTask import SchedulerTask


##ORM for SchedulerTask class
#
Base = declarative_base()
class SchedulerTaskScheme(Base):  # pylint: disable-all
  __tablename__ = "scheduler_task_scheme"
  __table_args__ = {'mysql_engine': 'MyISAM'}
  id = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=True)
  rTime = sqlalchemy.Column(sqlalchemy.BigInteger, unique=False, index=True , default=0)
  rTimeMax = sqlalchemy.Column(sqlalchemy.BigInteger, unique=False, index=True, default=0)
  state = sqlalchemy.Column(sqlalchemy.Integer, unique=False, index=True, default=0)
  priority = sqlalchemy.Column(sqlalchemy.Integer, unique=False, index=True, default=0)
  strategy = sqlalchemy.Column(sqlalchemy.Text, unique=False, index=False)
  tries = sqlalchemy.Column(sqlalchemy.BigInteger, unique=False, index=True)


  ##constructor
  #creates and sets all attributes from SchedulerTask object instance
  def __init__(self, schedulerTask):
    attributes = [attr for attr in dir(self) if not attr.startswith('__') and not attr.startswith('_')]
    for attr in attributes:
      setattr(self, attr, getattr(schedulerTask, attr, None))


  def _getSchedulerTask(self):
    schedulerTask = SchedulerTask()
    attributes = [attr for attr in dir(schedulerTask) if not attr.startswith('__') and not attr.startswith('_')]
    for attr in attributes:
      setattr(schedulerTask, attr, getattr(self, attr, None))
    return schedulerTask
