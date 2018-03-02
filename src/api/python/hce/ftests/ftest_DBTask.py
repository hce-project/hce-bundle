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
import base64
import time
import unittest
import os
import sys
import dtm.EventObjects
import dc.EventObjects
import dc.Constants
import dbi.EventObjects
import ConfigParser
import hashlib
import dc_db.Constants
import sqlite3
import MySQLdb.cursors
import MySQLdb as mdb
try:
  import cPickle as pickle
except ImportError:
  import pickle
from dc.Constants import EVENT_TYPES
from app.Utils import PathMaker
from contextlib import closing


CMD_SNEW1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_new1.dat")
CMD_SNEW2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_new2.dat")
CMD_SSTATUS1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_status1.dat")
CMD_SSTATUS2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_status2.dat")
CMD_SUPDATE2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_update2.dat")
CMD_SDELETE1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_delete1.dat")
CMD_SCLEANUP2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_cleanup2.dat")


CMD_USITE_NEW1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_site_new1.dat")
CMD_USITE_NEW2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_site_new2.dat")
CMD_UNEW1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new1.dat")
CMD_USTATUS1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_status1.dat")
CMD_USTATUS2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_status2.dat")
CMD_UFETCH1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_fetch1.dat")
CMD_UFETCH2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_fetch2.dat")
CMD_UNEW2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new2.dat")
CMD_UNEW3 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new3.dat")
CMD_USTATUS2_3 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_status2-3.dat")
CMD_UFETCH1_2_3 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_fetch1-2-3.dat")
CMD_UUPDATE2_3_4 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_update2-3-4.dat")
CMD_UCONTENT1_4 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_content1-4.dat")
CMD_UDELETE1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_delete1.dat")
CMD_UDELETE4 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_delete4.dat")
CMD_UCLEANUP1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_cleanup1.dat")
CMD_UCLEANUP2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_cleanup2.dat")
CMD_UFETCH2_3_4 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_fetch2-3-4.dat")
CMD_USTATUS2_3_4 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_status2-3-4.dat")

CMD_USITE_NEW5 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_new5.dat")
CMD_UNEW5 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new5.dat")
CMD_UCONTENT5 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_content5.dat")
CMD_UCONTENT5_EXT = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_content5_ext.dat")
CMD_UCONTENT5_DYN = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_content5_dyn.dat")

CMD_SNEW_INTEL = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_new_intel.dat")
CMD_UNEW_INTEL = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_intel.dat")
CMD_UNEW_INTEL1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_intel1.dat")

CMD_UDEL_CRITERIONS_DEL = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_del_criterions_del.dat")
CMD_UDEL_CRITERIONS_FETCH = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_del_criterions_fetch.dat")
CMD_UCLEANUP_CRITERIONS = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_cleanup_criterions.dat")

CMD_SDELETE_BAD = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_delete_bad.dat")

CMD_SUPDATE_CRITERIONS = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_update_criterions.dat")
CMD_SSTATUS_CRITERIONS = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_status_criterions.dat")

CMD_SNEW_44 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_new44.dat")
CMD_SNEW_55 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_new55.dat")
CMD_SUPDATE_5 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_update5.dat")

CMD_UCONTENT_DBFIELDS = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_content_dbfields.dat")


CMD_SQLCUSTOM_BAD1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/sql_custom_bad1.dat")
CMD_SQLCUSTOM_BAD2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/sql_custom_bad2.dat")
CMD_SQLCUSTOM_OK = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/sql_custom_ok.dat")
CMD_SINTEL_UPDATE_OK = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_intel1_update.dat")

CMD_SSTATUS_TMP_OK = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_status_tmp.dat")
CMD_SITE_FIND_OK = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_find.dat")


CMD_SDELETE_DELAY5 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_delete_delay5.dat")
CMD_SCLEANUP_DELAY_INTEL1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_cleanup_delay_intel1.dat")
CMD_UDELETE_DELAY1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_delete_delay1.dat")
CMD_UCLEANUP_DELAY44 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_cleanup_delay44.dat")
CMD_UNEW_DELAY10 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_delay10.dat")
CMD_UNEW_DELAY11 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_delay11.dat")
CMD_UNEW_DELAY40 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_delay40.dat")
CMD_UNEW_DELAY41 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_delay41.dat")
CMD_UNEW_DELAY_A1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_delay_a1.dat")
CMD_UNEW_DELAY_A2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_delay_a2.dat")
CMD_UPURGE_GROUP = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_purge_group.dat")
CMD_UPURGE_SELECT_SITE = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_purge_select_site.dat")

CMD_UNEW_DELAY_TEST1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_dtest1.dat")
CMD_UNEW_DELAY_TEST2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_dtest2.dat")
CMD_UNEW_DELAY_TEST3 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_dtest3.dat")
CMD_UNEW_DELAY_TEST4 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_dtest4.dat")
CMD_UNEW_DELAY_TEST5 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_dtest5.dat")
CMD_UNEW_DELAY_TEST6 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_dtest6.dat")
CMD_UNEW_DELAY_TEST7 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_dtest7.dat")
CMD_UNEW_DELAY_TEST8 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_dtest8.dat")
CMD_SCLEANUP_DTEST1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_cleanup_dtest1.dat")
CMD_SCLEANUP_DTEST2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_cleanup_dtest2.dat")
CMD_SCLEANUP_DTEST3 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_cleanup_dtest3.dat")
CMD_SCLEANUP_DTEST4 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_cleanup_dtest4.dat")
CMD_SCLEANUP_DTEST5 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_cleanup_dtest5.dat")
CMD_SCLEANUP_DTEST6 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_cleanup_dtest6.dat")
CMD_SCLEANUP_DTEST7 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_cleanup_dtest7.dat")
CMD_SCLEANUP_DTEST8 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_cleanup_dtest8.dat")
CMD_SDELETE_DTEST1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_delete_dtest1.dat")
CMD_SDELETE_DTEST2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_delete_dtest2.dat")
CMD_UNEW_DELAY_TEST1A = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_dtest1a.dat")
CMD_UNEW_DELAY_TEST2A = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_dtest2a.dat")

CMD_UPURGE3 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_purge3.dat")
CMD_UPURGE4 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_purge4.dat")

CMD_SRECALCULATE = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_field_recalculator.dat")

CMD_UNEW_VERIFY = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_verify.dat")
CMD_UNEW_VERIFY2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_verify2.dat")
CMD_UVERIFY = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_verify.dat")
CMD_UNEW_UPDATE5 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_update5.dat")

CMD_SRECALCULATE_ADD = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_field_recalculator_add.dat")
CMD_SRECALCULATE_ADD1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_field_recalculator_add1.dat")

CMD_UNEW_AGE = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_age.dat")
CMD_UNEW_AGE1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_age1.dat")
CMD_UNEW_AGE2 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_age2.dat")
CMD_UAGE = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_age.dat")

CMD_SNEW_CONTENT = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_new_content.dat")
CMD_CUSTOM_CONTENT = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/sql_custom_content.dat")
CMD_CUSTOM_CONTENT_INSERT = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/sql_custom_content_insert.dat")
CMD_UCONTENT_MYSQL = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_content_mysql.dat")
CMD_UNEW_PUT = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_new_put.dat")
CMD_UPUT = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_put.dat")
CMD_UPUT1 = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/url_put1.dat")


