#!/usr/bin/python
# coding: utf-8

import argparse
import json
import pickle
import os
import sys
sys.path.append(os.path.dirname(__file__) + "/../../hce")

from dcc.DCCObjectsSerializator import DCCObjectsSerializator

FORMAT_PICKLE = 'PICKLE'
FORMAT_JSON = 'JSON'
DEFAULT_FORMAT = FORMAT_PICKLE

OPERATION_PACK = 'PACK'
OPERATION_UNPACK = 'UNPACK'
DEFAULT_OPERATION = OPERATION_PACK

def createParser():
  pr = argparse.ArgumentParser()
  pr.add_argument('-f', '--format', choices=[FORMAT_PICKLE, FORMAT_JSON], default=DEFAULT_FORMAT)
  pr.add_argument('-o', '--operation', choices=[OPERATION_PACK, OPERATION_UNPACK], default=DEFAULT_OPERATION)

  return pr


if __name__ == '__main__':
  try:
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])

    if namespace.format == FORMAT_PICKLE and namespace.operation == OPERATION_PACK:
      sys.stdout.write(pickle.dumps(DCCObjectsSerializator().BatchDeserialize(json.loads(sys.stdin.read()))))
    elif namespace.format == FORMAT_PICKLE and namespace.operation == OPERATION_UNPACK:
      sys.stdout.write(json.dumps(pickle.loads(sys.stdin.read()).toJSON()))
    elif namespace.format == FORMAT_JSON and namespace.operation == OPERATION_PACK:
      sys.stdout.write(json.dumps(json.loads(sys.stdin.read())))
    elif namespace.format == FORMAT_JSON and namespace.operation == OPERATION_UNPACK:
      sys.stdout.write(json.dumps(json.loads(sys.stdin.read())))
    else:
      raise Exception("Unsupport command line parameter.")

  except Exception, err:
    sys.stderr.write(str(err) + '\n')
