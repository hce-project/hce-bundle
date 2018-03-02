<?php
/**
 * HCE project node manager library.
 * Samples of implementation of basic API library for searcher application.
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
require_once 'hce_sphinx_api.inc.php';

defined('LOG_MODE_JSON') or define('LOG_MODE_JSON', 3);
defined('RESPONSE_TIMEOUT_DEFAULT') or define('RESPONSE_TIMEOUT_DEFAULT', 5000);

if(php_sapi_name()!=='cli' || !defined('STDIN')){
  echo 'Only cli execution mode supported'.PHP_EOL;
  exit(1);
}

$args=cli_parse_arguments($argv);
if(isset($args['h']) || isset($args['help']) || !isset($args['q'])){
  echo 'Usage: '.
       $argv[0].
       ' [--q=query_string|"`query_string`">] [--f=<filters>] [--s=<sorting>] [--n=<max_queries_number>] [--r=<max_results>] [--d=<request_delay_ms>]'.
       ' [--l=<log_mode{0-no,1-result,2-params,3-json,4-result+object}>]'.
       ' [--t=<response_timeout_ms, '.RESPONSE_TIMEOUT_DEFAULT.' default>] [--host=<router_host>] [--port=<router_port>] [--cid=<client_id>]'.
       ' [--route=<route string include of node names list comma separated>]'.
       ' [--sphinx_timeout=<sphinx_searchd_timeout_ms '.HCE_SPHINX_SEARCH_FIELD_TIMEOUT_DEFAULT.' default>]'.PHP_EOL.
       'filters - list of filter items delimited by semicolon. Filter item: "type{integer},field_name{string},value1,...,valueN{integers},exclude{0,1}"'.PHP_EOL.
       'sort - list of sort parameters delimited by comma. Format: "algorithm{integer},field1[,...,fieldN]{strings},order{1,2}"'.PHP_EOL;
  exit(1);
}

$MAX_QUERIES=isset($args['n']) ? $args['n']+0 : '1';
$MAX_RESULTS=isset($args['r']) ? $args['r']+0 : '10';
$REQUEST_DELAY=isset($args['d']) ? $args['d']+0 : 0;
$LOG_MODE=isset($args['l']) ? $args['l']+0 : 2;
$RESPONSE_TIMEOUT=isset($args['t']) ? ($args['t']+0) : RESPONSE_TIMEOUT_DEFAULT;
$Connection_host=isset($args['host']) ? $args['host'] : 'localhost';
//$Connection_host='admindc03-10.snatz.com';
$Connection_port=isset($args['port']) ? $args['port'] : '5556';
$Route=isset($args['route']) ? $args['route'] : '';
$Client_Identity=isset($args['cid']) ? hce_unique_client_id.$args['cid'] : hce_unique_client_id();
//Query string
$query_string=isset($args['q']) ? str_replace('`', '"', stripslashes($args['q'])) : 'for';
//Sphinx request timeout
$sphinx_timeout=isset($args['sphinx_timeout']) ? ($args['sphinx_timeout']+0) : HCE_SPHINX_SEARCH_FIELD_TIMEOUT_DEFAULT;

//Json filters array
$filters=array();
if(isset($args['f'])){
  $filters1=explode(';', $args['f']);
  foreach($filters1 as $filter1){
    $filter1=explode(',', $filter1);
    if(count($filter1)>2){
      if($filter1[0]==0 || $filter1[0]==1  || $filter1[0]==2 ||  $filter1[0]==3){
        $type=$filter1[0]+0;
      }else{
        continue;
      }
      //Values list
      $values=array();
      for($i=2; $i<count($filter1)-1; $i++){
        $values[]=trim($filter1[$i]);
      }
      $filters[]=array(HCE_SPHINX_SEARCH_FIELD_FILTER_TYPE=>$type,
                       HCE_SPHINX_SEARCH_FIELD_FILTER_ATTRIB=>trim($filter1[1]),
                       HCE_SPHINX_SEARCH_FIELD_FILTER_VALUES=>$values,
                       HCE_SPHINX_SEARCH_FIELD_FILTER_EXCLUDE=>trim($filter1[count($filter1)-1])
                      );
    }else{
      echo 'Wrong number of filter parameters in filter item type:'.$filter1[0].', item ignored'.PHP_EOL;
    }
  }
}

//Json order array
$order=array();
if(isset($args['s'])){
  $order=explode(',', $args['s']);
  if(count($order>2)){
    $order=array(HCE_SPHINX_SEARCH_FIELD_ORDER_ALG=>($order[0]>0 ? $order[0] : '0'),
                 HCE_SPHINX_SEARCH_FIELD_ORDER_FIELDS=>array_slice($order, 1, count($order)-2), 
                 HCE_SPHINX_SEARCH_FIELD_ORDER_BY=>($order[count($order)-1]=='0' ? HCE_SPHINX_SEARCH_FIELD_ORDER_BY_ASC : HCE_SPHINX_SEARCH_FIELD_ORDER_BY_DESC)
                );
  }else{
    echo 'Wrong number of sort parameters, sort option ignored, default settings applied'.PHP_EOL;
  }
}

if($LOG_MODE==2){
  echo 'Parameters:'.PHP_EOL.'query_string:"'.$query_string.'", filters:"'.json_encode($filters).'", max_queries_number:'.$MAX_QUERIES.', max_results:'.$MAX_RESULTS.
       ', requet_delay_ms:'.$REQUEST_DELAY.', log_mode:'.$LOG_MODE.', response_timeout_ms:'.$RESPONSE_TIMEOUT.', router_host:'.$Connection_host.
       ', router_port:'.$Connection_port.', client_id:"'.$Client_Identity.'"'.PHP_EOL.PHP_EOL;
}

$ret_arrays_mask=(HCE_SPHINX_SEARCH_RET_TYPE_MI_INFO | HCE_SPHINX_SEARCH_RET_TYPE_RI_INFO | HCE_SPHINX_SEARCH_RET_TYPE_AT_INFO | HCE_SPHINX_SEARCH_RET_TYPE_WI_INFO).'';
$parameters_array=hce_sphinx_search_prepare_parameters($query_string, array(HCE_SPHINX_SEARCH_FIELD_TYPE_MASK=>$ret_arrays_mask,
                                                                            HCE_SPHINX_SEARCH_FIELD_MAX_RESULTS=>$MAX_RESULTS,
                                                                            HCE_SPHINX_SEARCH_FIELD_FILTERS=>$filters,
                                                                            HCE_SPHINX_SEARCH_FIELD_ORDER=>$order,
                                                                            HCE_SPHINX_SEARCH_FIELD_TIMEOUT=>$sphinx_timeout
                                                                           ));
$Request_body=hce_sphinx_search_create_json($parameters_array);

if($LOG_MODE==2 || $LOG_MODE==4){
  echo 'Request json:'.PHP_EOL.$Request_body.PHP_EOL.PHP_EOL;
}

?>