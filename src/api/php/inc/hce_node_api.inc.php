<?php
/**
 * HCE project node API.
 * Samples of implementation of basic API for manage of node application.
 *
 * @author bgv <bgv.hce@gmail.com>
 * @link http://hierarchical-cluster-engine.com/
 * @copyright Copyright &copy; 2013 IOIX Ukraine
 * @license http://hierarchical-cluster-engine.com/license/
 * @package HCE project node API
 * @since 0.1
 */

require_once 'zmsg.php';

/**
 * Define and init ACN protocol node handlers names.
 */
defined('HCE_HANDLER_ADMIN') or define('HCE_HANDLER_ADMIN', 'Admin');
defined('HCE_HANDLER_ROUTER_SERVER_PROXY') or define('HCE_HANDLER_ROUTER_SERVER_PROXY', 'RouterServerProxy');
defined('HCE_HANDLER_DATA_SERVER_PROXY') or define('HCE_HANDLER_DATA_SERVER_PROXY', 'DataServerProxy');
defined('HCE_HANDLER_DATA_CLIENT_PROXY') or define('HCE_HANDLER_DATA_CLIENT_PROXY', 'DataClientProxy');
defined('HCE_HANDLER_DATA_PROCESSOR_DATA') or define('HCE_HANDLER_DATA_PROCESSOR_DATA', 'DataProcessorData');
defined('HCE_HANDLER_DATA_CLIENT_DATA') or define('HCE_HANDLER_DATA_CLIENT_DATA', 'DataClientData');
defined('HCE_HANDLER_DATA_REDUCER_PROXY') or define('HCE_HANDLER_DATA_REDUCER_PROXY', 'DataReducerProxy');

/**
 * Define and init admin command names supported by all handlers.
 */
defined('HCE_CMD_ECHO') or define('HCE_CMD_ECHO', 'ECHO');
defined('HCE_CMD_LLGET') or define('HCE_CMD_LLGET', 'LLGET');
defined('HCE_CMD_LLSET') or define('HCE_CMD_LLSET', 'LLSET');
defined('HCE_CMD_MMGET') or define('HCE_CMD_MMGET', 'MMGET');
defined('HCE_CMD_MMSET') or define('HCE_CMD_MMSET', 'MMSET');
defined('HCE_CMD_MPMGET') or define('HCE_CMD_MPMGET', 'MPMGET');
defined('HCE_CMD_MPMSET') or define('HCE_CMD_MPMSET', 'MPMSET');
defined('HCE_CMD_MRCSGET') or define('HCE_CMD_MRCSGET', 'MRCSGET');
defined('HCE_CMD_MRCSSET') or define('HCE_CMD_MRCSSET', 'MRCSSET');
defined('HCE_CMD_POLL_TIMEOUT_GET') or define('HCE_CMD_POLL_TIMEOUT_GET', 'POLL_TIMEOUT_GET');
defined('HCE_CMD_POLL_TIMEOUT_SET') or define('HCE_CMD_POLL_TIMEOUT_SET', 'POLL_TIMEOUT_SET');
defined('HCE_CMD_PROPERTY_INTERVAL_GET') or define('HCE_CMD_PROPERTY_INTERVAL_GET', 'PROPERTY_INTERVAL_GET');
defined('HCE_CMD_PROPERTY_INTERVAL_SET') or define('HCE_CMD_PROPERTY_INTERVAL_SET', 'PROPERTY_INTERVAL_SET');
defined('HCE_CMD_DUMP_INTERVAL_GET') or define('HCE_CMD_DUMP_INTERVAL_GET', 'DUMP_INTERVAL_GET');
defined('HCE_CMD_DUMP_INTERVAL_SET') or define('HCE_CMD_DUMP_INTERVAL_SET', 'DUMP_INTERVAL_SET');

/**
 * Define and init admin command names supported by specific handlers.
 */
