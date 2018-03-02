#!/usr/bin/python

import sys
import argparse
import json

##parsing paramers
#
#@param - None
#@return - read from command line argument
def parseParams():
  listFile = ""
  jsonFile = ""
  try:
    parser = argparse.ArgumentParser(description='Process command line arguments.', add_help=False)
    parser.add_argument('-l', '--listFile', action='store', metavar='list_file', help='list file for test')
    parser.add_argument('-j', '--jsonFile', action='store', metavar='json_file', help='json file for test')

    args = parser.parse_known_args()

    if args is None or args[0] is None or args[0].listFile is None:
      raise Exception("Parameter 'listFile' is empty")

    listFile = str(args[0].listFile)

    if args is None or args[0] is None or args[0].jsonFile is None:
      raise Exception("Parameter 'jsonFile' is empty")

    jsonFile = str(args[0].jsonFile)

  except Exception, err:
    raise Exception('Error parse command line parameters: ' + str(err))

  return listFile, jsonFile


##Extract host and port inputLine
#
#@param inputLine - input line
#@return host, port  read from command line argument
def parseLine(inputLine):
  host = ''
  port = '80'

  params = inputLine.split(':', 1)

  if len(params) > 0:
    host = params[0]

  if len(params) > 1:
    port = params[1]

  return host, port


##Create map file with replased old data to new data
#
#@param old_data - old data
#@param old_data - new data
#@param file_name - file name
#@param map_file - map file
#@return host, port  read from command line argument
def createMapFile(old_data, new_data, file_name, map_file):
  with open(file_name) as file:
    text = file.read()
    file.close()
    text = text.replace(old_data, new_data)
    with open(map_file, 'w') as file:
      file.write(text)
      file.close()


if __name__ == "__main__":

  listFile, jsonFile = parseParams()

  f = open(listFile, 'r')
  lines = f.readlines()
  f.close()

  for line in lines:
    ln = line.splitlines()
    if len(ln) > 0 and ln[0] != "":
      host, port = parseLine(ln[0])
      if host and port:
        createMapFile('%HTTP_PROXY_HOST%', host, jsonFile, ln[0] + '.in')
        createMapFile('%HTTP_PROXY_PORT%', port, ln[0] + '.in', ln[0] + '.in')
