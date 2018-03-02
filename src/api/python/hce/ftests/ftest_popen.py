#coding: utf-8
'''
HCE project, Python bindings, DC dependencies
The popen research tests.

@package: drce
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2015 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import time

stdinStr = 'one\ntwo\nthree\nfour\nfive\nsix\n'

from subprocess import Popen, PIPE
from tempfile import SpooledTemporaryFile as tempfile
from subprocess import Popen
from subprocess import PIPE

s = time.time()

#cmd = '/bin/grep f'
#cmd = 'cd /home/bgv/hce-node-bundle/api/python/bin && ./processor-task.py'
#md = 'cd /home/bgv/hce-node-bundle/api/python/bin && ./processor-task.py --config=../ini/processor-task.ini'
#cmd = 'cd /home/bgv/hce-node-bundle/api/python/bin' #0.00332117080688
#cmd = 'cd /home/bgv/hce-node-bundle/api/python/bin && ./processor-task.py' #0.369460105896
#cmd = 'python --version'  #0.00488090515137
#cmd = 'python -c \'print "Hello!"\'' #0.0166239738464
#cmd = 'cd /home/bgv/hce-node-bundle/api/python/bin && ./processor_feed_parser.py'
#cmd = 'cd /home/bgv/hce-node-bundle/api/python/bin && ./processor_feed_parser.py --config=../ini/processor_feed_parser.ini'
#cmd = 'cd /home/bgv/hce-node-bundle/api/python/bin && ./scraper.py'
cmd = 'cd /home/bgv/hce-node-bundle/api/python/bin && ./scraper.py --config=../ini/scraper.ini'

process = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, shell=True, close_fds=True)
(output, err) = process.communicate(input=stdinStr)
print "error: " + str(err)
exit_code = process.wait()
print "exit_code: " + str(exit_code)
print output

print (time.time() - s)
