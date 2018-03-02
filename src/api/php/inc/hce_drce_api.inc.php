<?php
/**
 * HCE project Distributes Remote Command Execution node admin handler API.
 * Samples of implementation of basic API for DRCE handler functional object of the node application.
 *
 * @author bgv <bgv.hce@gmail.com>
 * @link http://hierarchical-cluster-engine.com/
 * @copyright Copyright &copy; 2013-2014 IOIX Ukraine
 * @license http://hierarchical-cluster-engine.com/license/
 * @package HCE project DRCE API
 * @since 0.1
 */

require_once 'hce_node_api.inc.php';

/**
 * Define and init DRCE FO encode base64 usage, 0 - not used, 1 - used
 */
defined('SPHINX_JSON_USE_BASE64') or define('SPHINX_JSON_USE_BASE64', 0);
/**
 * Define and init DRCE request timeout ms.
 */
defined('HCE_DRCE_EXEC_DEFAULT_TIMEOUT') or define('HCE_DRCE_EXEC_DEFAULT_TIMEOUT', 1000);
/**
 * Define and init DRCE request TTL ms.
 */
defined('HCE_DRCE_EXEC_DEFAULT_TTL') or define('HCE_DRCE_EXEC_DEFAULT_TTL', 1000);
/**
 * Define and init DRCE error codes.
 */
defined('HCE_DRCE_ERROR_OK') or define('HCE_DRCE_ERROR_OK', 0);
defined('HCE_DRCE_ERROR_CREATE_MESSAGE') or define('HCE_DRCE_ERROR_CREATE_MESSAGE', -100);
defined('HCE_DRCE_ERROR_PARSE_RESPONSE') or define('HCE_DRCE_ERROR_PARSE_RESPONSE', -101);
defined('HCE_DRCE_ERROR_CREATE_CONNECTION') or define('HCE_DRCE_ERROR_CREATE_CONNECTION', -102);
defined('HCE_DRCE_ERROR_WRONG_PARAMETERS') or define('HCE_DRCE_ERROR_WRONG_PARAMETERS', -103);

/**
 * Define and init DRCE request command name.
 */
defined('HCE_DRCE_CMD_EXEC') or define('HCE_DRCE_CMD_EXEC', 'DRCE_EXEC');

/**
 * Define and init DRCE request protocol json query fields names
 */
defined('HCE_DRCE_EXEC_FIELD_SESSION') or define('HCE_DRCE_EXEC_FIELD_SESSION', 'session');
defined('HCE_DRCE_EXEC_FIELD_COMMAND') or define('HCE_DRCE_EXEC_FIELD_COMMAND', 'command');
defined('HCE_DRCE_EXEC_FIELD_INPUT') or define('HCE_DRCE_EXEC_FIELD_INPUT', 'input');
defined('HCE_DRCE_EXEC_FIELD_FILES') or define('HCE_DRCE_EXEC_FIELD_FILES', 'files');
/**
 * Define and init DRCE request protocol json "session" fields names
 */
