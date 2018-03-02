#!/usr/bin/python


"""@package docstring
 @file demoTask.py
 @author Oleksii <developers.hce@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""


from dbi.dbi import db


##demo object
#create table schema
#
class DemoBackLogTask(db.Model):
    tid = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, unique=True, index=True)
    CDate = db.Column(db.DateTime, unique=False, index=True)
    SDate = db.Column(db.String, unique=False, index=True)
    EDate = db.Column(db.String, unique=False, index=True)
    FDate = db.Column(db.String, unique=False, index=True)
    PTime = db.Column(db.String, unique=False, index=True)
    PTimeMax = db.Column(db.String, unique=False, index=False)
    State = db.Column(db.String, unique=False, index=False)
    URRAM = db.Column(db.String, unique=False, index=False)
    UVRAM = db.Column(db.String, unique=False, index=False)
    UCPU = db.Column(db.String, unique=False, index=False)
    UThreads = db.Column(db.String, unique=False, index=False)
    Tries = db.Column(db.String, unique=False, index=False)


    ##constructor
    #init fields intersection with the incoming object's fields
    #
    #@param task is the class which will be mapped to the table
    #
    def __init__(self, task):
        attributes = [attr for attr in dir(self) if not attr.startswith('__') and not attr.startswith('_')]        
        for attr in attributes:
            setattr(self, attr, getattr(task, attr, None))