defined('HCE_CMD_STAT') or define('HCE_CMD_STAT', 'STAT');
defined('HCE_CMD_TIME') or define('HCE_CMD_TIME', 'TIME');
defined('HCE_CMD_PROPERTIES') or define('HCE_CMD_PROPERTIES', 'PROPERTIES');
defined('HCE_CMD_RESET_STAT_COUNTERS') or define('HCE_CMD_RESET_STAT_COUNTERS', 'RESET_STAT_COUNTERS');
defined('HCE_CMD_REBUILD_SERVER_CONNECTION') or define('HCE_CMD_REBUILD_SERVER_CONNECTION', 'REBUILD_SERVER_CONNECTION');
defined('HCE_CMD_DISCONNECT_SERVER_CONNECTION') or define('HCE_CMD_DISCONNECT_SERVER_CONNECTION', 'DISCONNECT_SERVER_CONNECTION');
defined('HCE_CMD_REBUILD_CLIENT_CONNECTION') or define('HCE_CMD_REBUILD_CLIENT_CONNECTION', 'REBUILD_CLIENT_CONNECTION');
defined('HCE_CMD_DISCONNECT_CLIENT_CONNECTION') or define('HCE_CMD_DISCONNECT_CLIENT_CONNECTION', 'DISCONNECT_CLIENT_CONNECTION');
defined('HCE_CMD_UPDATE_SCHEMA') or define('HCE_CMD_UPDATE_SCHEMA', 'UPDATE_SCHEMA');
defined('HCE_CMD_REBUILD_CLIENT_CONNECTION') or define('HCE_CMD_REBUILD_CLIENT_CONNECTION', 'REBUILD_CLIENT_CONNECTION');
defined('HCE_CMD_SHUTDOWN') or define('HCE_CMD_SHUTDOWN', 'SHUTDOWN');
defined('HCE_CMD_SPHINX') or define('HCE_CMD_SPHINX', 'SPHINX');
defined('HCE_CMD_DRCE') or define('HCE_CMD_DRCE', 'DRCE');
defined('HCE_CMD_DRCE_SET_HOST' ) or define ('HCE_CMD_DRCE_SET_HOST', 'DRCE_SET_HOST' );
defined('HCE_CMD_DRCE_GET_HOST' ) or define ('HCE_CMD_DRCE_GET_HOST', 'DRCE_GET_HOST' );
defined('HCE_CMD_DRCE_SET_PORT' ) or define ('HCE_CMD_DRCE_SET_PORT', 'DRCE_SET_PORT' );
defined('HCE_CMD_DRCE_GET_PORT' ) or define ('HCE_CMD_DRCE_GET_PORT', 'DRCE_GET_PORT' );
defined('HCE_CMD_DRCE_GET_TASKS' ) or define ('HCE_CMD_DRCE_GET_TASKS', 'DRCE_GET_TASKS' );  
defined('HCE_CMD_DRCE_GET_TASKS_INFO' ) or define ('HCE_CMD_DRCE_GET_TASKS_INFO', 'DRCE_GET_TASKS_INFO' );
defined('HCE_CMD_NODE_RECOVER_NOTIFICATION_CONNECTION' ) or define ('HCE_CMD_NODE_RECOVER_NOTIFICATION_CONNECTION', 'NODE_RECOVER_NOTIFICATION_CONNECTION');
defined('HCE_CMD_NODE_ROUTES' ) or define ('HCE_CMD_NODE_ROUTES', 'NODE_ROUTES');
defined('HCE_CMD_NODE_RESOURCE_USAGE' ) or define ('HCE_CMD_NODE_RESOURCE_USAGE', 'NODE_RESOURCE_USAGE');
defined('HCE_CMD_HEARTBEAT_DELAY_SET') or define ('HCE_CMD_HEARTBEAT_DELAY_SET', 'HEARTBEAT_DELAY_SET');
defined('HCE_CMD_HEARTBEAT_DELAY_GET') or define ('HCE_CMD_HEARTBEAT_DELAY_GET', 'HEARTBEAT_DELAY_GET');
defined('HCE_CMD_HEARTBEAT_TIMEOUT_SET') or define ('HCE_CMD_HEARTBEAT_TIMEOUT_SET', 'HEARTBEAT_TIMEOUT_SET');
defined('HCE_CMD_HEARTBEAT_TIMEOUT_GET') or define ('HCE_CMD_HEARTBEAT_TIMEOUT_GET', 'HEARTBEAT_TIMEOUT_GET');
defined('HCE_CMD_HEARTBEAT_MODE_SET') or define ('HCE_CMD_HEARTBEAT_MODE_SET', 'HEARTBEAT_MODE_SET');
defined('HCE_CMD_HEARTBEAT_MODE_GET') or define ('HCE_CMD_HEARTBEAT_MODE_GET', 'HEARTBEAT_MODE_GET');

