"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dtm
@file resources.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


from dbi.dbi import db
from dtm.EventObjects import Resource as eventResource
import datetime


class Resources(db.Model):
  nodeId = db.Column(db.Integer, primary_key=True, autoincrement=False)
  #nodeId = db.Column(db.String, unique=False, index=True)
  name = db.Column(db.String, unique=False, index=True)
  host = db.Column(db.String, unique=False, index=True)
  port = db.Column(db.Integer, unique=False, index=True)
  cpu = db.Column(db.Integer, unique=False, index=True)
  io = db.Column(db.Integer, unique=False, index=True)
  ramRU = db.Column(db.BigInteger, unique=False, index=True)
  ramVU = db.Column(db.BigInteger, unique=False, index=True)
  ramR = db.Column(db.BigInteger, unique=False, index=True)
  ramV = db.Column(db.BigInteger, unique=False, index=True)
  swap = db.Column(db.BigInteger, unique=False, index=True)
  swapU = db.Column(db.BigInteger, unique=False, index=True)
  disk = db.Column(db.BigInteger, unique=False, index=True)
  diskU = db.Column(db.BigInteger, unique=False, index=True)
  state = db.Column(db.Integer, unique=False, index=True)
  uDate = db.Column(db.DateTime, unique=False, index=True)
    

  def __init__(self, eventResource):
    self.uDate = datetime.datetime.now()
    attributes = [attr for attr in dir(self) if not attr.startswith('__') and not attr.startswith('_')]        
    for attr in attributes:
      setattr(self, attr, getattr(eventResource, attr, None))
    if not self.uDate:
      self.uDate = datetime.datetime.now()


    
