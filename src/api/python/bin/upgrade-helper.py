#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Upgrade-helper content main functional for group operation for upgrade MySQL database

@package: dc_processor
@file upgrade-helper.py
@author Alexander Vybornyh <alexander.hce.cluster@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2016 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


import ppath
from ppath import sys

import os
import sys
import copy
from cement.core import foundation
import app.Consts as APP_CONSTS
import ConfigParser
from dc_crawler.DBTasksWrapper import DBTasksWrapper
from app.Utils import varDump
from curses.ascii import isalpha
import app.Utils as Utils
import logging
import dc_crawler

APP_NAME = 'upgrade-helper'

##################################
# #
# # Sample of execution:
# # ./upgrade-helper.py -d=dc_attributes -p=att_ -t=dc_attributes -f=/home/hce/update_data.sql -c=../ini/db-task.ini
# #
# # For sample update_data.sql content string:
# # alter table `att_%SITE_ID%` MODIFY column `Value` longblob NOT NULL;
# #
##################################

# #Get cmd parameters
#
# @param - None
# @return dbName, fileName, configName - extrcated from cmd line
def getCmdParams():
  app = foundation.CementApp(APP_NAME)
  app.setup()
  app.add_arg('-d', '--db', action='store', metavar='use_database_name_for_show_tables', help='use database name for getting site_id')
  app.add_arg('-p', '--ptn', action='store', metavar='part_table_name', help='part of table_name')
  app.add_arg('-t', '--tdb', action='store', metavar='use_database_name_for_execution', help='use database name for execution')
  app.add_arg('-f', '--file', action='store', metavar='input_file_name', help='input file name with sql request')
  app.add_arg('-c', '--config', action='store', metavar='config_file_name', help='config ini-file', required=True)
  app.run()

  dbName = app.pargs.db
  partTableName = app.pargs.ptn
  tdbName = app.pargs.tdb
  fileName = app.pargs.file
  configName = app.pargs.config

  return dbName, partTableName, tdbName, fileName, configName


# # Get db task wrapper
#
# @param configName - config file name
# @return wrapper instance
def getDBTasksWrapper(configName):
  # variable for result value
  wrapper = None
  try:
    config = ConfigParser.ConfigParser()
    config.optionxform = str

    readOk = config.read(configName)
    if len(readOk) == 0:
      raise Exception("Wrong config file name '" + str(configName) + "'")

    wrapper = DBTasksWrapper(config)
  except Exception, err:
    raise Exception('Get DBTaskWrapper: ' + str(err))

  return wrapper


# #Get table name list
#
# @param response - response after sql request
# @param oldTableNamePart - mandatory part of old table names
# @param newTableNamePart - mandatory part of new table names
# @return list of names
def getTableNamesList(response, oldTableNamePart, newTableNamePart):
  result = []
  if isinstance(response, tuple):
    for elem in response:
      if len(elem) > 0:
        if elem[0].find(oldTableNamePart) > -1:
          name = copy.deepcopy(elem[0])
          name = name.replace(oldTableNamePart, newTableNamePart)
          result.append(name)

  return result


# #Extract request
#
# @param fileName - input file name for extract
# @return request, tableNamePart
def extractRequest(fileName):
  rawRequest = ''
  tableNamePart = ''

  f = open(fileName, 'r')
  rawRequest = f.read()
  f.close()

  words = rawRequest.split()
  for word in words:
    if word.count('%') > 1:
      tableNamePart = word[:word.find('%')]
      break

  for elem in tableNamePart:
    if isalpha(elem):
      tableNamePart = tableNamePart[tableNamePart.find(elem):]
      break

  return rawRequest, tableNamePart


# #Make SQL request
#
# @param rawRequest - raw request
# @param tableName - table name
# @param tableNamePart - part of table name
# @return SQL request
def makeSql(rawRequest, tableName, tableNamePart):
  sql = ''
  words = []
  for word in rawRequest.split():
    if word.find(tableNamePart) > -1:
      words.append(tableName)
    else:
      words.append(word)

  sql = ' '.join(words)

  return sql


if __name__ == '__main__':
  exit_code = APP_CONSTS.EXIT_SUCCESS
  try:
    dbName, partTableName, tdbName, fileName, configName = getCmdParams()
    wrapper = getDBTasksWrapper(configName)

    if wrapper is not None:
      sql = 'SHOW TABLES;'
      response = wrapper.customRequest(sql, dbName)
      rawRequest, tableNamePart = extractRequest(fileName)
      tableNames = getTableNamesList(response, partTableName, tableNamePart)

      dc_crawler.DBTasksWrapper.logger.addHandler(logging.NullHandler())
      for tableName in tableNames:
        print(tableName)
        sql = makeSql(rawRequest, tableName, tableNamePart)
        wrapper.customRequest(sql, tdbName)

      print('Affected success ' + str(len(tableNames)) + ' rows')

  except Exception as err:
    sys.stderr.write(str(err) + '\n')
    exit_code = APP_CONSTS.EXIT_FAILURE
  except:
    exit_code = EXIT_FAILURE
  finally:
    sys.stdout.flush()
    os._exit(exit_code)
