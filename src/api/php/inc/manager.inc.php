<?php
/**
 * HCE project node manager library.
 * Samples of implementation of basic API library for manager of node application.
 *
 * @author bgv <bgv.hce@gmail.com>
 * @link http://hierarchical-cluster-engine.com/
 * @copyright Copyright &copy; 2013 IOIX Ukraine
 * @license http://hierarchical-cluster-engine.com/license/
 * @package HCE project node API
 * @since 0.1
 */

require_once 'hce_cli_api.inc.php';
require_once 'hce_sphinx_api.inc.php';

/**
 * Define and init cluster node admin request default timeout ms.
 */
defined('HCE_CLUSTER_CMD_TIMEOUT') or define('HCE_CLUSTER_CMD_TIMEOUT', 100);
/**
 * Define synthetic cluster commands names. Synthetic commands defined and executed inside ACN manager implementation
 */
defined('HCE_CLUSTER_CMD_STRUCTURE_CHECK') or define('HCE_CLUSTER_CMD_STRUCTURE_CHECK', 'STRUCTURE_CHECK');
defined('HCE_CLUSTER_CMD_NODE_SHUTDOWN') or define('HCE_CLUSTER_CMD_NODE_SHUTDOWN', 'NODE_SHUTDOWN');
defined('HCE_CLUSTER_CMD_NODE_PROPERTIES') or define('HCE_CLUSTER_CMD_NODE_PROPERTIES', 'NODE_PROPERTIES');
defined('HCE_CLUSTER_CMD_NODE_RESET_STAT_COUNTERS') or define('HCE_CLUSTER_CMD_NODE_RESET_STAT_COUNTERS', 'NODE_RESET_STAT_COUNTERS');
defined('HCE_CLUSTER_CMD_NODE_RESOURCE_USAGE') or define('HCE_CLUSTER_CMD_NODE_RESOURCE_USAGE', 'NODE_RESOURCE_USAGE');

defined('HCE_CLUSTER_CMD_NODE_ECHO') or define('HCE_CLUSTER_CMD_NODE_ECHO', 'NODE_ECHO');
defined('HCE_CLUSTER_CMD_NODE_TIME') or define('HCE_CLUSTER_CMD_NODE_TIME', 'NODE_TIME');
defined('HCE_CLUSTER_CMD_NODE_LLSET') or define('HCE_CLUSTER_CMD_NODE_LLSET', 'NODE_LLSET');
defined('HCE_CLUSTER_CMD_NODE_LLGET') or define('HCE_CLUSTER_CMD_NODE_LLGET', 'NODE_LLGET');
defined('HCE_CLUSTER_CMD_NODE_HB_DELAY_SET') or define('HCE_CLUSTER_CMD_NODE_HB_DELAY_SET', 'NODE_HB_DELAY_SET');
defined('HCE_CLUSTER_CMD_NODE_HB_DELAY_GET') or define('HCE_CLUSTER_CMD_NODE_HB_DELAY_GET', 'NODE_HB_DELAY_GET');
defined('HCE_CLUSTER_CMD_NODE_HB_TIMEOUT_SET') or define('HCE_CLUSTER_CMD_NODE_HB_TIMEOUT_SET', 'NODE_HB_TIMEOUT_SET');
defined('HCE_CLUSTER_CMD_NODE_HB_TIMEOUT_GET') or define('HCE_CLUSTER_CMD_NODE_HB_TIMEOUT_GET', 'NODE_HB_TIMEOUT_GET');
defined('HCE_CLUSTER_CMD_NODE_HB_MODE_SET') or define('HCE_CLUSTER_CMD_NODE_HB_MODE_SET', 'NODE_HB_MODE_SET');
defined('HCE_CLUSTER_CMD_NODE_HB_MODE_GET') or define('HCE_CLUSTER_CMD_NODE_HB_MODE_GET', 'NODE_HB_MODE_GET');
defined('HCE_CLUSTER_CMD_NODE_POLL_TIMEOUT_SET') or define('HCE_CLUSTER_CMD_NODE_POLL_TIMEOUT_SET', 'NODE_POLL_TIMEOUT_SET');
defined('HCE_CLUSTER_CMD_NODE_POLL_TIMEOUT_GET') or define('HCE_CLUSTER_CMD_NODE_POLL_TIMEOUT_GET', 'NODE_POLL_TIMEOUT_GET');
defined('HCE_CLUSTER_CMD_NODE_PROPERTY_INTERVAL_SET') or define('HCE_CLUSTER_CMD_NODE_PROPERTY_INTERVAL_SET', 'NODE_PROPERTY_INTERVAL_SET');
defined('HCE_CLUSTER_CMD_NODE_PROPERTY_INTERVAL_GET') or define('HCE_CLUSTER_CMD_NODE_PROPERTY_INTERVAL_GET', 'NODE_PROPERTY_INTERVAL_GET');
defined('HCE_CLUSTER_CMD_NODE_DUMP_INTERVAL_SET') or define('HCE_CLUSTER_CMD_NODE_DUMP_INTERVAL_SET', 'NODE_DUMP_INTERVAL_SET');
defined('HCE_CLUSTER_CMD_NODE_DUMP_INTERVAL_GET') or define('HCE_CLUSTER_CMD_NODE_DUMP_INTERVAL_GET', 'NODE_DUMP_INTERVAL_GET');
defined('HCE_CLUSTER_CMD_NODE_MMSET') or define('HCE_CLUSTER_CMD_NODE_MMSET', 'NODE_MMSET');
defined('HCE_CLUSTER_CMD_NODE_MMGET') or define('HCE_CLUSTER_CMD_NODE_MMGET', 'NODE_MMGET');
defined('HCE_CLUSTER_CMD_NODE_MPMSET') or define('HCE_CLUSTER_CMD_NODE_MPMSET', 'NODE_MPMSET');
defined('HCE_CLUSTER_CMD_NODE_MPMGET') or define('HCE_CLUSTER_CMD_NODE_MPMGET', 'NODE_MPMGET');
defined('HCE_CLUSTER_CMD_NODE_MRCSSET') or define('HCE_CLUSTER_CMD_NODE_MRCSSET', 'NODE_MRCSSET');
defined('HCE_CLUSTER_CMD_NODE_MRCSGET') or define('HCE_CLUSTER_CMD_NODE_MRCSGET', 'NODE_MRCSGET');
defined('HCE_CLUSTER_CMD_NODE_SPHINX') or define('HCE_CLUSTER_CMD_NODE_SPHINX', 'SPHINX');
defined('HCE_CLUSTER_CMD_NODE_DRCE') or define('HCE_CLUSTER_CMD_NODE_DRCE', 'DRCE');

