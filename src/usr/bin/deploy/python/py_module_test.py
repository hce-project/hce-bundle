#! /usr/bin/python

"""
Import test
"""

import sys
from optparse import OptionParser

def py_try_import_module(mod):
  try:
    rc = 0
    module = __import__ (mod)
  except ImportError:
    rc = 1
  return rc

parser = OptionParser()
parser.add_option("-m", "--module", dest="mod")
(options, args) = parser.parse_args()

sys.stdout.write(str(py_try_import_module(options.mod)))
