<?php
/**
 * HCE project Sphinx search node admin handler API.
 * Samples of implementation of basic API for Sphinx search handler functional object of node application.
 *
 * @author bgv <bgv.hce@gmail.com>
 * @link http://hierarchical-cluster-engine.com/
 * @copyright Copyright &copy; 2013-2014 IOIX Ukraine
 * @license http://hierarchical-cluster-engine.com/license/
 * @package HCE project Sphinx search admin API
 * @since 0.1
 */

require_once 'hce_node_api.inc.php';

/**
 * Define and init Sphinx FO encode base64 usage, 0 - not used, 1 - used
 */
defined('SPHINX_JSON_USE_BASE64') or define('SPHINX_JSON_USE_BASE64', 0);
/**
 * Define and init Sphinx request type - admin.
 */
defined('HCE_SPHINX_CMD_TYPE_ADMIN') or define('HCE_SPHINX_CMD_TYPE_ADMIN', 2);
/**
 * Define and init Sphinx request timeout ms.
 */
defined('HCE_SPHINX_TIMEOUT') or define('HCE_SPHINX_TIMEOUT', 1500);
/**
 * Define and init Sphinx error codes.
 */
defined('HCE_SPHINX_ERROR_OK') or define('HCE_SPHINX_ERROR_OK', 0);
defined('HCE_SPHINX_ERROR_CREATE_MESSAGE') or define('HCE_SPHINX_ERROR_CREATE_MESSAGE', -100);
defined('HCE_SPHINX_ERROR_PARSE_RESPONSE') or define('HCE_SPHINX_ERROR_PARSE_RESPONSE', -101);
defined('HCE_SPHINX_ERROR_CREATE_CONNECTION') or define('HCE_SPHINX_ERROR_CREATE_CONNECTION', -102);
defined('HCE_SPHINX_ERROR_EMPTY_COMMAND') or define('HCE_SPHINX_ERROR_EMPTY_COMMAND', -103);
defined('HCE_SPHINX_ERROR_MESSAGE_NOT_FOUND') or define('HCE_SPHINX_ERROR_MESSAGE_NOT_FOUND', -104);
defined('HCE_SPHINX_ERROR_WRONG_PARAMETERS') or define('HCE_SPHINX_ERROR_WRONG_PARAMETERS', -105);

/**
 * Define and init Sphinx search admin command names.
 */
defined('HCE_SPHINX_CMD_INDEX_CREATE') or define('HCE_SPHINX_CMD_INDEX_CREATE', 'INDEX_CREATE');
defined('HCE_SPHINX_CMD_INDEX_CHECK') or define('HCE_SPHINX_CMD_INDEX_CHECK', 'INDEX_CHECK');
defined('HCE_SPHINX_CMD_INDEX_STORE_DATA_FILE') or define('HCE_SPHINX_CMD_INDEX_STORE_DATA_FILE', 'INDEX_STORE_DATA_FILE');
defined('HCE_SPHINX_CMD_INDEX_STORE_SCHEMA_FILE') or define('HCE_SPHINX_CMD_INDEX_STORE_SCHEMA_FILE', 'INDEX_STORE_SCHEMA_FILE');
defined('HCE_SPHINX_CMD_INDEX_REBUILD') or define('HCE_SPHINX_CMD_INDEX_REBUILD', 'INDEX_REBUILD');
defined('HCE_SPHINX_CMD_INDEX_SET_DATA_DIR') or define('HCE_SPHINX_CMD_INDEX_SET_DATA_DIR', 'INDEX_SET_DATA_DIR');
defined('HCE_SPHINX_CMD_INDEX_START') or define('HCE_SPHINX_CMD_INDEX_START', 'INDEX_START');
defined('HCE_SPHINX_CMD_INDEX_STOP') or define('HCE_SPHINX_CMD_INDEX_STOP', 'INDEX_STOP');
defined('HCE_SPHINX_CMD_INDEX_MERGE') or define('HCE_SPHINX_CMD_INDEX_MERGE', 'INDEX_MERGE');
defined('HCE_SPHINX_CMD_INDEX_DELETE_DATA_FILE') or define('HCE_SPHINX_CMD_INDEX_DELETE_DATA_FILE', 'INDEX_DELETE_DATA_FILE');
defined('HCE_SPHINX_CMD_INDEX_DELETE_SCHEMA_FILE') or define('HCE_SPHINX_CMD_INDEX_DELETE_SCHEMA_FILE', 'INDEX_DELETE_SCHEMA_FILE');
defined('HCE_SPHINX_CMD_INDEX_APPEND_DATA_FILE') or define('HCE_SPHINX_CMD_INDEX_APPEND_DATA_FILE', 'INDEX_APPEND_DATA_FILE');
defined('HCE_SPHINX_CMD_INDEX_DELETE_DOC') or define('HCE_SPHINX_CMD_INDEX_DELETE_DOC', 'INDEX_DELETE_DOC');
defined('HCE_SPHINX_CMD_INDEX_DELETE_DOC_NUMBER') or define('HCE_SPHINX_CMD_INDEX_DELETE_DOC_NUMBER', 'INDEX_DELETE_DOC_NUMBER');
defined('HCE_SPHINX_CMD_INDEX_PACK_DOC_DATA') or define('HCE_SPHINX_CMD_INDEX_PACK_DOC_DATA', 'INDEX_PACK_DOC_DATA');
defined('HCE_SPHINX_CMD_INDEX_REMOVE') or define('HCE_SPHINX_CMD_INDEX_REMOVE', 'INDEX_REMOVE');
defined('HCE_SPHINX_CMD_INDEX_COPY') or define('HCE_SPHINX_CMD_INDEX_COPY', 'INDEX_COPY');
defined('HCE_SPHINX_CMD_INDEX_RENAME') or define('HCE_SPHINX_CMD_INDEX_RENAME', 'INDEX_RENAME');
defined('HCE_SPHINX_CMD_INDEX_SET_CONFIG_VAR') or define('HCE_SPHINX_CMD_INDEX_SET_CONFIG_VAR', 'INDEX_SET_CONFIG_VAR');
defined('HCE_SPHINX_CMD_INDEX_MAX_DOC_ID') or define('HCE_SPHINX_CMD_INDEX_MAX_DOC_ID', 'INDEX_MAX_DOC_ID');
defined('HCE_SPHINX_CMD_INDEX_STATUS') or define('HCE_SPHINX_CMD_INDEX_STATUS', 'INDEX_STATUS');
defined('HCE_SPHINX_CMD_INDEX_STATUS_SEARCHD') or define('HCE_SPHINX_CMD_INDEX_STATUS_SEARCHD', 'INDEX_STATUS_SEARCHD');
defined('HCE_SPHINX_CMD_INDEX_DATA_LIST') or define('HCE_SPHINX_CMD_INDEX_DATA_LIST', 'INDEX_DATA_LIST');
defined('HCE_SPHINX_CMD_INDEX_CONNECT') or define('HCE_SPHINX_CMD_INDEX_CONNECT', 'INDEX_CONNECT');
defined('HCE_SPHINX_CMD_INDEX_DISCONNECT') or define('HCE_SPHINX_CMD_INDEX_DISCONNECT', 'INDEX_DISCONNECT');