/**
 * Define cluster node admin command properties names
 */
defined('HCE_CLUSTER_CMD_PROPERTY_NAME_LOG') or define('HCE_CLUSTER_CMD_PROPERTY_NAME_LOG', 'log');

/**
 * Define cluster node role names used as management alises in json schema structure definition files
 */
defined('HCE_CLUSTER_SCHEMA_ROLE_ROUTER') or define('HCE_CLUSTER_SCHEMA_ROLE_ROUTER', 'router');
defined('HCE_CLUSTER_SCHEMA_ROLE_SMANAGER') or define('HCE_CLUSTER_SCHEMA_ROLE_SMANAGER', 'smanager');
defined('HCE_CLUSTER_SCHEMA_ROLE_RMANAGER') or define('HCE_CLUSTER_SCHEMA_ROLE_RMANAGER', 'rmanager');
defined('HCE_CLUSTER_SCHEMA_ROLE_RMANAGER_RR') or define('HCE_CLUSTER_SCHEMA_ROLE_RMANAGER_RR', 'rmanager-round-robin');
defined('HCE_CLUSTER_SCHEMA_ROLE_RMANAGER_RND') or define('HCE_CLUSTER_SCHEMA_ROLE_RMANAGER_RND', 'rmanager-rnd');
defined('HCE_CLUSTER_SCHEMA_ROLE_RMANAGER_RU') or define('HCE_CLUSTER_SCHEMA_ROLE_RMANAGER_RU', 'rmanager-resources-usage');
defined('HCE_CLUSTER_SCHEMA_ROLE_REPLICA') or define('HCE_CLUSTER_SCHEMA_ROLE_REPLICA', 'replica');

/**
 * Define cluster node role code
 */
defined('HCE_CLUSTER_SCHEMA_ROLE_CODE_ROUTER') or define('HCE_CLUSTER_SCHEMA_ROLE_CODE_ROUTER', 3);
defined('HCE_CLUSTER_SCHEMA_ROLE_CODE_SMANAGER') or define('HCE_CLUSTER_SCHEMA_ROLE_CODE_SMANAGER', 0);
defined('HCE_CLUSTER_SCHEMA_ROLE_CODE_RMANAGER') or define('HCE_CLUSTER_SCHEMA_ROLE_CODE_RMANAGER', 1);
defined('HCE_CLUSTER_SCHEMA_ROLE_CODE_REPLICA') or define('HCE_CLUSTER_SCHEMA_ROLE_CODE_REPLICA', 2);
defined('HCE_CLUSTER_SCHEMA_ROLE_CODE_RMANAGER_RND') or define('HCE_CLUSTER_SCHEMA_ROLE_CODE_RMANAGER_RND', 4);
defined('HCE_CLUSTER_SCHEMA_ROLE_CODE_RMANAGER_RU') or define('HCE_CLUSTER_SCHEMA_ROLE_CODE_RMANAGER_RU', 5);

/**
 * Define cluster node role detection errors
 */
defined('HCE_CLUSTER_SCHEMA_ERROR_WRONG_DATA') or define('HCE_CLUSTER_SCHEMA_ERROR_WRONG_DATA', 'wrong data or network error');

