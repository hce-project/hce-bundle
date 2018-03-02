'''
Created on Apr 11, 2014

@package: dtm
@author: scorp, bgv
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import app.Consts as APP_CONSTS


# #Exceptions module keepts common exceptions
class DeserilizeException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)


class WrongEventObjectTypeException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)


class UrlParseException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)


class SeleniumFetcherException(Exception):
  def __init__(self, message, code=APP_CONSTS.ERROR_FETCHER_INTERNAL):
    Exception.__init__(self, message)

    self.code = code


class ProxyException(Exception):
  def __init__(self, message, code=APP_CONSTS.ERROR_NOT_EXIST_ANY_VALID_PROXY, statusUpdate=None):
    Exception.__init__(self, message)

    self.code = code
    self.statusUpdate = statusUpdate


class UrlAvailableException(Exception):
  def __init__(self, message, code=APP_CONSTS.ERROR_CONNECTION_ERROR):
    Exception.__init__(self, message)

    self.code = code


class DatabaseException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)
