'''
Created on Mar 13, 2014

@package: dtm
@author: scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

##Class describes structures of  task item used in ResourcesManager module
#
Base = declarative_base()
class ResourcesTable(Base):  # pylint: disable-all
  __tablename__ = "resources_table"
  __table_args__ = {'mysql_engine': 'MyISAM'}
  nodeId = sqlalchemy.Column(sqlalchemy.String(256), primary_key=True, autoincrement=False)
  nodeName = sqlalchemy.Column(sqlalchemy.String(256), primary_key=False)
  host = sqlalchemy.Column(sqlalchemy.String(256), primary_key=False)
  port = sqlalchemy.Column(sqlalchemy.Integer, primary_key=False)
  cpu = sqlalchemy.Column(sqlalchemy.Integer, primary_key=False)
  io = sqlalchemy.Column(sqlalchemy.Integer, primary_key=False)
  ramRU = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=False)
  ramVU = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=False)
  ramR = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=False)
  ramV = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=False)
  swap = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=False)
  swapU = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=False)
  disk = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=False)
  diskU = sqlalchemy.Column(sqlalchemy.BigInteger, primary_key=False)
  state = sqlalchemy.Column(sqlalchemy.Integer, primary_key=False)
  uDate = sqlalchemy.Column(sqlalchemy.DateTime, primary_key=False)
  cpuCores = sqlalchemy.Column(sqlalchemy.Integer, primary_key=False)
  threads = sqlalchemy.Column(sqlalchemy.Integer, primary_key=False)
  processes = sqlalchemy.Column(sqlalchemy.Integer, primary_key=False)


  # #constructor
  def __init__(self, eventObject=None):
    if eventObject == None:
      self.nodeId = None
      self.nodeName = None
      self.host = None
      self.port = None
      self.cpu = None
      self.io = None
      self.ramRU = None
      self.ramVU = None
      self.ramR = None
      self.ramV = None
      self.swap = None
      self.swapU = None
      self.disk = None
      self.diskU = None
      self.state = None
      self.uDate = None
      self.cpuCores = None
      self.threads = None
      self.processes = None
    else:
      self.initFieldsFromEventObject(eventObject)


  def initFieldsFromEventObject(self, eventObject):
    self.nodeId = eventObject.nodeId
    self.nodeName = eventObject.nodeName
    self.host = eventObject.host
    self.port = eventObject.port
    self.cpu = eventObject.cpu
    self.io = eventObject.io
    self.ramRU = eventObject.ramRU
    self.ramVU = eventObject.ramVU
    self.ramR = eventObject.ramR
    self.ramV = eventObject.ramV
    self.swap = eventObject.swap
    self.swapU = eventObject.swapU
    self.disk = eventObject.disk
    self.diskU = eventObject.diskU
    self.state = eventObject.state
    self.uDate = eventObject.uDate
    self.cpuCores = eventObject.cpuCores
    self.threads = eventObject.threads
    self.processes = eventObject.processes
