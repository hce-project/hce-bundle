<?php
/**
 * HCE project node manager library.
 * Samples of implementation of basic API library for drce application.
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

require_once 'hce_cli_api.inc.php';
require_once 'hce_drce_api.inc.php';


defined('LOG_MODE_JSON') or define('LOG_MODE_JSON', 3);
defined('RESPONSE_TIMEOUT_DEFAULT') or define('RESPONSE_TIMEOUT_DEFAULT', 5000);

if(php_sapi_name()!=='cli' || !defined('STDIN')){
  echo 'Only cli execution mode supported'.PHP_EOL;
  exit(1);
}

$args=cli_parse_arguments($argv);

if(isset($args['h']) || isset($args['help'])){
  echo 'Usage: '.
       $argv[0].
       ' [--host=<router_host>] [--port=<router_port>] [--request=<request_type{SET, CHECK, TERMINATE, GET, DELETE}>] [--id=<task_id>] [--json=<json_protocol_file>]'.
       ' [--n=<max_queries_number>] [--d=<request_delay_ms>] [--ttl=<request_msg_ttl_ms>] [--l=<log_mode{0-no,1-result,(2-params),3-json,4-result+object}>]'.
       ' [--t=<response_timeout_ms, '.RESPONSE_TIMEOUT_DEFAULT.' default>] [--cid=<client_id>] [--subtasks=<json_subtasks_file>]'.
       ' [--route=<route string include of node names list comma separated>]'.
       ' [--cover=<0-strip cover from response|1-response with cover> used only with --l=3]'.PHP_EOL;
  exit(1);
}

$MAX_QUERIES=isset($args['n']) ? $args['n']+0 : '1';
$REQUEST_DELAY=isset($args['d']) ? $args['d']+0 : 0;
$LOG_MODE=isset($args['l']) ? $args['l']+0 : 2;
$RESPONSE_TIMEOUT=isset($args['t']) ? ($args['t']+0) : HCE_DRCE_EXEC_DEFAULT_TIMEOUT;
$Connection_host=isset($args['host']) ? $args['host'] : 'localhost';
$Connection_port=isset($args['port']) ? $args['port'] : '5556';
$Route=isset($args['route']) ? $args['route'] : '';
$Client_Identity=isset($args['cid']) ? hce_unique_client_id.$args['cid'] : hce_unique_client_id();
$REQUEST_TYPE=isset($args['request']) ? $args['request'] : 'CHECK';
$REQUEST_TTL=isset($args['ttl']) ? ($args['ttl']+0) : HCE_DRCE_EXEC_DEFAULT_TTL;
$requests_names=array('SET'=>HCE_DRCE_REQUEST_TYPE_SET, 'CHECK'=>HCE_DRCE_REQUEST_TYPE_CHECK, 'TERMINATE'=>HCE_DRCE_REQUEST_TYPE_TERMINATE, 'GET'=>HCE_DRCE_REQUEST_TYPE_GET, 'DELETE'=>HCE_DRCE_REQUEST_TYPE_DELETE);
if(!in_array($REQUEST_TYPE, $requests_names)){
  echo 'Error: --request not supported "'.$REQUEST_TYPE.'"'.PHP_EOL;
  exit(1);
}else{
 $REQUEST_TYPE=$requests_names[$REQUEST_TYPE];
}
$REQUEST_ID=isset($args['id']) ? $args['id'] : 0;
if($REQUEST_ID==0 && $REQUEST_TYPE!=0){
  echo 'Error: this --request required --id value greater than zero'.PHP_EOL;
  exit(1);
}else{
  //Generate request Id
  if($REQUEST_ID==0 && $REQUEST_TYPE==0){
    $REQUEST_ID=sprintf('%u', crc32(hce_unique_message_id(1, microtime(true))));
  }
}

//Get json file
if(!isset($args['json']) || !file_exists($args['json'])){
  echo 'Error: --json required option or file not set or not found'.PHP_EOL;
  exit(1);
}else{
  $input_json=trim(file_get_contents($args['json']));
}

//Get subtasks file
if(isset($args['subtasks'])){
  if(!file_exists($args['subtasks'])){
    echo 'Error: --subtasks file not set or not found: "'.$args['subtasks'].'"'.PHP_EOL;
    exit(1);
  }else{
    //echo $args['subtasks'].PHP_EOL;
    $subtasks=file_get_contents($args['subtasks']);
    //echo $fc.PHP_EOL;
    $subtasks=json_encode(file_get_contents_json(json_decode($subtasks, true)));
    //echo 'subtasks1:['.cli_prettyPrintJson($subtasks, '  ').']'.PHP_EOL;
    //echo 'subtasks2:['.json_encode(hce_drce_create_subtasks_array($subtasks)).']'.PHP_EOL;
  }
}else{
  $subtasks='';
}

//Strip cover of general router protocol for resulted json. Can be used only for router request.
$strip_cover=isset($args['cover']) ? $args['cover']+0 : 1;

$Request_body=hce_drce_exec_prepare_request(hce_drce_exec_create_parameters_array($input_json, $REQUEST_TYPE), $REQUEST_TYPE, $REQUEST_ID, $REQUEST_TTL,
                                                                                  hce_drce_create_subtasks_array($subtasks));

if($LOG_MODE==2 || $LOG_MODE==4){
  echo 'Request json: '.PHP_EOL.$Request_body.PHP_EOL;
  if($LOG_MODE==4){
    $r=json_decode($Request_body, true);
    if(isset($r[HCE_DRCE_EXEC_FIELD_DATA])){
      $r[HCE_DRCE_EXEC_FIELD_DATA]=json_decode($r[HCE_DRCE_EXEC_FIELD_DATA], true);
      if(isset($r[HCE_DRCE_EXEC_FIELD_DATA][HCE_DRCE_EXEC_FIELD_DATA])){
        $r[HCE_DRCE_EXEC_FIELD_DATA][HCE_DRCE_EXEC_FIELD_DATA]=json_decode(base64_decode($r[HCE_DRCE_EXEC_FIELD_DATA][HCE_DRCE_EXEC_FIELD_DATA]), true);
        if(is_array($r[HCE_DRCE_EXEC_FIELD_DATA]['subtasks'])){
          foreach($r[HCE_DRCE_EXEC_FIELD_DATA]['subtasks'] as $key=>$st){
            if(is_array($st) && isset($st['data'])){
              $r[HCE_DRCE_EXEC_FIELD_DATA]['subtasks'][$key]['data']=json_decode(base64_decode($st['data']), true);
            }
          }
        }
        echo PHP_EOL.cli_prettyPrintJson(json_encode($r), '  ').PHP_EOL;
      }
    }
  }
}

if($Request_body===null){
  echo 'Error: create request json fault'.PHP_EOL;
  exit(1);
}

?>