defined('HCE_DRCE_EXEC_FIELD_TYPE') or define('HCE_DRCE_EXEC_FIELD_TYPE', 'type');
defined('HCE_DRCE_EXEC_FIELD_PORT') or define('HCE_DRCE_EXEC_FIELD_PORT', 'port');
defined('HCE_DRCE_EXEC_FIELD_USER') or define('HCE_DRCE_EXEC_FIELD_USER', 'user');
defined('HCE_DRCE_EXEC_FIELD_PASSWD') or define('HCE_DRCE_EXEC_FIELD_PASSWD', 'password');
defined('HCE_DRCE_EXEC_FIELD_SHELL') or define('HCE_DRCE_EXEC_FIELD_SHELL', 'shell');
defined('HCE_DRCE_EXEC_FIELD_ENV') or define('HCE_DRCE_EXEC_FIELD_ENV', 'environment');
defined('HCE_DRCE_EXEC_FIELD_TIMEOUT') or define('HCE_DRCE_EXEC_FIELD_TIMEOUT', 'timeout');
defined('HCE_DRCE_EXEC_FIELD_TMODE') or define('HCE_DRCE_EXEC_FIELD_TMODE', 'tmode');
defined('HCE_DRCE_EXEC_FIELD_HOME_DIR') or define('HCE_DRCE_EXEC_FIELD_HOME_DIR', '');
defined('HCE_DRCE_EXEC_FIELD_TIME_MAX') or define('HCE_DRCE_EXEC_FIELD_TIME_MAX', 'time_max');
defined('HCE_DRCE_EXEC_FIELD_TIME_MAX_DEFAULT') or define('HCE_DRCE_EXEC_FIELD_TIME_MAX_DEFAULT', 30000);
defined('HCE_DRCE_EXEC_FIELD_TMODE_DEFAUL') or define('HCE_DRCE_EXEC_FIELD_TMODE_DEFAUL', 1);
defined('HCE_DRCE_EXEC_FIELD_CLEANUP') or define('HCE_DRCE_EXEC_FIELD_CLEANUP', 'cleanup');
defined('HCE_DRCE_EXEC_FIELD_CLEANUP_YES') or define('HCE_DRCE_EXEC_FIELD_CLEANUP_YES', 1);
defined('HCE_DRCE_EXEC_FIELD_CLEANUP_NO') or define('HCE_DRCE_EXEC_FIELD_CLEANUP_NO', 0);
/**
 * Define and init DRCE request protocol json "limits" fields names
 */
defined('HCE_DRCE_EXEC_FIELD_LIMITS') or define('HCE_DRCE_EXEC_FIELD_LIMITS', 'limits');
/**
 * Define and init DRCE request protocol json "files" fields names
 */
defined('HCE_DRCE_EXEC_FIELD_NAME') or define('HCE_DRCE_EXEC_FIELD_NAME', 'name');
defined('HCE_DRCE_EXEC_FIELD_DATA') or define('HCE_DRCE_EXEC_FIELD_DATA', 'data');
defined('HCE_DRCE_EXEC_FIELD_ACTION') or define('HCE_DRCE_EXEC_FIELD_ACTION', 'action');
/**
 * Define and init DRCE response protocol json main fields names
 */
defined('HCE_DRCE_EXEC_FIELD_ERR_CODE') or define('HCE_DRCE_EXEC_FIELD_ERR_CODE', 'error_code');
defined('HCE_DRCE_EXEC_FIELD_ERR_MSG') or define('HCE_DRCE_EXEC_FIELD_ERR_MSG', 'error_message');
defined('HCE_DRCE_EXEC_FIELD_TIME') or define('HCE_DRCE_EXEC_FIELD_TIME', 'time');
defined('HCE_DRCE_EXEC_FIELD_RESULTS') or define('HCE_DRCE_EXEC_FIELD_RESULTS', 'results');
/**
 * Define and init DRCE response protocol json results item fields names
 */
defined('HCE_DRCE_EXEC_FIELD_STDOUT') or define('HCE_DRCE_EXEC_FIELD_STDOUT', 'stdout');
defined('HCE_DRCE_EXEC_FIELD_STDERR') or define('HCE_DRCE_EXEC_FIELD_STDERR', 'stderror');
defined('HCE_DRCE_EXEC_FIELD_FILES') or define('HCE_DRCE_EXEC_FIELD_FILES', 'files');
defined('HCE_DRCE_EXEC_FIELD_NODE') or define('HCE_DRCE_EXEC_FIELD_NODE', 'node');
defined('HCE_DRCE_EXEC_FIELD_TIME') or define('HCE_DRCE_EXEC_FIELD_TIME', 'time');
/**
 * Define and init DRCE request protocol json fields names
 */
defined('HCE_DRCE_REQUEST_TYPE_FIELD') or define('HCE_DRCE_REQUEST_TYPE_FIELD', 'type');
defined('HCE_DRCE_REQUEST_ID_FIELD') or define('HCE_DRCE_REQUEST_ID_FIELD', 'id');
defined('HCE_DRCE_REQUEST_DATA_FIELD') or define('HCE_DRCE_REQUEST_DATA_FIELD', 'data');
defined('HCE_DRCE_REQUEST_SUBTASKS_FIELD') or define('HCE_DRCE_REQUEST_SUBTASKS_FIELD', 'subtasks');
/**
 * Define and init DRCE request types
 */
