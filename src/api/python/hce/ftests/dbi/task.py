#!/usr/bin/python


"""@package docstring
 @file task.py
 @author Oleksii <developers.hce@gmail.com>
 @link http://hierarchical-cluster-engine.com/
 @copyright Copyright &copy; 2013 IOIX Ukraine
 @license http://hierarchical-cluster-engine.com/license/
 @package HCE project node API
 @since 0.1
"""


#from dbi import db


class Task(object):

    Tries = 10
    def __init__(self, id=None, command=None, input=None, files=None, session=None, strategy=None, Tries=None, CDate=None ):
        self.id = id
        self.command= command
        self.input = input
        self.files= files
        self.session = session
        self.strategy = strategy
        # for update testing fake value
        self.Tries = Tries
        self.CDate = CDate


    def __repr__(self):
        return "<User(id='%s', data='%s')>" % (self.id, self.data)
