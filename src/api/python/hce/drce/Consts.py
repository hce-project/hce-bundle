'''
Created on Feb 12, 2014

@author: igor
'''
##the file consist various constants related to
#execution of drce tasks(DRCE functional object message protocol.docx)

#command types
EXECUTE_TASK = 0
CHECK_TASK_STATE = 1
TERMINATE_TASK = 2
GET_TASK_DATA = 3
DELETE_TASK = 4

#task stat info
SIMPLE_STATUS_INFO = 1
EXTEND_STATUS_INFO = 2

#Get task data request
FETCH_DATA_DELETE = 1
FETCH_DATA_SAVE = 2

#Terminate task data request
TERMINATE_DATA_SAVE = 0
TERMINATE_DATA_DELETE = 1

#Terminate algorithm
TERMINATE_ALGORITHM_DEFAULT = 1
TERMINATE_ALGORITHM_CUSTOM = 2

