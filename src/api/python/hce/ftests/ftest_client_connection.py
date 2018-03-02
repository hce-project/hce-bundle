'''
Created on Mar 17, 2014

@author: igor
'''

from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.Event import EventBuilder
from dtm.EventObjects import NewTask
from dtm.Constants import EVENT_TYPES
import transport.Consts as consts

def build_event():
    taskId = "11"
    return NewTask("ls", taskId)


if __name__ == "__main__":
    addr = "127.0.0.1:5501"
    connectBuilder = ConnectionBuilderLight()
    eventBuilder = EventBuilder() 
    client = connectBuilder.build(consts.CLIENT_CONNECT, addr, consts.TCP_TYPE)
    event = eventBuilder.build(EVENT_TYPES.NEW_TASK, build_event())
    
    client.send(event)
    wait_response_timeout = 5000
    
    if client.poll(wait_response_timeout) == 0:
        print "no event"
    else:
        resp = client.recv()
        print "Finish", resp.__dict__
