'''
Created on Mar 3, 2014

@author: igor
'''

from app.BaseServerManager import BaseServerManager
from app.PollerManager import PollerManager
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from dtm.Constants import EVENT_TYPES
import transport.Consts
import random
import sys

clientConnectName = "testConnect"


class TestRequest(object):
    
    def __init__(self, uid, body):
        self.uid = uid
        self.body = body
        

class Client(BaseServerManager):
    
    def __init__(self, iterNumber, body):
        super(Client, self).__init__()
        self.iterNumber = iterNumber
        self.setEventHandler(EVENT_TYPES.NEW_TASK, self.newTaskHandler)
        # request id - response
        self.messages = dict()
        self.is_send = False
        self.body = body
        
                
    def newTaskHandler(self, event):                
        if event.eventType != EVENT_TYPES.NEW_TASK:
            raise Exception("get wrong event type " + str(event.eventType))
        
        testRequest = event.eventObj        
        if testRequest.uid in self.messages:                           
            if testRequest.body == self.messages[testRequest.uid]:                
                del self.messages[testRequest.uid]
                self.iterNumber = self.iterNumber - 1                
                if self.iterNumber == 0 and len(self.messages) == 0:
                    self.exit_flag = True
                    print "EXIT " + self.body
        
        
    def on_poll_timeout(self):
        if not self.is_send:
            self.sendRequest(self.body) 
            self.is_send = True
    
    
    def sendRequest(self, body):        
        for iter in xrange(0, self.iterNumber):
            testRequest = TestRequest(iter, body + str(iter))
            event = self.eventBuilder.build(EVENT_TYPES.NEW_TASK, testRequest)             
            self.messages[testRequest.uid] = testRequest.body
            self.connections[clientConnectName].send(event)
        
        

class Server(BaseServerManager):
    
    
    def __init__(self, pollerManager, totalExpectRequest): 
        super(Server, self).__init__(pollerManager)
        self.events = list()
        self.totalExpectRequest = totalExpectRequest                
        self.setEventHandler(EVENT_TYPES.NEW_TASK, self.newTaskHandler)
                
        
    def newTaskHandler(self, event):
        if event.eventType != EVENT_TYPES.NEW_TASK:
            raise Exception("get wrong event type " + str(event.eventType))
                                        
        self.events.append(event)        
        if len(self.events) == self.totalExpectRequest: #made random
            while len(self.events) > 0:
                index = random.randrange(0, len(self.events))
                self.reply(self.events[index], self.events[index])
                del self.events[index]
  
  
    
if __name__ == "__main__":    
    connectBuilder = ConnectionBuilderLight()        
    pollerManager = PollerManager(connectBuilder.zmq_poller)

    serverConnectAdmin = connectBuilder.build(transport.Consts.SERVER_CONNECT, BaseServerManager.ADMIN_CONNECT_ENDPOINT)        
     
    client_request = 500
    client_number = 5
    connect_endpoint = "test_server1"
    tcp_protocol = False
    
    if len(sys.argv) > 1:
        tcp_protocol = True
        connect_endpoint = "127.0.0.1:8090"
    
    clients = list()
    
    server = Server(pollerManager, client_request * client_number)    
    serverConnect = None
    if not tcp_protocol: 
        serverConnect = connectBuilder.build(transport.Consts.SERVER_CONNECT, connect_endpoint)        
    else:
        serverConnect = connectBuilder.build(transport.Consts.SERVER_CONNECT, connect_endpoint, transport.Consts.TCP_TYPE)
        
    server.addConnection("server", serverConnect)
    server.start()
        
    for index in xrange(0, client_number):
        client = Client(client_request, "client" + str(index))
        clientConnect = None
        if not tcp_protocol:
            clientConnect = connectBuilder.build(transport.Consts.CLIENT_CONNECT, connect_endpoint)    
        else:
            clientConnect = connectBuilder.build(transport.Consts.CLIENT_CONNECT, connect_endpoint, transport.Consts.TCP_TYPE)
            
        client.addConnection(clientConnectName, clientConnect)
        clients.append(client)
        client.start()
    
    print "START"
    
    for client in clients:
        client.join()
        
    server.exit_flag = True
    server.join()