defined('HCE_DRCE_REQUEST_TYPE_SET') or define('HCE_DRCE_REQUEST_TYPE_SET', 0);
defined('HCE_DRCE_REQUEST_TYPE_CHECK') or define('HCE_DRCE_REQUEST_TYPE_CHECK', 1);
defined('HCE_DRCE_REQUEST_TYPE_TERMINATE') or define('HCE_DRCE_REQUEST_TYPE_TERMINATE', 2);
defined('HCE_DRCE_REQUEST_TYPE_GET') or define('HCE_DRCE_REQUEST_TYPE_GET', 3);
defined('HCE_DRCE_REQUEST_TYPE_DELETE') or define('HCE_DRCE_REQUEST_TYPE_DELETE', 4);
/**
 * Define and init DRCE request type check types
 */
defined('HCE_DRCE_REQUEST_TYPE_CHECK_SIMPLE') or define('HCE_DRCE_REQUEST_TYPE_CHECK_SIMPLE', 1);
defined('HCE_DRCE_REQUEST_TYPE_CHECK_EXTENDED') or define('HCE_DRCE_REQUEST_TYPE_CHECK_EXTENDED', 2);
/**
 * Define and init DRCE request terminate alg
 */
defined('HCE_DRCE_EXEC_FIELD_TERMINATE_ALG') or define('HCE_DRCE_EXEC_FIELD_TERMINATE_ALG', 'alg');
defined('HCE_DRCE_EXEC_TERMINATE_ALG_SIMPLE') or define('HCE_DRCE_EXEC_TERMINATE_ALG_SIMPLE', 1);
defined('HCE_DRCE_EXEC_TERMINATE_ALG_EXTENDED') or define('HCE_DRCE_EXEC_TERMINATE_ALG_EXTENDED', 2);
/**
 * Define and init DRCE request terminate delay
 */
defined('HCE_DRCE_EXEC_FIELD_TERMINATE_DELAY') or define('HCE_DRCE_EXEC_FIELD_TERMINATE_DELAY', 'delay');
defined('HCE_DRCE_EXEC_TERMINATE_DELAY_DEFAULT') or define('HCE_DRCE_EXEC_TERMINATE_DELAY_DEFAULT', 1000);
/**
 * Define and init DRCE request terminate repeat
 */
defined('HCE_DRCE_EXEC_FIELD_TERMINATE_REPEAT') or define('HCE_DRCE_EXEC_FIELD_TERMINATE_REPEAT', 'repeat');
defined('HCE_DRCE_EXEC_TERMINATE_REPEAT_DEFAULT') or define('HCE_DRCE_EXEC_TERMINATE_REPEAT_DEFAULT', 3);
/**
 * Define and init DRCE request terminate signal
 */
defined('HCE_DRCE_EXEC_FIELD_TERMINATE_SIGNAL') or define('HCE_DRCE_EXEC_FIELD_TERMINATE_SIGNAL', 'sinal');
defined('HCE_DRCE_EXEC_TERMINATE_SIGNAL_DEFAULT') or define('HCE_DRCE_EXEC_TERMINATE_SIGNAL_DEFAULT', 15);
/**
 * Define and init DRCE request get type
 */
defined('HCE_DRCE_REQUEST_TYPE_FETCH_DELETE') or define('HCE_DRCE_REQUEST_TYPE_FETCH_DELETE', 1);
defined('HCE_DRCE_REQUEST_TYPE_FETCH_NOT_DELETE') or define('HCE_DRCE_REQUEST_TYPE_FETCH_NOT_DELETE', 2);
/**
 * Define and init DRCE request file i/o statement
 */
defined('HCE_DRCE_REQUEST_READ_FROM_FILE_STATEMENT') or define('HCE_DRCE_REQUEST_READ_FROM_FILE_STATEMENT', 'READ_FROM_FILE:');

