#!/usr/bin/php
<?php
/**
 * HCE project json field extractor utility
 *
 * @author bgv <bgv.hce@gmail.com>
 * @link http://hierarchical-cluster-engine.com/
 * @copyright Copyright &copy; 2014 IOIX Ukraine
 * @license http://hierarchical-cluster-engine.com/license/
 * @package HCE project node API
 * @since 0.1
 */

//Set default timezone if not set in host environment
@date_default_timezone_set(@date_default_timezone_get());

require_once '../inc/hce_cli_api.inc.php';

if(php_sapi_name()!=='cli' || !defined('STDIN')){
  echo 'Only cli execution mode supported'.PHP_EOL;
  exit(1);
}

$args=cli_parse_arguments($argv);

if(isset($args['h']) || isset($args['help'])){
  echo 'Usage: '.
       $argv[0].
       ' --field=<field_path> [--base64=<0-not decode|1-decode>] [--unicode=<0-not decode|1-decode>] [--json=<json_file>] [--compact=<0-yes|1-not>] [--xml=0-output as json|1-output as xml]'.PHP_EOL;
  exit(1);
}

$field_path=isset($args['field']) ? $args['field'] : '';
$base64=isset($args['base64']) ? $args['base64']+0 : 0;
$unicode=isset($args['unicode']) ? $args['unicode']+0 : 0;
$compact=isset($args['compact']) ? $args['compact']+0 : 0;
$json=isset($args['json']) ? $args['json'] : '';
$xml=isset($args['xml']) ? $args['xml']+0 : 0;

//Get json file
if($json!==''){
  if(file_exists($json)){
    $input_json=trim(file_get_contents($json));
  }else{
    echo 'File '.$json.' not found!'.PHP_EOL;
    exit(1);
  }
}else{
  $input_json=file_get_contents("php://stdin");
}

$out='';

if($input_json!=''){
  $input_json=@json_decode($input_json, true);
  if(is_array($input_json)){
    $field_path=explode(':', $field_path);
    foreach($field_path as $dir){
      $dir=rawurldecode($dir);
      if(isset($input_json[$dir])){
        $input_json=$input_json[$dir];
      }
    }
  }
}

$out=$input_json;

if(is_array($out)){
  if($xml>0){
    echo array2Xml($out);
  }else{
    echo $compact>0 ? json_encode($out) : cli_prettyPrintJson(json_encode($out), '  ');
  }
}else{
  if($unicode>0){
    $out=html_entity_decode(preg_replace("/U\+([0-9A-F]{4})/", "&#x\\1;", $out), ENT_NOQUOTES, 'UTF-8');
  }
  $out = $base64>0 ? base64_decode($out) : $out;
  if($xml>0 && $out!=''){
    $xml = array2Xml(array($out));
    echo $xml->asXML();
  }else{
    echo $out;
  }
}

function array2Xml($data, $xml = null){
    if (is_null($xml)) {
        $xml = simplexml_load_string('<' . key($data) . '/>');
        $data = current($data);
        $return = true;
    }
    if (is_array($data)) {
        foreach ($data as $name => $value) {
            //array2Xml($value, is_numeric($name) ? $xml : $xml->addChild($name));
            if( is_numeric($name)){
              array2Xml($value, $xml->addChild('item'.$name));
            }else{
              array2Xml($value, $xml->addChild($name));
            }
        }
    } else {
        $xml->{0} = $data;
    }
    if (!empty($return)) {
        return $xml->asXML();
    }
}

?>