/**
 * Define cluster node ports list
 */
defined('HCE_CLUSTER_SCHEMA_PORTS_DEFAULT') or define('HCE_CLUSTER_SCHEMA_PORTS_DEFAULT', '5540,5541,5542,5543,5544,5545,5546,5547,5548,5549,5550,5551,5552,5553,5554,5555,5556,5557,5558,5559');

/**
 * Define and init cluster node admin request default date format for responses.
 */
defined('HCE_CLUSTER_CMD_DATE_FORMAT') or define('HCE_CLUSTER_CMD_DATE_FORMAT', 'Y-m-d H:i:s');
defined('HCE_CLUSTER_CMD_TIME_FORMAT') or define('HCE_CLUSTER_CMD_TIME_FORMAT', 'H:i:s');

/**
 * Define and init cluster node admin PROPERTIES request fields names.
 */
defined('HCE_CLUSTER_CMD_PROPERTIES_FIELD_TIME') or define('HCE_CLUSTER_CMD_PROPERTIES_FIELD_TIME', 'startedAt');
defined('HCE_CLUSTER_CMD_PROPERTIES_FIELD_NAME') or define('HCE_CLUSTER_CMD_PROPERTIES_FIELD_NAME', 'name');
defined('HCE_CLUSTER_CMD_PROPERTIES_FIELD_CIDENTITY') or define('HCE_CLUSTER_CMD_PROPERTIES_FIELD_CIDENTITY', 'clientIdentity');
defined('HCE_CLUSTER_CMD_PROPERTIES_FIELD_CSTRING') or define('HCE_CLUSTER_CMD_PROPERTIES_FIELD_CSTRING', 'connectionString');
defined('HCE_CLUSTER_CMD_PROPERTIES_FIELD_NODEMODE') or define('HCE_CLUSTER_CMD_PROPERTIES_FIELD_NODEMODE', 'nodeMode');

/*
 * @desc return help textual conext
 * @param $node Ip address or domain name
 *
 * @return node info array
 */