/*
 * @desc make DRCE request request json message
 * @param $parameters_array - parameters array corresponds to the DRCE FO protocol Functional_object_message_format.docx
 *                            array(HCE_DRCE_EXEC_FIELD_Q=>'query string',
 *                                  HCE_DRCE_EXEC_FIELD_PARAMETERS=>array(array(HCE_DRCE_EXEC_FIELD_QUERY_ID=>123), array(HCE_DRCE_EXEC_FIELD_JSON_TYPE=>15))
 *                                 )
 *
 * @return string json encoded message or negative value in case of error: HCE_DRCE_ERROR_WRONG_PARAMETERS - wrong parameters array structure
 */
 function hce_drce_exec_create_parameters_array($parameters, $type){
   //Default DRCE request array initialization
   switch($type){
     case HCE_DRCE_REQUEST_TYPE_SET       : {
       $ret=array(HCE_DRCE_EXEC_FIELD_SESSION=>
                  array(HCE_DRCE_EXEC_FIELD_TYPE=>0, 
                        HCE_DRCE_EXEC_FIELD_PORT=>0,
                        HCE_DRCE_EXEC_FIELD_USER=>'',
                        HCE_DRCE_EXEC_FIELD_PASSWD=>'',
                        HCE_DRCE_EXEC_FIELD_SHELL=>'',
                        HCE_DRCE_EXEC_FIELD_ENV=>array(),
                        HCE_DRCE_EXEC_FIELD_HOME_DIR=>'',
                        HCE_DRCE_EXEC_FIELD_TIMEOUT=>0,
                        HCE_DRCE_EXEC_FIELD_TMODE=>HCE_DRCE_EXEC_FIELD_TMODE_DEFAUL,
                        HCE_DRCE_EXEC_FIELD_TIME_MAX=>HCE_DRCE_EXEC_FIELD_TIME_MAX_DEFAULT,
                        HCE_DRCE_EXEC_FIELD_CLEANUP=>HCE_DRCE_EXEC_FIELD_CLEANUP_YES,
                       ),
                  HCE_DRCE_EXEC_FIELD_COMMAND=>'',
                  HCE_DRCE_EXEC_FIELD_INPUT=>'',
                  HCE_DRCE_EXEC_FIELD_FILES=>array()
                 );
       break;
     }
     case HCE_DRCE_REQUEST_TYPE_CHECK     : {
       $ret=array(HCE_DRCE_EXEC_FIELD_TYPE=>HCE_DRCE_REQUEST_TYPE_CHECK_SIMPLE);
       break;
     }
     case HCE_DRCE_REQUEST_TYPE_TERMINATE : {
       $ret=array(
                 HCE_DRCE_EXEC_FIELD_TERMINATE_ALG=>HCE_DRCE_EXEC_TERMINATE_ALG_SIMPLE,
                 HCE_DRCE_EXEC_FIELD_TERMINATE_DELAY=>HCE_DRCE_EXEC_TERMINATE_DELAY_DEFAULT,
                 HCE_DRCE_EXEC_FIELD_TERMINATE_REPEAT=>HCE_DRCE_EXEC_TERMINATE_REPEAT_DEFAULT,
                 HCE_DRCE_EXEC_FIELD_TERMINATE_SIGNAL=>HCE_DRCE_EXEC_TERMINATE_SIGNAL_DEFAULT
                 );
       break;
     }
     case HCE_DRCE_REQUEST_TYPE_GET       : {
       $ret=array(
                 HCE_DRCE_EXEC_FIELD_TYPE=>HCE_DRCE_REQUEST_TYPE_FETCH_DELETE
                 );
       break;
     }
     case HCE_DRCE_REQUEST_TYPE_DELETE		: {
       $ret=array();
       break;
		 }
   }

   if(is_array($parameters)){
     //Create json array from parameters array
     //TODO:
   }else{
     //Create from json content string
     $json_in=@json_decode($parameters, true);
     if(is_array($json_in)){
       //Fill json array fields according with protocol specification
       switch($type){
         case HCE_DRCE_REQUEST_TYPE_SET : {
           //Fill session array
           if(isset($json_in[HCE_DRCE_EXEC_FIELD_SESSION])){
             foreach($ret[HCE_DRCE_EXEC_FIELD_SESSION] as $key=>$val){
               if(isset($json_in[HCE_DRCE_EXEC_FIELD_SESSION][$key])){
                 $ret[HCE_DRCE_EXEC_FIELD_SESSION][$key]=$json_in[HCE_DRCE_EXEC_FIELD_SESSION][$key];
               }
             }
           }
           //Fill command
           if(isset($json_in[HCE_DRCE_EXEC_FIELD_COMMAND])){
             $ret[HCE_DRCE_EXEC_FIELD_COMMAND]=$json_in[HCE_DRCE_EXEC_FIELD_COMMAND];
           }
           //Fill input stream
           if(isset($json_in[HCE_DRCE_EXEC_FIELD_INPUT])){
             $ret[HCE_DRCE_EXEC_FIELD_INPUT]=$json_in[HCE_DRCE_EXEC_FIELD_INPUT];
           }
           //Fill files array
           if(isset($json_in[HCE_DRCE_EXEC_FIELD_FILES]) && is_array($json_in[HCE_DRCE_EXEC_FIELD_FILES])){
             foreach($json_in[HCE_DRCE_EXEC_FIELD_FILES] as $key=>$value){
               if(is_array($value) && isset($value[HCE_DRCE_EXEC_FIELD_NAME]) && isset($value[HCE_DRCE_EXEC_FIELD_DATA]) && isset($value[HCE_DRCE_EXEC_FIELD_ACTION])){
                 if(strlen($value[HCE_DRCE_EXEC_FIELD_DATA])>15 && substr($value[HCE_DRCE_EXEC_FIELD_DATA], 0, 15)==HCE_DRCE_REQUEST_READ_FROM_FILE_STATEMENT){
                   //Read content of file and replace data stream
                   $file_name=substr($value[HCE_DRCE_EXEC_FIELD_DATA], 15);
                   if(file_exists($file_name)){
                     $value[HCE_DRCE_EXEC_FIELD_DATA]=file_get_contents($file_name);
                     if(($value[HCE_DRCE_EXEC_FIELD_ACTION]+0) & 2147483648/*0x80000000*/){
                       $value[HCE_DRCE_EXEC_FIELD_DATA]=base64_encode($value[HCE_DRCE_EXEC_FIELD_DATA]);
                     }
                   }else{
                     $value[HCE_DRCE_EXEC_FIELD_DATA]='File not found: '.$file_name;
                   }
                 }
                 $ret[HCE_DRCE_EXEC_FIELD_FILES][]=array(
                                                        HCE_DRCE_EXEC_FIELD_NAME=>$value[HCE_DRCE_EXEC_FIELD_NAME],
                                                        HCE_DRCE_EXEC_FIELD_DATA=>$value[HCE_DRCE_EXEC_FIELD_DATA],
                                                        HCE_DRCE_EXEC_FIELD_ACTION=>($value[HCE_DRCE_EXEC_FIELD_ACTION]+0)
                                                   );
               }
             }
           }
           //Fill limits array
           if(isset($json_in[HCE_DRCE_EXEC_FIELD_LIMITS])){
             foreach($ret[HCE_DRCE_EXEC_FIELD_LIMITS] as $key=>$val){
               if(isset($json_in[HCE_DRCE_EXEC_FIELD_LIMITS][$key])){
                 $ret[HCE_DRCE_EXEC_FIELD_LIMITS][$key]=$json_in[HCE_DRCE_EXEC_FIELD_LIMITS][$key];
               }
             }
           }
           break;
         }
         case HCE_DRCE_REQUEST_TYPE_CHECK : {
           //Fill check type
           if(isset($json_in[HCE_DRCE_EXEC_FIELD_TYPE])){
             $ret[HCE_DRCE_EXEC_FIELD_TYPE]=$json_in[HCE_DRCE_EXEC_FIELD_TYPE];
           }else{
             $ret[HCE_DRCE_EXEC_FIELD_TYPE]=HCE_DRCE_REQUEST_TYPE_CHECK_SIMPLE;
           }
           break;
         }
         case HCE_DRCE_REQUEST_TYPE_TERMINATE : {
           //Fill terminate algorithm
           if(isset($json_in[HCE_DRCE_EXEC_FIELD_TERMINATE_ALG])){
             $ret[HCE_DRCE_EXEC_FIELD_TERMINATE_ALG]=$json_in[HCE_DRCE_EXEC_FIELD_TERMINATE_ALG];
           }else{
             $ret[HCE_DRCE_EXEC_FIELD_TERMINATE_ALG]=HCE_DRCE_EXEC_TERMINATE_ALG_SIMPLE;
           }
           //Fill terminate delay
           if(isset($json_in[HCE_DRCE_EXEC_FIELD_TERMINATE_DELAY])){
             $ret[HCE_DRCE_EXEC_FIELD_TERMINATE_DELAY]=$json_in[HCE_DRCE_EXEC_FIELD_TERMINATE_DELAY];
           }else{
             $ret[HCE_DRCE_EXEC_FIELD_TERMINATE_DELAY]=HCE_DRCE_EXEC_TERMINATE_DELAY_DEFAULT;
           }
           //Fill terminate repeat
           if(isset($json_in[HCE_DRCE_EXEC_FIELD_TERMINATE_REPEAT])){
             $ret[HCE_DRCE_EXEC_FIELD_TERMINATE_REPEAT]=$json_in[HCE_DRCE_EXEC_FIELD_TERMINATE_REPEAT];
           }else{
             $ret[HCE_DRCE_EXEC_FIELD_TERMINATE_REPEAT]=HCE_DRCE_EXEC_TERMINATE_REPEAT_DEFAULT;
           }
           //Fill terminate signal
           if(isset($json_in[HCE_DRCE_EXEC_FIELD_TERMINATE_SIGNAL])){
             $ret[HCE_DRCE_EXEC_FIELD_TERMINATE_SIGNAL]=$json_in[HCE_DRCE_EXEC_FIELD_TERMINATE_SIGNAL];
           }else{
             $ret[HCE_DRCE_EXEC_FIELD_TERMINATE_SIGNAL]=HCE_DRCE_EXEC_TERMINATE_SIGNAL_DEFAULT;
           }
           break;
         }
         case HCE_DRCE_REQUEST_TYPE_GET : {
           //Fill fetch type
           if(isset($json_in[HCE_DRCE_EXEC_FIELD_TYPE])){
             $ret[HCE_DRCE_EXEC_FIELD_TYPE]=$json_in[HCE_DRCE_EXEC_FIELD_TYPE];
           }else{
             $ret[HCE_DRCE_EXEC_FIELD_TYPE]=HCE_DRCE_REQUEST_TYPE_FETCH_DELETE;
           }
           break;
         }
				 case HCE_DRCE_REQUEST_TYPE_DELETE : {
				   //According to protocol not exist fields for filling					 
         }
				 break;
			 }
     }else{
       echo 'Parsing input json file error: '.json_last_error();
       exit(1);
     }
   }

   return $ret;
 }


