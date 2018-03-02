'''
Created on Mar 18, 2014

@author: igor
'''

##The class allow to have only one instance of a object
#
class Singleton(type):

  _instances = {}

  def __call__(cls, *args, **kwargs):
    if cls not in cls._instances:
      cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
    return cls._instances[cls]