function hce_manage_get_help(){
  $ret='Usage: manager.php --command=<command> [--host=<host>] [--port=<port>] [--<option_name>=<option_value>,...] [--timeout=<timeout_ms>]'.
       ' [--log=<log_level_mask{0 - warnings, 1 - errors, 2 - debug}>] [--scan=<host_port_recombination{0 - for each host scan all listed ports, 1 - treate host and ports as pairs}>]'.
       ' [--ignore=<ignore_errors_mode{0 - not ignore, 1 - ignore not critical, 2 - ignore all}>] [-sphinx_properties_formatted] [--view={"json", "chart"}]'.PHP_EOL.PHP_EOL.
       'Cluster and node level commands:'.PHP_EOL.
       ' STRUCTURE_CHECK [--view={"json", "chart"}] [--fields={rhasc}] - detect and check cluster structure, return schema in json (default) or ASCII chart view'.PHP_EOL.
       '                 fields: r - role, h - host, a - admin, s - server, c - client connections'.PHP_EOL.
       ' NODE_SHUTDOWN - shutdown node'.PHP_EOL.
       ' NODE_ECHO - simple ping node with echo'.PHP_EOL.
       ' NODE_TIME - returns json with time of live of node, msec'.PHP_EOL.
       ' NODE_PROPERTIES --handler=<handler_names_csv>, --realtime=<parameters_json> - returns json with node properties of all handlers, for sample: {"parameters":"", "realtime":0}'.PHP_EOL.
       ' NODE_LLSET --handler=<handler_names_csv>, --level=<log_levels_value_csv> - set log level(s) for handler(s)'.PHP_EOL.
       ' NODE_LLGET --handler=<handler_names_csv> - returns json with log level(s) for handler(s)'.PHP_EOL.
       ' NODE_HB_DELAY_SET --handler=<handler_names_csv>, --hddelay=<heartbeat_delay> - set heartbeat delay value for handler(s)'.PHP_EOL.
       ' NODE_HB_DELAY_GET --handler=<handler_names_csv> - returns json with heartbeat delay values of handler(s)'.PHP_EOL.
       ' NODE_HB_TIMEOUT_SET --handler=<handler_names_csv>, --hbtimeout=<heartbeat_timeout> - set heartbeat timeout value for handler(s)'.PHP_EOL.
       ' NODE_HB_TIMEOUT_GET --handler=<handler_names_csv> - returns json with heartbeat timeout values of handler(s)'.PHP_EOL.       
       ' NODE_HB_MODE_SET --handler=<handler_names_csv>, --hbmode=<heartbeat_mode> - set heartbeat mode value for handler(s)'.PHP_EOL.
       ' NODE_HB_MODE_GET --handler=<handler_names_csv> - returns json with heartbeat mode values of handler(s)'.PHP_EOL.
       ' NODE_POLL_TIMEOUT_SET --handler=<handler_names_csv>, --ptimeout=<poll_timeout> - set poll timeout value for handler(s)'.PHP_EOL.
       ' NODE_POLL_TIMEOUT_GET --handler=<handler_names_csv> - returns json with poll timeout values of handler(s)'.PHP_EOL.    
       ' NODE_PROPERTY_INTERVAL_SET --handler=<handler_names_csv>, --interval=<property_interval> - set property interval value for handler(s)'.PHP_EOL.
       ' NODE_PROPERTY_INTERVAL_GET --handler=<handler_names_csv> - returns json with property interval values of handler(s)'.PHP_EOL.      
       ' NODE_DUMP_INTERVAL_SET --handler=<handler_names_csv>, --interval=<dump_interval> - set dump interval value for handler(s)'.PHP_EOL.
       ' NODE_DUMP_INTERVAL_GET --handler=<handler_names_csv> - returns json with dump interval values of handler(s)'.PHP_EOL.      
       ' NODE_MMSET --mode=<manager_mode_name{"smanager", "rmanager"}> - set manager mode'.PHP_EOL.
       ' NODE_MMGET - get manager mode'.PHP_EOL.
       ' NODE_MPMSET --purge=<purge_mode> - set purge mode'.PHP_EOL.
       ' NODE_MPMGET - get purge mode'.PHP_EOL.      
       ' NODE_MRCSSET --csize=<collected_size> - set resources usage collected size'.PHP_EOL.
       ' NODE_MRCSGET - get resources usage collected size'.PHP_EOL.
       ' NODE_RECOVER_NOTIFICATION_CONNECTION - recover notification connection'.PHP_EOL.
       ' NODE_ROUTES - get HCE-node routes list'.PHP_EOL.
       ' NODE_RESOURCE_USAGE - get HCE-node resources usage list'.PHP_EOL.  
       ' NODE_RESET_STAT_COUNTERS - reset stat counters and returns json with node properties of all handlers'.PHP_EOL.
       'Sphinx search level commands:'.PHP_EOL.
       ' INDEX_REMOVE'.PHP_EOL.
       ' INDEX_DELETE_DOC_NUMBER'.PHP_EOL.
       ' INDEX_CHECK'.PHP_EOL.
       ' INDEX_START'.PHP_EOL.
       ' INDEX_STOP'.PHP_EOL.
       ' INDEX_CREATE'.PHP_EOL.
       ' INDEX_APPEND_DATA_FILE'.PHP_EOL.
       ' INDEX_STORE_DATA_FILE'.PHP_EOL.
       ' INDEX_STORE_SCHEMA_FILE'.PHP_EOL.
       ' INDEX_PACK_DOC_DATA'.PHP_EOL.
       ' INDEX_MERGE'.PHP_EOL.
       ' INDEX_DELETE_DATA_FILE'.PHP_EOL.
       ' INDEX_REBUILD'.PHP_EOL.
       ' INDEX_DELETE_SCHEMA_FILE'.PHP_EOL.
       ' INDEX_DELETE_DOC'.PHP_EOL.
       ' INDEX_RENAME'.PHP_EOL.
       ' INDEX_COPY'.PHP_EOL.
       ' INDEX_SET_CONFIG_VAR'.PHP_EOL.
       ' INDEX_CONNECT'.PHP_EOL.
       ' INDEX_DISCONNECT'.PHP_EOL.
       'DRCE level commands:'.PHP_EOL.
       ' DRCE --request=request_type{SET, CHECK, TERMINATE, GET, DELETE} --id=<task_id> --json=<json_protocol_file>'.PHP_EOL.
       ' DRCE_SET_HOST - set DRCE host value'.PHP_EOL.
       ' DRCE_GET_HOST - get DRCE host value'.PHP_EOL.
       ' DRCE_SET_PORT - set DRCE connection port value'.PHP_EOL.
       ' DRCE_GET_PORT - get DRCE connection port value'.PHP_EOL.
       ' DRCE_GET_TASKS - get DRCE tasks list'.PHP_EOL.
	     ' DRCE_GET_TASKS_INFO - get DRCE tasks list info'.PHP_EOL.
       PHP_EOL;

 return $ret;
}


/*
 * @desc make admin request for node and return stat info
 * @param $node Ip address or domain name
 *
 * @return node info array
 */
function hce_manage_node_get_handler_properties($response_str, $delimiter=HCE_ADMIN_CMD_DELIMITER, $time_format=null){
 $timestampedProperties=array('startedAt', 'pstatsAt', 'heartbeatAt', 'heartbeatedAt');

 $ret=array();

 $properties=explode($delimiter, $response_str);
 if(isset($properties[0]) && $properties[0]==HCE_ADMIN_NODE_ADMIN_ERROR_OK){
   foreach($properties as $property){
     $property=explode('=', $property);
     if(count($property)>1){
       if($time_format!==null && in_array($property[0], $timestampedProperties)){
         $ret[$property[0]]=date($time_format, ceil($property[1]/1000));
       }else{
         $ret[$property[0]]=$property[1];
       }
     }
   }
 }else{
   $ret=false;
 }

 return $ret;
}