/*
 * @desc create DRCE exec request in json format for DRCE Cluster ($protocol==0) or HCE Admin ($protocol==1) interfaces protocol
 * @param $parameters_array - array of items to construct json formatted exec request;
 * @param $type - request action type;
 * @param $id - request/task Id;
 * @param $ttl - request TTL;
 *
 * @return DRCE exec request string in json format if success or null in case of error
 */
 function hce_drce_exec_prepare_request($parameters_array, $type, $id, $ttl, $subtasks=array()){
   $ret=null;

   $drce_admin_protocol=hce_drce_exec_prepare_request_admin($parameters_array, $type, $id, $subtasks);

   if(SPHINX_JSON_USE_BASE64){
     $drce_admin_protocol=base64_encode($drce_admin_protocol);
   }

   $ret=json_encode(array(
                         HCE_HANDLER_COVER_FIELD_TYPE=>HCE_HANDLER_TYPE_DRCE,
                         HCE_HANDLER_COVER_FIELD_DATA=>$drce_admin_protocol,
                         HCE_HANDLER_COVER_FIELD_TTL=>$ttl
                         )
                   );

   return $ret;
 }

/*
 * @desc create DRCE request in json format for HCE Admin interface protocol
 * @param $parameters_array - array of items to construct json formatted exec request;
 * @param $type - request action type;
 * @param $id - request/task Id;
 *
 * @return DRCE exec request string in json format if success or null in case of error
 */
 function hce_drce_exec_prepare_request_admin($parameters_array, $type, $id, $subtasks=array()){
   $ret=null;

   $ret=json_encode(
                   array(
                        HCE_DRCE_REQUEST_TYPE_FIELD=>$type, 
                        HCE_DRCE_REQUEST_DATA_FIELD=>base64_encode(json_encode($parameters_array)),
                        HCE_DRCE_REQUEST_ID_FIELD=>$id,
                        HCE_DRCE_REQUEST_SUBTASKS_FIELD=>$subtasks
                        )
                   );
   return $ret;
 }


