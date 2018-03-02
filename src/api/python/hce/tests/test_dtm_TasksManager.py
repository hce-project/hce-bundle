'''
Created on Mar 11, 2014

@author: igor
'''
import unittest
from mock import MagicMock, call, ANY
import ConfigParser
import tempfile
import os
from app.BaseServerManager import BaseServerManager
from dtm.TasksManager import TasksManager, DBIErr
from app.PollerManager import PollerManager
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.ConnectionLight import ConnectionLight
from transport.Event import EventBuilder
from dtm.EventObjects import NewTask, UpdateTaskFields, UpdateTask, DeleteTask, EEResponseData
from dtm.EventObjects import FetchTasksResultsFromCache, GetTasksStatus, GetTaskManagerFields, DeleteTaskData
from dtm.EventObjects import GeneralResponse
from dtm.EventObjects import FetchAvailabelTaskIds, AvailableTaskIds
from dtm.Constants import EVENT_TYPES
from dtm.TaskBackLogScheme import TaskBackLogScheme
from dtm.TaskLogScheme import TaskLogScheme
from dtm.TaskLog import TaskLog
from dbi.dbi import DBI
import transport.Consts as tr_consts

import logging
FORMAT = '%(asctime)s - %(thread)ld - %(threadName)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT) #basic logging configuration

#import logging
#logging.basicConfig(level=logging.DEBUG) #basic logging configuration



class Matcher(object):
    
    def __init__(self, compare, some_obj):
        self.compare = compare
        self.some_obj = some_obj
    
    def __eq__(self, other):
        return self.compare(self.some_obj, other)


def matchShedulerNewEvents(first, second):    
    files = first.eventObj.files
    first.eventObj.files = None
    ret = False
    if first.eventObj.__dict__ == second.eventObj.__dict__ and first.eventType == second.eventType:
        ret = True
    first.eventObj.files = files
    return ret


def matchDeleteTasksEvent(first, second):
    return first.eventType == second.eventType and first.eventObj.id == second.eventObj.id


