'''
Created on Apr 8, 2014

@package: dc
@author: scorp, bgv
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''

import time
import logging
import ConfigParser
from dateutil.parser import parse
from app.BaseServerManager import BaseServerManager
import app.Utils as Utils  # pylint: disable=F0401
import app.Consts as APP_CONSTS
from dc.Constants import EVENT_TYPES, LOGGER_NAME
from dc import EventObjects
import dc.Constants as DC_CONSTANTS
import transport.Consts as consts
import dtm.EventObjects


# Logger initialization
logger = Utils.MPLogger().getLogger()

class ClientInterfaceService(BaseServerManager):

  CONFIG_SECTION = "ClientInterfaceService"
  CONFIG_SERVER_HOST = "serverHost"
  CONFIG_SERVER_PORT = "serverPort"
  CONFIG_SITES_MANAGER = "clientSitesManager"
  SERVER_CONNECTION_NAME = "server"
  CONNECTION_PREFIX = "Connection"
  CONFIG_BATCH_TASKS_MANAGER_REALTIME = "clientBatchTasksManagerRealTime"
  CONFIG_DRCE_NODES = "DRCENodes"

  # #constructor
  # initialise all connections and event handlers
  # @param configParser config parser object
  # @param connectBuilderLight instance of ConnectBuilderLight object
  #
  def __init__(self, configParser, connectBuilderLight):
    '''
    Constructor
    '''
    BaseServerManager.__init__(self)

    serverHost = configParser.get(self.CONFIG_SECTION, self.CONFIG_SERVER_HOST)
    serverPort = configParser.get(self.CONFIG_SECTION, self.CONFIG_SERVER_PORT)
    server = serverHost + ":" + str(serverPort)
    self.sitesManager = configParser.get(self.CONFIG_SECTION, self.CONFIG_SITES_MANAGER)
    self.batchTasksManagerRealTime = configParser.get(self.CONFIG_SECTION, self.CONFIG_BATCH_TASKS_MANAGER_REALTIME)

    try:
      self.configVars[self.CONFIG_DRCE_NODES] = configParser.get(APP_CONSTS.CONFIG_APPLICATION_SECTION_NAME,
                                                                 self.CONFIG_DRCE_NODES)
    except ConfigParser.NoOptionError:
      self.configVars[self.CONFIG_DRCE_NODES] = 1

    serverConnection = connectBuilderLight.build(consts.SERVER_CONNECT, server, consts.TCP_TYPE)
    sitesManagerConnection = connectBuilderLight.build(consts.CLIENT_CONNECT, self.sitesManager)
    batchTasksManagerRealTimeConnection = connectBuilderLight.build(consts.CLIENT_CONNECT,
                                                                    self.batchTasksManagerRealTime)

    self.addConnection(self.SERVER_CONNECTION_NAME + self.CONNECTION_PREFIX, serverConnection)
    self.addConnection(str(self.sitesManager) + self.CONNECTION_PREFIX, sitesManagerConnection)
    self.addConnection(str(self.batchTasksManagerRealTime) + self.CONNECTION_PREFIX,
                       batchTasksManagerRealTimeConnection)

    self.setEventHandler(EVENT_TYPES.SITE_NEW, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.SITE_UPDATE, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.SITE_STATUS, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.SITE_DELETE, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.SITE_CLEANUP, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.SITE_FIND, self.onSitesManagerRoute)

    self.setEventHandler(EVENT_TYPES.URL_NEW, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.URL_STATUS, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.URL_UPDATE, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.URL_FETCH, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.URL_DELETE, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.URL_CLEANUP, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.URL_CONTENT, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.SQL_CUSTOM, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.URL_PUT, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.URL_HISTORY, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.URL_STATS, self.onSitesManagerRoute)

    self.setEventHandler(EVENT_TYPES.PROXY_NEW, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.PROXY_UPDATE, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.PROXY_DELETE, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.PROXY_STATUS, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.PROXY_FIND, self.onSitesManagerRoute)

    self.setEventHandler(EVENT_TYPES.ATTR_SET, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.ATTR_UPDATE, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.ATTR_DELETE, self.onSitesManagerRoute)
    self.setEventHandler(EVENT_TYPES.ATTR_FETCH, self.onSitesManagerRoute)

    self.setEventHandler(EVENT_TYPES.SITE_NEW_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.SITE_UPDATE_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.SITE_STATUS_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.SITE_DELETE_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.SITE_CLEANUP_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.SITE_FIND_RESPONSE, self.onDCClientRoute)

    self.setEventHandler(EVENT_TYPES.URL_NEW_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.URL_STATUS_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.URL_UPDATE_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.URL_FETCH_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.URL_DELETE_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.URL_CLEANUP_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.URL_CONTENT_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.SQL_CUSTOM_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.URL_PUT_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.URL_HISTORY_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.URL_STATS_RESPONSE, self.onDCClientRoute)

    self.setEventHandler(EVENT_TYPES.PROXY_NEW_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.PROXY_UPDATE_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.PROXY_DELETE_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.PROXY_STATUS_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.PROXY_FIND_RESPONSE, self.onDCClientRoute)

    self.setEventHandler(EVENT_TYPES.ATTR_SET_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.ATTR_UPDATE_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.ATTR_DELETE_RESPONSE, self.onDCClientRoute)
    self.setEventHandler(EVENT_TYPES.ATTR_FETCH_RESPONSE, self.onDCClientRoute)

    self.setEventHandler(EVENT_TYPES.BATCH, self.onBatchTasksManagerRealTimeRoute)
    self.setEventHandler(EVENT_TYPES.BATCH_RESPONSE, self.onDCClientRoute)

    # map of incoming event, which are in processing
    # event.uid => event without eventObj field
    self.processEvents = dict()



  # #handler to route all event to SitesManager
  #
  # @param even instance of Event object
  def onSitesManagerRoute(self, event):
    try:
      logger.debug("Received event: " + Utils.varDump(event))
      self.send(str(self.sitesManager) + self.CONNECTION_PREFIX, event)
      self.registerEvent(event)
    except KeyError as err:
      logger.error(err.message)
    except Exception, err:
      logger.error("Error `%s`", str(err))



  # #handler to route all event to BatchTasksManagerRealTime
  #
  # @param even instance of Event object
  def onBatchTasksManagerRealTimeRoute(self, event):
    try:
      logger.debug("Received event: " + Utils.varDump(event))
      self.send(str(self.batchTasksManagerRealTime) + self.CONNECTION_PREFIX, event)
      self.registerEvent(event)
    except KeyError as err:
      logger.error(err.message)
    except Exception, err:
      logger.error("Error `%s`", str(err))



  # #handler to route all response event to DCClient
  #
  # @param even instance of Event object
  def onDCClientRoute(self, event):
    try:
      request_event = self.getRequestEvent(event)
      if event.cookie is not None and isinstance(event.cookie, dict) and\
         DC_CONSTANTS.MERGE_PARAM_NAME in event.cookie and bool(event.cookie[DC_CONSTANTS.MERGE_PARAM_NAME]) is False:
        logger.debug("No merge results specified in Event.cookie!")
      else:
        logger.debug("Results merge try by default.")
        event.eventObj = self.mergeResultsData(event.eventType, event.eventObj, event.cookie)
      self.reply(request_event, event)
      logger.debug("Results sent to DCC.")
      self.unregisterEvent(request_event)
    except KeyError as err:
      logger.error(err.message)



  # #add event in map of processing events
  #
  # @param even instance of Event object
  def registerEvent(self, event):
    event.eventObj = None
    self.processEvents[event.uid] = event



  # #get request event from processEvents map
  # @param event instance of Event  object
  # @return event instance of Event object
  def getRequestEvent(self, event):
    return self.processEvents[event.uid]



  # #delete event in map of processing events
  #
  # @param even instance of Event object
  def unregisterEvent(self, event):
    del self.processEvents[event.uid]



  # #Merge results of operation request to represent results from several hosts as single merged data
  #
  # @param eventType type of event, see constants definition
  # @param eventObj response object for requested operation
  # @param eventCookie the event's cookie
  # @return eventObj object changed or not
  def mergeResultsData(self, eventType, eventObj, eventCookie):
    if isinstance(eventObj, EventObjects.ClientResponse):
      # If number of client response items grater than one perform the merging, else leave untouched
      if len(eventObj.itemsList) > 1:
        if isinstance(eventObj.itemsList[0], EventObjects.ClientResponseItem):
          # Create new list of ClientResponseItem items and fill it with first item from response
          newItemObject = None
          newHost = ""
          newPort = ""
          newNode = ""
          newTime = ""
          newErrorMessage = ""
          newErrorCode = ""
          logger.debug("Merging, response items: %s", str(len(eventObj.itemsList)))
          mergedCounter = 0
          # Cycle response items
          for clientResponseItem in eventObj.itemsList:
            # If response item exists
            if clientResponseItem.itemObject is not None:
              mergedCounter = mergedCounter + 1
              logger.debug("clientResponseItem:\n" + Utils.varDump(clientResponseItem))
              newHost += clientResponseItem.host + ";"
              newPort += str(clientResponseItem.port) + ";"
              newNode += clientResponseItem.node + ";"
              newTime += str(clientResponseItem.time) + ";"
              newErrorMessage += clientResponseItem.errorMessage
              newErrorCode += str(clientResponseItem.errorCode) + ";"
              if eventType == EVENT_TYPES.SITE_FIND_RESPONSE:
                # Merge SITE_FIND operation results response
                newItemObject = self.mergeResultsSiteFind(newItemObject, clientResponseItem)
              elif eventType == EVENT_TYPES.URL_FETCH_RESPONSE or eventType == EVENT_TYPES.URL_STATUS_RESPONSE:
                # Merge URL_FETCH operation results response
                newItemObject = self.mergeResultsURLFetch(newItemObject, clientResponseItem)
              elif eventType == EVENT_TYPES.URL_CONTENT_RESPONSE:
                # Merge URL_CONTENT operation results response
                newItemObject = self.mergeResultsURLContent(newItemObject, clientResponseItem)
              elif eventType == EVENT_TYPES.SITE_STATUS_RESPONSE:
                # Merge SITE_STATUS operation results response
                newItemObject = self.mergeResultsSiteStatus(newItemObject, clientResponseItem)
              # elif eventType == EVENT_TYPES.SITE_NEW_RESPONSE:
              #  #Merge SITE_NEW operation results response
              #  newItemObject = self.mergeResultsGeneralResponse(newItemObject, clientResponseItem.itemObject)
              #  #Merge BATCH_RESPONSE operation results response
              elif eventType == EVENT_TYPES.BATCH_RESPONSE:
                # Merge URL_CONTENT operation results response
                newItemObject = self.mergeResultsBatch(newItemObject, clientResponseItem)
              else:
                l = {EVENT_TYPES.SITE_NEW_RESPONSE, EVENT_TYPES.SITE_UPDATE_RESPONSE, EVENT_TYPES.SITE_DELETE_RESPONSE,
                     EVENT_TYPES.SITE_CLEANUP_RESPONSE, EVENT_TYPES.URL_NEW_RESPONSE, EVENT_TYPES.URL_UPDATE_RESPONSE,
                     EVENT_TYPES.URL_DELETE_RESPONSE, EVENT_TYPES.URL_CLEANUP_RESPONSE, EVENT_TYPES.URL_UPDATE_RESPONSE,
                     EVENT_TYPES.URL_DELETE_RESPONSE, EVENT_TYPES.URL_CLEANUP_RESPONSE}  # pylint: disable=unused-import
                if eventType in l:
                  # Merge another result types that no need special processing of fields but check and leave just one
                  newItemObject = self.mergeResultsGeneralResponse(newItemObject, clientResponseItem)
            else:
              # Object is null or wrong type
              logger.error("The clientResponseItem.itemObject is None!")
          # Replace items list with newly created and merged if itemObject is set
          if newItemObject is not None:
            eventObj.itemsList = [eventObj.itemsList[0]]
            eventObj.itemsList[0].errorCode = newErrorCode.rstrip(";")
            eventObj.itemsList[0].errorMessage = newErrorMessage.rstrip(";")
            eventObj.itemsList[0].itemObject = newItemObject
            eventObj.itemsList[0].host = newHost.rstrip(";")
            eventObj.itemsList[0].port = newPort.rstrip(";")
            eventObj.itemsList[0].node = newNode.rstrip(";")
            eventObj.itemsList[0].time = newTime.rstrip(";")
            if isinstance(newItemObject, list):
              itemsNumber = len(newItemObject)
            else:
              itemsNumber = 1
            logger.debug("Merged with " + str(mergedCounter) + " response objects, " + \
                         str(itemsNumber) + " merged items.")
            # Does event is URL_CONTENT_RESPONSE and sort criterion defined
            if eventType == EVENT_TYPES.URL_CONTENT_RESPONSE and eventCookie is not None\
              and isinstance(eventCookie, dict) and EventObjects.URLFetch.CRITERION_ORDER in eventCookie and\
              len(eventCookie[EventObjects.URLFetch.CRITERION_ORDER]) > 0 and\
              eventCookie[EventObjects.URLFetch.CRITERION_ORDER][0].strip() != '':
              # TODO: now use only criterion of the first item of request items list
              eventObj.itemsList[0].itemObject = self.sortURLContentResults(newItemObject,
                                                 eventCookie[EventObjects.URLFetch.CRITERION_ORDER][0])  #  pylint: disable=C0330
              logger.debug("URL_CONTENT results sorted by the: %s",
                           str(eventCookie[EventObjects.URLFetch.CRITERION_ORDER][0]))
            # Does event is URL_FETCH_RESPONSE and sort criterion defined
            elif eventType == EVENT_TYPES.URL_FETCH_RESPONSE and eventCookie is not None\
              and isinstance(eventCookie, dict) and EventObjects.URLFetch.CRITERION_ORDER in eventCookie and\
              len(eventCookie[EventObjects.URLFetch.CRITERION_ORDER]) > 0 and\
              eventCookie[EventObjects.URLFetch.CRITERION_ORDER][0].strip() != '':
              # TODO: now use only criterion of the first item of request items list
              eventObj.itemsList[0].itemObject = self.sortURLFetchResults(newItemObject,
                                                 eventCookie[EventObjects.URLFetch.CRITERION_ORDER][0])  #  pylint: disable=C0330
              logger.debug("URL_CONTENT results sorted by the: %s",
                           str(eventCookie[EventObjects.URLFetch.CRITERION_ORDER][0]))
            else:
              logger.debug("Sort conditions are not satisfied, results not sorted.")
          else:
            logger.debug("No items collected while merge procedure, merge skipped.")
        else:
          # Wrong type
          logger.error("Wrong eventObj.itemsList[0] type " + str(type(eventObj.itemsList[0])) + \
                         " expected EventObjects.ClientResponseItem\n" + Utils.varDump(eventObj.itemsList[0]))
    else:
      logger.error("Wrong eventObj type " + str(type(eventObj)) + " expected EventObjects.ClientResponse\n" + \
                   Utils.varDump(eventObj))

    return eventObj



  # #Sort results of operation URL_CONTENT
  #
  # @param itemObject items list to sort
  # @param itemsList current items list from current itemObject of node response results
  # @return sorted itemsList
  def sortURLContentResults(self, itemObject, criterion):
    ret = itemObject

    try:
      crits = criterion.split(',')
      crits = crits[0]
      crits = criterion.split(' ')
      if len(crits) == 0:
        crits = ('CDate', False)
      elif len(crits) == 1:
        crits = (crits[0], False)
      else:
        if crits[1] == 'ASC':
          crits[1] = False
        else:
          crits[1] = True

      if crits[0] == 'PDate':
        def orderKey(itemObject):
          if itemObject.dbFields['PDate'] is not None:
            return parse(itemObject.dbFields['PDate']).strftime('%s')
          else:
            return -1
      elif crits[0] == 'CDate':
        def orderKey(itemObject):
          return parse(itemObject.dbFields['CDate']).strftime('%s')
      elif crits[0] == 'UDate':
        def orderKey(itemObject):
          return parse(itemObject.dbFields['UDate']).strftime('%s')
      elif crits[0] == 'TcDate':
        def orderKey(itemObject):
          return parse(itemObject.dbFields['TcDate']).strftime('%s')
      elif crits[0] == 'Size':
        def orderKey(itemObject):
          return itemObject.dbFields['Size']
      elif crits[0] == 'Depth':
        def orderKey(itemObject):
          return itemObject.dbFields['Depth']
      elif crits[0] == 'TagsCount':
        def orderKey(itemObject):
          return itemObject.dbFields['TagsCount']
      elif crits[0] == 'ContentURLMd5':
        def orderKey(itemObject):
          return itemObject.dbFields['ContentURLMd5']
      else:
        def orderKey(itemObject):
          return itemObject.dbFields['CDate']

      ret = sorted(ret, key=orderKey, reverse=crits[1])

    except Exception, err:
      logger.error("Exception: '%s', criterion: '%s'", str(err), str(criterion))

    return ret


  # #Sort results of operation URL_FETCH
  #
  # @param itemObject items list to sort
  # @param itemsList current items list from current itemObject of node response results
  # @return sorted itemsList
  def sortURLFetchResults(self, itemObject, criterion):
    ret = itemObject

    try:
      crits = criterion.split(',')
      crits = crits[0]
      crits = criterion.split(' ')
      if len(crits) == 0:
        crits = ('CDate', False)
      elif len(crits) == 1:
        crits = (crits[0], False)
      else:
        if crits[1] == 'ASC':
          crits[1] = False
        else:
          crits[1] = True

      if crits[0] == 'PDate':
        def orderKey(itemObject):
          return parse(itemObject.pDate).strftime('%s')
      elif crits[0] == 'CDate':
        def orderKey(itemObject):
          return parse(itemObject.CDate).strftime('%s')
      elif crits[0] == 'UDate':
        def orderKey(itemObject):
          return parse(itemObject.UDate).strftime('%s')
      elif crits[0] == 'TcDate':
        def orderKey(itemObject):
          return parse(itemObject.tcDate).strftime('%s')
      elif crits[0] == 'Size':
        def orderKey(itemObject):
          return itemObject.size
      elif crits[0] == 'Depth':
        def orderKey(itemObject):
          return itemObject.depth
      elif crits[0] == 'TagsCount':
        def orderKey(itemObject):
          return itemObject.tagsCount
      elif crits[0] == 'ContentURLMd5':
        def orderKey(itemObject):
          return itemObject.contentURLMd5
      else:
        def orderKey(itemObject):
          return itemObject.CDate

      ret = sorted(ret, key=orderKey, reverse=crits[1])
    except Exception as err:
      logger.error("Exception: %s", str(err))

    return ret



  # #Merge results of operation URL_CONTENT
  #
  # @param newItemsList new itemsList for new merged itemObject
  # @param itemsList current items list from current itemObject of node response results
  # @return new itemsList for merged itemObject
  def mergeResultsURLContent(self, newItemsList, clientResponseItem):
    itemsList = clientResponseItem.itemObject

    # If this is first item in results list, init itemObject with empty list
    if newItemsList is None:
      newItemsList = []

    if isinstance(itemsList, list):
      # For each URLContentResponse object in the clientResponseItem.itemObject
      for urlContentResponse in itemsList:
        # If raw or processed content exists
        if len(urlContentResponse.rawContents) > 0 or len(urlContentResponse.processedContents) > 0:
          # Check is candidate valid
          for i, itemObject in enumerate(newItemsList):
            # Is item already exists in accumulated list by urlMd5 from the same site or by the rawContentMd5 or
            # the contentURLMd5 from another
            if itemObject.siteId == urlContentResponse.siteId and\
              (itemObject.urlMd5 == urlContentResponse.urlMd5 or\
               (urlContentResponse.rawContentMd5 != '' and urlContentResponse.rawContentMd5 != '""' and\
                itemObject.rawContentMd5 == urlContentResponse.rawContentMd5) or\
               (urlContentResponse.contentURLMd5 != '' and urlContentResponse.contentURLMd5 != '""' and\
                itemObject.contentURLMd5 == urlContentResponse.contentURLMd5)):
              # Is item that exists is not processed or migrated from another host and candidate is not
              # or status greater
              if 'Batch_Id' not in itemObject.dbFields:
                itemObject.dbFields['Batch_Id'] = 0
              if 'Batch_Id' not in urlContentResponse.dbFields:
                urlContentResponse.dbFields['Batch_Id'] = 0
              # Is both items have crawled and processed but some one is older by UDate (experimental).
              itemObjectUDate = 0
              urlContentResponseUDate = 0
              if 'UDate' in itemObject.dbFields:
                itemObjectUDate = self.getUnixTimeFromString(itemObject.dbFields['UDate'])
              if 'UDate' in urlContentResponse.dbFields:
                urlContentResponseUDate = self.getUnixTimeFromString(urlContentResponse.dbFields['UDate'])
              # logger.debug("urlContentResponseUDate: %s, itemObjectUDate: %s",
              #              str(urlContentResponseUDate), str(itemObjectUDate))
              if (int(itemObject.dbFields['Batch_Id']) == 0 and int(urlContentResponse.dbFields['Batch_Id']) != 0) or\
               (urlContentResponse.dbFields['Status'] > itemObject.dbFields['Status']) or\
               (urlContentResponseUDate > itemObjectUDate):
                # Item already exists and candidate is better and replaces it
                logger.debug("Already exists itemObject:\n" + Utils.varDump(itemObject.dbFields) + \
                             "\nand replaced urlContentResponse:\n" + Utils.varDump(urlContentResponse.dbFields))
                urlContentResponse.host = clientResponseItem.host
                # itemObject = urlContentResponse
                newItemsList[i] = urlContentResponse
              else:
                # Item already exists and better than candidate
                logger.debug("Already exists urlContentResponse:\n" + Utils.varDump(urlContentResponse))
              urlContentResponse = None
              break
          # Add content to list
          if urlContentResponse is not None:
            urlContentResponse.host = clientResponseItem.host
            newItemsList.append(urlContentResponse)
            logger.debug("Added urlContentResponse:\n" + Utils.varDump(urlContentResponse))
          else:
            logger.debug("Rejected urlContentResponse")
        else:
          logger.debug("Empty contents lists in urlContentResponse:\n" + Utils.varDump(urlContentResponse))
    else:
      # Object is null or wrong type
      logger.error("Wrong type of clientResponseItem.itemObject\n" + Utils.varDump(itemsList))

    return newItemsList



  # #Merge results of operation SITE_STATUS
  #
  # @param mergedSite new merged Site object
  # @param currentSite current Site object from itemObject item of response results
  # @return new merged Site object
  def mergeResultsSiteStatus(self, mergedSite, clientResponseItem):
    currentSite = clientResponseItem.itemObject

    if isinstance(currentSite, EventObjects.Site):
      # If this is first time call for results list init. with this Site object
      if mergedSite is None:
        mergedSite = currentSite
      else:
        logger.debug("Merge with Site object:\n" + Utils.varDump(currentSite))
        # Merge site's data
        mergedSite = self.mergeResultsSiteFields(mergedSite, currentSite)

      mergedSite.host = clientResponseItem.host
    else:
      # Object is null or wrong type
      logger.error("Wrong type of currentSite object: " + str(type(currentSite)) + ", Site expected\n" + \
                   Utils.varDump(currentSite))

    return mergedSite



  # #Merge Site object fields
  #
  # @param siteToMerge Site object that is used as base
  # @param siteMergeWith Site object that is merged with base
  # @return merged siteToMerge object
  def mergeResultsSiteFields(self, siteToMerge, siteMergeWith):
    # Set merged values for correspondent fields of the Site objects
    siteToMerge.resources += siteMergeWith.resources
    siteToMerge.contents += siteMergeWith.contents
    siteToMerge.collectedURLs += siteMergeWith.collectedURLs
    siteToMerge.newURLs += siteMergeWith.newURLs
    siteToMerge.deletedURLs += siteMergeWith.deletedURLs
    siteToMerge.iterations = max([siteToMerge.iterations, siteMergeWith.iterations])
    siteToMerge.errors += siteMergeWith.errors
    siteToMerge.errorMask |= siteMergeWith.errorMask
    siteToMerge.size += siteMergeWith.size
    siteToMerge.avgSpeed = min([siteToMerge.avgSpeed, siteMergeWith.avgSpeed])
    siteToMerge.avgSpeedCounter = min([siteToMerge.avgSpeedCounter, siteMergeWith.avgSpeedCounter])

    if self.configVars[self.CONFIG_DRCE_NODES] > 1:
      siteToMerge.maxURLs += siteMergeWith.maxURLs
      siteToMerge.maxResources += siteMergeWith.maxResources
      siteToMerge.maxErrors += siteMergeWith.maxErrors

    return siteToMerge



  # #Merge results of operation SITE_FIND
  #
  # @param newItemsList new itemsList for new merged itemObject
  # @param itemsList current items list from current itemObject of node response results
  # @return new itemsList for merged itemObject
  def mergeResultsSiteFind(self, newItemsList, clientResponseItem):
    itemsList = clientResponseItem.itemObject

    # If this is first item in results list, init itemObject with empty list
    if newItemsList is None:
      newItemsList = []

    if isinstance(itemsList, list):
      # For each Site object in the clientResponseItem.itemObject
      for site in itemsList:
        # Check presence of this site in the newItemsList
        present = False
        for addedSite in newItemsList:
          if addedSite.id == site.id:
            # Merge site's data
            addedSite = self.mergeResultsSiteFields(addedSite, site)
            addedSite.host = clientResponseItem.host
            present = True
            break
        if not present:
          # Add content to list
          site.host = clientResponseItem.host
          newItemsList.append(site)
          logger.debug("Added Site:\n" + Utils.varDump(site))
    else:
      # Object is null or wrong type
      logger.error("Wrong type of clientResponseItem.itemObject\n" + Utils.varDump(itemsList))

    return newItemsList



  # #Merge results of operation URL_FETCH
  #
  # @param newItemsList new itemsList for new merged itemObject
  # @param itemsList current items list from current itemObject of node response results
  # @return new itemsList for merged itemObject
  def mergeResultsURLFetch(self, newItemsList, clientResponseItem):
    itemsList = clientResponseItem.itemObject

    logger.debug("Merging object of URLFEtch, host: %s, items: %s", str(clientResponseItem.host), str(len(itemsList)))
    # If this is first item in results list, init itemObject with empty list
    if newItemsList is None:
      newItemsList = []

    replacements = 0
    insertions = 0

    if isinstance(itemsList, list):
      # For each URL object in the clientResponseItem.itemObject
      for url in itemsList:
        # Check presence of this url in the newItemsList
        present = False
        for i, addedURL in enumerate(newItemsList):
          if addedURL.urlMd5 == url.urlMd5:
            logger.debug("URL found in list: %s", url.urlMd5)
            # For case if both are valid - to get newer (experimental)
            addedURLUDate = self.getUnixTimeFromString(addedURL.UDate)
            urUDate = self.getUnixTimeFromString(url.UDate)
            # logger.debug("addedURLUDate: %s, urUDate: %s", str(addedURLUDate), str(urUDate))
            # Replace with the URL object with higher status value and not migrated from another host
            if (addedURL.status <= url.status and (url.crawled > 0 and url.processed > 0 and url.batchId > 0)) or\
               (addedURL.status == url.status and addedURL.crawled == 0 and url.crawled > 0) or\
               (addedURL.status == url.status and addedURL.crawled > 0 and url.crawled > 0 and urUDate > addedURLUDate):
              logger.debug("URL replaced in list with best fields values: %s, old.status=%s, new.status=%s, " + \
                           "old.crawled=%s, new.crawled=%s, old.processed=%s, new.processed=%s, old.batchId=%s, " + \
                           "new.batchId=%s, old.UDate=%s, new.UDate=%s",
                           url.urlMd5, str(addedURL.status), str(url.status), str(addedURL.crawled), str(url.crawled),
                           str(addedURL.processed), str(url.processed), str(addedURL.batchId), str(url.batchId),
                           str(addedURLUDate), str(urUDate))
              url.host = clientResponseItem.host
              newItemsList[i] = url
              replacements += 1
            else:
              logger.debug("URL not replaced cause conditions not matched, old url:\n%s\ncandidate url:\n%s",
                           str(addedURL), str(url))
            present = True
            break
        if not present:
          # Add content to list
          url.host = clientResponseItem.host
          newItemsList.append(url)
          logger.debug("Added URL: %s", str(url.urlMd5))
          insertions += 1
    else:
      # Object is null or wrong type
      logger.error("Wrong type of clientResponseItem.itemObject\n%s", Utils.varDump(itemsList))

    logger.debug("Merging object of URLFEtch finished, replacements: %s, insertions: %s", str(replacements),
                 str(insertions))

    return newItemsList



  # #Merge results of operation for GeneralResponse item object
  #
  # @param mergedGeneralResponse new merged GeneralResponse object
  # @param currentGeneralResponse current GeneralResponse object from itemObject item of response results
  # @return new merged GeneralResponse object
  def mergeResultsGeneralResponse(self, mergedGeneralResponse, clientResponseItem):
    currentGeneralResponse = clientResponseItem.itemObject

    if isinstance(currentGeneralResponse, dtm.EventObjects.GeneralResponse):
      if mergedGeneralResponse is None:
        # If this is first time call for results list init. with this Site object
        mergedGeneralResponse = currentGeneralResponse
        mergedGeneralResponse.host = clientResponseItem.host
        logger.debug("Merge init GeneralResponse object:\n" + Utils.varDump(currentGeneralResponse))
      else:
        logger.debug("Merge with GeneralResponse object:\n" + Utils.varDump(currentGeneralResponse))
        # Merge fields values
        mergedGeneralResponse.errorCode = str(mergedGeneralResponse.errorCode) + ";" + \
                                             str(currentGeneralResponse.errorCode)
        mergedGeneralResponse.errorMessage = str(mergedGeneralResponse.errorMessage) + ";" + \
                                             str(currentGeneralResponse.errorMessage)
        mergedGeneralResponse.statuses.extend(currentGeneralResponse.statuses)
    else:
      # Object is null or wrong type
      logger.error("Wrong type of currentGeneralResponse object: " + str(type(currentGeneralResponse)) + \
                   ", dtm.GeneralResponse expected\n" + Utils.varDump(currentGeneralResponse))

    return mergedGeneralResponse



  # #Merge results of operation BATCH
  #
  # @param newItemsList new itemsList for new merged itemObject
  # @param itemsList current items list from current itemObject of node response results
  # @return new itemsList for merged itemObject
  def mergeResultsBatch(self, newItemsList, clientResponseItem):
    itemsList = clientResponseItem.itemObject

    # If this is first item in results list, init itemObject with empty list
    if newItemsList is None:
      newItemsList = []

    if isinstance(itemsList, list):
      # For each URLContentResponse object in the clientResponseItem.itemObject
      for urlContentResponse in itemsList:
        # If raw or processed content exists
        # if len(urlContentResponse.rawContents) > 0 or len(urlContentResponse.processedContents) > 0:
        # Add content to list
        if urlContentResponse is not None:
          urlContentResponse.host = clientResponseItem.host
          newItemsList.append(urlContentResponse)
          logger.debug("Added urlContentResponse:\n" + Utils.varDump(urlContentResponse))
        else:
          logger.debug("Rejected urlContentResponse")
        # else:
        #  logger.debug("Empty contents lists in urlContentResponse:\n" + Utils.varDump(urlContentResponse))
    else:
      # Object is null or wrong type
      logger.error("Wrong type of clientResponseItem.itemObject\n" + Utils.varDump(itemsList))

    return newItemsList


  # #Converts a string representation of a time to Unix time
  #
  # @param buf - buffer to convert
  # @param dateFormat - format of a date representation
  # @param valueType - a type of a value to return, 0 - integer, another - floating point
  # @return returns a Unix time number of seconds or zero if wrong convert
  def getUnixTimeFromString(self, buf, dateFormat='%Y-%m-%d %H:%M:%S', valueType=0):
    ret = 0

    try:
      ret = time.mktime(time.strptime(str(buf), dateFormat))
      if valueType == 0:
        ret = int(ret)
    except Exception as err:
      logger.error("Error get date from: `%s` with format: `%s` : %s", str(buf), dateFormat, str(err))

    return ret