/**
 * Define and init Sphinx search protocol json fields names
 */
defined('HCE_SPHINX_SEARCH_FIELD_Q') or define('HCE_SPHINX_SEARCH_FIELD_Q', 'q');
defined('HCE_SPHINX_SEARCH_FIELD_FILTERS') or define('HCE_SPHINX_SEARCH_FIELD_FILTERS', 'filters');
defined('HCE_SPHINX_SEARCH_FIELD_PARAMETERS') or define('HCE_SPHINX_SEARCH_FIELD_PARAMETERS', 'parameters');
defined('HCE_SPHINX_SEARCH_FIELD_QUERY_ID') or define('HCE_SPHINX_SEARCH_FIELD_QUERY_ID', 'queryId');
defined('HCE_SPHINX_SEARCH_FIELD_JSON_TYPE') or define('HCE_SPHINX_SEARCH_FIELD_JSON_TYPE', 'JsonType');
defined('HCE_SPHINX_SEARCH_FIELD_TYPE') or define('HCE_SPHINX_SEARCH_FIELD_TYPE', 'type');
defined('HCE_SPHINX_SEARCH_FIELD_DATA') or define('HCE_SPHINX_SEARCH_FIELD_DATA', 'data');
defined('HCE_SPHINX_SEARCH_FIELD_MAX_RESULTS') or define('HCE_SPHINX_SEARCH_FIELD_MAX_RESULTS', 'max_results');
defined('HCE_SPHINX_SEARCH_FIELD_SORT_MODE') or define('HCE_SPHINX_SEARCH_FIELD_SORT_MODE', 'sort_mode');
defined('HCE_SPHINX_SEARCH_FIELD_SORT_BY') or define('HCE_SPHINX_SEARCH_FIELD_SORT_BY', 'sort_by');
defined('HCE_SPHINX_SEARCH_FIELD_TYPE_MASK') or define('HCE_SPHINX_SEARCH_FIELD_TYPE_MASK', 'type_mask');
defined('HCE_SPHINX_SEARCH_FIELD_ID') or define('HCE_SPHINX_SEARCH_FIELD_ID', 'id');
defined('HCE_SPHINX_SEARCH_FIELD_ORDER') or define('HCE_SPHINX_SEARCH_FIELD_ORDER', 'order');
defined('HCE_SPHINX_SEARCH_FIELD_ORDER_ALG') or define('HCE_SPHINX_SEARCH_FIELD_ORDER_ALG', 'algorithm');
defined('HCE_SPHINX_SEARCH_FIELD_ORDER_ALG_0') or define('HCE_SPHINX_SEARCH_FIELD_ORDER_ALG_0', '0');
defined('HCE_SPHINX_SEARCH_FIELD_ORDER_FIELDS') or define('HCE_SPHINX_SEARCH_FIELD_ORDER_FIELDS', 'fields');
defined('HCE_SPHINX_SEARCH_FIELD_ORDER_BY') or define('HCE_SPHINX_SEARCH_FIELD_ORDER_BY', 'order_by');
defined('HCE_SPHINX_SEARCH_FIELD_ORDER_BY_ASC') or define('HCE_SPHINX_SEARCH_FIELD_ORDER_BY_ASC', '1');
defined('HCE_SPHINX_SEARCH_FIELD_ORDER_BY_DESC') or define('HCE_SPHINX_SEARCH_FIELD_ORDER_BY_DESC', '2');
defined('HCE_SPHINX_SEARCH_FIELD_OFFSET') or define('HCE_SPHINX_SEARCH_FIELD_OFFSET', 'offset');
defined('HCE_SPHINX_SEARCH_FIELD_LIMIT') or define('HCE_SPHINX_SEARCH_FIELD_LIMIT', 'limit');
defined('HCE_SPHINX_SEARCH_FIELD_CUTOFF') or define('HCE_SPHINX_SEARCH_FIELD_CUTOFF', 'cutoff');
defined('HCE_SPHINX_SEARCH_FIELD_RET_EXT_FIELDS') or define('HCE_SPHINX_SEARCH_FIELD_RET_EXT_FIELDS', 'return_jason_ext_fields');
defined('HCE_SPHINX_SEARCH_FIELD_FILTER_TYPE') or define('HCE_SPHINX_SEARCH_FIELD_FILTER_TYPE', 'type');
defined('HCE_SPHINX_SEARCH_FIELD_FILTER_ATTRIB') or define('HCE_SPHINX_SEARCH_FIELD_FILTER_ATTRIB', 'attribute');
defined('HCE_SPHINX_SEARCH_FIELD_FILTER_VALUES') or define('HCE_SPHINX_SEARCH_FIELD_FILTER_VALUES', 'values');
defined('HCE_SPHINX_SEARCH_FIELD_FILTER_EXCLUDE') or define('HCE_SPHINX_SEARCH_FIELD_FILTER_EXCLUDE', 'exclude');
for($i=0; $i<6; $i++){
  defined('HCE_SPHINX_SEARCH_FIELD_ORDER_BY_'.$i) or define('HCE_SPHINX_SEARCH_FIELD_ORDER_BY_'.$i, $i.'');
}
defined('HCE_SPHINX_SEARCH_FIELD_TTL') or define('HCE_SPHINX_SEARCH_FIELD_TTL', 'ttl');
defined('HCE_SPHINX_SEARCH_FIELD_TTL_DEFAULT') or define('HCE_SPHINX_SEARCH_FIELD_TTL_DEFAULT', '1000');
defined('HCE_SPHINX_SEARCH_FIELD_TIMEOUT') or define('HCE_SPHINX_SEARCH_FIELD_TIMEOUT', 'timeout');
defined('HCE_SPHINX_SEARCH_FIELD_TIMEOUT_DEFAULT') or define('HCE_SPHINX_SEARCH_FIELD_TIMEOUT_DEFAULT', '10000');
defined('HCE_SPHINX_SEARCH_FIELD_JSON_TYPE_DEFAULT') or define('HCE_SPHINX_SEARCH_FIELD_JSON_TYPE_DEFAULT', '15');
defined('HCE_SPHINX_SEARCH_FIELD_ERROR') or define('HCE_SPHINX_SEARCH_FIELD_ERROR', 'error');

