'''
Created on Mar 14, 2014

@author: igor
'''
import unittest
from mock import MagicMock, ANY
import ConfigParser
import tempfile
import os
from app.BaseServerManager import BaseServerManager
from app.PollerManager import PollerManager
from dtm.Scheduler import PLANED, SELECTED_EE
from dtm.Scheduler import Scheduler
from dtm.SchedulerTask import SchedulerTask
from dtm.SchedulerTaskScheme import SchedulerTaskScheme
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.ConnectionLight import ConnectionLight
from transport.Event import EventBuilder
from dtm.EventObjects import NewTask, UpdateTask, DeleteTask, ResourcesAVG, GetScheduledTasks
from dtm.EventObjects import GetScheduledTasksResponse
from dtm.Constants import EVENT_TYPES
from dbi.dbi import DBI
from test_dtm_TasksManager import Matcher
import dbi.Constants as dbi_const
import transport.Consts as tr_consts
 
import logging
FORMAT = '%(asctime)s - %(thread)ld - %(threadName)s - %(name)s - %(funcName)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.DEBUG, format=FORMAT) #basic logging configuration
 
 
def matchGetAVGResourceEvent(first, second): 
    return first.uid == second.uid and first.eventType == second.eventType 


def matchEventUID(first, second):
    return first.uid == second.uid


def matchGetScheduledTasks(first, second): 
    print "first ", first.eventObj.__dict__, "second ", second.eventObj.__dict__
    return first.eventObj.__dict__ == second.eventObj.__dict__


