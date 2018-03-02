'''
Created on Apr 8, 2014

@author: igor
'''
import time
import datetime
import pprint
from dtm.Constants import EVENT_TYPES
from dtm.EventObjects import NewTask, GetTasksStatus, EEResponseData
from dtm.EventObjects import GeneralResponse
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.Event import EventBuilder
import transport.Consts as consts


def create_new_task(taskId, command, delta_time):
    newTask = NewTask(command, taskId)
    newTask.session["tmode"] = NewTask.TASK_MODE_ASYNCH
    
    planedTime = time.time() + delta_time
    rDate = datetime.datetime.fromtimestamp(planedTime)    
    newTask.setSessionVar("DATE", rDate.strftime("%Y-%m-%d %H:%M:%S,%f"))
    
    return newTask


def create_get_tasks_status(taskId):
    return GetTasksStatus([taskId])


def get_response_event(clientConnection, timeout):
    if clientConnection.poll(wait_response_timeout) == 0:
        print "NO EVENT"
        exit(1)        
    else:
        return  clientConnection.recv()


if __name__ == "__main__":
    taskId = 10
    #start task delay
    delta_time = 30 
    wait_response_timeout = 5000
    addr = "192.168.1.135:5501"
    connectBuilder = ConnectionBuilderLight()
    eventBuilder = EventBuilder() 
    
    client = connectBuilder.build(consts.CLIENT_CONNECT, addr, consts.TCP_TYPE)
    
    new_task_event = eventBuilder.build(EVENT_TYPES.NEW_TASK, create_new_task(taskId, "ls -la", delta_time))    
    get_tasks_status_event = eventBuilder.build(EVENT_TYPES.GET_TASK_STATUS, create_get_tasks_status(taskId))
    
           
    client.send(new_task_event)
    
    response_event = get_response_event(client, wait_response_timeout)
    if response_event.eventObj.errorCode != GeneralResponse.ERROR_OK:
        print "New task is failed"
        print response_event.eventObj.__dict__
        exit(1)
    print "NewTask is OK"
        
    
    client.send(get_tasks_status_event)
    response_event = get_response_event(client, wait_response_timeout)
    taskManagerFields = response_event.eventObj[0]
    
    assert taskManagerFields.fields["state"] == EEResponseData.TASK_STATE_NEW_SCHEDULED
    print "still TASK_STATE_NEW_SCHEDULED"
     
    time.sleep(delta_time - 5)
    #steel planed
    
    client.send(get_tasks_status_event)
    response_event = get_response_event(client, wait_response_timeout)
    taskManagerFields = response_event.eventObj[0]
    
    assert taskManagerFields.fields["state"] == EEResponseData.TASK_STATE_NEW_SCHEDULED
    print "still TASK_STATE_NEW_SCHEDULED"
        
    time.sleep(10)

    client.send(get_tasks_status_event)
    response_event = get_response_event(client, wait_response_timeout)
    taskManagerFields = response_event.eventObj[0]
    
    assert taskManagerFields.fields["state"] != EEResponseData.TASK_STATE_NEW_SCHEDULED
    
    print "PASSED"
