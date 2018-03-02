#!/usr/bin/python

# -*- coding: UTF-8 -*-

import sys
import argparse
import pickle
import json

def createParser ():
    parser = argparse.ArgumentParser()
    parser.add_argument ('-o', '--operation', choices=['PICKLE', 'UNPICKLE'], default='PICKLE')

    return parser


if __name__ == '__main__':
  try:
    parser = createParser()
    namespace = parser.parse_args(sys.argv[1:])
    if namespace.operation == 'PICKLE':
      sys.stdout.write(pickle.dumps(json.loads(sys.stdin.read())))
      pass
    elif namespace.operation == 'UNPICKLE':
      sys.stdout.write(json.dumps(pickle.loads(sys.stdin.read())))
    else:
      raise Exception("Unsupport command line parameter.")

  except Exception, err:
    sys.stderr.write(str(err) + '\n')