/**
 * Define and init ACN protocol error codes.
 */
defined('HCE_PROTOCOL_ERROR_OK') or define('HCE_PROTOCOL_ERROR_OK', 0);
defined('HCE_PROTOCOL_ERROR_CONNECTION_PARAMS') or define('HCE_PROTOCOL_ERROR_CONNECTION_PARAMS', -1);
defined('HCE_PROTOCOL_ERROR_CONTEXT_CREATE') or define('HCE_PROTOCOL_ERROR_CONTEXT_CREATE', -2);
defined('HCE_PROTOCOL_ERROR_SOCKET_CREATE') or define('HCE_PROTOCOL_ERROR_SOCKET_CREATE', -3);
defined('HCE_PROTOCOL_ERROR_TIMEOUT') or define('HCE_PROTOCOL_ERROR_TIMEOUT', -5);


/**
 * Define and init ACN protocol node admin command names.
 */
defined('HCE_ADMIN_CMD_SPHINX') or define('HCE_ADMIN_CMD_SPHINX', 'SPHINX');
defined('HCE_ADMIN_CMD_ECHO') or define('HCE_ADMIN_CMD_ECHO', 'ECHO');
defined('HCE_ADMIN_CMD_STAT') or define('HCE_ADMIN_CMD_STAT', 'STAT');
defined('HCE_ADMIN_CMD_REBUILD_SERVER_CONNECTION') or define('HCE_ADMIN_CMD_REBUILD_SERVER_CONNECTION', 'REBUILD_SERVER_CONNECTION');
defined('HCE_ADMIN_CMD_DISCONNECT_SERVER_CONNECTION') or define('HCE_ADMIN_CMD_DISCONNECT_SERVER_CONNECTION', 'DISCONNECT_SERVER_CONNECTION');
defined('HCE_ADMIN_CMD_REBUILD_CLIENT_CONNECTION') or define('HCE_ADMIN_CMD_REBUILD_CLIENT_CONNECTION', 'REBUILD_CLIENT_CONNECTION');
defined('HCE_ADMIN_CMD_DISCONNECT_CLIENT_CONNECTION') or define('HCE_ADMIN_CMD_DISCONNECT_CLIENT_CONNECTION', 'DISCONNECT_CLIENT_CONNECTION');
defined('HCE_ADMIN_CMD_UPDATE_SCHEMA') or define('HCE_ADMIN_CMD_UPDATE_SCHEMA', 'UPDATE_SCHEMA');
defined('HCE_ADMIN_CMD_REBUILD_CLIENT_CONNECTION') or define('HCE_ADMIN_CMD_REBUILD_CLIENT_CONNECTION', 'REBUILD_CLIENT_CONNECTION');
defined('HCE_ADMIN_CMD_SHUTDOWN') or define('HCE_ADMIN_CMD_SHUTDOWN', 'SHUTDOWN');

/**
 * Define and init ACN protocol node admin state codes.
 */
defined('HCE_ADMIN_NODE_ADMIN_ERROR_OK') or define('HCE_ADMIN_NODE_ADMIN_ERROR_OK', 'OK');
defined('HCE_ADMIN_NODE_ADMIN_ERROR_ERROR') or define('HCE_ADMIN_NODE_ADMIN_ERROR_ERROR', 'ERROR');

/**
 * Define and init ACN protocol node admin command parts delimiter.
 */
defined('HCE_ADMIN_CMD_DELIMITER') or define('HCE_ADMIN_CMD_DELIMITER', "\t"/*':'*/);

/**
 * Define and init default admin connection protocol.
 */
defined('HCE_PROTOCOL_ADMIN_DEFAULT') or define('HCE_PROTOCOL_ADMIN_DEFAULT', 'tcp');
/**
 * Define and init default admin connection host.
 */