/*
 * @desc parse DRCE admin response in json format
 * @param $response_body - content of response json string
 *
 * @return ACN DRCE admin request response array
 */
 function hce_drce_exec_parse_response($response_body){
   return json_decode($response_body, true);
 }

/*
 * @desc parse DRCE request response in json format
 * @param $response_body - content of response json string
 *
 * @return ACN DRCE request request response array
 */
 function hce_drce_exec_parse_response_json($response_body){
   $ret=array('Error'=>'', 'Data'=>null);

   $tmp=json_decode($response_body, true);

   if(isset($tmp[HCE_DRCE_EXEC_FIELD_TYPE]) && $tmp[HCE_DRCE_EXEC_FIELD_TYPE]==HCE_HANDLER_TYPE_DRCE){
     if(isset($tmp[HCE_DRCE_EXEC_FIELD_DATA])){
       if(SPHINX_JSON_USE_BASE64){
         $ret['Data']=json_decode(base64_decode($tmp[HCE_DRCE_EXEC_FIELD_DATA]), true);
       }else{
         $ret['Data']=json_decode($tmp[HCE_DRCE_EXEC_FIELD_DATA], true);
       }
     }else{
       //Structure error
       $ret['Error']='Structure error: `data` field not found!';
     }
   }else{
     //Structure or type value error
     $ret['Error']='Structure error: `type` field not found or type is not a proper value!';
   }

   return $ret;
 }