class TestScheduler(unittest.TestCase):


    def setUp(self):
        self.config = ConfigParser.RawConfigParser() 
        cfg_section = "Scheduler"
        
        tf = tempfile.NamedTemporaryFile()          
        sql_name = "sqlite:///" +  os.path.basename(tf.name) + "Scheduler.db"               
        
        self.config.add_section(cfg_section)
        self.config.set(cfg_section, Scheduler.SERVER, "Scheduler")
        self.config.set(cfg_section, Scheduler.RESOURCES_MANAGER_CLIENT, "ResourcesManager")        
        self.config.set(cfg_section, "db_name", sql_name)
        
        connectionBuilderLight = ConnectionBuilderLight()
        self.adminServerFake = connectionBuilderLight.build(tr_consts.SERVER_CONNECT, BaseServerManager.ADMIN_CONNECT_ENDPOINT)
                
        self.pollerManager_mock = MagicMock(spec=PollerManager)
        self.connectionBuilderLight_mock = MagicMock(spec=ConnectionBuilderLight )
        
        self.dbi_mock = MagicMock(DBI)
        self.serverConnection_mock = MagicMock(spec=ConnectionLight)
        self.resourcesManager_mock = MagicMock(spec=ConnectionLight)        
        self.connections_mock = [self.serverConnection_mock, self.resourcesManager_mock]
        
        self.connectionBuilderLight_mock.build.side_effect = self.connections_mock
        
        self.scheduler = Scheduler(self.config, self.connectionBuilderLight_mock, self.pollerManager_mock)
        self.eventBuilder = EventBuilder()
        
        self.taskId = 1
        self.newTask = NewTask("ls", self.taskId)
        self.updateTask =  UpdateTask(self.taskId)
        self.deleteTask = DeleteTask(0, self.taskId)
        self.resourceAVG = ResourcesAVG()
        self.resourceAVGEvent = self.eventBuilder.build(EVENT_TYPES.GET_AVG_RESOURCES_RESPONSE, self.resourceAVG)
        self.newTaskEvent = self.eventBuilder.build(EVENT_TYPES.SCHEDULE_TASK, self.newTask)
        self.updateTaskEvent = self.eventBuilder.build(EVENT_TYPES.UPDATE_TASK, self.updateTask)
        self.deleteTaskEvent = self.eventBuilder.build(EVENT_TYPES.DELETE_TASK, self.deleteTask)
        self.getScheduledTasksEvent = self.eventBuilder.build(EVENT_TYPES.GET_SCHEDULED_TASKS, GetScheduledTasks(10))
        self.getScheduledTasksResponse = GetScheduledTasksResponse([])
        
        self.pollerManager_mock.poll.return_value = [self.scheduler.SERVER]
        
     
    def tearDown(self): 
        self.adminServerFake.close()


    def check_task_in_dbi(self, task, state_condition=None):
        schedulerTask = SchedulerTask()
        schedulerTask.id = task.id
        lookSchedulerTaskScheme = SchedulerTaskScheme(schedulerTask)         
        resSchedulerTaskScheme = self.scheduler.dbi.fetch(lookSchedulerTaskScheme, "id=%s" % task.id)[0]        
        resTaskLog = resSchedulerTaskScheme._getSchedulerTask()
        
        if task.id == resTaskLog.id:
            if state_condition:
                if resTaskLog.state == state_condition:
                    return True
                else:
                    return False
            return True
        return False


    def check_task_not_in_dbi(self, task):
        schedulerTask = SchedulerTask()
        schedulerTask.id = task.id
        lookSchedulerTaskScheme = SchedulerTaskScheme(schedulerTask) 
        resSchedulerTaskScheme = self.scheduler.dbi.fetch(lookSchedulerTaskScheme, "id=%s" % task.id)[0]                
        if resSchedulerTaskScheme == None:
            return True
        return False
    

    def delete_task_in_dbi(self, task):
        schedulerTask = SchedulerTask()
        schedulerTask.id = task.id
        lookSchedulerTaskScheme = SchedulerTaskScheme(schedulerTask) 
        self.scheduler.dbi.delete(lookSchedulerTaskScheme, "id=%s" % task.id)
        self.scheduler.checkDBIState()
    
    
    def test_new_task(self):
        self.serverConnection_mock.recv.return_value = self.newTaskEvent
        
        expect_GetAVGResourceEvent = self.eventBuilder.build(EVENT_TYPES.GET_AVG_RESOURCES, None)
        expect_GetAVGResourceEvent.uid = self.newTaskEvent.uid
        
        match_event = Matcher(matchGetAVGResourceEvent, expect_GetAVGResourceEvent)
        
        self.scheduler.poll()
        
        self.assertEqual(self.scheduler.waitResourcesTasks[self.newTask.id], True, "")
        self.assertEqual(self.scheduler.waitResourcesEvents[self.newTaskEvent.uid], self.newTaskEvent, "")
        self.resourcesManager_mock.send.assert_called_once_with(match_event)
        
        
    def test_update_task_no_pending_task(self):
        self.serverConnection_mock.recv.return_value = self.updateTaskEvent

        expect_GetAVGResourceEvent = self.eventBuilder.build(EVENT_TYPES.GET_AVG_RESOURCES, None)
        expect_GetAVGResourceEvent.uid = self.updateTaskEvent.uid        
        match_event = Matcher(matchGetAVGResourceEvent, expect_GetAVGResourceEvent)
                
        self.scheduler.poll()

        self.assertEqual(self.scheduler.waitResourcesTasks[self.updateTask.id], True, "")
        self.assertEqual(self.scheduler.waitResourcesEvents[self.updateTaskEvent.uid], self.updateTaskEvent, "")
        self.resourcesManager_mock.send.assert_called_once_with(match_event)
        
        
    def test_update_task_present_in_pending_tasks(self):
        #add  pending task
        self.scheduler.waitResourcesTasks[self.taskId] = True
                
        self.serverConnection_mock.recv.return_value = self.updateTaskEvent

        self.scheduler.poll()
        
        self.assertEqual(self.resourcesManager_mock.send.call_count, 0, "event send to resourceManager")
        self.serverConnection_mock.send.assert_called_once_with(ANY)
        
        
    def test_delete_task_present_in_pending_tasts(self):
        #add  pending task
        self.scheduler.waitResourcesTasks[self.taskId] = True
        
        self.serverConnection_mock.recv.return_value = self.deleteTaskEvent
        
        self.scheduler.poll()
        
        self.assertEqual(self.resourcesManager_mock.send.call_count, 0, "event send to resourceManager")
        self.serverConnection_mock.send.assert_called_once_with(ANY)


    def test_delete_task_no_present_in_schedule(self):
        self.serverConnection_mock.recv.return_value = self.deleteTaskEvent
        
        self.scheduler.poll()
        
        self.serverConnection_mock.send.assert_called_once_with(ANY)
        
        
    def test_delete_task_present_in_schedule(self):
        self.scheduler.modifyTaskInSchedule(self.newTask)
        self.scheduler.checkDBIState()

        self.serverConnection_mock.recv.return_value = self.deleteTaskEvent
        
        self.scheduler.poll()
        
        self.serverConnection_mock.send.assert_called_once_with(ANY)
        self.assertTrue(self.check_task_not_in_dbi(self.newTask), "task is still in schedule")
        
        self.delete_task_in_dbi(self.newTask)        
        
        
    def test_resourceAVG_finish_add(self):
        self.newTaskEvent.connect_name = Scheduler.SERVER
        self.scheduler.addPendingEvent(self.newTaskEvent)
        self.resourceAVGEvent.uid = self.newTaskEvent.uid
        
        self.serverConnection_mock.recv.return_value = self.resourceAVGEvent        
        match_event = Matcher(matchEventUID, self.newTaskEvent)
        
        self.scheduler.poll()

        self.assertEqual(len(self.scheduler.waitResourcesTasks), 0, "")
        self.assertEqual(len(self.scheduler.waitResourcesEvents), 0, "")
        self.assertTrue(self.check_task_in_dbi(self.newTask), "")        
        self.serverConnection_mock.send.assert_called_once_with(match_event)
        
        self.delete_task_in_dbi(self.newTask)        
        

    def test_resourceAVG_finish_no_pending_event(self):
        self.serverConnection_mock.recv.return_value = self.resourceAVGEvent        
        match_event = Matcher(matchEventUID, self.newTaskEvent)
        
        self.scheduler.poll()


    def test_resourceAVG_finish_update(self):
        self.updateTaskEvent.connect_name = Scheduler.SERVER
        self.scheduler.addPendingEvent(self.updateTaskEvent)
        self.scheduler.modifyTaskInSchedule(self.newTask)
        self.resourceAVGEvent.uid = self.updateTaskEvent.uid
                        
        self.serverConnection_mock.recv.return_value = self.resourceAVGEvent        
        match_event = Matcher(matchEventUID, self.updateTaskEvent)
        
        self.scheduler.poll()

        self.assertEqual(len(self.scheduler.waitResourcesTasks), 0, "")
        self.assertEqual(len(self.scheduler.waitResourcesEvents), 0, "")
        self.assertTrue(self.check_task_in_dbi(self.updateTask), "")        
        self.serverConnection_mock.send.assert_called_once_with(match_event)
        
        self.delete_task_in_dbi(self.newTask)        
        
        
    def test_resourceAVG_resources_exceed(self):
        self.newTaskEvent.connect_name = Scheduler.SERVER
        self.scheduler.addPendingEvent(self.newTaskEvent)
        self.resourceAVGEvent.uid = self.newTaskEvent.uid
        self.resourceAVG.cpu = 200
        
        self.serverConnection_mock.recv.return_value = self.resourceAVGEvent 
        
        self.scheduler.poll()

        self.assertEqual(len(self.scheduler.waitResourcesTasks), 0, "")
        self.assertEqual(len(self.scheduler.waitResourcesEvents), 0, "")
        self.assertTrue(self.check_task_not_in_dbi(self.updateTask), "")        
        self.serverConnection_mock.send.assert_called_once_with(ANY)
        
        
    def test_resourceAVG_insert_thesame_task(self):
        self.newTaskEvent.connect_name = Scheduler.SERVER
        self.scheduler.addPendingEvent(self.newTaskEvent)
        self.scheduler.modifyTaskInSchedule(self.newTask)
        self.resourceAVGEvent.uid = self.newTaskEvent.uid
        
        self.serverConnection_mock.recv.return_value = self.resourceAVGEvent
        
        self.scheduler.poll()

        self.assertEqual(len(self.scheduler.waitResourcesTasks), 0, "")
        self.assertEqual(len(self.scheduler.waitResourcesEvents), 0, "")
        self.assertTrue(self.check_task_in_dbi(self.updateTask), "")        
        self.serverConnection_mock.send.assert_called_once_with(ANY)
        
        self.delete_task_in_dbi(self.newTask)
        
        
    def test_resourceAVG_update_non_exist_task(self):
        self.updateTaskEvent.connect_name = Scheduler.SERVER
        self.scheduler.addPendingEvent(self.updateTaskEvent)
        self.resourceAVGEvent.uid = self.updateTaskEvent.uid
        
        self.serverConnection_mock.recv.return_value = self.resourceAVGEvent
        
        self.scheduler.poll()
        
        self.assertEqual(len(self.scheduler.waitResourcesTasks), 0, "")
        self.assertEqual(len(self.scheduler.waitResourcesEvents), 0, "")
        self.serverConnection_mock.send.assert_called_once_with(ANY)


    def test_get_scheduled_tasks_empty_db(self):
        self.serverConnection_mock.recv.return_value = self.getScheduledTasksEvent 
        expect_response_event = self.eventBuilder.build(EVENT_TYPES.GET_SCHEDULED_TASKS_RESPONSE, self.getScheduledTasksResponse)
        match_event = Matcher(matchGetScheduledTasks, expect_response_event)
                
        self.scheduler.poll()
                
        self.serverConnection_mock.send.assert_called_once_with(match_event)


    def test_get_scheduled_tasks_broken_db(self):
        self.serverConnection_mock.recv.return_value = self.getScheduledTasksEvent 
        expect_response_event = self.eventBuilder.build(EVENT_TYPES.GET_SCHEDULED_TASKS_RESPONSE, self.getScheduledTasksResponse)
        match_event = Matcher(matchGetScheduledTasks, expect_response_event)
        
        self.scheduler.dbi.errorCode = dbi_const.DBI_DELETE_ERROR_CODE
                
        self.scheduler.poll()
                
        self.serverConnection_mock.send.assert_called_once_with(match_event)
        
                
    def test_get_scheduled_tasks_select_one_task(self):
        self.scheduler.modifyTaskInSchedule(self.newTask) 
        self.getScheduledTasksResponse = GetScheduledTasksResponse([self.newTask.id])
        
        self.serverConnection_mock.recv.return_value = self.getScheduledTasksEvent 
        expect_response_event = self.eventBuilder.build(EVENT_TYPES.GET_SCHEDULED_TASKS_RESPONSE, self.getScheduledTasksResponse)
        match_event = Matcher(matchGetScheduledTasks, expect_response_event)
        
        self.scheduler.poll()
                
        self.serverConnection_mock.send.assert_called_once_with(match_event)
        self.check_task_in_dbi(self.newTask, SELECTED_EE)
        
        self.delete_task_in_dbi(self.newTask)
        
        
    def test_get_scheduler_tasks_all_tasks_selected_by_ee(self):
        schedulerTask = SchedulerTask()
        schedulerTask.id = self.newTask.id
        schedulerTask.state = SELECTED_EE
        self.scheduler.dbi.insert(SchedulerTaskScheme(schedulerTask))        
        self.scheduler.checkDBIState()
        
        self.serverConnection_mock.recv.return_value = self.getScheduledTasksEvent 
        expect_response_event = self.eventBuilder.build(EVENT_TYPES.GET_SCHEDULED_TASKS_RESPONSE, self.getScheduledTasksResponse)
        match_event = Matcher(matchGetScheduledTasks, expect_response_event)
        
        self.scheduler.poll()
                
        self.serverConnection_mock.send.assert_called_once_with(match_event)
        
        self.delete_task_in_dbi(self.newTask)
        

    def test_get_scheduler_tasks_check_select_order(self):
        tasks = [self.newTask, NewTask("ls", 2), NewTask("ls", 3)]
        for task in tasks: 
            self.scheduler.modifyTaskInSchedule(task)
            self.scheduler.checkDBIState()
            
        self.getScheduledTasksResponse = GetScheduledTasksResponse([self.newTask.id, 2, 3])        
        self.serverConnection_mock.recv.return_value = self.getScheduledTasksEvent 
        expect_response_event = self.eventBuilder.build(EVENT_TYPES.GET_SCHEDULED_TASKS_RESPONSE, self.getScheduledTasksResponse)
        match_event = Matcher(matchGetScheduledTasks, expect_response_event)
        
        self.scheduler.poll()
                
        self.serverConnection_mock.send.assert_called_once_with(match_event)
        for task in tasks:
            self.check_task_in_dbi(task, SELECTED_EE)
        
        for task in tasks:
            self.delete_task_in_dbi(task)
