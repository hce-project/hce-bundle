import unittest
from drce.DRCEManager import DRCEManager
from drce.Commands import TaskExecuteRequest
from drce.DRCEManager import HostParams
from drce.DRCEManager import ConnectionTimeout, TransportInternalErr, CommandExecutorErr


class TestDRCEManager(unittest.TestCase):

    def setUp(self):
        hostParams = HostParams("10.0.0.10", 2323)         
        self.drce_manager = DRCEManager()
        self.drce_manager.activate_host(hostParams)
            

    def test_send_executeCommand(self):
        #
        request_id = "101"
        taskExecuteRequest = TaskExecuteRequest(request_id)
        #set taskExecuteRequest fields
        taskExecuteRequest.data.session = "Some data"
        timeout = 2000
        
        try:
            task_response = self.drce_manager.process(taskExecuteRequest, timeout)
            
        except (ConnectionTimeout, TransportInternalErr, CommandExecutorErr) as err:
            print "Some err ", err.message
        
        
        print task_response