'''
Created on Feb 13, 2014

@author: igor
'''
import unittest
from mock import MagicMock
from mock import call
from mock import ANY


from drce.CommandExecutor import CommandExecutor
from drce.CommandExecutor import CommandExecutorErr
from drce.CommandConvertor import CommandConvertor
from drce.CommandConvertor import CommandConvertorError
from drce.Commands import TaskCheckRequest
from transport.Connection import Connection
from transport.Connection import ConnectionTimeout
from transport.Response import Response
from transport.Response import ResponseFormatErr
  
import drce.Consts as consts


class TestCommandExecutor(unittest.TestCase):


    def setUp(self):
        self.connect_mock = MagicMock(spec=Connection)        
        self.cmd_executor = CommandExecutor(self.connect_mock, CommandConvertor())


    def teEst_execute_request(self):
        response = Response([
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
        
        connect_mock_cfg = {"send.return_value": None,
                                             "recv.return_value": response}        
        self.connect_mock.configure_mock(**connect_mock_cfg)
             
        #check
        connect_expect_calls = [call.send(ANY), call.recv(ANY)]
        
        task_request = TaskCheckRequest("task_id", consts.EXTEND_STATUS_INFO)
        task_response = self.cmd_executor.execute(task_request)
          
        self.connect_mock.assert_has_calls(connect_expect_calls)
        
        test_err_str = "json parsing is failed"
        self.assertEqual(task_response.error_code, 0, test_err_str)
        self.assertEqual(task_response.error_msg, "msg", test_err_str )
        self.assertEqual(task_response.state, 1, test_err_str)
        self.assertEqual(len(task_response.data), 1, test_err_str)
        self.assertEqual(task_response.pid, 101, test_err_str)
        
      
          
    def test_let_out_timeout_exception(self):
        self.connect_mock.send.return_value = None
        self.connect_mock.recv.side_effect = ConnectionTimeout("Boom")
        task_request = TaskCheckRequest("task_id", consts.EXTEND_STATUS_INFO)
        
        with self.assertRaises(ConnectionTimeout):
            list(self.cmd_executor.execute(task_request))
            
            
            
    def test_catch_convert_exception_msg_format(self):
        self.connect_mock.send.return_value = None
        self.connect_mock.recv.side_effect = ResponseFormatErr("Boom")
        
        task_request = TaskCheckRequest("task_id", consts.EXTEND_STATUS_INFO)

        with self.assertRaises(CommandExecutorErr):
            list(self.cmd_executor.execute(task_request))
         

    def test_catch_convert_exception_cmd_format(self):
        self.connect_mock.send.return_value = None
        self.connect_mock.recv.side_effect = CommandConvertorError("Boom")
        
        task_request = TaskCheckRequest("task_id", consts.EXTEND_STATUS_INFO)

        with self.assertRaises(CommandExecutorErr):
            list(self.cmd_executor.execute(task_request))
        