/**
 * Define and init Sphinx Functional Object protocol consts for search
 */
defined('HCE_SPHINX_FO_SEARCH') or define('HCE_SPHINX_FO_SEARCH', '0');
defined('HCE_SPHINX_FO_INDEX') or define('HCE_SPHINX_FO_INDEX', '1');
defined('HCE_SPHINX_FO_ADMIN') or define('HCE_SPHINX_FO_ADMIN', '2');
defined('HCE_SPHINX_SEARCH_RET_TYPE_MI_INFO') or define('HCE_SPHINX_SEARCH_RET_TYPE_MI_INFO', 1);
defined('HCE_SPHINX_SEARCH_RET_TYPE_RI_INFO') or define('HCE_SPHINX_SEARCH_RET_TYPE_RI_INFO', 2);
defined('HCE_SPHINX_SEARCH_RET_TYPE_AT_INFO') or define('HCE_SPHINX_SEARCH_RET_TYPE_AT_INFO', 4);
defined('HCE_SPHINX_SEARCH_RET_TYPE_WI_INFO') or define('HCE_SPHINX_SEARCH_RET_TYPE_WI_INFO', 8);
defined('HCE_SPHINX_SEARCH_MAX_RESULTS_FROM_NODE_DEFAULT') or define('HCE_SPHINX_SEARCH_MAX_RESULTS_FROM_NODE_DEFAULT', '10');
defined('HCE_SPHINX_SEARCH_SORT_BY_DEFAULT') or define('HCE_SPHINX_SEARCH_SORT_BY_DEFAULT', '');
//Sort modes
defined('HCE_SPHINX_SEARCH_SORT_MODE_NONE') or define('HCE_SPHINX_SEARCH_SORT_MODE_NONE', '0');
defined('HCE_SPHINX_SEARCH_SORT_MODE_ASC') or define('HCE_SPHINX_SEARCH_SORT_MODE_ASC', '1');
defined('HCE_SPHINX_SEARCH_SORT_MODE_DESC') or define('HCE_SPHINX_SEARCH_SORT_MODE_DESC', '2');

/**
 * Define and init Sphinx Functional Object protocol consts for results json
 */