defined('HCE_HOST_ADMIN_DEFAULT') or define('HCE_HOST_ADMIN_DEFAULT', 'localhost');
/**
 * Define and init default admin connection port.
 */
defined('HCE_PORT_ADMIN_DEFAULT') or define('HCE_PORT_ADMIN_DEFAULT', 5548);
/**
 * Define and init default data connection port.
 */
defined('HCE_PORT_ROUTER_DEFAULT') or define('HCE_PORT_ROUTER_DEFAULT', 5557);
/**
 * Define and init default command delimiter.
 */
defined('HCE_CMD_DELIMITER') or define('HCE_CMD_DELIMITER', ':');
/**
 * Define and init client identity prefix.
 */
defined('HCE_CLIENT_IDENTITY_PREFIX') or define('HCE_CLIENT_IDENTITY_PREFIX', 'HCE-CLU-');
/**
 * Define and init message Id prefix.
 */
defined('HCE_MSG_ID_PREFIX') or define('HCE_MSG_ID_PREFIX', 'ID-');
/**
 * Define and init message requests` response timeout.
 */
defined('HCE_MSG_RESPONSE_TIMEOUT') or define('HCE_MSG_RESPONSE_TIMEOUT', 1500);
/**
 * Define and init connection types.
 */
defined('HCE_CONNECTION_TYPE_ADMIN') or define('HCE_CONNECTION_TYPE_ADMIN', 0);
defined('HCE_CONNECTION_TYPE_ROUTER') or define('HCE_CONNECTION_TYPE_ROUTER', 1);

/**
 * Define handler types for client request message.
 */
defined('HCE_HANDLER_TYPE_NULL') or define('HCE_HANDLER_TYPE_NULL', 0);
defined('HCE_HANDLER_TYPE_SPHINX') or define('HCE_HANDLER_TYPE_SPHINX', 1);
defined('HCE_HANDLER_TYPE_DRCE') or define('HCE_HANDLER_TYPE_DRCE', 2);
defined('HCE_HANDLER_TYPE_SQLITE') or define('HCE_HANDLER_TYPE_SQLITE', 3);
defined('HCE_HANDLER_TYPE_MYSQL') or define('HCE_HANDLER_TYPE_MYSQL', 4);
defined('HCE_HANDLER_TYPE_FAKE') or define('HCE_HANDLER_TYPE_FAKE', 5);

/**
 * Define handler cover data protocol
 */
defined('HCE_HANDLER_COVER_FIELD_TYPE') or define('HCE_HANDLER_COVER_FIELD_TYPE', 'type');
defined('HCE_HANDLER_COVER_FIELD_DATA') or define('HCE_HANDLER_COVER_FIELD_DATA', 'data');
defined('HCE_HANDLER_COVER_FIELD_TTL') or define('HCE_HANDLER_COVER_FIELD_TTL', 'ttl');


