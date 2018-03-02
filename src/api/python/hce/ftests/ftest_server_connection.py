'''
Created on Mar 17, 2014

@author: igor
'''

from app.BaseServerManager import BaseServerManager
from app.PollerManager import PollerManager
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from dtm.Constants import EVENT_TYPES
from dtm.EventObjects import NewTask
import transport.Consts

clientConnectName = "testConnect"

        
class Server(BaseServerManager):
    
    
    def __init__(self, pollerManager, totalExpectRequest): 
        super(Server, self).__init__(pollerManager)
        self.events = list()
        self.totalExpectRequest = totalExpectRequest                
        self.setEventHandler(EVENT_TYPES.NEW_TASK, self.newTaskHandler)
                
        
    def newTaskHandler(self, event):
        if event.eventType != EVENT_TYPES.NEW_TASK:
            raise Exception("get wrong event type " + str(event.eventType))
                                                
        print "get event\t", event.__dict__
        response = self.eventBuilder.build(EVENT_TYPES.NEW_TASK_RESPONSE, NewTask("response", "2"))
        self.reply(event, response)                
    
    
if __name__ == "__main__":    
    connectBuilder = ConnectionBuilderLight()
    pollerManager = PollerManager(connectBuilder.zmq_poller) 
    connect_endpoint = "127.0.0.1:8090"
    tcp_protocol = True
    
    serverConnectAdmin = connectBuilder.build(transport.Consts.SERVER_CONNECT, BaseServerManager.ADMIN_CONNECT_ENDPOINT)
    
    clients = list()
    
    server = Server(pollerManager, 10)    
    serverConnect = None
    if not tcp_protocol: 
        serverConnect = connectBuilder.build(transport.Consts.SERVER_CONNECT, connect_endpoint)
    else:
        serverConnect = connectBuilder.build(transport.Consts.SERVER_CONNECT, connect_endpoint, transport.Consts.TCP_TYPE)
        
    server.addConnection("server", serverConnect)
    server.start()
    server.join()
