'''
HCE project, Python bindings, Distributed Crawler application.
BatchTasksManager object functional tests.

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
import dc.BatchTasksManager
import dc.EventObjects
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
  TTL = 60 * 60

  #Test SitesManager instantiation
  CONFIG_SECTION = "BatchTasksManager"
  config = ConfigParser.RawConfigParser()
  config.add_section(CONFIG_SECTION)
  config.set(CONFIG_SECTION, "server", CONFIG_SECTION)
  config.set(CONFIG_SECTION, "DTMDHost", "localhost")
  config.set(CONFIG_SECTION, "DTMDPort", "5501")
  config.set(CONFIG_SECTION, "DTMDTimeout", "2000")
  config.set(CONFIG_SECTION, "clientSitesManager", "SitesManager")
  config.set(CONFIG_SECTION, "PollingTimeout", "30000")
  config.set(CONFIG_SECTION, "DRCECrawlerAppName", "cd api/python/bin && ./crawler-task.py -c=../ini/crawler-task.ini")
  config.set(CONFIG_SECTION, "BatchDefaultMaxURLs", "5")
  config.set(CONFIG_SECTION, "BatchMaxExecutionTime", "100")
  config.set(CONFIG_SECTION, "RemoveUnprocessedBatchItems", "1")
  config.set(CONFIG_SECTION, "IncrMinFreq", "100")
  config.set(CONFIG_SECTION, "IncrMaxDepth", "100")
  config.set(CONFIG_SECTION, "IncrMaxURLs", "100")
  config.set(CONFIG_SECTION, "IncrMode", "5")
  config.set(CONFIG_SECTION, "IncrPeriod", "1")
  config.set(CONFIG_SECTION, "BatchDefaultMaxExecutionTime", "360")
  config.set(CONFIG_SECTION, "ReturnURLsMaxNumber", "300")
  config.set(CONFIG_SECTION, "ReturnURLsPeriod", "500")
  config.set(CONFIG_SECTION, "ReturnURLsTTL", "600")
  config.set(CONFIG_SECTION, "ReturnURLsMode", "60")
  config.set(CONFIG_SECTION, "CrawledURLStrategy", "0")
  config.set(CONFIG_SECTION, "BatchDefaultOrderByURLs", "LENGTH(`ParentMd5`) ASC, Priority DESC, Depth ASC, `UDate` DESC")
  config.set(CONFIG_SECTION, "BatchDefaultMaxTasks", "2")
  config.set(CONFIG_SECTION, "RegularCrawlingPeriod", "20")
  config.set(CONFIG_SECTION, "RegularCrawlingMode", "1")
  config.set(CONFIG_SECTION, "RegularCrawlingPropagateURLs", "1")
  config.set(CONFIG_SECTION, "BatchQueueProcessingPeriod", "5")
  config.set(CONFIG_SECTION, "BatchDefaultFetchTypeOptions", "{\"splitter\":1.75,\"dfetcher_BatchMaxExecutionTime\":2400,\"dfetcher_BatchQueueTaskTTL\":2500,\"dfetcher_BatchDefaultMaxURLs\":4}")
  config.set(CONFIG_SECTION, "BatchQueueTaskTTL", "900")
  config.set(CONFIG_SECTION, "BatchQueueTaskCheckStateMethod", "1")
  config.set(CONFIG_SECTION, "BatchTask_IO_WAIT_MAX", "30")
  config.set(CONFIG_SECTION, "BatchTask_CPU_LOAD_MAX", "60")
  config.set(CONFIG_SECTION, "BatchTask_RAM_FREE_MIN", "512000000")
  config.set(CONFIG_SECTION, "BatchTask_RDELAY", "30000")
  config.set(CONFIG_SECTION, "BatchTask_RETRY", "20")
  config.set(CONFIG_SECTION, "BatchTask_STARTER", "hce-starter-dc-crawl.sh")
  config.set(CONFIG_SECTION, "BatchTask_autocleanup_TTL", "1000")
  config.set(CONFIG_SECTION, "BatchTask_autocleanup_DeleteType", "1")
  config.set(CONFIG_SECTION, "BatchTask_autocleanup_DeleteRetries", "8")
  config.set(CONFIG_SECTION, "BatchTask_autocleanup_State", "1")
  config.set(CONFIG_SECTION, "BatchDefaultCheckURLsInActiveBatches", "1")
  config.set(CONFIG_SECTION, "PurgeMode", "1")
  config.set(CONFIG_SECTION, "PurgeBatchDefaultMaxTasks", "2")
  config.set(CONFIG_SECTION, "PurgePeriod", "2")
  config.set(CONFIG_SECTION, "PurgeBatchDefaultMaxExecutionTime", "3600")
  config.set(CONFIG_SECTION, "PurgeBatchDefaultMaxURLs", "100")
  config.set(CONFIG_SECTION, "PurgeBatchQueueTaskTTL", "4000")
  config.set(CONFIG_SECTION, "PurgeBatchTask_STARTER", "hce-starter-bash.sh")
  config.set(CONFIG_SECTION, "DRCEDBAppName", "cd api/python/bin && ./db-task.py --c=../ini/db-task.ini")
  config.set(CONFIG_SECTION, "BatchTaskDTMNameCrawl", "crawl")
  config.set(CONFIG_SECTION, "BatchTaskDTMNamePurge", "purge")
  config.set(CONFIG_SECTION, "BatchTaskDTMNameAging", "aging")
  config.set(CONFIG_SECTION, "BatchTaskDTMTypeCrawl", "1")
  config.set(CONFIG_SECTION, "BatchTaskDTMTypePurge", "2")
  config.set(CONFIG_SECTION, "BatchTaskDTMTypeAging", "3")
  config.set(CONFIG_SECTION, "AgingMode", "1")
  config.set(CONFIG_SECTION, "AgingPeriod", "2")
  config.set(CONFIG_SECTION, "AgingBatchDefaultMaxExecutionTime", "3600")
  config.set(CONFIG_SECTION, "AgingBatchDefaultMaxURLsTotal", "10000")
  config.set(CONFIG_SECTION, "AgingBatchDefaultMaxURLsSite", "100")
  config.set(CONFIG_SECTION, "AgingBatchDefaultMaxSites", "0")
  config.set(CONFIG_SECTION, "AgingBatchQueueTaskTTL", "4000")
  config.set(CONFIG_SECTION, "AgingBatchTask_STARTER", "hce-starter-bash.sh")
  config.set(CONFIG_SECTION, "AgingBatchDefaultMaxTasks", "2")
  config.set(CONFIG_SECTION, "AgingBatchURLsCriterion", "(NOW() > DATE_ADD(UDate, INTERVAL ((SELECT `RecrawlPeriod` FROM `dc_sites`.`sites` WHERE `Id`='%SITE_ID%')*2) MINUTE) OR ( NOW() > DATE_ADD(CDate, INTERVAL ((SELECT `RecrawlPeriod` FROM `dc_sites`.`sites` WHERE `Id`='%SITE_ID%')*2) MINUTE) AND UDate IS NULL) ) AND ParentMd5<>''")
  config.set(CONFIG_SECTION, "AgingBatchSitesCriterion", "`sites`.`Id`<>'0' AND `sites`.`State` IN (1,3) AND IFNULL((SELECT `Value` FROM `sites_properties` WHERE `Name`='MODES_FLAG') & 16, 1)<>0")
  config.set(CONFIG_SECTION, "BatchMaxIterations", "1")
  config.set(CONFIG_SECTION, "BatchMaxExecutionTime", "360")
  config.set(CONFIG_SECTION, "RemoveUnprocessedBatchItems", "0")

  connectionBuilderLight = ConnectionBuilderLight()

  #Admin server connection sumulator
  adminServerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.SERVER_CONNECT,
                                                       BaseServerManager.ADMIN_CONNECT_ENDPOINT)

  time.sleep(1)

  #Create instance
  btm = dc.BatchTasksManager.BatchTasksManager(config)
  print TEST_TITLE + btm.__class__.__name__ + TEST_TITLE_OBJECT, vars(btm)
  btm.setName(btm.__class__.__name__)
  btm.start()

  #Simulate ExecuteTask request
  eventBuilder = EventBuilder()
  urlObj = dc.EventObjects.URL("0", "http://127.0.0.1/")
  clientResponseItem = dc.EventObjects.ClientResponseItem([urlObj])
  clientResponse = dc.EventObjects.ClientResponse([clientResponseItem])
  event = eventBuilder.build(DC_CONSTS.EVENT_TYPES.URL_FETCH, clientResponse)
  btm.onURLFetchResponse(event)
  print "ExecuteTask event sent"

  time.sleep(TTL)
  btm.exit_flag = True

  print "Stopped after " + str(TTL) + " sec!"