/*
 * @desc make admin request for all node handlers and return stat info
 * @param $host    - node Ip address or domain name
 *        $port    - node handler's port
 *        $timeout - response timeout
 *
 * @return node info array
 */
function hce_manage_node_get_info($host, $port, $timeout, $params=''){
  $handlers=array(HCE_HANDLER_ADMIN, HCE_HANDLER_ROUTER_SERVER_PROXY, HCE_HANDLER_DATA_SERVER_PROXY, HCE_HANDLER_DATA_CLIENT_PROXY, HCE_HANDLER_DATA_PROCESSOR_DATA,
                  HCE_HANDLER_DATA_CLIENT_DATA, HCE_HANDLER_DATA_REDUCER_PROXY);

  $ret=array('error'=>0, 'data'=>null, 'host'=>$host, 'port'=>$port);

  $hce_connection=hce_connection_create(array('host'=>$host, 'port'=>$port, 'type'=>HCE_CONNECTION_TYPE_ADMIN, 'identity'=>hce_unique_client_id()));

  if(!$hce_connection['error']){
    foreach($handlers as $handler){
      hce_message_send($hce_connection, array('id'=>hce_unique_message_id(), 'body'=>hce_admin_message_create($handler, HCE_CMD_PROPERTIES, $params))); 
      $hce_responses=hce_message_receive($hce_connection, $timeout);
      if($hce_responses['error']==HCE_PROTOCOL_ERROR_OK){
        foreach($hce_responses['messages'] as $hce_message){
          $ret['data'][$handler]=$hce_message['body'];
        }
      }else{
        $ret['error']=$hce_responses['error'];
        //If admin handler not responded properly or timed out - skip all another
        if($handler==HCE_HANDLER_ADMIN){
          break;
        }
      }
    }
    hce_connection_delete($hce_connection);
  }else{
    $ret['error']=$hce_connection['error'];
  }

  return $ret;
}

/*
 * @desc make admin request for node handler and return response
 * @param $host    - node Ip address or domain name
 *        $port    - node handler's port
 *        $handler - node handler
 *        $command - handler's port
 *        $timeout - response timeout
 *
 * @return node info array
 */
function hce_manage_node_handler_command($host, $port, $handler=HCE_HANDLER_ADMIN, $command=HCE_CMD_PROPERTIES, $parameters='', $timeout){
  $ret=array('error'=>0, 'data'=>null, 'host'=>$host, 'port'=>$port);

  $hce_connection=hce_connection_create(array('host'=>$host, 'port'=>$port, 'type'=>HCE_CONNECTION_TYPE_ADMIN, 'identity'=>hce_unique_client_id()));

  if(!$hce_connection['error']){
    hce_message_send($hce_connection, array('id'=>hce_unique_message_id(), 'body'=>hce_admin_message_create($handler, $command, $parameters)));

    $hce_responses=hce_message_receive($hce_connection, $timeout);
    if($hce_responses['error']==HCE_PROTOCOL_ERROR_OK){
      foreach($hce_responses['messages'] as $hce_message){
        $ret['data'][$handler]=$hce_message['body'];
      }
    }else{
      $ret['error']=$hce_responses['error'];
    }

    hce_connection_delete($hce_connection);
  }else{
    $ret['error']=$hce_connection['error'];
  }

  return $ret;
}

/*
 * @desc detects and fill nodes info array
 * @param $args cli arguments parsed
 *
 * @return array node_info('host:port'=>array())
 */
function hce_manage_nodes_get_info($args){
 $node_info=array();
 $hosts=explode(',', $args['host']);
 $ports=explode(',', $args['port']);

 if(isset($args['realtime'])) {
   $param_value=$args['realtime'];
 }else{
   $param_value='';
 }

 //Fill nodes info array
 if($args['scan']==0){
   if(count($hosts)!=count($ports)){
     //For each host
     for($i=0; $i<count($hosts); $i++){
       $host=$hosts[$i];
       //For each port
       for($j=0; $j<count($ports); $j++){
         $port=$ports[$j];
         if($args['log'] > 0){
           echo 'trying exact '.$host.':'.$port.'...'.PHP_EOL;
         }
         $node_info[$host.':'.$port]=hce_manage_node_get_info($host, $port, $args['timeout'], $param_value);
       }
     }
   }else{
     //For each host
     for($i=0; $i<count($hosts); $i++){
       $host=$hosts[$i];
       //For each port
       $port=$ports[$i];
       if($args['log'] > 0){
         echo 'trying exact '.$host.':'.$port.'...'.PHP_EOL;
       }
       $node_info[$host.':'.$port]=hce_manage_node_get_info($host, $port, $args['timeout'], $param_value);
     }
   }
 }else{
   //For each host and port
   for($i=0; $i<count($hosts); $i++){
     if($args['log'] & 1 > 0){
       echo 'trying scan '.$hosts[$i].':'.$ports[$i].'...'.PHP_EOL;
     }
     $node_info[$hosts[$i].':'.$ports[$i]]=hce_manage_node_get_info($hosts[$i], $ports[$i], $args['timeout'], $param_value);
   }
 }

 return $node_info;
}


