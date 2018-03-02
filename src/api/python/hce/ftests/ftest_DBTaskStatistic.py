'''
@package: dc
@author scorp
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''
import ppath

import threading
import unittest
import os
try:
  import cPickle as pickle
except ImportError:
  import pickle

CMD_SNEW1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-stat-data/site_new1.dat")
CMD_SNEW2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-stat-data/site_new2.dat")
CMD_SNEW3 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-stat-data/site_new3.dat")
CMD_SNEW4 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-stat-data/site_new4.dat")
CMD_UNEW1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-stat-data/url_new1.dat")
CMD_UUPDATE1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-stat-data/url_update1.dat")
CMD_UUPDATE2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-stat-data/url_update2.dat")
CMD_UUPDATE3 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-stat-data/url_update3.dat")
CMD_UUPDATE4 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-stat-data/url_update4.dat")
CMD_UDELETE1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-stat-data/url_delete1.dat")
CMD_UAGE1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-stat-data/url_age1.dat")
CMD_SCEANUP1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-stat-data/site_cleanup1.dat")
CMD_SCEANUP2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-stat-data/site_cleanup2.dat")
CMD_UPURGE1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-stat-data/url_purge1.dat")


class Test(unittest.TestCase):

  mutex = threading.Lock()

  def setUp(self):
    pass


  def tearDown(self):
    pass


  def execCommand(self, command, step):
    obj = None
    print ">>> Start = " + str(command)
    fd = os.popen(command)
    if fd:
      localStr = fd.read()
      fd.close()
      print ">>> Finish = " + str(command)
      try:
        obj = pickle.loads(localStr)
      except EOFError:
        self.assertTrue(False, "Step%s >>> Invalid return data" % str(step))
    else:
      print ">>> Bad FD " +  + str(command)
    return obj


  def testSuite1(self):
    try:
      self.mutex.acquire()
      print "Suite1"
      self.execCommand(CMD_SNEW1, 0)
      self.execCommand(CMD_SNEW2, 0)
      self.execCommand(CMD_SNEW3, 0)
      self.execCommand(CMD_SNEW4, 0)
      self.execCommand(CMD_UNEW1, 1)
      self.execCommand(CMD_UUPDATE1, 2)
      self.execCommand(CMD_UUPDATE2, 2)
      self.execCommand(CMD_UUPDATE3, 2)
      self.execCommand(CMD_UUPDATE4, 2)
      self.execCommand(CMD_UDELETE1, 3)
      self.execCommand(CMD_UAGE1, 4)
      self.execCommand(CMD_SCEANUP1, 5)
      self.execCommand(CMD_SCEANUP2, 5)
      self.execCommand(CMD_UPURGE1, 6)
      print "Suite1 FN"
      self.mutex.release()
    except:
      self.mutex.release()
      raise


if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.TestLoader.sortTestMethodsUsing = None
  unittest.main()