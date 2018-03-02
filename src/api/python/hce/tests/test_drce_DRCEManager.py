'''
Created on Feb 14, 2014

@author: igor
'''
import unittest
from mock import MagicMock, call, ANY

from drce.DRCEManager import DRCEManager, HostParams
from drce.ConnectionManager import ConnectionManager
from drce.CommandExecutor import CommandExecutor, CommandExecutorErr
from drce.Commands import TaskCheckRequest
from transport.Connection import ConnectionParams, Connection
from transport.Connection import ConnectionTimeout, TransportInternalErr
from transport.Response import Response
import drce.Consts as consts


class TestDRCEManager(unittest.TestCase):


    def setUp(self):
        self.drce_manager = DRCEManager()
        self.response = Response([
          "1",
        """  
        {
          "error_code":0,
          "error_message" :"msg",
          "time":10,
          "state":1,
          "pid":101,
          "data":[
          {"files":[{"name":"f1", "data":"data1", "action":12}],
             "stdout":"out",
             "stderror":"error",
             "exit_status":5,
             "node":"n1",
             "time":100
          }
          ]
        }         
        """ ])
        self.connect_mock = MagicMock(spec=Connection)
        self.task_request = TaskCheckRequest("task_id", consts.EXTEND_STATUS_INFO)
            

    def test_set_host_params_translation(self):
        host = HostParams("ibm.com", 125)
        connect_params = ConnectionParams(host.host, host.port)
        connect_manager_mock = MagicMock(spec=ConnectionManager)
        mock_cfg = {"create_connection.return_value": None}
        connect_manager_mock.configure_mock(**mock_cfg)        
        expect_calls = [call.create_connection(connect_params)]
        
        self.drce_manager.connect_manager = connect_manager_mock        
        self.drce_manager.activate_host(host)
          
        self.assertEquals(expect_calls, connect_manager_mock.mock_calls, "")
                
        
    def test_clear_host(self):        
        connect_manager_mock = MagicMock(spec=ConnectionManager)
        manager_expect_calls = [call.destroy_connection(ANY)]
        
        cmd_executor_mock = MagicMock(spec = CommandExecutor)
        executor_expect_calls = [call.replace_connection(ANY)]
        
        self.drce_manager.cmd_executor = cmd_executor_mock
        self.drce_manager.connect_manager = connect_manager_mock        
        self.drce_manager.clear_host()
        
        self.assertEquals(manager_expect_calls, connect_manager_mock.mock_calls, "")
        self.assertEquals(executor_expect_calls, cmd_executor_mock.mock_calls, "")

        
    def teEst_check_main_processing(self):        
        connect_cfg = {"send.return_value": None,
                                   "recv.return_value": self.response}
        self.connect_mock.configure_mock(**connect_cfg)        
        self.drce_manager.cmd_executor.replace_connection(self.connect_mock)
                
        task_response = self.drce_manager.process(self.task_request)
        
        test_err_str = "processing is failed"
        self.assertEqual(task_response.error_code, 0, test_err_str)
        self.assertEqual(task_response.error_msg, "msg", test_err_str )
        self.assertEqual(task_response.state, 1, test_err_str)
        self.assertEqual(len(task_response.data), 1, test_err_str)
        self.assertEqual(task_response.pid, 101, test_err_str)
        
        
        
    def test_raise_connection_timeout(self):
        self.connect_mock.send.return_value = None
        self.connect_mock.recv.side_effect = ConnectionTimeout("Boom")
        self.drce_manager.cmd_executor.replace_connection(self.connect_mock)
                        
        with self.assertRaises(ConnectionTimeout):
            list(self.drce_manager.process(self.task_request))
            
                        
    def test_raise_transport_internal_err(self):
        self.connect_mock.send.return_value = None
        self.connect_mock.recv.side_effect = TransportInternalErr("Boom")
        self.drce_manager.cmd_executor.replace_connection(self.connect_mock)
            
        with self.assertRaises(TransportInternalErr):
            list(self.drce_manager.process(self.task_request))
            
                        
    def test_raise_command_executor_err(self):
        self.connect_mock.send.return_value = None
        self.connect_mock.recv.side_effect = CommandExecutorErr("Boom")
        self.drce_manager.cmd_executor.replace_connection(self.connect_mock)
            
        with self.assertRaises(CommandExecutorErr):
            list(self.drce_manager.process(self.task_request))