/*
 * @desc execute manager command : cluster structure check and return json encoded cluster schema
 * @param $args array command line argiments parsed
 *
 * @return $ret array('error_code'=>0, 'error_message'=>'', 'data'=>null), data - json encoded cluster schema or empty string if error
 */
function hce_manage_command_cluster_structure_check($args){
 $ret=array('error_code'=>0, 'error_message'=>'', 'data'=>null);

 //Get node info array
 $node_info=hce_manage_nodes_get_info($args);

 //Detect hosts roles and fill structure info
 foreach($node_info as $node=>$node_data){
   $node_info[$node]['structure']=hce_manage_node_detect_role($node_data);
 }

 //Detect and set cluster structure relations for node info
 $r=hce_manage_node_set_structure_relations($node_info);
 if($r['error_code']>0){
   if($args['log'] & 1 > 0){
     $ret['error_code']=1;
     $ret['error_message']='structure error : '.$r['error_message'].PHP_EOL;
   }
 }

 if($ret['error_code']==0 || ($ret['error_code']>0 && $args['ignore']==0)){
   //Fill schema json array
   $schema_cover=array('cluster'=>array('name'=>$args['name'], 'nodes'=>array()));
   foreach($node_info as $node_data){
     if($node_data['structure']['role']){
       $schema_cover['cluster']['nodes'][]=$node_data['structure']['schema'];
     }
   }
   //Create resulted schema json
   if(count($schema_cover['cluster']['nodes'])>0){
     if(!isset($args['view']) || $args['view']!='chart'){
       $ret['data']=cli_prettyPrintJson(json_encode($schema_cover), ' ').PHP_EOL;
     }else{
       //Define recusive seek and insert procedure
       $insertNodeInASCIIChartArray = function($chartArray, $targetNodeName, $nodeName) use(&$insertNodeInASCIIChartArray){
         foreach($chartArray as $key=>$val){
           $lines=explode(PHP_EOL, $key);
           if($lines[0]==$targetNodeName){
             if(is_array($val)){
               $chartArray[$key]=array_merge($val, array($nodeName=>null));
             }else{
               $chartArray[$key]=array($nodeName=>null);
             }
             break;
           }else{
             if(is_array($val)){
               $chartArray[$key]=$insertNodeInASCIIChartArray($val, $targetNodeName, $nodeName);
             }
           }
         }

         return $chartArray;
       };

       //Define collect node fields values
       $getNodeFieldsValues = function($node, $fields=null){
         $values='';
         //Supported short fields names and correspondent full names in properties node fields set
         $fields_names=array('n'=>'name', 'r'=>'role', 'h'=>'host', 'a'=>'admin', 's'=>'server', 'c'=>'client');

         if($fields==null){
           $fields=array('n');
         }else{
           if(!in_array('n', $fields)){
             $fields=array_merge(array('n'), $fields);
           }
         }
         foreach($fields_names as $key=>$val){
           if(in_array($key, $fields)){
             if(in_array($key, array('a', 's', 'c'))){
               if($node[$val]!='' && $node[$val]!='0'){
                 $values.=strtoupper($key).'['.str_replace('tcp://', '', $node[$val]).']'.PHP_EOL;
               }
             }else{
               $values.=$node[$val].PHP_EOL;
             }
           }
         }

         return $values;
       };

       //Prepare fields short names array
       $fields=str_split((isset($args['fields']) ? $args['fields'] : 'n'));

       //Prepare array for ASCII chart
       $chartArray=array();
       //Insert router node as root or chart
       foreach($schema_cover['cluster']['nodes'] as $node){
         if($node['role']==HCE_CLUSTER_SCHEMA_ROLE_ROUTER){
           $chartArray[$getNodeFieldsValues($node, $fields)]=null;
           break;
         }
       }
       //Insert connected nodes type "smanager" or "rmanager"
       foreach($schema_cover['cluster']['nodes'] as $node){
         if(isset($node['connection']) && $node['connection']!=''
           && ($node['role']==HCE_CLUSTER_SCHEMA_ROLE_SMANAGER || $node['role']==HCE_CLUSTER_SCHEMA_ROLE_RMANAGER || $node['role']==HCE_CLUSTER_SCHEMA_ROLE_RMANAGER_RR
               || $node['role']==HCE_CLUSTER_SCHEMA_ROLE_RMANAGER_RND || $node['role']==HCE_CLUSTER_SCHEMA_ROLE_RMANAGER_RU)){
           //Insert in to the correspondent router or manager nodes array
           $chartArray=$insertNodeInASCIIChartArray($chartArray, $node['connection'], $getNodeFieldsValues($node, $fields));
         }
       }
       //Insert connected nodes type "replica"
       foreach($schema_cover['cluster']['nodes'] as $node){
         if(isset($node['connection']) && $node['connection']!='' && $node['role']==HCE_CLUSTER_SCHEMA_ROLE_REPLICA){
           //Insert in to the correspondent router or manager nodes array
           $chartArray=$insertNodeInASCIIChartArray($chartArray, $node['connection'], $getNodeFieldsValues($node, $fields));
         }
       }
       //Generate ASCII chart for connected nodes
       //$screen=cli_getScreenSize();
       $ret['data']=cli_getASCIITreeFromArray($chartArray, array('max_width'=>1/*($screen['width']>$screen['height'] ? $screen['width'] : $screen['height'])*/)).PHP_EOL;

       //Add to chart another not connected nodes as list of bottom level items
       $chartArray=array();
       //Insert emty title node as root or chart
       $chartArray['']=null;
       //Insert not connected nodes
       foreach($schema_cover['cluster']['nodes'] as $node){
         if((!isset($node['connection']) || trim($node['connection'])=='') && $node['role']!=='router'){
           $chartArray=$insertNodeInASCIIChartArray($chartArray, '', $getNodeFieldsValues($node, $fields));
         }
       }
       //Generate ASCII chart for not connected nodes
       $ret['data'].=cli_getASCIITreeFromArray($chartArray, array('max_width'=>1, 'hline_char'=>' ', 'vline_char'=>' ')).PHP_EOL;
     }
   }else{
     $ret['data']='';
   }
 }

 return $ret;
}

