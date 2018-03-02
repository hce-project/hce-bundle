'''
Created on Feb 17, 2014

@author: scorp
'''

import Constants as CONSTANTS

TEST_TIMEOUT = 1000
bodyString = "String Body"
requestString = CONSTANTS.ERROR_CODE_OK + CONSTANTS.ITEM_DELIM + "param1" 
testResponseString1 = "bad"
testResponseString2 = "bad" + CONSTANTS.ITEM_DELIM + "param1"
testResponseString3 = CONSTANTS.ERROR_CODE_ERROR + CONSTANTS.ITEM_DELIM + "param1"
testResponseString4 = CONSTANTS.ERROR_CODE_OK + CONSTANTS.ITEM_DELIM + "param1" + CONSTANTS.FIELD_DELIM + "val1" + \
CONSTANTS.ITEM_DELIM + "param2" + CONSTANTS.FIELD_DELIM + "val2"
