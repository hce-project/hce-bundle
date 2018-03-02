#!/usr/bin/python


"""
HCE project, Python bindings, Distributed Tasks Manager application.
Event objects definitions.

@package: dc
@file URLFetch_json_to_db-task_convertor.py
@author Oleksii <developers.hce@gmail.com>
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
"""


from subprocess import Popen
from subprocess import PIPE


if __name__ == "__main__":
  cmd = "cat scraper_input.bin | /usr/bin/python ./scraper.py --config=../ini/scraper.ini"
  # cmd = "cat ../data/ftests/test_url_to_batch_converter/url_fetch.json | ./url_fetch_json_to_db_task_convertor.py -c ../ini/url_fetch_json_to_db_task_convertor.ini | ./urls-to-batch-task.py  | ./processor-task.py --config=../ini/processor-task.ini"
  process = Popen(cmd, stdout=PIPE, stdin=PIPE, shell=True, close_fds=True)
  (output, err) = process.communicate(input='')
  exit_code = process.wait()
