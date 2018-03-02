'''
Created on Mar 18, 2014

@author: igor
'''

from app.BaseServerManager import BaseServerManager
from dtm.Constants import EVENT_TYPES
from transport.ConnectionBuilder import ConnectionBuilder
from transport.ConnectionBuilderLight import ConnectionBuilderLight
from transport.IDGenerator import IDGenerator
from transport.Response import Response
from transport.Request import Request
from transport.Connection import ConnectionParams
import transport.Consts as consts


class TCPServerRaw(BaseServerManager):


    def __init__(self, expect_response):
        super(TCPServerRaw, self).__init__()        
        self.expect_response = expect_response
        
        self.setEventHandler(EVENT_TYPES.SERVER_TCP_RAW, self.onServerTCPRaw)
                
        
    def onServerTCPRaw(self, event):
        print "get event ", event.__dict__, vars(event.eventObj)         
        response = event.eventObj        
        if response.body == self.expect_response.body and response.uid == self.expect_response.uid:
            print "bye"
            self.exit_flag = True


if __name__ == "__main__":
    connectBuilder = ConnectionBuilderLight()
    serverConnectAdmin = connectBuilder.build(consts.SERVER_CONNECT, BaseServerManager.ADMIN_CONNECT_ENDPOINT)    
    
    connectBuilder = ConnectionBuilder(IDGenerator())
    expect_response = Response(["id", "body"])
    request = Request("id")
    request.add_data("body")
    
    tcpServerRaw = TCPServerRaw(expect_response)
    
    connectParams = ConnectionParams("127.0.0.1", 9181)
    serverConnect = connectBuilder.build(consts.ADMIN_CONNECT_TYPE, connectParams, consts.SERVER_CONNECT) 
    
    tcpServerRaw.addConnection("raw_server", serverConnect)
    tcpServerRaw.start()
    
    clientConnect = connectBuilder.build(consts.ADMIN_CONNECT_TYPE, connectParams, consts.CLIENT_CONNECT)    
    clientConnect.send(request)
    
    tcpServerRaw.join()    
    print "OK"