/*
 * @desc parse DRCE subtasks file content in json format
 * @param $subtasks - content of subtasks file json string
 *
 * @return subtasks json array
 */
 function  hce_drce_create_subtasks_array($subtasks){
   //echo 'subtasks3:'.cli_prettyPrintJson($subtasks, '  ').PHP_EOL;

   $json_in=json_decode($subtasks, true);

   $ret=array();

   //Fill subtasks array
   if(is_array($json_in)){
     foreach($json_in as $subtask_item){
       //Chck 'data' field
       if(is_array($subtask_item) && isset($subtask_item[HCE_DRCE_EXEC_FIELD_DATA]) && is_string($subtask_item[HCE_DRCE_EXEC_FIELD_DATA])){
         if(strlen($subtask_item[HCE_DRCE_EXEC_FIELD_DATA])>15 && substr($subtask_item[HCE_DRCE_EXEC_FIELD_DATA], 0, 15)==HCE_DRCE_REQUEST_READ_FROM_FILE_STATEMENT){
           $file_name=substr($subtask_item[HCE_DRCE_EXEC_FIELD_DATA], 15);
           if(file_exists($file_name)){
             $subtask_data=file_get_contents($file_name);
           }else{
             $subtask_data='file not found "'.$file_name.'"';
           }
         }else{
           $subtask_data=$subtask_item[HCE_DRCE_EXEC_FIELD_DATA];
         }
         $subtask_item[HCE_DRCE_EXEC_FIELD_DATA]=base64_encode($subtask_data);
         $ret[]=$subtask_item;
       }elseif(is_array($subtask_item) && isset($subtask_item[HCE_DRCE_EXEC_FIELD_DATA]) && is_array($subtask_item[HCE_DRCE_EXEC_FIELD_DATA])){
         $subtask_data=json_encode($subtask_item[HCE_DRCE_EXEC_FIELD_DATA]);
         $subtask_item[HCE_DRCE_EXEC_FIELD_DATA]=base64_encode($subtask_data);
       }
       //Chck 'subtasks' field
       if(is_array($subtask_item) && isset($subtask_item[HCE_DRCE_REQUEST_SUBTASKS_FIELD]) && is_array($subtask_item[HCE_DRCE_REQUEST_SUBTASKS_FIELD])){
         $subtask_item[HCE_DRCE_REQUEST_SUBTASKS_FIELD]=hce_drce_create_subtasks_array(json_encode($subtask_item[HCE_DRCE_REQUEST_SUBTASKS_FIELD]));
       }
       $ret[]=$subtask_item;
     }
   }

   return $ret;
 }

?>
