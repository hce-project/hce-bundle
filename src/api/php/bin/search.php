#!/usr/bin/php
<?php
/**
 * HCE project node searcher application.
 *
 * @author bgv <bgv.hce@gmail.com>
 * @link http://hierarchical-cluster-engine.com/
 * @copyright Copyright &copy; 2013-2014 IOIX Ukraine
 * @license http://hierarchical-cluster-engine.com/license/
 * @package HCE project node API
 * @since 0.1
 */


//Set default timezone if not set in host environment
@date_default_timezone_set(@date_default_timezone_get());

require_once '../inc/hce_node_api.inc.php';
require_once '../inc/search.ini.php';

$hce_connection=hce_connection_create(array('host'=>$Connection_host, 'port'=>$Connection_port, 'type'=>HCE_CONNECTION_TYPE_ROUTER, 'identity'=>$Client_Identity));

if(!$hce_connection['error']){
  if($LOG_MODE!=3){
    echo 'Client ['.$Client_Identity.'] conected, start to send '.$MAX_QUERIES.' message requests...'.PHP_EOL.PHP_EOL;
  }

  $t=time();
  $Timedout=0;

  for($i=1; $i<=$MAX_QUERIES; $i++){
    //$Request_Id=uniqid('ID-'.$i.'-'.date('H:i:s').'-', TRUE);
    $Request_Id=hce_unique_message_id(1, $i.'-'.date('H:i:s').'-');
    $msg_fields=array('id'=>$Request_Id, 'body'=>$Request_body, 'route'=>$Route);
    hce_message_send($hce_connection, $msg_fields);

    if($LOG_MODE!=3){
      echo 'request message '.$i.' ['.$Request_Id.'] sent...'.PHP_EOL;
    }

    $hce_responses=hce_message_receive($hce_connection, $RESPONSE_TIMEOUT);
    if($hce_responses['error']===0){
      foreach($hce_responses['messages'] as $hce_message){
        //var_dump($hce_message);
        if($LOG_MODE==3){
          echo $hce_message['body'];
        }else{
          $rjson=hce_sphinx_search_parse_json($hce_message['body']);
          if($LOG_MODE!=0){
            echo 'Message: id=['.$hce_message['id'].'], body=['.$hce_message['body'].']'.PHP_EOL;
          }
          if($LOG_MODE==4){
            echo var_export($rjson, true).PHP_EOL;
          }
          $DocumentsNumber=hce_sphinx_search_result_get($rjson, HCE_SPHINX_SEARCH_RESULTS_MI);
          echo 'Documents:'.$DocumentsNumber=hce_sphinx_search_result_get($rjson, HCE_SPHINX_SEARCH_RESULTS_MI).PHP_EOL;
        }
      }
    }else{
      if($hce_responses['error']==HCE_PROTOCOL_ERROR_TIMEOUT){
        $Timedout++;
        if($LOG_MODE!=3){
          echo 'request timeout'.PHP_EOL;
        }
      }else{
        if($LOG_MODE!=3){
          echo 'request unknown error'.PHP_EOL;
        }
      }
    }

    if($REQUEST_DELAY>0){
      sleep($REQUEST_DELAY);
    }
  }

  hce_connection_delete($hce_connection);
  if($LOG_MODE!=3){
    echo PHP_EOL.'Finished '.$MAX_QUERIES.' queries, '.(time()-$t).' sec, '.floor($MAX_QUERIES/(time()-$t+0.00001)).' rps, '.$Timedout.' timedout'.PHP_EOL;
  }
}else{
  if($LOG_MODE!=3){
    echo 'Connection create error '.$hce_connection['error'].PHP_EOL;
  }else{
    echo json_encode(array('data'=>array('match_info'=>array(), 'word_info'=>array(), 'doc_info'=>array())));
  }
}

exit();

?>