'''
Created on Apr 2, 2014

@author: igor
'''
import time
import pprint
from dtm.Constants import EVENT_TYPES
from dtm.EventObjects import NewTask, CheckTaskState, GetTasksStatus, DeleteTask
from dtm.EventObjects import GeneralResponse
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.Event import EventBuilder
import transport.Consts as consts


def create_new_task(taskId, command):
    newTask = NewTask(command, taskId)
    
    return newTask


def create_check_task_state(taskId):
    return CheckTaskState(taskId, CheckTaskState.TYPE_FULL)


def create_get_tasks_status(taskId):
    return GetTasksStatus([taskId])


def create_delete_task(deletedTaskId, taskId, host, port):
    delTask = DeleteTask(deletedTaskId, taskId)
    delTask.host = host
    delTask.port = port
    return delTask


def get_response_event(clientConnection, timeout):
    if clientConnection.poll(wait_response_timeout) == 0:
        print "NO EVENT"
        exit(1)        
    else:
        return  clientConnection.recv()
    

if __name__ == "__main__":
    taskId = 10
    wait_response_timeout = 5000
    addr = "192.168.1.135:5501"
    connectBuilder = ConnectionBuilderLight()
    eventBuilder = EventBuilder() 
    
    client = connectBuilder.build(consts.CLIENT_CONNECT, addr, consts.TCP_TYPE)
    
    new_task_event = eventBuilder.build(EVENT_TYPES.NEW_TASK, create_new_task(taskId, "ls -la"))
    check_task_state_event = eventBuilder.build(EVENT_TYPES.CHECK_TASK_STATE, create_check_task_state(taskId))
    get_tasks_status_event = eventBuilder.build(EVENT_TYPES.GET_TASK_STATUS, create_get_tasks_status(taskId))
    
           
    client.send(new_task_event)
    
    response_event = get_response_event(client, wait_response_timeout)
    if response_event.eventObj.errorCode != GeneralResponse.ERROR_OK:
        print "New task is failed"
        print response_event.eventObj.__dict__
        exit(1)
    print "NewTask is OK"
    
    client.send(check_task_state_event)
    response_event = get_response_event(client, wait_response_timeout)
    print "EERESPONSE"
    print response_event.eventObj.__dict__
    
    
    client.send(get_tasks_status_event)
    response_event = get_response_event(client, wait_response_timeout)
    print "Tasks Status"
    host = None
    port = None
    for taskManagerField in response_event.eventObj:
        host = taskManagerField.fields["host"]
        port = taskManagerField.fields["port"]
        pprint.pprint(taskManagerField.__dict__)
        #print taskManagerField.__dict__
        
    
    delete_task_event = eventBuilder.build(EVENT_TYPES.DELETE_TASK, 
                                           create_delete_task(taskId, taskId + 1, host, port))
    client.send(delete_task_event)
    response_event = get_response_event(client, wait_response_timeout)
    if response_event.eventObj.errorCode != GeneralResponse.ERROR_OK:
        print "Delete task is failed"
        print response_event.eventObj.__dict__
    else:
        print "Delete is OK"
        print response_event.eventObj.__dict__
    
    time.sleep(15)
    
    
    #check status of deleted task
    get_tasks_status_event1 = eventBuilder.build(EVENT_TYPES.GET_TASK_STATUS, create_get_tasks_status(taskId + 1))
    client.send(get_tasks_status_event1)
    response_event = get_response_event(client, wait_response_timeout)
    for taskManagerField in response_event.eventObj:
        pprint.pprint(taskManagerField.__dict__)    
