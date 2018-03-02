'''
Created on Mar 25, 2014

@author: igor
'''

from drce.Commands import TaskCheckRequest
from drce.CommandConvertor import CommandConvertor
from admin.Command import Command
from admin.Node import Node
from admin.NodeManagerRequest import NodeManagerRequest
from drce.Consts import SIMPLE_STATUS_INFO
import admin.Constants as consts

def getCommand_json():
    commandConvertor = CommandConvertor()
    request_id = "1"
    task_check_request = TaskCheckRequest(request_id, SIMPLE_STATUS_INFO)
            
    return commandConvertor.to_json(task_check_request)


if __name__ == '__main__':
    host = "127.0.0.1"
    port = 10022
    timeout = 1000
    
    node = Node(host, port)
    hceNodeManagerRequest = NodeManagerRequest()
    
    command = Command(consts.COMMAND_NAMES.DRCE, [getCommand_json()],                                    
                                           consts.ADMIN_HANDLER_TYPES.DATA_PROCESSOR_DATA,
                                           timeout)                                    
    requestBody = command.generateBody()
    message = {consts.STRING_MSGID_NAME : "101", consts.STRING_BODY_NAME : requestBody}
    
    response = hceNodeManagerRequest.makeRequest(node, message)    
    
    print response.__dict__
    print "OK"
    