class Test(unittest.TestCase):

  CD_PATH = "../../bin"
  CLASS_NAME = "TasksManager"
  KEY_VALUE_STORAGE_DIR = "key_value_storage_dir"
  RAW_DATA_DIR = "raw_data_dir"
  mutex = threading.Lock()
  contentType = dc_db.Constants.DB_DATA_MYSQL


  def setUp(self):
    self.url = None
    self.siteId = None
    self.urlMd5 = None


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


  def checkSStep1(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_NEW_RESPONSE, "Step%s >>> Bad return Event type"  % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse,
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.errorCode == dtm.EventObjects.GeneralResponse.ERROR_OK,
                    "Step%s >>> Some Error in Return object" % str(step))


  def checkSStep2(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_STATUS_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dc.EventObjects.Site, "Step%s >>> Bad return objsct type" % str(step))
    self.assertTrue(obj.eventObject.state == dc.EventObjects.Site.STATE_NOT_FOUND,
                    "Step%s >>> Wrong 'state' field value" % str(step))


  def checkSStep3(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_NEW_RESPONSE, "Step%s >>> Bad return Event type"  % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse,
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.errorCode == dtm.EventObjects.GeneralResponse.ERROR_OK,
                    "Step%s >>> Some Error in Return object" % str(step))


  def checkSStep4(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_STATUS_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dc.EventObjects.Site, "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.state != dc.EventObjects.Site.STATE_NOT_FOUND,
                    "Step%s >>> Wrong 'state' field value" % str(step))
    self.assertTrue(obj.eventObject.id == "z2", "Step%s >>> Wrong 'id' field value" % str(step))
    self.assertTrue(obj.eventObject.state == 1, "Step%s >>> Wrong 'state' field value" % str(step))


  def checkSStep5(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_UPDATE_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse,
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.errorCode == dtm.EventObjects.GeneralResponse.ERROR_OK,
                    "Step%s >>> Wrong 'errorCode' field value" % str(step))


  def checkSStep6(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_DELETE_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse,
                    "Step%s >>> Bad return object type" % str(step))


  def checkSStep7(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_STATUS_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dc.EventObjects.Site, "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.state == dc.EventObjects.Site.STATE_NOT_FOUND,
                    "Step%s >>> Wrong 'state' field value" % str(step))


  def checkSStep8(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_STATUS_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dc.EventObjects.Site, "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.state != dc.EventObjects.Site.STATE_NOT_FOUND,
                    "Step%s >>> Wrong 'state' field value" % str(step))
    self.assertTrue(obj.eventObject.id == "z2", "Step%s >>> Wrong 'id' field value" % str(step))
    self.assertTrue(obj.eventObject.state == 55, "Step%s >>> Wrong 'state' field value" % str(step))
    self.assertTrue(type(obj.eventObject.uDate) == str, "Step%s >>> Wrong 'uDate' field type" % str(step))
    self.assertTrue(type(obj.eventObject.tcDate) == str, "Step%s >>> Wrong 'tcDate' field type" % str(step))
    self.assertTrue(type(obj.eventObject.cDate) == str, "Step%s >>> Wrong 'cDate' field type" % str(step))
    self.assertTrue(type(obj.eventObject.recrawlDate) == str, "Step%s >>> Wrong 'recrawlDate' field type" % str(step))
    self.assertTrue(type(obj.eventObject.description) == str, "Step%s >>> Wrong 'description' field type" % str(step))
    self.assertTrue(obj.eventObject.description == '33', "Step%s >>> Wrong 'description' value" % str(step))


  def checkSStep9(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_CLEANUP_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse,
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.errorCode == dtm.EventObjects.GeneralResponse.ERROR_OK,
                    "Step%s >>> errorCode badvalue" % str(step))


  def checkSStep10(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_STATUS_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dc.EventObjects.Site, "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.state != dc.EventObjects.Site.STATE_NOT_FOUND,
                    "Step%s >>> Wrong 'state' field value" % str(step))
    self.assertTrue(obj.eventObject.id == "z2", "Step%s >>> Wrong 'id' field value" % str(step))
    self.assertTrue(obj.eventObject.state == dc.EventObjects.Site.STATE_ACTIVE, 
                    "Step%s >>> Wrong 'state' field value" % str(step))
    self.assertTrue(type(obj.eventObject.properties) == type([]),
                    "Step%s >>> Wrong 'properties' field type" % str(step))
    self.assertTrue(type(obj.eventObject.filters) == type([]),
                    "Step%s >>> Wrong 'filters' field type" % str(step))
    self.assertTrue(len(obj.eventObject.properties) == 2, "Step%s >>> Wrong 'properties' field size" % str(step))
    self.assertTrue(type(obj.eventObject.properties[0]["cDate"]) == str,
                    "Step%s >>> Wrong 'properties[0][cDate]' field value" % str(step))
    self.assertTrue(obj.eventObject.properties[0]["uDate"] == None,
                    "Step%s >>> Wrong 'properties[0][uDate]' field value" % str(step))
    self.assertTrue(len(obj.eventObject.properties) == 2, "Step%s >>> Wrong 'properties' field size" % str(step))
    self.assertTrue(len(obj.eventObject.filters) == 1, "Step%s >>> Wrong 'filters' field size" % str(step))


  def checkUStep1(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_NEW_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse, 
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.errorCode == dtm.EventObjects.GeneralResponse.ERROR_OK,
                    "Step%s >>> GeneralResponse come error" % str(step))
  

  def checkUStep2(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_STATUS_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 1, "Step%s >>> Bad return object len" % str(step))
    self.assertTrue(obj.eventObject[0].siteId == "z1", "Step%s >>> Bad return object [0].siteId value" % str(step))
  

  def checkUStep3(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_STATUS_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 0, "Step%s >>> Bad return object len" % str(step))


  def checkUStep4(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_FETCH_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 1, "Step%s >>> Bad return object len" % str(step))
    self.assertTrue(obj.eventObject[0].siteId == "z1", "Step%s >>> Bad return object [0].siteId value" % str(step))


  def checkUStep5(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_FETCH_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 0, "Step%s >>> Bad return object len" % str(step))


  def checkUStep6(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_NEW_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse, 
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.errorCode == dtm.EventObjects.GeneralResponse.ERROR_OK,
                    "Step%s >>> GeneralResponse come error" % str(step))
  
  
  def checkUStep7(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_NEW_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse, 
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.errorCode == dtm.EventObjects.GeneralResponse.ERROR_OK,
                    "Step%s >>> GeneralResponse come error" % str(step))
  

  def checkUStep8(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_STATUS_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 2, "Step%s >>> Bad return object len" % str(step))
    self.assertTrue(obj.eventObject[0].siteId == "z1", "Step%s >>> Bad return object[0].siteId value" % str(step))
    self.assertTrue(obj.eventObject[0].url == 
                    "http://url2.com/", "Step%s >>> Bad return object[0].url value" % str(step))
    
    self.assertTrue(type(obj.eventObject[0].UDate) == str, "Step%s >>> Wrong 'UDate' field type" % str(step))
    self.assertTrue(type(obj.eventObject[0].CDate) == str, "Step%s >>> Wrong 'CDate' field type" % str(step))
    self.assertTrue(type(obj.eventObject[0].lastModified) == str, 
                    "Step%s >>> Wrong 'lastModified' field type" % str(step))
    self.assertTrue(obj.eventObject[0].tcDate == None, "Step%s >>> Wrong 'tcDate' field type" % str(step))

    self.assertTrue(obj.eventObject[1].siteId == "z2", "Step%s >>> Bad return object[1].siteId value" % str(step))
    self.assertTrue(obj.eventObject[1].url == 
                    "http://url3.com/", "Step%s >>> Bad return object10].url value" % str(step))

    self.assertTrue(type(obj.eventObject[1].UDate) == str, "Step%s >>> Wrong 'UDate' field type" % str(step))
    self.assertTrue(type(obj.eventObject[1].CDate) == str, "Step%s >>> Wrong 'CDate' field type" % str(step))
    self.assertTrue(type(obj.eventObject[1].lastModified) == str, 
                    "Step%s >>> Wrong 'lastModified' field type" % str(step))
    self.assertTrue(obj.eventObject[1].tcDate == None, "Step%s >>> Wrong 'tcDate' field type" % str(step))
    
  
  def checkUStep9(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_FETCH_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 3, "Step%s >>> Bad return object len" % str(step))
    self.assertTrue(obj.eventObject[0].siteId == "z1", "Step%s >>> Bad return object[0].siteId value" % str(step))
    self.assertTrue(obj.eventObject[0].url == 
                    "http://url1.com/", "Step%s >>> Bad return object[0].url value" % str(step))
    self.assertTrue(obj.eventObject[0].UDate == None, "Step%s >>> Wrong 'UDate' field type" % str(step))
    self.assertTrue(type(obj.eventObject[0].CDate) == str, "Step%s >>> Wrong 'CDate' field type" % str(step))
    self.assertTrue(obj.eventObject[0].lastModified == None, 
                    "Step%s >>> Wrong 'lastModified' field type" % str(step))
    self.assertTrue(obj.eventObject[0].tcDate == None, "Step%s >>> Wrong 'tcDate' field type" % str(step))
    self.assertTrue(obj.eventObject[1].siteId == "z1", "Step%s >>> Bad return object[1].siteId value" % str(step))
    self.assertTrue(obj.eventObject[1].url == 
                    "http://url2.com/", "Step%s >>> Bad return object[1].url value" % str(step))
    self.assertTrue(type(obj.eventObject[1].UDate) == str, "Step%s >>> Wrong 'UDate' field type" % str(step))
    self.assertTrue(type(obj.eventObject[1].CDate) == str, "Step%s >>> Wrong 'CDate' field type" % str(step))
    self.assertTrue(type(obj.eventObject[1].lastModified) == str, 
                    "Step%s >>> Wrong 'lastModified' field type" % str(step))
    self.assertTrue(obj.eventObject[1].tcDate == None, "Step%s >>> Wrong 'tcDate' field type" % str(step))
    self.assertTrue(obj.eventObject[2].siteId == "z2", "Step%s >>> Bad return object[2].siteId value" % str(step))
    self.assertTrue(obj.eventObject[2].url == 
                    "http://url3.com/", "Step%s >>> Bad return object[2].url value" % str(step))
    self.assertTrue(type(obj.eventObject[2].UDate) == str, "Step%s >>> Wrong 'UDate' field type" % str(step))
    self.assertTrue(type(obj.eventObject[2].CDate) == str, "Step%s >>> Wrong 'CDate' field type" % str(step))
    self.assertTrue(type(obj.eventObject[2].lastModified) == str, 
                    "Step%s >>> Wrong 'lastModified' field type" % str(step))
    self.assertTrue(obj.eventObject[2].tcDate == None, "Step%s >>> Wrong 'tcDate' field type" % str(step))


  def checkUStep10(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_UPDATE_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse, 
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject.statuses) == 4, "Step%s >>> Wrong GeneralResponse.statuses len" % str(step))
    self.assertTrue(obj.eventObject.statuses[0] == True,
                    "Step%s >>> Wrong GeneralResponse.statuses[0] value" % str(step))
    self.assertTrue(obj.eventObject.statuses[1] == True,
                    "Step%s >>> Wrong GeneralResponse.statuses[1] value" % str(step))
    self.assertTrue(obj.eventObject.statuses[2] == False,
                    "Step%s >>> Wrong GeneralResponse.statuses[2] value" % str(step))
    self.assertTrue(obj.eventObject.statuses[3] == True,
                    "Step%s >>> Wrong GeneralResponse.statuses[3] value" % str(step))


  def checkUStep11(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_CONTENT_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 2, "Step%s >>> Bad return object len" % str(step))
    self.assertTrue(obj.eventObject[0].url ==
                    "http://url1.com/", "Step%s >>> Bad return object[0].url value" % str(step))
    self.assertTrue(type(obj.eventObject[0].rawContents) == type([]),
                    "Step%s >>> Bad return object[0].rawContent type" % str(step))
    self.assertTrue(len(obj.eventObject[0].rawContents) == 0,
                    "Step%s >>> Bad return object[0].rawContent len" % str(step))
    self.assertTrue(obj.eventObject[1].url == 
                    "http://url4.com/", "Step%s >>> Bad return object[1].url value" % str(step))
    self.assertTrue(type(obj.eventObject[1].rawContents) == type([]),
                    "Step%s >>> Bad return object[1].rawContent type" % str(step))
    self.assertTrue(len(obj.eventObject[1].rawContents) == 0,
                    "Step%s >>> Bad return object[1].rawContent len" % str(step))


  def checkUStep12(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_DELETE_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse, 
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(type(obj.eventObject.statuses) == type([]),
                    "Step%s >>> Bad return object.statuses type" % str(step))
    self.assertTrue(len(obj.eventObject.statuses) == 1, "Step%s >>> Bad return object.statuses len" % str(step))
    self.assertTrue(obj.eventObject.statuses[0] == True, "Step%s >>> Bad return object.statuses[0] value" % str(step))
  
  
  def checkUStep13(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_DELETE_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse, 
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(type(obj.eventObject.statuses) == type([]),
                    "Step%s >>> Bad return object.statuses type" % str(step))
    self.assertTrue(len(obj.eventObject.statuses) == 1, "Step%s >>> Bad return object.statuses len" % str(step))
    self.assertTrue(obj.eventObject.statuses[0] == False, "Step%s >>> Bad return object.statuses[0] value" % str(step))
  

  def checkUStep14(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_CLEANUP_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse, 
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(type(obj.eventObject.statuses) == type([]),
                    "Step%s >>> Bad return object.statuses type" % str(step))
    self.assertTrue(len(obj.eventObject.statuses) == 1, "Step%s >>> Bad return object.statuses len" % str(step))
    self.assertTrue(obj.eventObject.statuses[0] == False, "Step%s >>> Bad return object.statuses[0] value" % str(step))
    
  
  def checkUStep15(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_CLEANUP_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse, 
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(type(obj.eventObject.statuses) == type([]),
                    "Step%s >>> Bad return object.statuses type" % str(step))
    self.assertTrue(len(obj.eventObject.statuses) == 1, "Step%s >>> Bad return object.statuses len" % str(step))
    self.assertTrue(obj.eventObject.statuses[0] == False, "Step%s >>> Bad return object.statuses[0] value" % str(step))
  

  def checkUStep16(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_FETCH_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 1, "Step%s >>> Bad return object len" % str(step))
    self.assertTrue(obj.eventObject[0].siteId == "z2", "Step%s >>> Bad return object[0].siteId value" % str(step))
    self.assertTrue(obj.eventObject[0].url == 
                    "http://url3.com/", "Step%s >>> Bad return object[0].url value" % str(step))


  def checkUStep17(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_STATUS_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 2, "Step%s >>> Bad return object len" % str(step))
    self.assertTrue(obj.eventObject[0].siteId == "z1", "Step%s >>> Bad return object[0].siteId value" % str(step))
    self.assertTrue(obj.eventObject[0].url == 
                    "http://url2.com/", "Step%s >>> Bad return object[0].url value" % str(step))
    self.assertTrue(obj.eventObject[1].siteId == "z2", "Step%s >>> Bad return object[1].siteId value" % str(step))
    self.assertTrue(obj.eventObject[1].url == 
                    "http://url3.com/", "Step%s >>> Bad return object[0].url value" % str(step))


  def checkCStep1(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_CONTENT_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 3, "Step%s >>> Bad return object len" % str(step))
    self.assertTrue(obj.eventObject[0].url == 
                    "http://url1.com/", "Step%s >>> Bad return object[0].url value" % str(step))
    self.assertTrue(type(obj.eventObject[0].rawContents) == type([]),
                    "Step%s >>> Bad return object[0].rawContent type" % str(step))
    self.assertTrue(len(obj.eventObject[0].rawContents) == 0,
                    "Step%s >>> Bad return object[0].rawContent len" % str(step))

    self.assertTrue(type(obj.eventObject[0].processedContents) == type([]),
                    "Step%s >>> Bad return object[0].processedContents type" % str(step))
    self.assertTrue(len(obj.eventObject[0].processedContents) == 0,
                    "Step%s >>> Bad return object[0].processedContents len" % str(step))
    self.assertTrue(obj.eventObject[1].url == 
                    "http://url5.com/", "Step%s >>> Bad return object[1].url value" % str(step))
    self.assertTrue(type(obj.eventObject[1].rawContents) == type([]),
                    "Step%s >>> Bad return object[1].rawContent type" % str(step))

    self.assertTrue(len(obj.eventObject[1].rawContents) == 2,
                    "Step%s >>> Bad return object[1].rawContent len" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].rawContents[0].buffer)
    self.assertTrue(baseStr == "EEEEE",
                    "Step%s >>> Bad return obj.eventObject[1].rawContents[1].buffer value" % str(step))
    print(obj.eventObject[1].rawContents[0].cDate)
    self.assertTrue(len(obj.eventObject[1].processedContents) == 1,
                    "Step%s >>> Bad return object[1].processedContents len" % str(step))
    self.assertTrue(obj.eventObject[1].processedContents[0].buffer == "EEEEE",
                    "Step%s >>> Bad return obj.processedContents[1].rawContents[0].buffer value" % str(step))
    print(obj.eventObject[1].rawContents[0].cDate)
    baseStr = base64.b64decode(obj.eventObject[1].rawContents[1].buffer)
    self.assertTrue(baseStr == "ArashTIDY",
                    "Step%s >>> Bad return obj.eventObject[1].rawContents[1].buffer value" % str(step))
    self.assertTrue(obj.eventObject[1].rawContents[1].typeId == dc.EventObjects.Content.CONTENT_TIDY_CONTENT,
                    "Step%s >>> Bad return obj.eventObject[1].rawContents[1].typeId value" % str(step))
    print(obj.eventObject[1].rawContents[1].cDate)

    self.assertTrue(obj.eventObject[2].url == 
                    "http://url5.com/", "Step%s >>> Bad return object[1].url value" % str(step))
    self.assertTrue(type(obj.eventObject[2].rawContents) == type([]),
                    "Step%s >>> Bad return object[1].rawContent type" % str(step))
    self.assertTrue(len(obj.eventObject[2].rawContents) == 10,
                    "Step%s >>> Bad return object[2].rawContent len" % str(step))
    baseStr = base64.b64decode(obj.eventObject[2].rawContents[0].buffer)
    self.assertTrue(baseStr == "EEEEE",
                    "Step%s >>> Bad return obj.eventObject[2].rawContents[0].buffer value" % str(step))
    print(obj.eventObject[2].rawContents[0].cDate)
    baseStr = base64.b64decode(obj.eventObject[2].rawContents[1].buffer)
    self.assertTrue(baseStr == "AAAAA",
                    "Step%s >>> Bad return obj.eventObject[2].rawContents[1].buffer value" % str(step))
    print(obj.eventObject[2].rawContents[1].cDate)
    baseStr = base64.b64decode(obj.eventObject[2].rawContents[2].buffer)
    self.assertTrue(baseStr == "AAAAA",
                    "Step%s >>> Bad return obj.eventObject[2].rawContents[2].buffer value" % str(step))
    print(obj.eventObject[2].rawContents[2].cDate)
    baseStr = base64.b64decode(obj.eventObject[2].rawContents[3].buffer)
    self.assertTrue(baseStr == "BBBBB",
                    "Step%s >>> Bad return obj.eventObject[2].rawContents[3].buffer value" % str(step))
    print(obj.eventObject[2].rawContents[3].cDate)
    baseStr = base64.b64decode(obj.eventObject[2].rawContents[4].buffer)
    self.assertTrue(baseStr == "CCCCC",
                    "Step%s >>> Bad return obj.eventObject[2].rawContents[4].buffer value" % str(step))
    print(obj.eventObject[2].rawContents[4].cDate)
    baseStr = base64.b64decode(obj.eventObject[2].rawContents[5].buffer)
    self.assertTrue(baseStr == "EEEEE",
                    "Step%s >>> Bad return obj.eventObject[2].rawContents[5].buffer value" % str(step))
    print(obj.eventObject[2].rawContents[5].cDate)
    baseStr = base64.b64decode(obj.eventObject[2].rawContents[6].buffer)
    self.assertTrue(baseStr == "ArashTIDY",
                    "Step%s >>> Bad return obj.eventObject[2].rawContents[6].buffer value" % str(step))
    self.assertTrue(obj.eventObject[2].rawContents[6].typeId == dc.EventObjects.Content.CONTENT_TIDY_CONTENT,
                    "Step%s >>> Bad return obj.eventObject[2].rawContents[6].typeId value" % str(step))
    print(obj.eventObject[2].rawContents[6].cDate)

    baseStr = base64.b64decode(obj.eventObject[2].rawContents[7].buffer)
    self.assertTrue(baseStr == "AAATIDY",
                    "Step%s >>> Bad return obj.eventObject[1].rawContents[7].buffer value" % str(step))
    self.assertTrue(obj.eventObject[2].rawContents[7].typeId == dc.EventObjects.Content.CONTENT_TIDY_CONTENT,
                    "Step%s >>> Bad return obj.eventObject[1].rawContents[7].typeId value" % str(step))
    print(obj.eventObject[2].rawContents[7].cDate)
    baseStr = base64.b64decode(obj.eventObject[2].rawContents[8].buffer)
    self.assertTrue(baseStr == "AAATIDY",
                    "Step%s >>> Bad return obj.eventObject[2].rawContents[8].buffer value" % str(step))
    self.assertTrue(obj.eventObject[2].rawContents[8].typeId == dc.EventObjects.Content.CONTENT_TIDY_CONTENT,
                    "Step%s >>> Bad return obj.eventObject[2].rawContents[8].typeId value" % str(step))
    print(obj.eventObject[2].rawContents[8].cDate)
    baseStr = base64.b64decode(obj.eventObject[2].rawContents[9].buffer)
    self.assertTrue(baseStr == "ArashTIDY",
                    "Step%s >>> Bad return obj.eventObject[2].rawContents[9].buffer value" % str(step))
    self.assertTrue(obj.eventObject[2].rawContents[9].typeId == dc.EventObjects.Content.CONTENT_TIDY_CONTENT,
                    "Step%s >>> Bad return obj.eventObject[2].rawContents[9].typeId value" % str(step))
    print(obj.eventObject[2].rawContents[9].cDate)
    self.assertTrue(len(obj.eventObject[1].processedContents) == 1,
                    "Step%s >>> Bad return object[1].processedContents len" % str(step))
    self.assertTrue(obj.eventObject[1].processedContents[0].buffer == "EEEEE",
                    "Step%s >>> Bad return obj.processedContents[1].rawContents[0].buffer value" % str(step))
    print(obj.eventObject[1].processedContents[0].cDate)


  def checkCStep2(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_CONTENT_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 3, "Step%s >>> Bad return object len" % str(step))
    self.assertTrue(obj.eventObject[0].url == 
                    "http://url1.com/", "Step%s >>> Bad return object[0].url value" % str(step))
    self.assertTrue(type(obj.eventObject[0].rawContents) == type([]),
                    "Step%s >>> Bad return object[0].rawContent type" % str(step))
    self.assertTrue(len(obj.eventObject[0].rawContents) == 0,
                    "Step%s >>> Bad return object[0].rawContent len" % str(step))

    self.assertTrue(type(obj.eventObject[0].processedContents) == type([]),
                    "Step%s >>> Bad return object[0].processedContents type" % str(step))
    self.assertTrue(len(obj.eventObject[0].processedContents) == 0,
                    "Step%s >>> Bad return object[0].processedContents len" % str(step))
    self.assertTrue(type(obj.eventObject[0].headers) == type([]),
                    "Step%s >>> Bad return object[0].headers type" % str(step))
    self.assertTrue(len(obj.eventObject[0].headers) == 0,
                    "Step%s >>> Bad return object[0].headers len" % str(step))
    self.assertTrue(type(obj.eventObject[0].requests) == type([]),
                    "Step%s >>> Bad return object[0].requests type" % str(step))
    self.assertTrue(len(obj.eventObject[0].requests) == 0,
                    "Step%s >>> Bad return object[0].requests len" % str(step))
    self.assertTrue(type(obj.eventObject[0].meta) == type([]),
                    "Step%s >>> Bad return object[0].meta type" % str(step))
    self.assertTrue(len(obj.eventObject[0].meta) == 0,
                    "Step%s >>> Bad return object[0].meta len" % str(step))
    self.assertTrue(type(obj.eventObject[0].cookies) == type([]),
                    "Step%s >>> Bad return object[0].cookies type" % str(step))
    self.assertTrue(len(obj.eventObject[0].cookies) == 0,
                    "Step%s >>> Bad return object[0].cookies len" % str(step))

    self.assertTrue(obj.eventObject[1].url == 
                    "http://url5.com/", "Step%s >>> Bad return object[0].url value" % str(step))
    self.assertTrue(type(obj.eventObject[1].rawContents) == type([]),
                    "Step%s >>> Bad return object[1].rawContent type" % str(step))
    self.assertTrue(len(obj.eventObject[1].rawContents) == 8,
                    "Step%s >>> Bad return object[1].rawContent len" % str(step))
    self.assertTrue(len(obj.eventObject[1].headers) == 5,
                    "Step%s >>> Bad return object[1].headers len" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].headers[0].buffer)
    self.assertTrue(baseStr == "AAAAAheaders",
                    "Step%s >>> Bad return obj.eventObject[1].headers[0].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].headers[1].buffer)
    self.assertTrue(baseStr == "AAAAAheaders",
                    "Step%s >>> Bad return obj.eventObject[1].headers[1].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].headers[2].buffer)
    self.assertTrue(baseStr == "BBBBBheaders",
                    "Step%s >>> Bad return obj.eventObject[1].headers[2].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].headers[3].buffer)
    self.assertTrue(baseStr == "CCCCCheaders",
                    "Step%s >>> Bad return obj.eventObject[1].headers[3].buffer value" % str(step))
    self.assertTrue(len(obj.eventObject[1].requests) == 5,
                    "Step%s >>> Bad return object[1].requests len" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].requests[0].buffer)
    self.assertTrue(baseStr == "AAAAArequests",
                    "Step%s >>> Bad return obj.eventObject[1].requests[0].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].requests[1].buffer)
    self.assertTrue(baseStr == "AAAAArequests",
                    "Step%s >>> Bad return obj.eventObject[1].requests[1].buffer value" % str(step))
    self.assertTrue(obj.eventObject[1].requests[2] == None,
                    "Step%s >>> Bad return obj.eventObject[1].requests[2].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].requests[3].buffer)
    self.assertTrue(baseStr == "CCCCCrequests",
                    "Step%s >>> Bad return obj.eventObject[1].requests[3].buffer value" % str(step))
    self.assertTrue(len(obj.eventObject[1].meta) == 5,
                    "Step%s >>> Bad return object[1].meta len" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].meta[0].buffer)
    self.assertTrue(baseStr == "AAAAAmeta",
                    "Step%s >>> Bad return obj.eventObject[1].meta[0].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].meta[1].buffer)
    self.assertTrue(baseStr == "AAAAAmeta",
                    "Step%s >>> Bad return obj.eventObject[1].meta[1].buffer value" % str(step))
    self.assertTrue(obj.eventObject[1].meta[2] == None,
                    "Step%s >>> Bad return obj.eventObject[1].meta[2].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].meta[3].buffer)
    self.assertTrue(baseStr == "CCCCCmeta",
                    "Step%s >>> Bad return obj.eventObject[1].meta[3].buffer value" % str(step))
    self.assertTrue(len(obj.eventObject[1].cookies) == 5,
                    "Step%s >>> Bad return object[1].cookies len" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].cookies[0].buffer)
    self.assertTrue(baseStr == "AAAAAcookies",
                    "Step%s >>> Bad return obj.eventObject[1].cookies[0].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].cookies[1].buffer)
    self.assertTrue(baseStr == "AAAAAcookies",
                    "Step%s >>> Bad return obj.eventObject[1].cookies[1].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].cookies[2].buffer)
    self.assertTrue(baseStr == "BBBBBcookies",
                    "Step%s >>> Bad return obj.eventObject[1].cookies[2].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].cookies[3].buffer)
    self.assertTrue(baseStr == "CCCCCcookies",
                    "Step%s >>> Bad return obj.eventObject[1].cookies[3].buffer value" % str(step))
    
    self.assertTrue(obj.eventObject[2].url == 
                    "http://url5.com/", "Step%s >>> Bad return object[0].url value" % str(step))
    self.assertTrue(type(obj.eventObject[2].rawContents) == type([]),
                    "Step%s >>> Bad return object[2].rawContent type" % str(step))
    self.assertTrue(len(obj.eventObject[2].rawContents) == 8,
                    "Step%s >>> Bad return object[2].rawContent len" % str(step))
    self.assertTrue(len(obj.eventObject[2].headers) == 5,
                    "Step%s >>> Bad return object[2].headers len" % str(step))
    baseStr = base64.b64decode(obj.eventObject[2].headers[0].buffer)
    self.assertTrue(baseStr == "AAAAAheaders",
                    "Step%s >>> Bad return obj.eventObject[2].headers[0].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[2].headers[1].buffer)
    self.assertTrue(baseStr == "AAAAAheaders",
                    "Step%s >>> Bad return obj.eventObject[2].headers[1].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[2].headers[2].buffer)
    self.assertTrue(baseStr == "BBBBBheaders",
                    "Step%s >>> Bad return obj.eventObject[2].headers[2].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[2].headers[3].buffer)
    self.assertTrue(baseStr == "CCCCCheaders",
                    "Step%s >>> Bad return obj.eventObject[2].headers[3].buffer value" % str(step))
    self.assertTrue(len(obj.eventObject[2].requests) == 5,
                    "Step%s >>> Bad return object[2].requests len" % str(step))
    baseStr = base64.b64decode(obj.eventObject[2].requests[0].buffer)
    self.assertTrue(baseStr == "AAAAArequests",
                    "Step%s >>> Bad return obj.eventObject[2].requests[0].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[2].requests[1].buffer)
    self.assertTrue(baseStr == "AAAAArequests",
                    "Step%s >>> Bad return obj.eventObject[2].requests[1].buffer value" % str(step))
    self.assertTrue(obj.eventObject[2].requests[2] == None,
                    "Step%s >>> Bad return obj.eventObject[2].requests[2].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[2].requests[3].buffer)
    self.assertTrue(baseStr == "CCCCCrequests",
                    "Step%s >>> Bad return obj.eventObject[2].requests[3].buffer value" % str(step))
    self.assertTrue(len(obj.eventObject[2].meta) == 5,
                    "Step%s >>> Bad return object[2].meta len" % str(step))
    baseStr = base64.b64decode(obj.eventObject[2].meta[0].buffer)
    self.assertTrue(baseStr == "AAAAAmeta",
                    "Step%s >>> Bad return obj.eventObject[2].meta[0].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[2].meta[1].buffer)
    self.assertTrue(baseStr == "AAAAAmeta",
                    "Step%s >>> Bad return obj.eventObject[2].meta[1].buffer value" % str(step))
    self.assertTrue(obj.eventObject[2].meta[2] == None,
                    "Step%s >>> Bad return obj.eventObject[2].meta[2].buffer value" % str(step))
    baseStr = base64.b64decode(obj.eventObject[2].meta[3].buffer)
    self.assertTrue(baseStr == "CCCCCmeta",
                    "Step%s >>> Bad return obj.eventObject[2].meta[3].buffer value" % str(step))
    self.assertTrue(len(obj.eventObject[2].cookies) == 0,
                    "Step%s >>> Bad return object[2].cookies len" % str(step))


  def checkCStep3(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_CONTENT_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 3, "Step%s >>> Bad return object len" % str(step))

    self.assertTrue(obj.eventObject[1].url == 
                    "http://url5.com/", "Step%s >>> Bad return object[0].url value" % str(step))
    self.assertTrue(type(obj.eventObject[1].rawContents) == type([]),
                    "Step%s >>> Bad return object[1].rawContent type" % str(step))
    self.assertTrue(len(obj.eventObject[1].rawContents) == 7,
                    "Step%s >>> Bad return object[1].rawContent len" % str(step))
    self.assertTrue(len(obj.eventObject[1].headers) == 5,
                    "Step%s >>> Bad return object[1].headers len" % str(step))
    baseStr = base64.b64decode(obj.eventObject[1].rawContents[6].buffer)
    self.assertTrue(baseStr == "AAADYN",
                    "Step%s >>> Bad return obj.eventObject[1].rawContents[6].buffer value" % str(step))
    self.assertTrue(obj.eventObject[1].rawContents[6].typeId == dc.EventObjects.Content.CONTENT_DYNAMIC_CONTENT,
                    "Step%s >>> Bad return obj.eventObject[1].rawContents[6].typeId value" % str(step))
    print(obj.eventObject[1].rawContents[6].cDate)
    
    self.assertTrue(obj.eventObject[2].url == 
                    "http://url5.com/", "Step%s >>> Bad return object[0].url value" % str(step))
    self.assertTrue(type(obj.eventObject[2].rawContents) == type([]),
                    "Step%s >>> Bad return object[2].rawContent type" % str(step))
    self.assertTrue(len(obj.eventObject[2].rawContents) == 7,
                    "Step%s >>> Bad return object[2].rawContent len" % str(step))
    self.assertTrue(len(obj.eventObject[2].headers) == 5,
                    "Step%s >>> Bad return object[2].headers len" % str(step))
    baseStr = base64.b64decode(obj.eventObject[2].rawContents[6].buffer)
    self.assertTrue(baseStr == "AAADYN",
                    "Step%s >>> Bad return obj.eventObject[2].rawContents[6].buffer value" % str(step))
    self.assertTrue(obj.eventObject[2].rawContents[6].typeId == dc.EventObjects.Content.CONTENT_DYNAMIC_CONTENT,
                    "Step%s >>> Bad return obj.eventObject[2].rawContents[6].typeId value" % str(step))
    print(obj.eventObject[2].rawContents[6].cDate)
    

  def checkIntelStep0(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_NEW_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse,
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.errorCode == dtm.EventObjects.GeneralResponse.ERROR_OK,
                    "Step%s >>> Some Error in Return object" % str(step))
    self.assertTrue(len(obj.eventObject.statuses) == 1, "Step%s >>> obj.eventObject.statuses len != 1" % str(step))
    self.assertTrue(obj.eventObject.statuses[0] == "intel1", "Step%s >>> obj.eventObject.statuses[0] != \"intel1\"" 
                    % str(step))


  def checkIntelStep3(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_NEW_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse,
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.errorCode == dc_db.Constants.TASK_DUPLICATE_ERR,
                    "Step%s >>> Some Error in Return object" % str(step))
    self.assertTrue(len(obj.eventObject.statuses) == 1, "Step%s >>> obj.eventObject.statuses len != 1" % str(step))
    self.assertTrue(obj.eventObject.statuses[0] == None, "Step%s >>> obj.eventObject.statuses[3] != None"
                    % str(step))


  def checkCriterions2(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_FETCH_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 3, "Step%s >>> Bad return object len" % str(step))
    self.assertTrue(obj.eventObject[0].siteId == "z2", "Step%s >>> Bad return object[0].siteId value" % str(step))
    self.assertTrue(obj.eventObject[1].siteId == "intel1", "Step%s >>> Bad return object[1].siteId value" % str(step))
    self.assertTrue(obj.eventObject[1].url == 
                    "http://intel.com/path1/path2", "Step%s >>> Bad return object[1].url value" % str(step))
    self.assertTrue(obj.eventObject[1].state == 77, "Step%s >>> Bad return object[1].state value" % str(step))
    self.assertTrue(obj.eventObject[1].status == 77, "Step%s >>> Bad return object[1].status value" % str(step))
    self.assertTrue(obj.eventObject[2].siteId == "intel1", "Step%s >>> Bad return object[2].siteId value" % str(step))
    self.assertTrue(obj.eventObject[2].url == 
                    "http://intel.com/path1/", "Step%s >>> Bad return object[2].url value" % str(step))
    
    
  def checkDeleteBad(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_DELETE_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse,
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.errorCode == dtm.EventObjects.GeneralResponse.ERROR_OK,
                    "Step%s >>> Wrong obj.eventObject.errorCode value" % str(step))
    self.assertTrue(obj.eventObject.errorMessage == "",
                    "Step%s >>> Wrong obj.eventObject.errorMessage value" % str(step))


  def checkSiteCriterions1(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_UPDATE_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse,
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject.statuses) == 1, "Step%s >>> Bad return object statuses len" % str(step))
    for status in obj.eventObject.statuses:
      self.assertTrue(status == dtm.EventObjects.GeneralResponse.ERROR_OK, 
                      "Step%s >>> Bad return object statuses value" % str(step))


  def checkSiteCriterions2(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_STATUS_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dc.EventObjects.Site, "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.maxResources == 6688, 
                    "Step%s >>> Bad return eventObject.maxResources value" % str(step))
    
    
  def checkURLContentBDFields(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_CONTENT_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 2, "Step%s >>> Bad return object len" % str(step))
    self.assertTrue(obj.eventObject[0].url == 
                    "http://url1.com/", "Step%s >>> Bad return object[0].url value" % str(step))
    self.assertTrue(type(obj.eventObject[0].dbFields) == type({}), 
                    "Step%s >>> Wrong object[0].dbFields type" % str(step))
    self.assertTrue(len(obj.eventObject[0].dbFields) == 0, "Step%s >>> Wrong object[0].dbFields len" % str(step))
    self.assertTrue(obj.eventObject[1].url == 
                    "http://url1.com/", "Step%s >>> Bad return object[1].url value" % str(step))
    self.assertTrue(type(obj.eventObject[1].dbFields) == type({}), 
                    "Step%s >>> Wrong object[1].dbFields type" % str(step))
    self.assertTrue(len(obj.eventObject[1].dbFields) == 4,
                    "Step%s >>> Wrong object[1].dbFields len" % str(step))
    self.assertTrue(obj.eventObject[1].dbFields["CDate"] != None,
                    "Step%s >>> Wrong object[1].dbFields[CDate] value" % str(step))
    self.assertTrue(obj.eventObject[1].dbFields["RawContentMd5"] != None,
                    "Step%s >>> Wrong object[1].dbFields[RawContentMd5] value" % str(step))
    self.assertTrue(obj.eventObject[1].dbFields["MRate"] != None,
                    "Step%s >>> Wrong object[1].dbFields[MRate] value" % str(step))
    self.assertTrue(obj.eventObject[1].dbFields["emptyF"] == None,
                    "Step%s >>> Wrong object[1].dbFields[emptyF] value" % str(step))


  def checkSQLCustom1(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SQL_CUSTOM_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dbi.EventObjects.CustomResponse,
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.errString == "Error: wrong SQL request or DBName")
    self.assertTrue(type(obj.eventObject.result) == tuple)
    self.assertTrue(len(obj.eventObject.result) == 0)


  def checkSQLCustom2(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SQL_CUSTOM_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dbi.EventObjects.CustomResponse,
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.errString == "Error: wrong SQL request or DBName")
    self.assertTrue(type(obj.eventObject.result) == tuple)
    self.assertTrue(len(obj.eventObject.result) == 0)


  def checkSQLCustom3(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SQL_CUSTOM_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == dbi.EventObjects.CustomResponse,
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(obj.eventObject.errString is None)
    self.assertTrue(type(obj.eventObject.result) == tuple)
    self.assertTrue(len(obj.eventObject.result) > 0)


  def checkSStatusUrls(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_STATUS_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    print obj.eventObject.id
    print obj.eventObject.contents
    print obj.eventObject.urls
    print obj.eventObject.urls[0].__dict__


  def checkSiteFind(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.SITE_FIND_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 1, "Step%s >>> Bad return object len" % str(step))
    self.assertTrue(type(obj.eventObject[0].properties) == type([]),
                    "Step%s >>> Bad return object.properties type" % str(step))
    self.assertTrue(len(obj.eventObject[0].properties) == 2,
                    "Step%s >>> Bad return object.properties len" % str(step))
    self.assertTrue(type(obj.eventObject[0].filters) == type([]),
                    "Step%s >>> Bad return object.filters type" % str(step))
    self.assertTrue(len(obj.eventObject[0].filters) == 1, "Step%s >>> Bad return object.filters len" % str(step))


  def checkFieldRecalculator(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.FIELD_RECALCULATE_RESPONSE, 
                    "Step%s >>> Bad return Event type"  % str(step))
    self.assertTrue(type(obj.eventObject) == dtm.EventObjects.GeneralResponse,
                    "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject.statuses) == 12, "Step%s >>> Bad return object len" % str(step))


  def checkVerify(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_VERIFY_RESPONSE, "Step%s >>> Bad return Event type"  % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 7, "Step%s >>> Bad return object len" % str(step))
    self.assertTrue(obj.eventObject[0] is not None, "Step%s >>> Bad return object eventObject[0]" % str(step))
    self.assertTrue(obj.eventObject[1] is not None, "Step%s >>> Bad return object eventObject[1]" % str(step))
    self.assertTrue(obj.eventObject[2] is None, "Step%s >>> Bad return object eventObject[2]" % str(step))
    self.assertTrue(obj.eventObject[3] is None, "Step%s >>> Bad return object eventObject[3]" % str(step))
    self.assertTrue(obj.eventObject[4] is not None, "Step%s >>> Bad return object eventObject[4]" % str(step))
    self.assertTrue(obj.eventObject[5] is not None, "Step%s >>> Bad return object eventObject[5]" % str(step))
    self.assertTrue(obj.eventObject[6] is None, "Step%s >>> Bad return object eventObject[6]" % str(step))


  def checkMySQLContent(self, obj, step):
    self.assertTrue(type(obj) == dc.Constants.DRCESyncTasksCover, "Step%s >>> Bad return type" % str(step))
    self.assertTrue(obj.eventType == EVENT_TYPES.URL_CONTENT_RESPONSE, "Step%s >>> Bad return Event type" % str(step))
    self.assertTrue(type(obj.eventObject) == type([]), "Step%s >>> Bad return object type" % str(step))
    self.assertTrue(len(obj.eventObject) == 1, "Step%s >>> Bad return object len" % str(step))
    self.assertTrue(type(obj.eventObject[0].processedContents) == type([]),
                    "Step%s >>> Bad return object[0].processedContents type" % str(step))
    self.assertTrue(len(obj.eventObject[0].processedContents) == 1,
                    "Step%s >>> Bad return object[0].processedContents len" % str(step))
    self.assertTrue(len(obj.eventObject[0].processedContents) == 1,
                    "Step%s >>> Bad return object[0].processedContents len" % str(step))
    self.assertTrue(obj.eventObject[0].processedContents[0].buffer == "blob data",
                    "Step%s >>> Bad return object[0].processedContents.buffer value" % str(step))
    self.assertTrue(obj.eventObject[0].processedContents[0].cDate == "2010-10-10 10:10:10",
                    "Step%s >>> Bad return object[0].processedContents.cDate value" % str(step))


  def fileCreate(self, directory, fName, data):
    time.sleep(0.3)
    fd = open(directory + "/" + fName, "w")
    fd.write(data)
    fd.close()


  def makeContent(self):
    savePath = os.getcwd()
    os.chdir(self.CD_PATH)        
    configParser = ConfigParser.ConfigParser()
    configParser.read("../ini/db-task.ini")
    keyValueStorageDir = configParser.get(self.CLASS_NAME, self.KEY_VALUE_STORAGE_DIR)
    rawDataDir = configParser.get(self.CLASS_NAME, self.RAW_DATA_DIR)
    print(keyValueStorageDir + "\n" + rawDataDir)
# Files creating
    dataDir = rawDataDir + "/" + self.siteId +"/"+ PathMaker(self.urlMd5).getDir()
    try:
      os.makedirs(dataDir)
    except Exception:
      print ">>>----  "+ str(dataDir) + " path already exist !!!"
    self.fileCreate(dataDir, "A1.bin", "AAAAA")
    self.fileCreate(dataDir, "A1.headers.txt", "AAAAAheaders")
    self.fileCreate(dataDir, "A1.requests.txt", "AAAAArequests")
    self.fileCreate(dataDir, "A1.meta.txt", "AAAAAmeta")
    self.fileCreate(dataDir, "A1.cookies.txt", "AAAAAcookies")
    self.fileCreate(dataDir, "A1.tidy", "AAATIDY")
    self.fileCreate(dataDir, "B1.bin", "BBBBB")
    self.fileCreate(dataDir, "B1.headers.txt", "BBBBBheaders")
    self.fileCreate(dataDir, "B1.cookies.txt", "BBBBBcookies")
    self.fileCreate(dataDir, "C1.bin", "CCCCC")
    self.fileCreate(dataDir, "C1.headers.txt", "CCCCCheaders")
    self.fileCreate(dataDir, "C1.requests.txt", "CCCCCrequests")
    self.fileCreate(dataDir, "C1.meta.txt", "CCCCCmeta")
    self.fileCreate(dataDir, "C1.cookies.txt", "CCCCCcookies")
    self.fileCreate(dataDir, "D1.meta.txt", "DDDDDmeta")
    self.fileCreate(dataDir, "E1.bin", "EEEEE")
    self.fileCreate(dataDir, "arash.tidy", "ArashTIDY")
    self.fileCreate(dataDir, "arash.dyn", "AAADYN")
# KV_DB creating
    localUrlContent = dc.EventObjects.URLContentRequest(0, "http")
    localUrlMD5 = localUrlContent.fillMD5(self.url)
    if self.contentType == dc_db.Constants.DB_DATA_KVDB:
      dbName = dc_db.Constants.KEY_VALUE_FILE_NAME_TEMPLATE % self.siteId
      dbFileName = keyValueStorageDir + "/" + dbName
      INSERT_SQL = "INSERT INTO `articles` (Id, Data, CDate) VALUES('%s', '%s', %s)"
      query = INSERT_SQL % (localUrlMD5, "EEEEE", str(int(time.time())))
      if os.path.exists(dbFileName):
        dbConnect = sqlite3.connect(dbFileName)
        dbConnect.text_factory = str
        cursor = dbConnect.cursor()
        cursor.execute(query)
        dbConnect.commit()
    elif self.contentType == dc_db.Constants.DB_DATA_MYSQL:
      print ">>>> CREATE MYSQL !!!"
      mysqlConnUrl = mdb.connect("192.168.253.113", "hce", "hce12345", "dc_contents", 3306)
      bdName = "contents_%s" % self.siteId
      CREATE_SQL = "CREATE TABLE IF NOT EXISTS `%s` (`id` varchar(32) NOT NULL DEFAULT '\"\"', \
              `data` BLOB NOT NULL, `CDate` datetime DEFAULT NULL, KEY `id` (`id`), KEY `CDate` (`CDate`)) \
              ENGINE=MyISAM DEFAULT CHARSET=utf8"
      query = CREATE_SQL % bdName
      INSERT_SQL = "INSERT INTO `%s` (Id, Data, CDate) VALUES('%s', '%s', %s)"
      query1 = INSERT_SQL % (bdName, localUrlMD5, "EEEEE", "NOW()")
      if mysqlConnUrl is not None:
        with closing(mysqlConnUrl.cursor()) as cursor:
          cursor.execute(query)
          mysqlConnUrl.commit()
          cursor.execute(query1)
          mysqlConnUrl.commit()
      else:
        print ">>>> WRONG DB_CONTENT CONNECTION !!!"
    os.chdir(savePath)

  '''
  def test_01_CommonSiteSuite(self):
    self.mutex.acquire()
    print "test_01_CommonSiteSuite"
    obj = self.execCommand(CMD_SNEW1, 1)
    if obj != None:
      self.checkSStep1(obj, 1)
    obj = self.execCommand(CMD_SSTATUS2, 2)
    if obj != None:
      self.checkSStep2(obj, 2)
    obj = self.execCommand(CMD_SNEW2, 3)
    if obj != None:
      self.checkSStep3(obj, 3)
    obj = self.execCommand(CMD_SSTATUS2, 4)
    if obj != None:
      self.checkSStep4(obj, 4)
    obj = self.execCommand(CMD_SUPDATE2, 5)
    if obj != None:
      self.checkSStep5(obj, 5)
    obj = self.execCommand(CMD_SDELETE1, 6)
    if obj != None:
      self.checkSStep6(obj, 6)
    obj = self.execCommand(CMD_SSTATUS1, 7)
    if obj != None:
      self.checkSStep7(obj, 7)
    obj = self.execCommand(CMD_SSTATUS2, 8)
    if obj != None:
      self.checkSStep8(obj, 8)
    obj = self.execCommand(CMD_SCLEANUP2, 9)
    if obj != None:
      self.checkSStep9(obj, 9)
    obj = self.execCommand(CMD_SSTATUS2, 10)
    if obj != None:
      self.checkSStep10(obj, 10)
    print "test_01_CommonSiteSuite FN"
    self.mutex.release()


  def test_02_CommonURLSuite(self):
    self.mutex.acquire()
    print "test_02_CommonURLSuite"
    self.execCommand(CMD_USITE_NEW1, 0)
    self.execCommand(CMD_USITE_NEW2, 0)
    obj = self.execCommand(CMD_UNEW1, 1)
    if obj != None:
      self.checkUStep1(obj, 1)
    obj = self.execCommand(CMD_USTATUS1, 2)
    if obj != None:
      self.checkUStep2(obj, 2)
    obj = self.execCommand(CMD_USTATUS2, 3)
    if obj != None:
      self.checkUStep3(obj, 3)
    obj = self.execCommand(CMD_UFETCH1, 4)
    if obj != None:
      self.checkUStep4(obj, 4)
    obj = self.execCommand(CMD_UFETCH2, 5)
    if obj != None:
      self.checkUStep5(obj, 5)
    obj = self.execCommand(CMD_UNEW2, 6)
    if obj != None:
      self.checkUStep6(obj, 6)
    obj = self.execCommand(CMD_UNEW3, 7)
    if obj != None:
      self.checkUStep7(obj, 7)
    obj = self.execCommand(CMD_USTATUS2_3, 8)
    if obj != None:
      self.checkUStep8(obj, 8)
    obj = self.execCommand(CMD_UFETCH1_2_3, 9)
    if obj != None:
      self.checkUStep9(obj, 9)
    obj = self.execCommand(CMD_UUPDATE2_3_4, 10)
    if obj != None:
      self.checkUStep10(obj, 10)
    obj = self.execCommand(CMD_UCONTENT1_4, 11)
    if obj != None:
      self.checkUStep11(obj, 11)
    obj = self.execCommand(CMD_UDELETE1, 12)
    if obj != None:
      self.checkUStep12(obj, 12)
    obj = self.execCommand(CMD_UDELETE4, 13)
    if obj != None:
      self.checkUStep13(obj, 13)
    obj = self.execCommand(CMD_UCLEANUP1, 14)
    if obj != None:
      self.checkUStep14(obj, 14)
    obj = self.execCommand(CMD_UCLEANUP2, 15)
    if obj != None:
      self.checkUStep15(obj, 15)
    obj = self.execCommand(CMD_UFETCH2_3_4, 16)
    if obj != None:
      self.checkUStep16(obj, 16)
    obj = self.execCommand(CMD_USTATUS2_3_4, 17)
    if obj != None:
      self.checkUStep17(obj, 17)
    print "test_02_CommonURLSuite FN"
    self.mutex.release()


  def test_03_URLContent(self):
    self.mutex.acquire()
    print "test_03_URLContent"
    self.url = "http://url5.com/"
    self.siteId = "z5"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.execCommand(CMD_USITE_NEW5, 0)
    self.execCommand(CMD_UNEW5, 0)
    self.makeContent()
    obj = self.execCommand(CMD_UCONTENT5, 1)
    if obj != None:
      self.checkCStep1(obj, 1)
    obj = self.execCommand(CMD_UCONTENT5_EXT, 2)
    if obj != None:
      self.checkCStep2(obj, 2)
    obj = self.execCommand(CMD_UCONTENT5_DYN, 3)
    if obj != None:
      self.checkCStep3(obj, 3)
    print "test_03_URLContent FN"
    self.mutex.release()


  def test_04_UrlNewSiteExtractor(self):
    self.mutex.acquire()
    print "test_04_UrlNewSiteExtractor"
    obj = self.execCommand(CMD_SNEW_INTEL, 0)
    if obj != None:
      self.checkIntelStep0(obj, 0)
    self.execCommand(CMD_UNEW_INTEL, 1)
    obj = self.execCommand(CMD_UNEW_INTEL1, 2)
    obj = self.execCommand(CMD_SNEW_INTEL, 3)
    if obj != None:
      self.checkIntelStep3(obj, 3)
    print "test_04_UrlNewSiteExtractor FN"
    self.mutex.release()


  def test_05_AdditionCriterions(self):
    self.mutex.acquire()
    print "test_05_AdditionCriterions"
    self.execCommand(CMD_UDEL_CRITERIONS_DEL, 0)
    self.execCommand(CMD_UCLEANUP_CRITERIONS, 1)
    obj = self.execCommand(CMD_UDEL_CRITERIONS_FETCH, 2)
    if obj != None:
      self.checkCriterions2(obj, 2)
    print "test_05_AdditionCriterions FN"
    self.mutex.release()


  def test_07_DeleteAbsentSite(self):
    self.mutex.acquire()
    print "test_07_DeleteAbsentSite"
    obj = self.execCommand(CMD_SDELETE_BAD, 0)
    if obj != None:
      self.checkDeleteBad(obj, 0)
    print "test_07_DeleteAbsentSite FN"
    self.mutex.release()


  def test_10_SiteNewCriterions(self):
    self.mutex.acquire()
    print "test_10_SiteNewCriterions"
    obj = self.execCommand(CMD_SUPDATE_CRITERIONS, 0)
    if obj != None:
      self.checkSiteCriterions1(obj, 0)
    obj = self.execCommand(CMD_SSTATUS_CRITERIONS, 1)
    if obj != None:
      self.checkSiteCriterions2(obj, 1)
    print "test_10_SiteNewCriterions FN"
    self.mutex.release()


  def test_11_SiteNewProp(self):
    self.mutex.acquire()
    print "test_11_SiteNewProp"
    self.execCommand(CMD_SNEW_44, 0)
    self.execCommand(CMD_SNEW_55, 0)
    self.execCommand(CMD_SUPDATE_5, 0)
    print "test_11_SiteNewProp FN"
    self.mutex.release()


  def test_12_URLContentDBFields(self):
    self.mutex.acquire()
    print "test_12_URLContentDBFields"
    obj = self.execCommand(CMD_UCONTENT_DBFIELDS, 0)
    if obj != None:
      self.checkURLContentBDFields(obj, 0)
    print "test_12_URLContentDBFields FN"
    self.mutex.release()


  def test_08_SQLCommon(self):
    self.mutex.acquire()
    print "test_08_SQLCommon"
    obj = self.execCommand(CMD_SQLCUSTOM_BAD1, 0)
    if obj != None:
      self.checkSQLCustom1(obj, 0)
    obj = self.execCommand(CMD_SQLCUSTOM_BAD1, 1)
    if obj != None:
      self.checkSQLCustom2(obj, 1)
    obj = self.execCommand(CMD_SQLCUSTOM_OK, 2)
    if obj != None:
      self.checkSQLCustom3(obj, 2)
    print "test_08_SQLCommon FN"
    self.mutex.release()


  def test_06_Common1(self):
    self.mutex.acquire()
    print "test_06_Common1"
    self.execCommand(CMD_SNEW_INTEL, 0)
    self.execCommand(CMD_SINTEL_UPDATE_OK, 1)
    print "test_06_Common1 FN"
    self.mutex.release()


  def test_09_SiteFind(self):
    self.mutex.acquire()
    print "test_09_SiteFind"
    obj = self.execCommand(CMD_SITE_FIND_OK, 0)
    if obj != None:
      self.checkSiteFind(obj, 0)
    print "test_09_SiteFind FN"
    self.mutex.release()


  def test_13_Delay(self):
    self.mutex.acquire()
    print "test_13_Delay"
    self.url = "http://url1.com/"
    self.siteId = "z5"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://intel.com/path1/"
    self.siteId = "intel1"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://intel.com/path1/path2"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://url10.com/"
    self.siteId = "z1"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://url_a1.com/"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://url_a2.com/"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://url44.com/"
    self.siteId = "z44"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://url40.com/"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://url41.com/"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.execCommand(CMD_UNEW_DELAY10, 0)
    self.execCommand(CMD_UNEW_DELAY11, 0)
    self.execCommand(CMD_UNEW_DELAY40, 0)
    self.execCommand(CMD_UNEW_DELAY41, 0)
    self.execCommand(CMD_UNEW_DELAY_A1, 0)
    self.execCommand(CMD_UNEW_DELAY_A2, 0)
    self.execCommand(CMD_SCLEANUP_DELAY_INTEL1, 1)
    self.execCommand(CMD_UDELETE_DELAY1, 2)
    self.execCommand(CMD_UCLEANUP_DELAY44, 3)
    self.execCommand(CMD_UPURGE_GROUP, 4)
    self.execCommand(CMD_UPURGE_SELECT_SITE, 5)
    print "test_13_Delay FN"
    self.mutex.release()


  def test_14_Delay(self):
    self.mutex.acquire()
    print "test_14_Delay"
    self.url = "http://dtest1.com/page1.html"
    self.siteId = "e543803a822340b0706477699ef78709"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://dtest1.com/page2.html"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://dtest1.com/page3.html"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://dtest2.com/page1.html"
    self.siteId = "50f5c4c74336ccda936bb807c93b73b7"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://dtest2.com/page2.html"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://dtest3.com/page1.html"
    self.siteId = "9a6f413ba2fc3b04825f9f6b294ad2ea"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://dtest3.com/page.html"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://dtest4.com/page1.html"
    self.siteId = "844fb110d58d096a4a441091e2cf375f"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.execCommand(CMD_UNEW_DELAY_TEST1, 0)
    self.execCommand(CMD_UNEW_DELAY_TEST2, 0)
    self.execCommand(CMD_UNEW_DELAY_TEST3, 0)
    self.execCommand(CMD_UNEW_DELAY_TEST4, 0)

    self.execCommand(CMD_SCLEANUP_DTEST1, 1)
    self.execCommand(CMD_SCLEANUP_DTEST2, 2)
    self.execCommand(CMD_SCLEANUP_DTEST3, 3)
    self.execCommand(CMD_SCLEANUP_DTEST4, 4)

    for i in xrange(5, 12):
      self.execCommand(CMD_UPURGE3, i)

    self.execCommand(CMD_UNEW_DELAY_TEST5, 13)
    self.execCommand(CMD_UNEW_DELAY_TEST6, 13)
    self.execCommand(CMD_UNEW_DELAY_TEST7, 13)
    self.execCommand(CMD_UNEW_DELAY_TEST8, 13)

    self.execCommand(CMD_SCLEANUP_DTEST5, 14)
    self.execCommand(CMD_SCLEANUP_DTEST6, 15)
    self.execCommand(CMD_SCLEANUP_DTEST7, 16)
    self.execCommand(CMD_SCLEANUP_DTEST8, 17)
    
    self.execCommand(CMD_UPURGE4, 18)
    
    self.execCommand(CMD_SDELETE_DTEST1, 19)
    self.execCommand(CMD_SDELETE_DTEST2, 20)

    self.url = "http://dtest1.com/page1.html"
    self.siteId = "e543803a822340b0706477699ef78709"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://dtest1.com/page2.html"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://dtest1.com/page3.html"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://dtest2.com/page1.html"
    self.siteId = "50f5c4c74336ccda936bb807c93b73b7"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.url = "http://dtest2.com/page2.html"
    self.urlMd5 = hashlib.md5(self.url).hexdigest()
    self.makeContent()
    self.execCommand(CMD_UNEW_DELAY_TEST1A, 21)
    self.execCommand(CMD_UNEW_DELAY_TEST2A, 21)

    self.execCommand(CMD_SCLEANUP_DTEST1, 22)
    self.execCommand(CMD_SCLEANUP_DTEST2, 23)

    for i in xrange(24, 30):
      self.execCommand(CMD_UPURGE3, i)

    print "test_14_Delay FN"
    self.mutex.release()


  def test_15_FieldRecalculator(self):
    self.mutex.acquire()
    print "test_15_FieldRecalculator"
    obj = self.execCommand(CMD_SRECALCULATE, 0)
    if obj != None:
      self.checkFieldRecalculator(obj, 0)
    print "test_15_FieldRecalculator FN"
    self.mutex.release()


  def test_16_UrlVerify(self):
    self.mutex.acquire()
    print "test_16_UrlVerify"
    self.execCommand(CMD_UNEW_VERIFY, 0)
    self.execCommand(CMD_UNEW_VERIFY2, 0)
    obj = self.execCommand(CMD_UVERIFY, 1)
    if obj != None:
      self.checkVerify(obj, 1)
    print "test_16_UrlVerify FN"
    self.mutex.release()


  def test_17_UrlNewUpdate(self):
    self.mutex.acquire()
    print "test_17_UrlNewUpdate"
    self.execCommand(CMD_UNEW_UPDATE5, 0)
    print "test_17_UrlNewUpdate FN"
    self.mutex.release()


  def test_18_AdditionFieldRecalculator(self):
    self.mutex.acquire()
    print "test_18_AdditionFieldRecalculator"
    self.execCommand(CMD_SRECALCULATE_ADD, 0)
    self.execCommand(CMD_SRECALCULATE_ADD1, 0)
    print "test_18_AdditionFieldRecalculator FN"
    self.mutex.release()


  def test_19_UrlAging(self):
    self.mutex.acquire()
    print "test_19_UrlAging"
    self.execCommand(CMD_UNEW_AGE, 0)
    self.execCommand(CMD_UNEW_AGE1, 0)
    self.execCommand(CMD_UNEW_AGE2, 0)
    self.execCommand(CMD_UAGE, 1)
    print "test_19_UrlAging FN"
    self.mutex.release()
  '''

  '''
  def test_20_MySQLContent(self):
    self.mutex.acquire()
    print "test_20_MySQLContent"
    self.execCommand(CMD_SNEW_CONTENT, 0)
    self.execCommand(CMD_CUSTOM_CONTENT, 1)
    self.execCommand(CMD_CUSTOM_CONTENT_INSERT, 2)
    obj = self.execCommand(CMD_UCONTENT_MYSQL, 3)
    if obj != None:
      self.checkMySQLContent(obj, 4)
    print "test_20_MySQLContent FN"
    self.mutex.release()


  CMD_SNEW_TEST = ("cd ../../bin && /usr/bin/python ./db-task.py --cfg=../ini/db-task.ini " +
        "<../hce/ftests/db-task-data/site_new_test.dat")

  def test_21_MySQLContent(self):
    self.execCommand(self.CMD_SNEW_TEST, 0)
  '''


  def test_22_UrlPutTest(self):
    self.mutex.acquire()
    print "test_22_UrlPutTest"
    self.execCommand(CMD_UNEW_PUT, 0)
    self.execCommand(CMD_UPUT, 1)
    self.execCommand(CMD_UPUT1, 2)
    print "test_22_UrlPutTest FN"
    self.mutex.release()


if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.TestLoader.sortTestMethodsUsing = None
  unittest.main()