/*
 * @desc detects host role by host's information returned from handler's by HCE_CMD_PROPERTIES command.
 * @param $host array of data returned by hce_manage_get_host_info() call
 *
 * @return node role string name {'router', 'smanager', 'rmanager', 'replica'}
 */
function hce_manage_node_detect_role($node){
 $connection_names=array('client'=>'client', 'server'=>'server', 'admin'=>'admin');

 $ret=array('error'=>0, 'role'=>null, 'schema'=>array('name'=>null, 'role'=>null, 'host'=>null, $connection_names['client']=>null, $connection_names['server']=>null, $connection_names['admin']=>null));

 if($node['error']==0){
   $handlers=$node['data'];
   $ret['schema']['host']=$node['host'];
   //Ckeck is it a router
   if(array_key_exists(HCE_HANDLER_ROUTER_SERVER_PROXY, $handlers) && array_key_exists(HCE_HANDLER_DATA_SERVER_PROXY, $handlers)){
     //Split array of response parameters
     $properties=hce_manage_node_get_handler_properties($handlers[HCE_HANDLER_ROUTER_SERVER_PROXY]);
     if($properties!==false){
       $ret['role']=HCE_CLUSTER_SCHEMA_ROLE_ROUTER;
       $ret['schema']['role']=$ret['role'];
       $ret['schema'][$connection_names['client']]=$properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_CSTRING];
     }
    //Split array of response parameters
    $properties=hce_manage_node_get_handler_properties($handlers[HCE_HANDLER_DATA_SERVER_PROXY]);
    if($properties!==false){
      $ret['schema'][$connection_names['server']]=$properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_CSTRING];
    }
   }

   //Ckeck is it a manager "s" or "r"
   if(array_key_exists(HCE_HANDLER_DATA_SERVER_PROXY, $handlers) && array_key_exists(HCE_HANDLER_DATA_CLIENT_PROXY, $handlers)){
     //Split array of response parameters
     $properties=hce_manage_node_get_handler_properties($handlers[HCE_HANDLER_DATA_SERVER_PROXY]);
     if($properties!==false){
       if($properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_NODEMODE]==HCE_CLUSTER_SCHEMA_ROLE_CODE_SMANAGER){
         $ret['role']=HCE_CLUSTER_SCHEMA_ROLE_SMANAGER;
       }elseif($properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_NODEMODE]==HCE_CLUSTER_SCHEMA_ROLE_CODE_RMANAGER){
         $ret['role']=HCE_CLUSTER_SCHEMA_ROLE_RMANAGER;
       }elseif($properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_NODEMODE]==HCE_CLUSTER_SCHEMA_ROLE_CODE_RMANAGER_RND){
         $ret['role']=HCE_CLUSTER_SCHEMA_ROLE_RMANAGER_RND;
       }elseif($properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_NODEMODE]==HCE_CLUSTER_SCHEMA_ROLE_CODE_RMANAGER_RU){
         $ret['role']=HCE_CLUSTER_SCHEMA_ROLE_RMANAGER_RU;
       }
       $ret['schema'][$connection_names['server']]=$properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_CSTRING];
     }
     //Split array of response parameters
     $properties=hce_manage_node_get_handler_properties($handlers[HCE_HANDLER_DATA_CLIENT_PROXY]);
     if($properties!==false){
       $ret['schema'][$connection_names['client']]=$properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_CSTRING];
     }
   }

   //Ckeck is it a replica
   if(array_key_exists(HCE_HANDLER_DATA_CLIENT_DATA, $handlers) && array_key_exists(HCE_HANDLER_DATA_PROCESSOR_DATA, $handlers)){
     //Split array of response parameters
     $properties=hce_manage_node_get_handler_properties($handlers[HCE_HANDLER_DATA_CLIENT_DATA]);
     if($properties!==false){
       $ret['role']=HCE_CLUSTER_SCHEMA_ROLE_REPLICA;
       $ret['schema'][$connection_names['client']]=$properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_CSTRING];
       $ret['schema'][$connection_names['server']]='';
     }
     /*
     //Split array of response parameters
     $properties=hce_manage_get_node_properties($handlers[HCE_HANDLER_DATA_CLIENT_PROXY]);
     if($properties!==false){

     }
     */
   }

   //Ckeck is it a admin
   if(array_key_exists(HCE_HANDLER_ADMIN, $handlers)){
     //Split array of response parameters
     $properties=hce_manage_node_get_handler_properties($handlers[HCE_HANDLER_ADMIN]);
     if($properties!==false){
       $ret['schema']['name']=$properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_CIDENTITY];
       $ret['schema'][$connection_names['admin']]=$properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_CSTRING];
     }
   }

   //Set role for schema json
   if($ret['role']){
     $ret['schema']['role']=$ret['role'];
   }
 }else{
   $ret['error']=HCE_CLUSTER_SCHEMA_ERROR_WRONG_DATA.' ['.$node['error'].']';
 }

 return $ret;
}