/*
 * @desc create ACN connection (new zmq context, zmq socket and connect using specified or default options)
 * @param $connection_array - array of connection configuration options: host, port, type {HCE_CONNECTION_TYPE_ADMIN, HCE_CONNECTION_TYPE_ROUTER}, identity - string of unique client Id
 *                            in cluster
 *
 * @return ACN connection array; error item is HCE_PROTOCOL_ERROR_OK - if success and negative error code: HCE_PROTOCOL_ERROR_CONNECTION_PARAMS - wrong one or several connection parameter,
 *                                             HCE_PROTOCOL_ERROR_CONTEXT_CREATE - error create zmq context, HCE_PROTOCOL_ERROR_SOCKET_CREATE - error create zmq socket
 */
 function hce_connection_create($connection_array=null){
   //Init returned connection
   $ret=array('error'=>HCE_PROTOCOL_ERROR_OK, 'context'=>null, 'socket'=>null, 'type'=>null, 'host'=>null, 'port'=>null, 'identity'=>null);

   //Check connection parameters
   if($connection_array===null){
     $con_ar=array('host'=>HCE_HOST_ADMIN_DEFAULT, 'port'=>HCE_PORT_ADMIN_DEFAULT, 'type'=>HCE_CONNECTION_TYPE_ADMIN, 'identity'=>hce_unique_client_id());
   }else{
     if(!isset($connection_array['host']) || !isset($connection_array['port']) || !isset($connection_array['type']) || !isset($connection_array['identity'])){
       $ret['error']=HCE_PROTOCOL_ERROR_CONNECTION_PARAMS;
     }else{
       $con_ar=$connection_array;
     }
   }

   //Create connection
   if($ret['error']==HCE_PROTOCOL_ERROR_OK){
     //Create zmq context
     $ret['context']=new ZMQContext();
     if($ret['context']==null){
       $ret['error']=HCE_PROTOCOL_ERROR_CONTEXT_CREATE;
     }else{
       //Create zmq socket
       $ret['socket']=new ZMQSocket($ret['context'], ZMQ::SOCKET_DEALER);
       if($ret['socket']==null){
         $ret['error']=HCE_PROTOCOL_ERROR_SOCKET_CREATE;
       }else{
         //Set request identity
         $ret['socket']->setSockOpt(ZMQ::SOCKOPT_IDENTITY, $con_ar['identity']);
         if($con_ar['type']==HCE_CONNECTION_TYPE_ADMIN){
           //Set linger 0, do not wait on close
           $ret['socket']->setSockOpt(ZMQ::SOCKOPT_LINGER, 0);
         }

         //Connect
         $ret['socket']->connect(HCE_PROTOCOL_ADMIN_DEFAULT.'://'.$con_ar['host'].':'.$con_ar['port']);

         //Set properties
         $ret['host']=$con_ar['host'];
         $ret['port']=$con_ar['port'];
         $ret['type']=$con_ar['type'];
         $ret['identity']=$con_ar['identity'];
       }
     }
   }

   return $ret;
 }

/*
 * @desc delete ACN connection (disconnect zmq socket, free zmq socket and context)
 * @param $connection_array - array of connection configuration options: host, port, type and identity
 *
 * @return ACN connection array in initial state
 */
 function hce_connection_delete(&$connection_array){
   $connection_array['context']=NULL;
   $connection_array['socket']=NULL;
   $connection_array['host']=NULL;
   $connection_array['port']=NULL;
   $connection_array['type']=NULL;
   $connection_array['identity']=NULL;

   return $connection_array;
 }

/*
 * @desc send ACN connection message
 * @param $hce_connection - acn connection returned by hce_connection_create() call
 *        $fields_array   - array of message fields 'id' and 'body'
 *
 * @return acn message array or error HCE_PROTOCOL_ERROR_FIELDS_NOT_SET - fields array not set proper way
 */
 function hce_message_send($hce_connection, $fields_array){
   //Init return acn message array
   $ret=array('error'=>HCE_PROTOCOL_ERROR_OK, 'message'=>null);

   if(!isset($fields_array['body']) || !isset($fields_array['id'])){
     $ret['error']=HCE_PROTOCOL_ERROR_FIELDS_NOT_SET;
   }else{
     //Create message
     $ret['message']=new Zmsg($hce_connection['socket']);

     //Set route value to message depends from existing or not value input data about route
	 if(isset($fields_array['route']) && trim($fields_array['route'])!=''){
	     $ret['message']->wrap($fields_array['route'], NULL); 
	 }		

     //Set fields
     $ret['message']->wrap($fields_array['body'], NULL);
     $ret['message']->wrap($fields_array['id'], NULL);

     //Send message
     $ret['message']->send();
   }

   return $ret;
 }

/*
 * @desc receive ACN connection message
 * @param $hce_connection - acn connection returned by hce_connection_create() call
 *
 * @return ACN responses array or HCE_PROTOCOL_ERROR_TIMEOUT - if timeout reached
 */
 function hce_message_receive($hce_connection, $timeout=HCE_MSG_RESPONSE_TIMEOUT){
   //Init return acn response array
   $ret=array('error'=>HCE_PROTOCOL_ERROR_OK, 'messages'=>array());

   //Poll socket for a reply, with timeout
   $read=$write=array();
   $poll=new ZMQPoll();
   $poll->add($hce_connection['socket'], ZMQ::POLL_IN);
   $events=$poll->poll($read, $write, $timeout);
   //Handle events
   if($events){
     foreach($read as $socket) {
       $zmsg_r=new Zmsg($socket);
       $zmsg_r->recv();
       //echo PHP_EOL.'---------'.PHP_EOL.$zmsg_r->__toString().PHP_EOL.'---------'.PHP_EOL;
       $ret['messages'][]=array('error'=>HCE_PROTOCOL_ERROR_OK, 'message'=>$zmsg_r, 'id'=>$zmsg_r->unwrap(), 'body'=>$zmsg_r->unwrap());
     }
   }else{
     $ret['error']=HCE_PROTOCOL_ERROR_TIMEOUT;
   }
   $poll->remove($hce_connection['socket']);

   return $ret;
 }

