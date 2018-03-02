#!/usr/bin/python

"""
HCE project,  Python bindings, DC service utility
Batch from json preparation utility.

@package: dc
@file digest.py
@author bgv <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


import ppath
from ppath import sys

# For profiling
import app.Profiler as Profiler

# Start profiling
pr = Profiler.Profiler()
if pr and pr.status > 0:
  pr.start()

import os
import sys
import app.Utils as Utils
import app.Consts as APP_CONSTS
from cement.core import foundation
import copy
import hashlib
import json


exit_code = APP_CONSTS.EXIT_FAILURE

if __name__ == "__main__":
  try:
    # Create the application
    app = foundation.CementApp('myapp')
    app.setup()
    app.args.add_argument('-t', '--txt', action='store', dest='txt', help='the text file one URL per line')
    app.args.add_argument('-j', '--json', action='store', dest='json', help='the json file used as the Batch template, if omitted - read stdin')
    app.args.add_argument('-o', '--out', action='store', dest='out', help='the output json file, if omitted write stdout')
    app.run()

    if app.pargs.txt:
      with open(app.pargs.txt, 'r') as f:
        urlsList = f.read().splitlines()

      if app.pargs.json:
        with open(app.pargs.json, 'r') as f:
          batchDict = json.loads(f.read())
      else:
        batchDict = json.loads(sys.stdin.read())

      items = []
      for url in urlsList:
        url = url.strip()
        if url != '':
          item = copy.deepcopy(batchDict['items'][0])
          item['urlObj']['url'] = url
          item['urlObj']['urlMd5'] = hashlib.md5(url).hexdigest()
          item['urlId'] = item['urlObj']['urlMd5']
          items.append(item)

      batchDict['items'] = items

      if app.pargs.out:
        with open(out, 'w') as f:
          f.write(json.dumps(batchDict))
      else:
        print json.dumps(batchDict)
    else:
      sys.stderr.write('Required text file with URLs not provided, use with -h to see required arguments.')

    # Close the application
    app.close()
  except Exception as err:
    sys.stderr.write(str(err) + '\n')
    exit_code = APP_CONSTS.EXIT_FAILURE
  except:
    exit_code = APP_CONSTS.EXIT_FAILURE
  finally:
    # close the app
    if app:
      app.close()
    # stop profiling
    if pr:
      pr.stop()
    sys.stdout.flush()
    os._exit(exit_code)

