Functional tests requests and responses for DTMD, DTMC and DTMA applications.

File name format for DTMC request json:
---------------------------------------
dtmc_<operation_name>_<task_id>_request.json

  <operation_name> - {"new_task", "check", "delete", "fetch", "update"}
                   and "_err" - for fault response
  <task_id>        - unique Id, numeric


File name format for DTMD simulator response json:
--------------------------------------------------
dtmds_<operation_name>_<task_id>_response.json


File name format for DTMC response json:
----------------------------------------
dtmc_<operation_name>_<task_id>_response.json


File name format for DTMA response json:
----------------------------------------
dtma_<operation_name>_<task_id>_response.json


The task_id value of response file name corresponds with the request file name.
