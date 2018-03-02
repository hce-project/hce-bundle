'''
Created on Mar 18, 2014

@author: igor
'''

from app.BaseServerManager import BaseServerManager
from dtm.Constants import EVENT_TYPES
from dtm.EventObjects import AdminState
from transport.Event import EventBuilder
from transport.ConnectionBuilderLight import ConnectionBuilderLight
import transport.Consts as consts


class SomeClass(BaseServerManager):


    def __init__(self):
        super(SomeClass, self).__init__()
            
                                                             

if __name__ == "__main__":
    connectBuilder = ConnectionBuilderLight()
    serverConnect = connectBuilder.build(consts.SERVER_CONNECT, BaseServerManager.ADMIN_CONNECT_ENDPOINT)    
    eventBuilder = EventBuilder()
    
    someClass = SomeClass()
    someClass.start()
    
    ready_event = serverConnect.recv()
    print "readyEvent ", ready_event.__dict__ 

    adminState = AdminState("SomeClass", AdminState.STATE_SHUTDOWN)
    adminEvent = eventBuilder.build(EVENT_TYPES.ADMIN_STATE, adminState)
    adminEvent.connect_identity = ready_event.connect_identity    
    serverConnect.send(adminEvent)
    
    response = serverConnect.recv()
    print "response ", response.__dict__
    someClass.join()
    print "OK"