defined('HCE_SPHINX_SEARCH_RESULTS_MI') or define('HCE_SPHINX_SEARCH_RESULTS_MI', 'MI');
defined('HCE_SPHINX_SEARCH_RESULTS_AT') or define('HCE_SPHINX_SEARCH_RESULTS_AT', 'At');
defined('HCE_SPHINX_SEARCH_RESULTS_WI') or define('HCE_SPHINX_SEARCH_RESULTS_WI', 'WI');
defined('HCE_SPHINX_SEARCH_RESULTS_RI') or define('HCE_SPHINX_SEARCH_RESULTS_RI', 'RI');
defined('HCE_SPHINX_SEARCH_RESULTS_ID') or define('HCE_SPHINX_SEARCH_RESULTS_ID', 'Id');
defined('HCE_SPHINX_SEARCH_RESULTS_WEIGHT') or define('HCE_SPHINX_SEARCH_RESULTS_WEIGHT', 'W');
defined('HCE_SPHINX_SEARCH_RESULTS_SWEIGHT') or define('HCE_SPHINX_SEARCH_RESULTS_SWEIGHT', 'sw');

/*
 * @desc send Sphinx admin request message using zmq-based ACN API
 * @param $request_array - array with 'id' and 'request' items; id - is an unique request Id, if not set will be generated; 'request' - is a message string in json format with command content
 *        $connection_array - ACN connection array is null - new admin type will be created
 *
 * @return ACN Sphinx API result array; array(HCE_SPHINX_SEARCH_FIELD_ERROR=0, 'response', 'hce_connection_array'); If HCE_SPHINX_SEARCH_FIELD_ERROR item is zero - command executed successfully, 'response' item contains response json
 *         and error code in other cases: HCE_SPHINX_ERROR_EMPTY_COMMAND - The command json is empty or not set, HCE_SPHINX_ERROR_CREATE_CONNECTION - error connection create;
 *         HCE_SPHINX_ERROR_MESSAGE_NOT_FOUND - Response message not found by Id
 */
 function hce_sphinx_admin_request($request_array, $connection_array=null, $response_timeout=HCE_MSG_RESPONSE_TIMEOUT){
   //Init returned ACN Sphinx API result array
   $ret=array(HCE_SPHINX_SEARCH_FIELD_ERROR=>HCE_SPHINX_ERROR_OK, 'response'=>null, 'hce_connection_array'=>null);

   if(strlen($request_array['request'])>0){
     if($connection_array===null){
       //Create and init acn connection array from default
       $ret['hce_connection_array']=hce_connection_create(array('host'=>HCE_HOST_ADMIN_DEFAULT, 'port'=>HCE_PORT_ADMIN_DEFAULT, 'type'=>HCE_CONNECTION_TYPE_ADMIN, 
                                                                'identity'=>hce_unique_client_id()
                                                          ));
     }else{
       $ret['hce_connection_array']=$connection_array;
     }
     if(isset($ret['hce_connection_array'][HCE_SPHINX_SEARCH_FIELD_ERROR]) && $ret['hce_connection_array'][HCE_SPHINX_SEARCH_FIELD_ERROR]==HCE_PROTOCOL_ERROR_OK){
       //Make request id
       if(empty($request_array['id'])){
         $request_array['id']=hce_unique_message_id();
       }
       //Send message
       hce_message_send($ret['hce_connection_array'], array('id'=>$request_array['id'], 'body'=>$request_array['request']));

       //Receive response message(s)
       $hce_responses=hce_message_receive($ret['hce_connection_array'], $response_timeout);

       //Process message(s)
       if($hce_responses[HCE_SPHINX_SEARCH_FIELD_ERROR]==HCE_PROTOCOL_ERROR_OK){
         //Response message not found by Id
         $ret[HCE_SPHINX_SEARCH_FIELD_ERROR]=HCE_SPHINX_ERROR_MESSAGE_NOT_FOUND;
         foreach($hce_responses['messages'] as $hce_message){
           //Find proper response
           if($hce_message['id']==$request_array['id']){
              $ret['response']=$hce_message['body'];
              $ret[HCE_SPHINX_SEARCH_FIELD_ERROR]=HCE_SPHINX_ERROR_OK;
              break;
           }
         }
       }else{
         $ret[HCE_SPHINX_SEARCH_FIELD_ERROR]=$hce_responses[HCE_SPHINX_SEARCH_FIELD_ERROR];
       }
     }else{
       //Wrong connection or error create connection
       $ret[HCE_SPHINX_SEARCH_FIELD_ERROR]=HCE_SPHINX_ERROR_CREATE_CONNECTION;
     }
     if($connection_array===null){
       //Free ACN connection resources
       hce_connection_delete($ret['hce_connection_array']);
     }
   }else{
     //The command json is empty or not set
     $ret[HCE_SPHINX_SEARCH_FIELD_ERROR]=HCE_SPHINX_ERROR_EMPTY_COMMAND;
   }

   return $ret;
 }

/*
 * @desc create Sphinx admin request in json format
 * @param $command - command name; $parameters_array - array of items to construct json formatted admin request;
 *
 * @return ACN Sphinx admin request string in json format if success or null in case of error
 */
 function hce_sphinx_prepare_request($command, $parameters_array){
   //Encode for POCO json implementation compatibility reason
   return json_encode(array('command'=>$command, 'options'=>json_encode($parameters_array)));
 }

/*
 * @desc parse Sphinx admin response in json format
 * @param $response_body - content of response json string
 *
 * @return ACN Sphinx admin request response array
 */
 function hce_sphinx_parse_response($response_body){
   return json_decode($response_body, true);
 }