/*
 * @desc generate unique client identifier
 *
 * @return unique client identifier string
 */
 function hce_unique_client_id($type=1, $prefix=null){
   if($prefix===null){
     $prefix=date('Y-m-d H:i:s').'-'.microtime(true).'-';
   }

   $ret=HCE_CLIENT_IDENTITY_PREFIX.$prefix;

   if($type==0){
     //Simple fast
     $ret.=hce_unique_id(1);
   }else{
     //More accurate complexity
     $ret.=hce_unique_id(3).'-'.hce_unique_id(5);
   }

   return $ret;
 }

/*
 * @desc generate unique message identifier
 *
 * @return unique message identifier string
 */
 function hce_unique_message_id($type=1, $prefix=''){
   $ret=HCE_MSG_ID_PREFIX.$prefix;

   if($type==0){
     //Simple fast
     $ret.=hce_unique_id(0);
   }else{
     //More accurate complexity
     //$ret.=hce_unique_id(3).'-'.hce_unique_id(5);
     $ret.=hce_unique_id(4);
   }

   return $ret;
 }

/*
 * @desc create ACN API admin message
 *
 * @return ACN API admin message string
 */
 function hce_admin_message_create($handler, $command, $parameters){
   return $handler.HCE_ADMIN_CMD_DELIMITER.$command.HCE_ADMIN_CMD_DELIMITER.$parameters.HCE_ADMIN_CMD_DELIMITER;
 }


/*
 * @desc generate unique identifier by one of several methods
 *
 * @return unique message identifier string
 */
 function hce_unique_id($type=0){
   $ret=null;

   if($type==0){
     //Complex string
     $ret=uniqid(md5(rand()), true);
   }elseif($type==1){
     //Complex string hexadec
     $ret=dechex(time()).dechex(mt_rand(1, 65535));
   }elseif($type==2){
     //Random for better crypto cypher hexadec
     $r=unpack('v*', fread(fopen('/dev/random', 'r'), 16));
     $ret=sprintf('%04x%04x-%04x-%04x-%04x-%04x%04x%04x', $r[1], $r[2], $r[3], $r[4] & 0x0fff | 0x4000, $r[5] & 0x3fff | 0x8000, $r[6], $r[7], $r[8]);
   }elseif($type==3){
     //Host name and microseconds
     $ret=uniqid(php_uname('n').'-', true);
   }elseif($type==4){
     //Another fast useful for file name
     $ret=time().substr(md5(microtime(true)), 0, rand(5, 12));
   }elseif($type==5){
     //The field names refer to RFC 4122 section 4.1.2
     $ret=sprintf('%04x%04x-%04x-%03x4-%04x-%04x%04x%04x',
                  mt_rand(0, 65535), mt_rand(0, 65535), // 32 bits for "time_low"
                  mt_rand(0, 65535), // 16 bits for "time_mid"
                  mt_rand(0, 4095),  // 12 bits before the 0100 of (version) 4 for "time_hi_and_version"
                  bindec(substr_replace(sprintf('%016b', mt_rand(0, 65535)), '01', 6, 2)),
                  // 8 bits, the last two of which (positions 6 and 7) are 01, for "clk_seq_hi_res"
                  // (hence, the 2nd hex digit after the 3rd hyphen can only be 1, 5, 9 or d)
                  // 8 bits for "clk_seq_low"
                  mt_rand(0, 65535), mt_rand(0, 65535), mt_rand(0, 65535) // 48 bits for "node"  
          );  
   }

   return $ret;
 }

?>
