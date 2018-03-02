'''
Created on Apr 1, 2014

@author: igor
'''
from app.BaseServerManager import BaseServerManager
from dtm.Constants import EVENT_TYPES
from dtm.EventObjects import AdminState, AdminStatData
from transport.Event import EventBuilder
from transport.ConnectionBuilderLight import ConnectionBuilderLight
import transport.Consts as consts


class UserClass(BaseServerManager):


    def __init__(self):
        super(UserClass, self).__init__()
            
                                                             

if __name__ == "__main__":
    connectBuilder = ConnectionBuilderLight()
    adminServer = connectBuilder.build(consts.SERVER_CONNECT, BaseServerManager.ADMIN_CONNECT_ENDPOINT)    
    eventBuilder = EventBuilder()
    
    someConnect = connectBuilder.build(consts.SERVER_CONNECT, "127.0.0.1:9080", consts.TCP_TYPE)

    userClass = UserClass()
    userClass.addConnection("FakeConnection", someConnect)
    userClass.start()
    
    ready_event = adminServer.recv()
    ready_response = ready_event.eventObj 
    if isinstance(ready_response, AdminState) and ready_response.command == AdminState.STATE_READY:
        print "Userclass is ready"
        
    #get all stat fields 
    admin_request = AdminStatData(ready_response.className)
    request_event = eventBuilder.build(EVENT_TYPES.ADMIN_FETCH_STAT_DATA, admin_request)
    request_event.connect_identity = ready_event.connect_identity
    
    adminServer.send(request_event)
    
    stat_response_event = adminServer.recv()
    adminStatData = stat_response_event.eventObj
    
    print "Get stat, class ", adminStatData.className
    print adminStatData.fields

    #get some stat fields 
    admin_request = AdminStatData(ready_response.className, dict({"Admin_send_cnt":None, "no_such_field":None}))
    request_event = eventBuilder.build(EVENT_TYPES.ADMIN_FETCH_STAT_DATA, admin_request)
    request_event.connect_identity = ready_event.connect_identity

    adminServer.send(request_event)
    
    stat_response_event = adminServer.recv()
    adminStatData = stat_response_event.eventObj
    
    print "Get stat, class ", adminStatData.className
    print adminStatData.fields

        
    adminState = AdminState(ready_response.className, AdminState.STATE_SHUTDOWN)
    adminEvent = eventBuilder.build(EVENT_TYPES.ADMIN_STATE, adminState)
    adminEvent.connect_identity = ready_event.connect_identity    
    adminServer.send(adminEvent)
    
    userClass.join()
    print "OK"