/*
 * @desc detects and set structure relations for cluster
 * @param $node_info array of node data with cluster role info filled
 *
 * @return response array {'error_code'=>0, 'error_message'=>''}
 */
function hce_manage_node_set_structure_relations(&$node_info){
 $ret=array('error_code'=>0, 'error_message'=>'');
 foreach($node_info as $node=>$node_data){
   foreach($node_info as $node1=>$node_data1){
     if($node_data1['error']==0 && $node_data['error']==0 && isset($node_data['structure']['schema']['server']) && isset($node_data1['structure']['schema']['client'])){
       //Node schema parse
       $schema=parse_url($node_data['structure']['schema']['server']);
       //Correct host with value from request that is cover the value from local configuration settings of node
       if($node_data['structure']['schema']['host']!='localhost' && isset($schema['host']) && ($schema['host']=='*' || $schema['host']=='localhost')){
         //Requested data fetched not from "localhost"
         $schema['host']=$node_data['structure']['schema']['host'];
       }

       //Node1 schema parse
       $schema1=parse_url($node_data1['structure']['schema']['client']);
       //Correct host with value from request that is cover the value from local configuration settings of node
       if($node_data1['structure']['schema']['host']!='localhost' && isset($schema1['host']) && ($schema1['host']=='*' || $schema1['host']=='localhost')){
         //Requested data fetched not from "localhost"
         $schema1['host']=$node_data1['structure']['schema']['host'];
       }

       //Check connection relation of node and node1
       if(isset($schema['host']) && isset($schema1['host']) && isset($schema['port']) && isset($schema1['port']) &&
         ($schema['host']==$schema1['host'] || $schema['host']=='*') && ($schema['port']==$schema1['port'])){
         $node_info[$node1]['structure']['schema']['connection']=$node_data['structure']['schema']['name'];
       }
     }
   }
 }

 return $ret;
}


/*
 * @desc execute manager command : scan and executes command on specified nodes, return json encoded results
 * @param $args array command line argiments parsed
 *
 * @return $ret array('error_code'=>0, 'error_message'=>'', 'data'=>null), data - json encoded results or empty string if error
 */
function hce_manage_command_cluster_node_handler_command($args, $handler=HCE_HANDLER_ADMIN, $command=HCE_CMD_ECHO, $parameters=''){
 $ret=array();

 //Get nodes info
 $node_info=hce_manage_nodes_get_info($args);

 //Execute command for all nodes
 foreach($node_info as $node=>$node_data){
   if($node_data['error']==0){   	
     $ret[$node]=hce_manage_node_handler_command($node_data['host'], $node_data['port'], $handler, $command, $parameters, $args['timeout']);
     if($ret[$node]['error']==0){
       $ret[$node]=$ret[$node]['data'];
     }else{
       $ret[$node]='Error '.$ret[$node]['error'];
     }
   }else{
     if($node_data['error']==-5){
       $node_data['error']='Node not found at '.$node.' or connection timeout.';
     }
     $ret[$node]='Error '.$node_data['error'];
   }
 }

 return $ret;
}

?>
