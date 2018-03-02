'''
HCE project, Python bindings, Distributed Tasks Manager application.
ResourcesStateMonitor object and related classes definitions.
This object acts as monitor of resources of HCE Cluster.
Periodically reads cluster schema from json schema file and make DRCE synch task request for all "replica" or
"shard" nodes. The DRCE task request is prepared and stored in the json external file that read each time when
monitoring cycle happened. The DRCE synch task acts as set of Linux commands and collects system information like
AVG CPU, disk, memory usage and so on. This information parsed and some system resource usage indicators detected.
This indicators updated the resource database that used for tasks planning.


@package: dtm
@author bgv bgv.hce@gmail.com
@link: http://hierarchical-cluster-engine.com/
@copyright: Copyright &copy; 2013-2014 IOIX Ukraine
@license: http://hierarchical-cluster-engine.com/license/
@since: 0.1
'''


import json
import logging
import re

import admin.Command
import admin.Node
import admin.NodeManagerRequest
from app.BaseServerManager import BaseServerManager
from app.LogFormatter import LogFormatterEvent
from drce.CommandConvertor import CommandConvertor
import dtm.EventObjects
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.UIDGenerator import UIDGenerator
import dtm.Constants as DTM_CONSTS
import transport.Consts as TRANSPORT_CONSTS
import app.Utils
from app.Utils import varDump

# Logger initialization
# logger = logging.getLogger(__name__)
logger = logging.getLogger(DTM_CONSTS.LOGGER_NAME)


