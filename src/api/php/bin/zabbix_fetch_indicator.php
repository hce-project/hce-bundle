#!/usr/bin/php
<?php
/**
 * HCE project node Zabbix indicator data fetcher from logs in json format
 * cli argument -p=<parameter_name> that consists on two parts - host->handler->parameter, for example: admindc03-10.snatz.com:5546->routerserver_proxy->requests
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

$PARAMETER_NAME_DELIMITER='->';
$LOG_FILE='../log/c112_localhost_properties.sh.log';

require_once '../inc/hce_cli_api.inc.php';

//Parse cli arguments
$args=cli_parse_arguments($argv);

//Check delimiter
if(isset($args['d']) && $args['d']!=''){
  $PARAMETER_NAME_DELIMITER=$args['d'];
}

//Check mandatory arguments
if(!isset($args['p']) || empty($args['p'])){
  echo 'ERROR: parameter not specified, use --p=<parameter_name>'.PHP_EOL;
  exit();
}

//Check optional arguments
//echo $args['l'].PHP_EOL;
//exit();
if(isset($args['l']) && !empty($args['l'])){
  if($args['l']{0}=='/'){
    //Absolute path
    $LOG_FILE=$args['l'];
  }else{
    //Relative path
    $LOG_FILE='../log/'.$args['l'];
  }
}

//Parse indicator path name
$data_keys=explode($PARAMETER_NAME_DELIMITER, $args['p']);
if(count($data_keys)<3){
  echo 'ERROR: wrong parameter_name structure, expected host'.$PARAMETER_NAME_DELIMITER.'handler'.$PARAMETER_NAME_DELIMITER.'parameter'.PHP_EOL;
  exit(1);
}

if(!file_exists($LOG_FILE)){
  echo 'ERROR: data file not found: '.$LOG_FILE.PHP_EOL;
  exit(1);
}


//Fetch log file
$data=array(json_decode(file_get_contents($LOG_FILE), true));

//Parse structure and fetch data indicator
$ret='';

$bad_key='';
foreach($data_keys as $key){
 if(isset($data[$key])){
   if(is_array($data[$key])){
     $data=$data[$key];
   }else{
     $ret=$data[$key];
   }
 }else{
   $bad_key=$key;
   break;
 }
}

if(is_array($ret)){
  echo json_encode($ret);
}else{
  if($ret=='' && $bad_key!=''){
    echo 'ERROR: parameter '.$bad_key.' not found in log data'.PHP_EOL;
  }else{
    if($ret-floor($ret)>0){
      if(floatval(sprintf('%f', $ret+0))==0.0){
        echo 0;
      }else{
        echo sprintf('%f', $ret+0);
      }
    }else{
      echo $ret;
    }
  }
}

exit();

?>