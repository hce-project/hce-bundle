'''
HCE project, Python bindings, Distributed Crawler application.
SitesManager object functional tests.

@package: dc
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import ConfigParser
import logging
import sys
import time

from app.BaseServerManager import BaseServerManager
import dc.EventObjects
import dc.SitesManager
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.Event import EventBuilder
import dc.Constants as DC_CONSTS
import transport.Consts as TRANSPORT_CONSTS


if __name__ == "__main__":
  logger = logging.getLogger(DC_CONSTS.LOGGER_NAME)
  ch = logging.StreamHandler(sys.stdout)
  ch.setLevel(logging.DEBUG)
  logger.setLevel(logging.DEBUG)
  formatter = logging.Formatter('%(asctime)s - %(thread)ld - %(threadName)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s')
  ch.setFormatter(formatter)
  logger.addHandler(ch)

if __name__ == "__main__":
  TEST_TITLE = "Test "
  TEST_TITLE_OBJECT = " object:\n"
  TTL = 7

  #Test SitesManager instantiation
  CONFIG_SECTION = "SitesManager"
  config = ConfigParser.RawConfigParser()
  config.add_section(CONFIG_SECTION)
  config.set(CONFIG_SECTION, "server", CONFIG_SECTION)
  config.set(CONFIG_SECTION, "DRCEHost", "localhost")
  config.set(CONFIG_SECTION, "DRCEPort", "5656")
  config.set(CONFIG_SECTION, "DRCETimeout", "5000")
  config.set(CONFIG_SECTION, "DRCEDBAppName", "cd api/python/bin && ./db-task.py")
  config.set(CONFIG_SECTION, "DRCERoute", "")
  config.set(CONFIG_SECTION, "RecrawlSiteMode", "1")
  config.set(CONFIG_SECTION, "RecrawlSiteMax", "1")
  config.set(CONFIG_SECTION, "RecrawlSiteIterationPeriod", "60")
  config.set(CONFIG_SECTION, "RecrawlSiteRecrawlDateExpression", "DATE_ADD(DATE_FORMAT(NOW(),'%Y-%m-%d 00:00:00'), INTERVAL ( CEIL( ( ( HOUR(NOW())*60 + MINUTE(NOW()) + SECOND(NOW())/60) / `RecrawlPeriod` )*`RecrawlPeriod` ) + `RecrawlPeriod` ) MINUTE)")
  config.set(CONFIG_SECTION, "RecrawlSiteSelectCriterion", "`State`=1 AND `RecrawlDate` IS NOT NULL AND NOW()>`RecrawlDate` AND (Id IN (SELECT Site_Id AS Id FROM `sites_properties` WHERE `Name`='MODES_FLAG' AND (`Value` & 8)>0) OR Id IN (SELECT Site_Id AS Id FROM `sites_properties` WHERE `Name`<>'MODES_FLAG'))")
  config.set(CONFIG_SECTION, "RecrawlSiteSelectOrder", "`RecrawlDate` ASC")
  config.set(CONFIG_SECTION, "RecrawlSiteMaxThreads", "2")
  config.set(CONFIG_SECTION, "RecrawlSiteLockState", "4")
  config.set(CONFIG_SECTION, "RecrawlSiteOptimize", "1")
  config.set(CONFIG_SECTION, "RecrawlSiteDRCETimeout", "3600")
  config.set(CONFIG_SECTION, "RecrawlSitePeriodMode", "0")
  config.set(CONFIG_SECTION, "RecrawlSitePeriodMax", "1440")
  config.set(CONFIG_SECTION, "RecrawlSitePeriodMin", "15")
  config.set(CONFIG_SECTION, "RecrawlSitePeriodStep", "15")
  config.set(CONFIG_SECTION, "RecrawlDelayBefore", "60")
  config.set(CONFIG_SECTION, "RecrawlDelayAfter", "60")
  config.set(CONFIG_SECTION, "PollingTimeout", "10000")
  config.set(CONFIG_SECTION, "DefaultRecrawUpdatelCriterion", "ParentMd5=''")
  config.set(CONFIG_SECTION, "DefaultRecrawDeleteOld", "0")
  config.set(CONFIG_SECTION, "DefaultRecrawDeleteOldCriterion", "((`Status`=4 AND `Crawled`=0 AND `Processed`=0) OR (`Status`=4 AND `Crawled`>0 AND `Processed`=0 AND `ErrorMask`>0) OR (`Status`=7 AND `TagsCount`=0)) AND `ParentMd5`<>''")
  config.set(CONFIG_SECTION, "PurgeMethod", "0")
  config.set(CONFIG_SECTION, "DRCENodes", "1")

  config.add_section('Application')
  config.set('Application', "instantiateSequence", "SitesManager")

  print sys.version

  connectionBuilderLight = ConnectionBuilderLight()

  #Admin server connection sumulator
  adminServerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT,
                                                       BaseServerManager.ADMIN_CONNECT_ENDPOINT)

  time.sleep(1)

  #Create instance
  sm = dc.SitesManager.SitesManager(config)

  print TEST_TITLE + sm.__class__.__name__ + TEST_TITLE_OBJECT, vars(sm)

  sm.setName(sm.__class__.__name__)
  sm.start()

  #Simulate ExecuteTask request
  eventBuilder = EventBuilder()
  siteStatus = dc.EventObjects.SiteStatus("1235151254141")
  print "type(siteStatus)=" + str(type(siteStatus))
  event = eventBuilder.build(DC_CONSTS.EVENT_TYPES.SITE_STATUS, siteStatus)
  event.connect_name = sm.serverName

  sm.onEventsHandler(event)
  print "ExecuteTask event sent"

  sm.exit_flag = True

  print "Stopped after" + str(TTL) + " sec of run!"