/*
 * @desc create Sphinx admin request message body in json format according with admin request type HCE_SPHINX_CMD_TYPE_ADMIN
 * @param $response_body - content of response json string
 *
 * @return ACN Sphinx admin request message
 */
 function hce_sphinx_admin_message_create($admin_request_body){
   return hce_admin_message_create(HCE_HANDLER_DATA_PROCESSOR_DATA, HCE_ADMIN_CMD_SPHINX, json_encode(array('type'=>HCE_SPHINX_CMD_TYPE_ADMIN, 'data'=>$admin_request_body)));
 }

/*
 * @desc execute Sphinx admin request
 * @param $command - command name corrsponded with command_string; $options_array - array of options corresponded with command_options_string; $timeout - response timeout
 *
 * @return array of Sphinx admin response if success or negative value if error; HCE_SPHINX_ERROR_CREATE_MESSAGE - error create message,
 *         HCE_SPHINX_ERROR_PARSE_RESPONSE - response parse error, or hce_sphinx_admin_request() call error
 */
 function hce_sphinx_exec($command, $options_array, $connection_array, $timeout){
   $ret=array();

   $message=hce_sphinx_admin_message_create(hce_sphinx_prepare_request($command, $options_array));
   if(empty($message)){
     //Error create message
     $ret=HCE_SPHINX_ERROR_CREATE_MESSAGE;
   }else{
     $response=hce_sphinx_admin_request(array('request'=>$message), $connection_array, $timeout);
     if($response[HCE_SPHINX_SEARCH_FIELD_ERROR]==HCE_SPHINX_ERROR_OK){
       $ret=hce_sphinx_parse_response($response['response']);
       if($ret===null || !is_array($ret)){
         //Response parse error
         $ret=HCE_SPHINX_ERROR_PARSE_RESPONSE;
       }
     }else{
       $ret=$response[HCE_SPHINX_SEARCH_FIELD_ERROR];
     }
   }

   return $ret;
 }


/*
 * @desc make Sphinx search request json message
 * @param $parameters_array - parameters array corresponds to the Sphinx FO protocol Functional_object_message_format.docx
 *                            array(HCE_SPHINX_SEARCH_FIELD_Q=>'query string',
 *                                  HCE_SPHINX_SEARCH_FIELD_PARAMETERS=>array(array(HCE_SPHINX_SEARCH_FIELD_QUERY_ID=>123), array(HCE_SPHINX_SEARCH_FIELD_JSON_TYPE=>15))
 *                                 )
 *
 * @return string json encoded message or negative value in case of error: HCE_SPHINX_ERROR_WRONG_PARAMETERS - wrong parameters array structure
 */
 function hce_sphinx_search_create_json($parameters_array){
   $ret=array(HCE_SPHINX_SEARCH_FIELD_TYPE=>HCE_SPHINX_FO_SEARCH, HCE_SPHINX_SEARCH_FIELD_DATA=>null);
   $ret1=array(HCE_SPHINX_SEARCH_FIELD_TYPE=>HCE_HANDLER_TYPE_SPHINX, HCE_SPHINX_SEARCH_FIELD_DATA=>null, HCE_SPHINX_SEARCH_FIELD_TTL=>HCE_SPHINX_SEARCH_FIELD_TTL_DEFAULT);

   if(!isset($parameters_array[HCE_SPHINX_SEARCH_FIELD_Q]) ||
      !isset($parameters_array[HCE_SPHINX_SEARCH_FIELD_FILTERS]) ||
      !isset($parameters_array[HCE_SPHINX_SEARCH_FIELD_PARAMETERS]) ||
      !isset($parameters_array[HCE_SPHINX_SEARCH_FIELD_PARAMETERS][0][HCE_SPHINX_SEARCH_FIELD_QUERY_ID]) ||
      !isset($parameters_array[HCE_SPHINX_SEARCH_FIELD_PARAMETERS][1][HCE_SPHINX_SEARCH_FIELD_JSON_TYPE])
     ){
      $ret=HCE_SPHINX_ERROR_WRONG_PARAMETERS;
   }else{
     if(SPHINX_JSON_USE_BASE64){
       $parameters_array[HCE_SPHINX_SEARCH_FIELD_Q]=base64_encode($parameters_array[HCE_SPHINX_SEARCH_FIELD_Q]);
       $parameters_array[HCE_SPHINX_SEARCH_FIELD_FILTERS]=base64_encode(json_encode($parameters_array[HCE_SPHINX_SEARCH_FIELD_FILTERS]));
     }else{
       $parameters_array[HCE_SPHINX_SEARCH_FIELD_Q]=$parameters_array[HCE_SPHINX_SEARCH_FIELD_Q];
       $parameters_array[HCE_SPHINX_SEARCH_FIELD_FILTERS]=json_encode($parameters_array[HCE_SPHINX_SEARCH_FIELD_FILTERS]);
     }
     $ret[HCE_SPHINX_SEARCH_FIELD_DATA]=json_encode($parameters_array);
   }
   if(SPHINX_JSON_USE_BASE64){
     $ret1[HCE_SPHINX_SEARCH_FIELD_DATA]=base64_encode(json_encode($ret));
   }else{
     $ret1[HCE_SPHINX_SEARCH_FIELD_DATA]=json_encode($ret);
   }
   $ret=$ret1;

   return json_encode($ret);
 }