class TestTasksManager(unittest.TestCase):


    def setUp(self):        
        self.config = ConfigParser.RawConfigParser() 
        cfg_section = "TasksManager"
        
        tf = tempfile.NamedTemporaryFile()          
        sql_name = "sqlite:///" +  os.path.basename(tf.name) + ".db"               
                
        self.config.add_section(cfg_section)
        self.config.set(cfg_section, TasksManager.SERVER, "TasksManager")
        self.config.set(cfg_section, TasksManager.TASKS_DATA_MANAGER_CLIENT, "TasksDataManager")
        self.config.set(cfg_section, TasksManager.SCHEDULER_CLIENT, "Scheduler")
        self.config.set(cfg_section, "db_name", sql_name)

        connectionBuilderLight = ConnectionBuilderLight()
        self.adminServerFake = connectionBuilderLight.build(tr_consts.SERVER_CONNECT, BaseServerManager.ADMIN_CONNECT_ENDPOINT)
        
        self.pollerManager_mock = MagicMock(spec=PollerManager)
        self.connectionBuilderLight_mock = MagicMock(spec=ConnectionBuilderLight )
        
        self.dbi_mock = MagicMock(DBI)
        self.serverConnection_mock = MagicMock(spec=ConnectionLight)
        self.tasksDataManager_mock = MagicMock(spec=ConnectionLight)
        self.scheduler_mock = MagicMock(spec=ConnectionLight)
        self.connections_mock = [self.serverConnection_mock, self.tasksDataManager_mock, self.scheduler_mock]
        
        self.connectionBuilderLight_mock.build.side_effect = self.connections_mock
        
        self.tasksManager = TasksManager(self.config, self.connectionBuilderLight_mock, self.pollerManager_mock)
        self.eventBuilder = EventBuilder()
        
        self.taskId = 1
        self.newTask = NewTask("ls", self.taskId)
        self.generalResponse = GeneralResponse()
        self.updateTask = UpdateTask(self.taskId)
        self.deleteTasks = DeleteTask(self.taskId)
        self.fetchTasksResultsFromCache = FetchTasksResultsFromCache([self.taskId])
                

    def tearDown(self):
        lookBackTaskLogScheme = TaskBackLogScheme(self.newTask)
        self.tasksManager.dbi.delete(lookBackTaskLogScheme, "id=%s" % self.newTask.id)
        self.adminServerFake.close()
                    
    
    def check_task_in_dbi(self, task, full_compare=True):
        lookBackTaskLogScheme = TaskBackLogScheme(task) 
        resBackTaskLogScheme = self.tasksManager.dbi.fetch(lookBackTaskLogScheme, "id=%s" % task.id)[0]        
        resTaskLog = resBackTaskLogScheme._getTaskLog()
                
        if not full_compare:
            if task.id == resTaskLog.id:
                return True
            else:
                return False
            
        if task.__dict__ == resTaskLog.__dict__:
            return True
        return False


    def test_add_new_task(self):        
        newTaskEvent = self.eventBuilder.build(EVENT_TYPES.NEW_TASK, self.newTask)
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = newTaskEvent
        
        match_event = Matcher(matchShedulerNewEvents, newTaskEvent)
                
        self.tasksManager.poll()
                
        self.assertEqual(len(self.tasksManager.tasksQueue), 0, "task is in tasksQueue")                        
        self.assertEqual(len(self.tasksManager.pendingTasks), 1, "")
        self.tasksDataManager_mock.send.assert_called_once_with(match_event)        
        
        
        
    def test_new_task_tasksDataManager_response(self):
        ##first step
        newTaskEvent = self.eventBuilder.build(EVENT_TYPES.SCHEDULE_TASK, self.newTask)         
        self.tasksManager.onNewTask(newTaskEvent)
                
        generalResponseEvent = self.eventBuilder.build(EVENT_TYPES.NEW_TASK_RESPONSE, self.generalResponse)
        generalResponseEvent.uid = newTaskEvent.uid
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = generalResponseEvent        

        match_event = Matcher(matchShedulerNewEvents, newTaskEvent)                
        taskLog = self.tasksManager.createTaskLog(self.newTask)
        self.tasksManager.poll()
        
        self.assertEqual(len(self.tasksManager.tasksQueue), 1, "task isnot in tasksQueue")
        self.assertEqual(len(self.tasksManager.pendingTasks), 1, "")
        self.assertTrue(self.check_task_in_dbi(taskLog, False), "insertion in dbi is broken")        
        self.scheduler_mock.send.assert_called_once_with(match_event)
        
        
    def test_fetch_available_tasks(self):
        req = FetchAvailabelTaskIds(100)
        event = self.eventBuilder.build(EVENT_TYPES.FETCH_AVAILABLE_TASK_IDS, req)
        event.connect_identity = "333"
        taskLog1 = TaskLog()
        taskLog1.id = "1"
        taskLog2 = TaskLog()
        taskLog2.id = "2"
        taskLog3 = TaskLog()
        taskLog3.id = "3"
        self.tasksManager.dbi = self.dbi_mock
        self.dbi_mock.sql.return_value = [TaskLogScheme(taskLog1), TaskLogScheme(taskLog2), TaskLogScheme(taskLog3)]
        event.connect_name = TasksManager.SERVER
        self.tasksManager.onFetchAvailableTasks(event)
        args = self.serverConnection_mock.send.call_args
        self.assertEqual(args[0][0].eventObj.ids, ["1", "2", "3"])

    def test_new_task_tasksDataManager_response_err(self):        
        ##first step
        newTaskEvent = self.eventBuilder.build(EVENT_TYPES.NEW_TASK, self.newTask)
        newTaskEvent.connect_name = "server"
        self.tasksManager.onNewTask(newTaskEvent)
                
        self.generalResponse.errorCode = self.generalResponse.ERROR_OK  + 1
        generalResponseEvent = self.eventBuilder.build(EVENT_TYPES.NEW_TASK_RESPONSE, self.generalResponse)        
        generalResponseEvent.uid = newTaskEvent.uid
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = generalResponseEvent
        
        self.tasksManager.addConnection("server", self.serverConnection_mock)
        
        self.tasksManager.poll()
        
        self.assertEqual(len(self.tasksManager.tasksQueue), 0, "task is in tasksQueue")
        self.assertEqual(len(self.tasksManager.pendingTasks), 0, "")
        self.serverConnection_mock.send.assert_called_once_with(ANY) #send response         
        self.assertEqual(self.scheduler_mock.send.call_count, 0, "")
        
        
        
    def test_add_new_task_dbi_exception(self):
        ##first step
        newTaskEvent = self.eventBuilder.build(EVENT_TYPES.NEW_TASK, self.newTask)
        newTaskEvent.connect_name = "server"
        self.tasksManager.onNewTask(newTaskEvent)
                
        generalResponseEvent = self.eventBuilder.build(EVENT_TYPES.NEW_TASK_RESPONSE, self.generalResponse)        
        generalResponseEvent.uid = newTaskEvent.uid
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = generalResponseEvent
        
        self.tasksManager.addConnection("server", self.serverConnection_mock)
        
        self.tasksManager.tasksQueue[self.newTask.id] = self.newTask

        self.tasksManager.dbi = self.dbi_mock
        self.dbi_mock.insert.side_effect = DBIErr(11, "some err")
         
        #self.tasksManager.poll()
        deleteTaskData = DeleteTaskData(self.taskId)
        deleteEvent = self.eventBuilder.build(EVENT_TYPES.DELETE_TASK_DATA, deleteTaskData)
                
        match_event = Matcher(matchDeleteTasksEvent, deleteEvent)
        
        self.tasksManager.poll()
        
        self.assertEqual(len(self.tasksManager.tasksQueue), 0, "task is in tasksQueue")
        self.assertEqual(len(self.tasksManager.pendingTasks), 0, "")
        self.tasksDataManager_mock.send.assert_called_with(match_event)        
        self.serverConnection_mock.send.assert_called_once_with(ANY) #send response
                
        
    def test_add_new_task_scheduler_exception(self):
        ##first step
        newTaskEvent = self.eventBuilder.build(EVENT_TYPES.NEW_TASK, self.newTask)
        newTaskEvent.connect_name = "server"
        self.tasksManager.onNewTask(newTaskEvent)
        ##second_step
        generalResponseEvent = self.eventBuilder.build(EVENT_TYPES.NEW_TASK_RESPONSE, self.generalResponse)
        generalResponseEvent.uid = newTaskEvent.uid
        self.tasksManager.onTasksManagerGeneralResponse(generalResponseEvent)
        
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        generalResponseErr = GeneralResponse(GeneralResponse.ERROR_OK + 1, "")
        generalResponseErrEvent = self.eventBuilder.build(EVENT_TYPES.SCHEDULE_TASK_RESPONSE, generalResponseErr)
        generalResponseErrEvent.uid = newTaskEvent.uid
        self.serverConnection_mock.recv.return_value = generalResponseErrEvent
        
        self.tasksManager.addConnection("server", self.serverConnection_mock)
                
        self.tasksManager.poll()
                
        self.assertEqual(len(self.tasksManager.tasksQueue), 0, "task is in tasksQueue")
        self.assertEqual(len(self.tasksManager.pendingTasks), 0, "")
        self.serverConnection_mock.send.assert_called_once_with(ANY) #send response
        

    def test_add_new_task_scheduler_ok(self):
        ##first step
        newTaskEvent = self.eventBuilder.build(EVENT_TYPES.NEW_TASK, self.newTask)
        newTaskEvent.connect_name = "server"
        self.tasksManager.onNewTask(newTaskEvent)
        ##second_step
        generalResponseEvent = self.eventBuilder.build(EVENT_TYPES.SCHEDULE_TASK_RESPONSE, self.generalResponse)
        generalResponseEvent.uid = newTaskEvent.uid
        self.tasksManager.onTasksManagerGeneralResponse(generalResponseEvent)
        
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = generalResponseEvent
        
        self.tasksManager.addConnection("server", self.serverConnection_mock)
        taskLog = self.tasksManager.createTaskLog(self.newTask)
        
        self.tasksManager.poll()
                
        self.assertEqual(len(self.tasksManager.tasksQueue), 1, "task is in tasksQueue")
        self.assertEqual(len(self.tasksManager.pendingTasks), 0, "")
        self.serverConnection_mock.send.assert_called_once_with(ANY) #send response
        self.assertTrue(self.check_task_in_dbi(taskLog, False), "insertion in dbi is broken")

    
    def test_update_task(self):
        #add task
        self.tasksManager.tasksQueue[self.newTask.id] = self.newTask
        
        updateTaskEvent = self.eventBuilder.build(EVENT_TYPES.UPDATE_TASK, self.updateTask)
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = updateTaskEvent
        
        match_event = Matcher(matchShedulerNewEvents, updateTaskEvent)        
        self.tasksManager.poll()
                        
        self.assertEqual(len(self.tasksManager.tasksQueue), 1, "task isnt in tasksQueue")                        
        self.tasksDataManager_mock.send.assert_called_once_with(updateTaskEvent)        
        self.scheduler_mock.send.assert_called_once_with(match_event)
        self.serverConnection_mock.send.assert_called_once_with(ANY)


    def test_update_task_not_procssing_task(self):        
        updateTaskEvent = self.eventBuilder.build(EVENT_TYPES.UPDATE_TASK, self.updateTask)
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = updateTaskEvent
                        
        self.tasksManager.poll()
        
        self.assertEqual(self.tasksDataManager_mock.send.call_count, 0, "event send to tasksDataManager")
        self.assertEqual(self.scheduler_mock.send.call_count, 0, "event send to scheduler")
        self.serverConnection_mock.send.assert_called_once_with(ANY)
        
        
    def test_delete_tasks(self):
        #add task
        newTaskEvent = self.eventBuilder.build(EVENT_TYPES.NEW_TASK, self.newTask)
        self.tasksManager.addNewTaskData(newTaskEvent)
        
        print self.check_task_in_dbi(self.newTask, False)
        #self.tasksManager.tasksQueue[self.newTask.id] = self.newTask

        deleteTaskEvent = self.eventBuilder.build(EVENT_TYPES.DELETE_TASK, self.deleteTasks)
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = deleteTaskEvent
        
        sendTaskEvent = self.eventBuilder.build(EVENT_TYPES.NEW_TASK, self.deleteTasks)
        match_event = Matcher(matchDeleteTasksEvent, sendTaskEvent)
        
        self.tasksManager.poll()

        self.assertEqual(len(self.tasksManager.tasksQueue), 1, "task is in tasksQueue")                        
        self.tasksDataManager_mock.send.assert_called_once_with(match_event)        
        self.assertEqual(self.scheduler_mock.send.call_count, 0, "")
        self.assertEqual(self.serverConnection_mock.send.call_count, 0, "")
        
    
    def test_delete_task_not_processing_task(self):
        deleteTaskEvent = self.eventBuilder.build(EVENT_TYPES.DELETE_TASK, self.deleteTasks)
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = deleteTaskEvent
        
        self.tasksManager.poll()

        self.serverConnection_mock.send.assert_called_once_with(ANY)
        
        
    def test_delete_task_dbi_error(self):
        #add task
        self.tasksManager.tasksQueue[self.newTask.id] = self.newTask
        
        deleteTaskEvent = self.eventBuilder.build(EVENT_TYPES.DELETE_TASK, self.deleteTasks)
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = deleteTaskEvent
        
        old_dbi = self.tasksManager.dbi
        self.tasksManager.dbi = self.dbi_mock
        self.dbi_mock.delete.side_effect = DBIErr(11, "some err")

        match_event = Matcher(matchDeleteTasksEvent, deleteTaskEvent)
        
        self.tasksManager.poll()

        self.serverConnection_mock.send.assert_called_once_with(ANY)
        
        self.tasksManager.dbi  = old_dbi
        
        
    def test_fetch_result_cache(self):
        #add task
        self.tasksManager.tasksQueue[self.newTask.id] = self.newTask
        
        fetchTasksResultsFromCacheEvent = self.eventBuilder.build(EVENT_TYPES.FETCH_RESULTS_CACHE, self.fetchTasksResultsFromCache)
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = fetchTasksResultsFromCacheEvent
        
        self.tasksManager.poll()
        
        self.assertEqual(len(self.tasksManager.fetchEvents), 1, "")
        self.tasksDataManager_mock.send.assert_called_once_with(fetchTasksResultsFromCacheEvent)


    def test_fetch_result_cache_no_task(self):        
        fetchTasksResultsFromCacheEvent = self.eventBuilder.build(EVENT_TYPES.FETCH_RESULTS_CACHE, self.fetchTasksResultsFromCache)
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = fetchTasksResultsFromCacheEvent
        
        self.tasksManager.poll()
        
        self.assertEqual(len(self.tasksManager.fetchEvents), 0, "")
        self.assertEqual(self.tasksDataManager_mock.send.call_count, 0, "event send to tasksDataManager")
        self.serverConnection_mock.send.assert_called_once_with(ANY)
        
        
    def test_get_status_request(self):
        getTasksStatus = GetTasksStatus([self.taskId])
        getTasksStatusEvent = self.eventBuilder.build(EVENT_TYPES.GET_TASK_STATUS, getTasksStatus)
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = getTasksStatusEvent
        
        self.tasksManager.poll()
        self.serverConnection_mock.send.assert_called_once_with(ANY)
        
        
    def test_get_task_fields(self):
        getTaskManagerFields = GetTaskManagerFields(self.taskId)
        getTaskManagerFieldsEvent = self.eventBuilder.build(EVENT_TYPES.GET_TASK_FIELDS, getTaskManagerFields)
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = getTaskManagerFieldsEvent

        self.tasksManager.poll()
        self.serverConnection_mock.send.assert_called_once_with(ANY)
        
        
    def test_update_task_field1(self):
        updateTaskFields = UpdateTaskFields(self.taskId)
        updateTaskFieldsEvent = self.eventBuilder.build(EVENT_TYPES.UPDATE_TASK_FIELDS, updateTaskFields)
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = updateTaskFieldsEvent

        self.tasksManager.poll()
        
        
    def test_fetch_result_response(self):
        event = self.eventBuilder.build(EVENT_TYPES.FETCH_RESULTS_CACHE, "")
        event.uid = "2"
        event.connect_name = self.tasksManager.SERVER
        self.tasksManager.fetchEvents[event.uid] = event
        
        eeResponseData = EEResponseData(self.taskId)
        eeResponseDataEvent = self.eventBuilder.build(EVENT_TYPES.FETCH_TASK_RESULTS_RESPONSE, eeResponseData)
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = eeResponseDataEvent                
        
        self.tasksManager.poll()
        
        self.assertEqual(len(self.tasksManager.fetchEvents), 0, "event is still here")
        self.serverConnection_mock.send.assert_called_once_with(ANY)
        
        
    def test_fetch_result_response_wrong_event_uid(self):
        eeResponseData = EEResponseData(self.taskId)
        eeResponseDataEvent = self.eventBuilder.build(EVENT_TYPES.FETCH_TASK_RESULTS_RESPONSE, eeResponseData)
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = eeResponseDataEvent                
        
        self.tasksManager.poll()
        
        self.assertEqual(len(self.tasksManager.fetchEvents), 0, "event is still here")
        self.assertEqual(self.serverConnection_mock.send.call_count, 0, "send reply")                
        
        
    def test_update_task_field(self):
        #add task
        newTaskEvent = self.eventBuilder.build(EVENT_TYPES.NEW_TASK, self.newTask)
        self.tasksManager.addNewTaskData(newTaskEvent)
        
        self.check_task_in_dbi(self.newTask, False)
        
        updateTaskFields = UpdateTaskFields(self.taskId)
        updateTaskFields.fields["state"] = EEResponseData.TASK_STATE_TERMINATED

        updateTaskEvent = self.eventBuilder.build(EVENT_TYPES.UPDATE_TASK_FIELDS, updateTaskFields)
        self.pollerManager_mock.poll.return_value = [self.tasksManager.SERVER]
        self.serverConnection_mock.recv.return_value = updateTaskEvent
                
        self.tasksManager.poll()

        self.assertEqual(len(self.tasksManager.tasksQueue), 0, "task is in tasksQueue")                        
        self.assertEquals(self.tasksDataManager_mock.send.call_count, 2, "")
         
        lookBackTaskLogScheme = TaskBackLogScheme(self.newTask) 
        resBackTaskLogScheme = self.tasksManager.dbi.fetch(lookBackTaskLogScheme, "id=%s" % self.taskId)[0]        
        assert resBackTaskLogScheme is None
        
        lookTaskLogScheme = TaskLogScheme(self.newTask)
        resTaskLogScheme = self.tasksManager.dbi.fetch(lookTaskLogScheme, "id=%s" % self.taskId)[0]
        assert resTaskLogScheme is not None

if __name__ == '__main__':
    unittest.main()