'''
Created on Apr 8, 2014

@author: igor
'''

import time 
from dtm.Constants import EVENT_TYPES
from dtm.EventObjects import NewTask, GetTasksStatus, EEResponseData
from dtm.EventObjects import GeneralResponse
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.Event import EventBuilder
import transport.Consts as consts


def create_new_task_ASAP(taskId, command, resource_field, resource_value):
    newTask = NewTask(command, taskId)
    newTask.session["tmode"] = NewTask.TASK_MODE_ASYNCH
    newTask.setStrategyVar(resource_field, resource_value)
        
    return newTask


def create_get_tasks_status(taskId):
    return GetTasksStatus([taskId])


def get_response_event(clientConnection, timeout):
    if clientConnection.poll(wait_response_timeout) == 0:
        print "NO EVENT"
        exit(1)        
    else:
        return  clientConnection.recv()


def get_task_state(clientConnection, timeout, taskId): 
    get_tasks_status_event = eventBuilder.build(EVENT_TYPES.GET_TASK_STATUS, create_get_tasks_status(taskId))
    clientConnection.send(get_tasks_status_event)
    response_event = get_response_event(clientConnection, timeout)
    taskManagerFields = response_event.eventObj[0]
    return taskManagerFields.fields["state"]
    
    

if __name__ == "__main__":
    taskId = 20    
    wait_response_timeout = 5000
    addr = "192.168.1.135:5501"
    connectBuilder = ConnectionBuilderLight()
    eventBuilder = EventBuilder() 
    
    client = connectBuilder.build(consts.CLIENT_CONNECT, addr, consts.TCP_TYPE)
    
    new_task_event1 = eventBuilder.build(EVENT_TYPES.NEW_TASK, create_new_task_ASAP(taskId, "ls -la", "CPU", 200))    
    new_task_event2 = eventBuilder.build(EVENT_TYPES.NEW_TASK, create_new_task_ASAP(taskId + 1, "ls -la", "CPU_LOAD_MAX", 20))    
    new_task_event3 = eventBuilder.build(EVENT_TYPES.NEW_TASK, create_new_task_ASAP(taskId + 2, "ls -la", "IO_WAIT_MAX", 50))    
    new_task_event4 = eventBuilder.build(EVENT_TYPES.NEW_TASK, create_new_task_ASAP(taskId  + 3, "ls -la", "RAM_FREE", 1048576000 * 2))    
                   
    res_exceed_tasks = [new_task_event1, new_task_event2, new_task_event3, new_task_event4]
                   
    for task_event in res_exceed_tasks:
        client.send(task_event)                    
        
        response_event = get_response_event(client, wait_response_timeout)
        if response_event.eventObj.errorCode != GeneralResponse.ERROR_OK:
            print "New task is failed"
            exit(1)
        print "NewTAsk is OK"
        
    time.sleep(20)
    for curId in xrange(taskId, taskId + 4):
        assert get_task_state(client, wait_response_timeout, curId) == EEResponseData.TASK_STATE_NEW_SCHEDULED
        print "Task ", curId, " still TASK_STATE_NEW_SCHEDULED"
        
    print "PASSED"
        
    