/*
 * @desc make Sphinx search request json message
 * @param $query_string - search string in Sphinx query string format. It will be provided directly to Sphinx searchd to process
 *        $parameters   - array of parameters: 
 *                        id          - unique search query identifier, used to identify the query in the cluster. If not set or NULL - will be generated
 *                        type_mask   - mask to define the information that can be returned from Sphinx search in result. Defined as return_json_type_mask in
 *                                      Functional_object_message_format.docx.
 *                                      default value is HCE_SPHINX_SEARCH_RET_TYPE_ID_INFO|HCE_SPHINX_SEARCH_RET_TYPE_DOC_INFO|HCE_SPHINX_SEARCH_RET_TYPE_STAT_INFO
 *                        max_results - max results number to return
 *                        sort_mode   - sort mode, 0 - no sort, 1 - ASC, 2 - DESC
 *                        sort_by     - field name to use as sort criterion, "weight" - by default
 *
 * @return parameters array ready to be used in hce_sphinx_create_search_json() call or negative value in case of error: HCE_SPHINX_ERROR_WRONG_PARAMETERS - query string not set or empty
 */
 function hce_sphinx_search_prepare_parameters($query_string, $parameters=null, $order=null){
   $ret=array(HCE_SPHINX_SEARCH_FIELD_Q=>null,
              HCE_SPHINX_SEARCH_FIELD_FILTERS=>null,
              HCE_SPHINX_SEARCH_FIELD_PARAMETERS=>array(array(HCE_SPHINX_SEARCH_FIELD_QUERY_ID=>null),
                                                        array(HCE_SPHINX_SEARCH_FIELD_JSON_TYPE=>HCE_SPHINX_SEARCH_FIELD_JSON_TYPE_DEFAULT),
                                                        array(HCE_SPHINX_SEARCH_FIELD_SORT_BY=>HCE_SPHINX_SEARCH_SORT_BY_DEFAULT),
                                                        array(HCE_SPHINX_SEARCH_FIELD_ORDER_BY=>HCE_SPHINX_SEARCH_FIELD_ORDER_BY_0),
                                                        array(HCE_SPHINX_SEARCH_FIELD_OFFSET=>'0'),
                                                        array(HCE_SPHINX_SEARCH_FIELD_LIMIT=>'0'),
                                                        array(HCE_SPHINX_SEARCH_FIELD_CUTOFF=>'0'),
                                                        array(HCE_SPHINX_SEARCH_FIELD_RET_EXT_FIELDS=>array()),
                                                        array(HCE_SPHINX_SEARCH_FIELD_MAX_RESULTS=>HCE_SPHINX_SEARCH_MAX_RESULTS_FROM_NODE_DEFAULT),
                                                        array(HCE_SPHINX_SEARCH_FIELD_TIMEOUT=>HCE_SPHINX_SEARCH_FIELD_TIMEOUT_DEFAULT)
                                                       ),

              HCE_SPHINX_SEARCH_FIELD_ORDER=>array(array(HCE_SPHINX_SEARCH_FIELD_ORDER_ALG=>HCE_SPHINX_SEARCH_FIELD_ORDER_ALG_0), array(HCE_SPHINX_SEARCH_FIELD_ORDER_FIELDS=>array()))
             );

   //Parameters array is not set
   if($parameters===null){
     $parameters=array(HCE_SPHINX_SEARCH_FIELD_ID=>null, HCE_SPHINX_SEARCH_FIELD_TYPE_MASK=>null, HCE_SPHINX_SEARCH_FIELD_MAX_RESULTS=>HCE_SPHINX_SEARCH_MAX_RESULTS_FROM_NODE_DEFAULT,
                       HCE_SPHINX_SEARCH_FIELD_SORT_MODE=>HCE_SPHINX_SEARCH_SORT_MODE_ASC, HCE_SPHINX_SEARCH_FIELD_SORT_BY=>HCE_SPHINX_SEARCH_SORT_BY_DEFAULT);
   }
   //Default initialization
   if(!isset($parameters[HCE_SPHINX_SEARCH_FIELD_ID])){
     //Generate unique query ID
     $parameters[HCE_SPHINX_SEARCH_FIELD_ID]=sprintf('%u', crc32(hce_unique_message_id()));
   }
   if(!isset($parameters[HCE_SPHINX_SEARCH_FIELD_TYPE_MASK])){
     //Include only document's Id and weight info
     $parameters[HCE_SPHINX_SEARCH_FIELD_TYPE_MASK]=HCE_SPHINX_SEARCH_RET_TYPE_MI_INFO;
   }
   if(!isset($parameters[HCE_SPHINX_SEARCH_FIELD_SORT_MODE])){
     //Sort mode ASC
     $parameters[HCE_SPHINX_SEARCH_FIELD_SORT_MODE]=HCE_SPHINX_SEARCH_SORT_MODE_ASC;
   }
   if(!isset($parameters[HCE_SPHINX_SEARCH_FIELD_SORT_BY])){
     //Sort by "weight"
     $parameters[HCE_SPHINX_SEARCH_FIELD_SORT_BY]=HCE_SPHINX_SEARCH_SORT_BY_DEFAULT;
   }
   if(!isset($parameters[HCE_SPHINX_SEARCH_FIELD_OFFSET])){
     //Offset 0
     $parameters[HCE_SPHINX_SEARCH_FIELD_OFFSET]='0';
   }
   if(!isset($parameters[HCE_SPHINX_SEARCH_FIELD_LIMIT])){
     //Resources to erturn 10
     $parameters[HCE_SPHINX_SEARCH_FIELD_LIMIT]='0';
   }
   if(!isset($parameters[HCE_SPHINX_SEARCH_FIELD_CUTOFF])){
     //Sphinx specification
     $parameters[HCE_SPHINX_SEARCH_FIELD_CUTOFF]='0';
   }
   if(!isset($parameters[HCE_SPHINX_SEARCH_FIELD_RET_EXT_FIELDS])){
     //Empty list of fields lead that all defined in schema fields returned
     $parameters[HCE_SPHINX_SEARCH_FIELD_RET_EXT_FIELDS]=array();
   }
   if(!isset($parameters[HCE_SPHINX_SEARCH_FIELD_FILTERS])){
     //Empty filters array
     $parameters[HCE_SPHINX_SEARCH_FIELD_FILTERS]=array();
   }
   if(!isset($parameters[HCE_SPHINX_SEARCH_FIELD_ORDER_BY])){
     //Empty sort order by for Sphinx
     $parameters[HCE_SPHINX_SEARCH_FIELD_ORDER_BY]=HCE_SPHINX_SEARCH_FIELD_ORDER_BY_0;
   }
/*
   if(!isset($parameters[HCE_SPHINX_SEARCH_FIELD_TTL])){
     //Empty ttl
     $parameters[HCE_SPHINX_SEARCH_FIELD_TTL]=HCE_SPHINX_SEARCH_FIELD_TTL_DEFAULT;
   }
*/
   if(!isset($parameters[HCE_SPHINX_SEARCH_FIELD_TIMEOUT])){
     //Empty timeout
     $parameters[HCE_SPHINX_SEARCH_FIELD_TIMEOUT]=HCE_SPHINX_SEARCH_FIELD_TIMEOUT_DEFAULT;
   }

   //Order array is not set
   if($order===null){
     $order=array(array(HCE_SPHINX_SEARCH_FIELD_ORDER_ALG=>HCE_SPHINX_SEARCH_FIELD_ORDER_ALG_0),
                  array(HCE_SPHINX_SEARCH_FIELD_ORDER_FIELDS=>array()),
                  array(HCE_SPHINX_SEARCH_FIELD_ORDER_BY=>HCE_SPHINX_SEARCH_FIELD_ORDER_BY_DESC));
   }

   //Set main fields
   $ret[HCE_SPHINX_SEARCH_FIELD_Q]=$query_string;
   $ret[HCE_SPHINX_SEARCH_FIELD_FILTERS]=$parameters[HCE_SPHINX_SEARCH_FIELD_FILTERS];

   //Set parameters
   $ret[HCE_SPHINX_SEARCH_FIELD_PARAMETERS][0][HCE_SPHINX_SEARCH_FIELD_QUERY_ID]=$parameters[HCE_SPHINX_SEARCH_FIELD_ID];
   $ret[HCE_SPHINX_SEARCH_FIELD_PARAMETERS][1][HCE_SPHINX_SEARCH_FIELD_JSON_TYPE]=$parameters[HCE_SPHINX_SEARCH_FIELD_TYPE_MASK];
   $ret[HCE_SPHINX_SEARCH_FIELD_PARAMETERS][2][HCE_SPHINX_SEARCH_FIELD_SORT_BY]=$parameters[HCE_SPHINX_SEARCH_FIELD_SORT_BY];
   $ret[HCE_SPHINX_SEARCH_FIELD_PARAMETERS][3][HCE_SPHINX_SEARCH_FIELD_ORDER_BY]=$parameters[HCE_SPHINX_SEARCH_FIELD_ORDER_BY];
   $ret[HCE_SPHINX_SEARCH_FIELD_PARAMETERS][4][HCE_SPHINX_SEARCH_FIELD_OFFSET]=$parameters[HCE_SPHINX_SEARCH_FIELD_OFFSET];
   $ret[HCE_SPHINX_SEARCH_FIELD_PARAMETERS][5][HCE_SPHINX_SEARCH_FIELD_LIMIT]=$parameters[HCE_SPHINX_SEARCH_FIELD_LIMIT];
   $ret[HCE_SPHINX_SEARCH_FIELD_PARAMETERS][6][HCE_SPHINX_SEARCH_FIELD_CUTOFF]=$parameters[HCE_SPHINX_SEARCH_FIELD_CUTOFF];
   $ret[HCE_SPHINX_SEARCH_FIELD_PARAMETERS][7][HCE_SPHINX_SEARCH_FIELD_RET_EXT_FIELDS]=$parameters[HCE_SPHINX_SEARCH_FIELD_RET_EXT_FIELDS];
   $ret[HCE_SPHINX_SEARCH_FIELD_PARAMETERS][8][HCE_SPHINX_SEARCH_FIELD_MAX_RESULTS]=$parameters[HCE_SPHINX_SEARCH_FIELD_MAX_RESULTS];
//   $ret[HCE_SPHINX_SEARCH_FIELD_PARAMETERS][9][HCE_SPHINX_SEARCH_FIELD_TTL]=$parameters[HCE_SPHINX_SEARCH_FIELD_TTL];
   $ret[HCE_SPHINX_SEARCH_FIELD_PARAMETERS][9][HCE_SPHINX_SEARCH_FIELD_TIMEOUT]=$parameters[HCE_SPHINX_SEARCH_FIELD_TIMEOUT];

   //Set order
   $ret[HCE_SPHINX_SEARCH_FIELD_ORDER]=$order;

   return $ret;
 }