# #The ResourcesStateMonitor class, is a monitor of resources of HCE Cluster.
#
# This object acts as monitor of resources of HCE Cluster.
# Periodically reads cluster schema from json schema file and make DRCE synch task request for all "replica" or
# "shard" nodes. The DRCE task request is prepared and stored in the json external file that read each time when
# monitoring cycle happened. The DRCE synch task acts as set of Linux commands and collects system information like
# AVG CPU, disk, memory usage and so on. This information parsed and some system resource usage indicators detected.
# This indicators updated the resource database that used for tasks planning.
#
class ResourcesStateMonitor(BaseServerManager):

  # Configuration settings options names
  CONFIG_RESOURCES_MANAGER_CLIENT = "clientResourcesManager"
  CONFIG_HCE_NODE_ADMIN_TIMEOUT = "HCENodeAdminTimeout"
  CONFIG_UPDATE_RESOURCES_DRCE_JSON = "FetchResourcesStateDRCEJsonFile"
  CONFIG_HCE_CLUSTER_SCHEMA_FILE = "HCEClusterSchemaFile"
  CONFIG_POLLING_TIMEOUT = "PollingTimeout"

  ERROR_UPDATE_RESOURCES = "Not all resources updated!"
  ERROR_JSON_DECODE = "Json decode error!"
  ERROR_RESOURCES_LISTS_NOT_EQUAL = "Lists of sent and received messages not equal!"
  ERROR_READ_FILE = "Error read file"
  ERROR_READ_DRCE_JSON_FILE = "Error read DRCE update resources state request json file"
  ERROR_HCE_RESPONSE_PROCESSING_EXCEPTION = "HCE node Admin API response processing exception"
  ERROR_HCE_CLUSTER_SCHEMA_STRUCTURE_WRONG = "Wrong structure of HCE cluster schema object"
  ERROR_HCE_NODE_REQUEST_ERROR = "HCE node request error"
  ERROR_HCE_RESPONSE_PROCESSING_FORMAT_ADMIN = "HCE node response format error, cant to split"
  ERROR_HCE_RESPONSE_PROCESSING_NO_RESOURCE_IN_RESPONSE = "No resource data found in response or response with error"
  ERROR_NO_ITEMS_IN_DRCE_RESPONSE = "No items in DRCE response"
  ERROR_DRCE_RESPONSE_ERROR_CODE = "DRCE response with error"
  ERROR_RE_PARSE_NO_MATCHES = "RE parse results from DRCE node, no matches!"


  # #constructor
  # initialize fields
  #
  # @param configParser config parser object
  # @param connectBuilderLight connection builder light
  #
  def __init__(self, configParser, connectionBuilderLight=None):
    super(ResourcesStateMonitor, self).__init__()

    # Instantiate the connection builder light if not set
    if connectionBuilderLight == None:
      connectionBuilderLight = ConnectionBuilderLight()

    className = self.__class__.__name__

    # Get configuration settings
    self.clientResourcesManagerName = configParser.get(className, self.CONFIG_RESOURCES_MANAGER_CLIENT)
    self.resourcesUpdateDRCERequestJsonFile = configParser.get(className, self.CONFIG_UPDATE_RESOURCES_DRCE_JSON)
    self.hceClusterSchemaFile = configParser.get(className, self.CONFIG_HCE_CLUSTER_SCHEMA_FILE)

    # Set connections poll timeout, defines period of HCE cluster monitoring cycle
    # self.pollTimeout = configParser.getint(className, self.CONFIG_POLLING_TIMEOUT)
    self.configVars[self.POLL_TIMEOUT_CONFIG_VAR_NAME] = configParser.getint(className, self.CONFIG_POLLING_TIMEOUT)

    # Create connections and raise bind or connect actions for correspondent connection type
    resourcesManagerConnection = connectionBuilderLight.build(TRANSPORT_CONSTS.CLIENT_CONNECT,
                                                              self.clientResourcesManagerName)

    # Add connections to the polling set
    self.addConnection(self.clientResourcesManagerName, resourcesManagerConnection)

    # Set event handler for EXECUTE_TASK event
    self.setEventHandler(DTM_CONSTS.EVENT_TYPES.UPDATE_RESOURCES_DATA_RESPONSE, self.onUpdateResourcesDataResponse)

    # Initialize HCE node Admin API
    self.hceNodeAdminTimeout = configParser.getint(className, self.CONFIG_HCE_NODE_ADMIN_TIMEOUT)
    self.hceNodeManagerRequest = admin.NodeManagerRequest.NodeManagerRequest()

    # Initialize unique Id generator
    self.drceIdGenerator = UIDGenerator()
    # Initialize DRCE commands convertor
    self.drceCommandConvertor = CommandConvertor()
    logger.debug("Constructor passed")


  # #onUpdateResourcesDataResponse event handler
  #
  # @param event instance of Event object
  def onUpdateResourcesDataResponse(self, event):
    # Get task Id from event
    generalResponse = event.eventObj
    # Get list of sent resources to update
    resourcesToUpdate = event.cookie
    if len(resourcesToUpdate) == len(generalResponse.statuses):
      errorObjects = []
      for i in range(len(generalResponse.statuses)):
        if generalResponse.statuses[i] == False:
          errorObjects.append(resourcesToUpdate[i])
          logger.error(LogFormatterEvent(event, errorObjects, self.ERROR_UPDATE_RESOURCES))
    else:
      logger.error(LogFormatterEvent(event, [], self.ERROR_RESOURCES_LISTS_NOT_EQUAL + "\n" +
                                     "send " + str(len(resourcesToUpdate)) + " returned " +
                                     str(len(generalResponse.statuses))
                                     ))



  # #Events wait timeout handler, for timeout state of the connections polling. Executes periodical processing of EE
  # resources state monitoring
  #
  def on_poll_timeout(self):
    # Initialize list of resources objects to update
    resources = []
    try:
      # Get HCE Cluster schema
      clusterSchemaObj = self.getObjectFromJsonFile(self.hceClusterSchemaFile)
      # Get DRCE FO request to get resources state from file
      drceRequestJson = self.loadFromFile(self.resourcesUpdateDRCERequestJsonFile)
      if drceRequestJson is not None:
        # Get connected data nodes from schema
        nodes = self.getConnectedNodesFromSchema(clusterSchemaObj)
        # For each DRCE node execute HCE node admin request
        for node in nodes:
          # Send request to HCE node Admin API
          rawResponse = self.sendToHCENodeAdmin(node.host, node.port, drceRequestJson)
          if rawResponse is not None:
            try:
              # Split admin response parts
              logger.debug("Raw node response: " + str(rawResponse) + ", type = " + str(type(rawResponse)))
              parts = rawResponse.split(admin.Constants.COMMAND_DELIM)
              if len(parts) > 1:
                # Convert DRCE jason protocol response to TaskResponse object
                taskResponse = self.drceCommandConvertor.from_json(parts[1])
                logger.debug("Received taskResponse object: " + str(vars(taskResponse)))
                # Get resource info data from the TaskResponse object and create Resource object
                resource = self.getResourceFromTaskResponse(taskResponse)
                logger.debug("Received Resource object: " + str(varDump(resource)))
                # Collect resource if valid data detected
                if resource is not None:
                  resources.append(resource)
                else:
                  logger.error(self.ERROR_HCE_RESPONSE_PROCESSING_NO_RESOURCE_IN_RESPONSE)
              else:
                logger.error(self.ERROR_HCE_RESPONSE_PROCESSING_FORMAT_ADMIN)
            except Exception, e:
              logger.error(self.ERROR_HCE_RESPONSE_PROCESSING_EXCEPTION + " : " + str(e.message) + "\n" + \
                           app.Utils.getTracebackInfo())

        # Send update for collected resources objects
        if len(resources) > 0:
          self.sendUpdateResourceDataRequest(resources)
      else:
        logger.error(self.ERROR_READ_DRCE_JSON_FILE + " " + self.resourcesUpdateDRCERequestJsonFile)
    except Exception, err:
      logger.error("Exception: %s", str(err))


  # #Get the Resource object created on the basis of information from the TaskResponse object of DRCE get resources data
  # request
  #
  # @param taskResponseObjects The TaskResponse objects container
  # @return the first Resource object if success or None if not
  def getResourceFromTaskResponse(self, taskResponseObjects):
    resource = None
    try:
      if len(taskResponseObjects.items) > 0:
        # logger.debug("Received taskResponseObjects.items[0]:" + str(vars(taskResponseObjects.items[0])))

        if taskResponseObjects.items[0].error_code == 0 or taskResponseObjects.items[0].error_code > 0:
          resource = dtm.EventObjects.Resource(taskResponseObjects.items[0].host + ":" +
                                               str(taskResponseObjects.items[0].port))
          resource.nodeName = taskResponseObjects.items[0].node
          resource.state = dtm.EventObjects.Resource.STATE_ACTIVE
          # logger.debug("Received stdout:\n" + str(taskResponseObjects.items[0].stdout))
          reTemplate1 = r"---CPU LA---(.*)"\
                         "---cpu cores---(.*)"\
                         "---vmstat---(.*)"\
                         "---processes---(.*)"\
                         "---threads max---(.*)"\
                         "---threads actual---(.*)"\
                         "---RAM---(.*)"\
                         "---Disk---(.*)"\
                         "---uptime---(.*)"\
                         "---END---(.*)"
          groupsItems = re.match (reTemplate1, taskResponseObjects.items[0].stdout, re.M | re.I | re.S)
          if groupsItems:
            # CPU LA
            # cpuLA = int(float(groupsItems.group(1).split(" ")[0].lstrip()) * 100)
            # print "cpuLA*100%=" + str(cpuLA)

            # CPU cores
            cpuCores = int(groupsItems.group(2))
            # print "cpuCores=" + str(cpuCores)
            resource.cpuCores = cpuCores

            # CPU Load
            lines = (' '.join(groupsItems.group(3).split("\n")[4].split())).split(' ')
            cpuIdle = int(lines[14])
            # logger.error("cpuIdle=" + str(cpuIdle))
            cpuLoad = 100 - cpuIdle
            if cpuLoad > 100:
              cpuLoad = 100
            else:
              if cpuLoad < 0:
                cpuLoad = 0
            # print "cpuLoad=" + str(cpuLoad)
            resource.cpu = cpuLoad

            # IO wait
            lines = (' '.join(groupsItems.group(3).split("\n")[4].split())).split(' ')
            cpuIO = int(lines[15])
            # logger.error("cpuIO=" + str(cpuIO))
            resource.io = cpuIO

            # Processes
            processes = int(groupsItems.group(4).lstrip().rstrip())
            # print "processes=" + str(processes)
            resource.processes = processes

            # Threads max
            # threadsMax = int(groupsItems.group(5).lstrip().rstrip())
            # print "threadsMax=" + str(threadsMax)

            # Threads actual
            threadsActual = int(groupsItems.group(6).lstrip().rstrip())
            # print "threadsActual=" + str(threadsActual)
            resource.threads = threadsActual

            # RAM
            lines = groupsItems.group(7).split("\n")
            # RAM total
            ramTotal = int(lines[2][4: 18].lstrip()) * 1000
            # print "[" + str(ramTotal) + "]"
            resource.ramR = ramTotal
            # RAM used
            ramUsed = int(lines[2][19: 29].lstrip()) * 1000
            # print "[" + str(ramUsed) + "]"
            resource.ramRU = ramUsed
            # RAM cached
            ramCached = int(lines[2][63:].lstrip()) * 1000
            # print "[" + str(ramCached) + "]"
            resource.ramRU = resource.ramRU - ramCached

            # Swap total
            swapTotal = int(lines[4][5: 18].lstrip()) * 1000
            # print "swapTotal=" + str(swapTotal)
            resource.swap = swapTotal
            # Swap used
            swapUsed = int(lines[4][19: 29].lstrip()) * 1000
            # print "swapUsed=" + str(swapUsed)
            resource.swapU = swapUsed

            # Disk
            lines = groupsItems.group(8).split("\n")
            lines = (' '.join(lines[2].split())).split(" ")
            # Disk total
            diskTotal = int(lines[1]) * 1024
            # print "diskTotal=" + str(diskTotal)
            resource.disk = diskTotal
            # Disk used
            diskUsed = int(lines[2]) * 1024
            # print "diskUsed=" + str(diskUsed)
            resource.diskU = diskUsed

            resource.ramV = 0
            resource.ramVU = 0

            # print vars(resource)
          else:
            logger.error(self.ERROR_RE_PARSE_NO_MATCHES + ", node:" + resource.nodeName + "\nstdout:\n" +
                         taskResponseObjects.items[0].stdout + "\nstderr:\n" + taskResponseObjects.items[0].stderror)
            resource = None
        else:
          logger.error(self.ERROR_DRCE_RESPONSE_ERROR_CODE + " : " + str(taskResponseObjects.items[0].error_code) + \
                       " : " + taskResponseObjects.items[0].error_message)
          resource = None
      else:
        logger.error(self.ERROR_NO_ITEMS_IN_DRCE_RESPONSE)

    except Exception, err:
      logger.error("Exception: %s", str(err))

    return resource



  # #Send UpdateResourceData request to the ResourcesManager object
  #
  # @param resourcesList The list of Resource objects to send
  def sendUpdateResourceDataRequest(self, resourcesList):
    try:
      # Get TaskManager fields
      # Prepare synch GetTaskFields request to the TasksManager
      updateResourceDataEvent = self.eventBuilder.build(DTM_CONSTS.EVENT_TYPES.UPDATE_RESOURCES_DATA, resourcesList)
      updateResourceDataEvent.cookie = resourcesList
      self.send(self.clientResourcesManagerName, updateResourceDataEvent)
    except Exception, err:
      logger.error("Exception: %s", str(err))


  # #Get the list of admin.Node objects from the cluster schema representation
  #
  # @param clusterSchemaObj The schema dic object
  # @return the list of admin.Node objects or empty list if error of schema object structure
  def getConnectedNodesFromSchema(self, clusterSchemaObj):
    nodes = []
    # Not sure in structure integrity
    try:
      # Seek on connected data node
      for item in clusterSchemaObj["cluster"]["nodes"]:
        if (item["role"] == "replica" or item["role"] == "shard") and ('connection' in item):
          port = item["admin"].split(":")
          if len(port) > 2:
            nodes.append(admin.Node.Node(item["host"], port[2]))
    except Exception, e:
      logger.error(self.ERROR_HCE_CLUSTER_SCHEMA_STRUCTURE_WRONG + " : " + str(e))

    return nodes



  # #Send to EE transport node admin connection
  #
  # @param host HCE node host
  # @param port HCE node port
  # @param messageParameters HCE node Admin request message parameters string
  # @return the raw body of HCE Admin API response
  def sendToHCENodeAdmin(self, host, port, messageParameters):
    response = None

    logger.debug("sendToHCENodeAdmin() use Host: '%s' and Port '%s'", str(host), str(port))
    try:
      # Execute EE node admin request
      node = admin.Node.Node(host, port)
      params = [messageParameters]
      command = admin.Command.Command(admin.Constants.COMMAND_NAMES.DRCE,
                                      params,
                                      admin.Constants.ADMIN_HANDLER_TYPES.DATA_PROCESSOR_DATA
                                      )
      requestBody = command.generateBody()
      message = {admin.Constants.STRING_MSGID_NAME : self.drceIdGenerator.get_uid(),
                 admin.Constants.STRING_BODY_NAME : requestBody}

      logger.debug("!!! Before makeRequest() msg_id = %s", str(message[admin.Constants.STRING_MSGID_NAME]))
      response = self.hceNodeManagerRequest.makeRequest(node, message, self.hceNodeAdminTimeout)
    except Exception, e:
      logger.error(self.ERROR_HCE_NODE_REQUEST_ERROR + " : " + str(e))

    if response is None:
      return response
    else:
      return response.getBody()



  # #Get dict object from json file
  #
  # @param filePath The file path name
  # @return the dict object or None if error
  def getObjectFromJsonFile(self, filePath):
    # Initialize returned dic
    schemaDic = None

    # Load schema from file
    schemaJsonString = self.loadFromFile(filePath)
    if schemaJsonString is not None:
      try:
        # Decode json
        # schemaDic = json.loads(schemaJsonString).decode('utf-8')
        schemaDic = json.loads(str(schemaJsonString))
      except ValueError:
        logger.error(self.ERROR_JSON_DECODE)
        logger.debug(schemaJsonString)
      except Exception, err:
        logger.error("Exception: %s", str(err))

    return schemaDic



  # #Get DRCE request json formated to fetch resources state of HCE node
  # Supposes execution of regular Linux commands and accumulation the textual printout to parse
  #
  # @param filePath The file pathname
  # @return the file content or None if error
  def loadFromFile(self, filePath):
    # Initialize file content
    fileContent = None
    try:
      fileContent = open(filePath, 'r').read()
    except IOError:
      logger.error(self.ERROR_READ_FILE + " " + filePath)
    except Exception, err:
      logger.error("Exception: %s", str(err))

    return fileContent