/*
 * @desc parse Sphinx search response in json format
 * @param $response_body - content of response message json string
 *
 * @return ACN Sphinx search response array
 *         error codes: 1 - Error of message type, is not Sphinx or general json parsing error, 2 - Error of message structure, no HCE_SPHINX_SEARCH_FIELD_DATA field
 */
 function hce_sphinx_search_parse_json($response_body){
   $ret=array(HCE_SPHINX_SEARCH_FIELD_ERROR=>0, HCE_SPHINX_SEARCH_FIELD_DATA=>null, HCE_SPHINX_SEARCH_FIELD_TYPE=>0, HCE_SPHINX_SEARCH_FIELD_TTL=>0);

   $tmp=@json_decode($response_body, true);

   //Set type
   if(isset($tmp[HCE_SPHINX_SEARCH_FIELD_TYPE])){
     $ret[HCE_SPHINX_SEARCH_FIELD_TYPE]=$tmp[HCE_SPHINX_SEARCH_FIELD_TYPE];
   }

   //Set ttl
   if(isset($tmp[HCE_SPHINX_SEARCH_FIELD_TTL])){
     $ret[HCE_SPHINX_SEARCH_FIELD_TTL]=$tmp[HCE_SPHINX_SEARCH_FIELD_TTL];
   }

   //Set data
   if(isset($tmp[HCE_SPHINX_SEARCH_FIELD_TYPE]) && $tmp[HCE_SPHINX_SEARCH_FIELD_TYPE]==HCE_HANDLER_TYPE_SPHINX){
     if(isset($tmp[HCE_SPHINX_SEARCH_FIELD_DATA])){
       if(SPHINX_JSON_USE_BASE64){
         $ret[HCE_SPHINX_SEARCH_FIELD_DATA]=json_decode(base64_decode($tmp[HCE_SPHINX_SEARCH_FIELD_DATA]), true);
       }else{
         $ret[HCE_SPHINX_SEARCH_FIELD_DATA]=json_decode($tmp[HCE_SPHINX_SEARCH_FIELD_DATA], true);
       }
     }else{
       //Error of message structure, no data field
       $ret[HCE_SPHINX_SEARCH_FIELD_ERROR]=2;
     }
   }else{
     //Error of message type, is not Sphinx or general json parsing error
     $ret[HCE_SPHINX_SEARCH_FIELD_ERROR]=1;
   }

   return $ret;
 }

/*
 * @desc get data field value from Sphinx search result object
 * @param $response_body - content of response message json string
 *
 * @return ACN Sphinx search response array
 *         error codes: 1 - Error of message type, is not Sphinx or general json parsing error, 2 - Error of message structure, no HCE_SPHINX_SEARCH_FIELD_DATA field
 */
 function hce_sphinx_search_result_get($result, $struct_name, $field_name=null, $index=null){
   $ret=0;

   if(isset($result[HCE_SPHINX_SEARCH_FIELD_DATA])){
     if($struct_name==HCE_SPHINX_SEARCH_RESULTS_MI && isset($result[HCE_SPHINX_SEARCH_FIELD_DATA][HCE_SPHINX_SEARCH_RESULTS_MI])){
       //Match info data
       if($index!==null){
         $mi=$result[HCE_SPHINX_SEARCH_FIELD_DATA][HCE_SPHINX_SEARCH_RESULTS_MI];
         if(isset($mi[$index])){
           if($field_name==HCE_SPHINX_SEARCH_RESULTS_WEIGHT || $field_name==HCE_SPHINX_SEARCH_RESULTS_ID){
             $ret=$mi[$index][$field_name];
           }else{
             foreach($mi[$index][HCE_SPHINX_SEARCH_RESULTS_AT] as $attribute){
               if(isset($attribute[$field_name])){
                 $ret=$attribute[$field_name];
                 break;
               }
             }
           }
         }
       }else{
         $ret=count($result[HCE_SPHINX_SEARCH_FIELD_DATA][HCE_SPHINX_SEARCH_RESULTS_MI]);
       }
     }elseif($struct_name==HCE_SPHINX_SEARCH_RESULTS_RI && isset($result[HCE_SPHINX_SEARCH_FIELD_DATA][HCE_SPHINX_SEARCH_RESULTS_RI])){
       if($index!==null && isset($result[HCE_SPHINX_SEARCH_FIELD_DATA][HCE_SPHINX_SEARCH_RESULTS_RI][$index][$field_name])){
         $ret=$result[HCE_SPHINX_SEARCH_FIELD_DATA][HCE_SPHINX_SEARCH_RESULTS_RI][$index][$field_name];
       }else{
         $ret=count($result[HCE_SPHINX_SEARCH_FIELD_DATA][HCE_SPHINX_SEARCH_RESULTS_RI]);
       }
     }elseif($struct_name==HCE_SPHINX_SEARCH_RESULTS_WI && $index!==null && isset($result[HCE_SPHINX_SEARCH_FIELD_DATA][HCE_SPHINX_SEARCH_RESULTS_RI][$index][HCE_SPHINX_SEARCH_RESULTS_WI])){
       $ret=$result[HCE_SPHINX_SEARCH_FIELD_DATA][HCE_SPHINX_SEARCH_RESULTS_RI][$index][HCE_SPHINX_SEARCH_RESULTS_WI];
     }
   }

   return $ret;
 }

?>