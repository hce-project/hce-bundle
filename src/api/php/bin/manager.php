#!/usr/bin/php
<?php
/**
 * HCE project node manager application.
 *
 * @author bgv <bgv.hce@gmail.com>
 * @link http://hierarchical-cluster-engine.com/
 * @copyright Copyright &copy; 2013 IOIX Ukraine
 * @license http://hierarchical-cluster-engine.com/license/
 * @package HCE project node API
 * @since 0.1
 */


//Set default timezone if not set in host environment
@date_default_timezone_set(@date_default_timezone_get());

require_once '../inc/manager.inc.php';

if(php_sapi_name()!=='cli' || !defined('STDIN')){
  echo 'Only cli execution mode supported'.PHP_EOL;
  exit(1);
}

$args=cli_parse_arguments($argv);

if(!isset($args['host']) || empty($args['host'])){
  $args['host']='localhost';
}else{
  //Re-build hosts lists to remove empty values
  $h=explode(',', $args['host']);
  foreach($h as $key=>$hs){
    if(trim($hs)==''){
      unset($h[$key]);
    }
  }
  $args['host']=implode(',', $h);
}

if(!isset($args['port']) || empty($args['port'])){
  $args['port']=HCE_CLUSTER_SCHEMA_PORTS_DEFAULT;
}else{
  //Re-build ports lists to remove empty values
  $h=explode(',', $args['port']);
  foreach($h as $key=>$hs){
    $hs=trim($hs);
    if($hs=='' || !is_numeric($hs) || ($hs+0)==0){
      unset($h[$key]);
    }
  }
  $args['port']=implode(',', $h);
}

if(!isset($args['timeout']) || empty($args['timeout'])){
  $args['timeout']=HCE_CLUSTER_CMD_TIMEOUT;
}

if(!isset($args['log']) || $args['log']===''){
  $args['log']=0; //Silent default
}

if(!isset($args['scan']) || empty($args['scan'])){
  $args['scan']=0;
}

if(!isset($args['ignore']) || empty($args['ignore'])){
  $args['ignore']=0;
}

if(!isset($args['tformat']) || empty($args['tformat'])){
  $args['tformat']=null;
}

if(!isset($args['port'], $args['command']) || empty($args['command']) || empty($args['port'])){
  echo hce_manage_get_help();
  exit(1);
}

$aborted='';
$options_array=array();
$command_category=0;                          //0 - Sphinx admin, 1 - cluster structure
switch($args['command']){
  case HCE_SPHINX_CMD_INDEX_CONNECT           :
  case HCE_SPHINX_CMD_INDEX_DISCONNECT        :
  case HCE_SPHINX_CMD_INDEX_DATA_LIST         :
  case HCE_SPHINX_CMD_INDEX_STATUS_SEARCHD    :
  case HCE_SPHINX_CMD_INDEX_STATUS            :
  case HCE_SPHINX_CMD_INDEX_MAX_DOC_ID        :
  case HCE_SPHINX_CMD_INDEX_REMOVE            :
  case HCE_SPHINX_CMD_INDEX_DELETE_DOC_NUMBER :
  case HCE_SPHINX_CMD_INDEX_CHECK             :
  case HCE_SPHINX_CMD_INDEX_START             :
  case HCE_SPHINX_CMD_INDEX_STOP              :
  case HCE_SPHINX_CMD_INDEX_DELETE_SCHEMA_FILE:
  case HCE_SPHINX_CMD_INDEX_CREATE            : {
    if(!isset($args['name'])){
      $aborted='--name=<index_name> ';
    }else{
      $options_array['index']=$args['name'];
    }
    break;
  }
  case HCE_SPHINX_CMD_INDEX_APPEND_DATA_FILE  :
  case HCE_SPHINX_CMD_INDEX_STORE_DATA_FILE   : {
    if(!isset($args['name'])){
      $aborted='--name=<index_name> ';
    }else{
      $options_array['index']=$args['name'];
    }
    if(!isset($args['branch'])){
      $aborted.='--branch=<branch_name> ';
    }else{
      $options_array['branch']=$args['branch'];
    }
    if(!isset($args['data'])){
      $aborted.='--data=<data_file> ';
    }else{
      if(!file_exists($args['data'])){
        $aborted.='file '.$args['data'].' ';
      }else{
        if(SPHINX_JSON_USE_BASE64){
          $options_array['data']=base64_encode(file_get_contents($args['data']));
        }else{
          $options_array['data']=file_get_contents($args['data']);
        }
      }
    }
    break;
  }
  case HCE_SPHINX_CMD_INDEX_STORE_SCHEMA_FILE : {
    if(!isset($args['name'])){
      $aborted='--name=<index_name> ';
    }else{
      $options_array['index']=$args['name'];
    }
    if(!isset($args['data'])){
      $aborted.='--data=<data_file> ';
    }else{
      if(!file_exists($args['data'])){
        $aborted.='file '.$args['data'].' ';
      }else{
        if(SPHINX_JSON_USE_BASE64){
          $options_array['data']=base64_encode(file_get_contents($args['data']));
        }else{
          $options_array['data']=file_get_contents($args['data']);
        }
      }
    }
    break;
  }
  case HCE_SPHINX_CMD_INDEX_PACK_DOC_DATA     :
  case HCE_SPHINX_CMD_INDEX_MERGE             :
  case HCE_SPHINX_CMD_INDEX_DELETE_DATA_FILE  :
  case HCE_SPHINX_CMD_INDEX_REBUILD           : {
    if(!isset($args['name'])){
      $aborted='--name=<index_name> ';
    }else{
      $options_array['index']=$args['name'];
    }
    if(!isset($args['branches'])){
      $aborted.='--branches=<branches_list_csv> ';
    }else{
      $options_array['branches']=explode(',', $args['branches']);
    }
    break;
  }
  case HCE_SPHINX_CMD_INDEX_DELETE_DOC        : {
    if(!isset($args['name'])){
      $aborted='--name=<index_name> ';
    }else{
      $options_array['index']=$args['name'];
    }
    if(!isset($args['documents'])){
      $aborted.='--documents=<documents_list_csv> ';
    }else{
      $options_array['documents']=explode(',', $args['documents']);
    }
    break;
  }
  case HCE_SPHINX_CMD_INDEX_RENAME            :
  case HCE_SPHINX_CMD_INDEX_COPY              : {
    if(!isset($args['from'])){
      $aborted='--from=<index_from> ';
    }else{
      $options_array['index_from']=$args['from'];
    }
    if(!isset($args['to'])){
      $aborted.='--to=<index_to> ';
    }else{
      $options_array['index_to']=$args['to'];
    }
    break;
  }
  case HCE_SPHINX_CMD_INDEX_SET_CONFIG_VAR    : {
    if(!isset($args['index'])){
      $aborted='--index=<index_name> ';
    }else{
      $options_array['index_name']=$args['index'];
    }
    if(!isset($args['type'])){
      $aborted.='--type=<config_type> ';
    }else{
      $options_array['type']=$args['type'];
    }
    if(!isset($args['section'])){
      $aborted='--section=<section_name> ';
    }else{
      $options_array['section']=$args['section'];
    }
    if(!isset($args['parameter'])){
      $aborted.='--parameter=<parameter_name> ';
    }else{
      $options_array['parameter']=$args['parameter'];
    }
    if(!isset($args['value'])){
      $aborted.='--value=<parameter_value> ';
    }else{
      $options_array['value']=$args['value'];
    }
    break;
  }
  case HCE_CLUSTER_CMD_STRUCTURE_CHECK        : {
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
    }else{
      if(!isset($args['name'])){
        $args['name']='';
      }
      $r=hce_manage_command_cluster_structure_check($args);
      if($r['error_code']==0){
        echo $r['data'];
      }else{
        if($args['log'] & 1 > 0){
          echo $r['error_message'];
        }
      }
    }

    $command_category=1;
    break;
  }
  case HCE_CLUSTER_CMD_NODE_SHUTDOWN        : {
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
    }else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_ADMIN, HCE_CMD_SHUTDOWN);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  case HCE_CLUSTER_CMD_NODE_MMGET        : {
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
    }else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_REDUCER_PROXY, HCE_CMD_MMGET);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_SERVER_PROXY, HCE_CMD_MMGET);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  case HCE_CLUSTER_CMD_NODE_MMSET        : {
    $modes=array('smanager'=>0, 'rmanager'=>1, 'rmanager-rnd'=>4, 'rmanager-resources-usage'=>5);
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
    }else if(!isset($args['mode']) || !array_key_exists($args['mode'], $modes)){
      $aborted='--mode must be set as "smanager", "rmanager", "rmanager-rnd" or "rmanager-resources-usage"';
    }else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_REDUCER_PROXY, HCE_CMD_MMSET, $modes[$args['mode']]);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_SERVER_PROXY, HCE_CMD_MMSET, $modes[$args['mode']]);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  case HCE_CLUSTER_CMD_NODE_MPMGET        : {
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
    }else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_REDUCER_PROXY, HCE_CMD_MPMGET);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_SERVER_PROXY, HCE_CMD_MPMGET);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  case HCE_CLUSTER_CMD_NODE_MPMSET        : {
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
    }else if(!isset($args['purge'])) {
      $aborted='--purge must be set as "1" or "0"';
    }else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_REDUCER_PROXY, HCE_CMD_MPMSET, $args['purge']);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_SERVER_PROXY, HCE_CMD_MPMSET, $args['purge']);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  case HCE_CLUSTER_CMD_NODE_MRCSGET        : {
  	if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
  	}else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_SERVER_PROXY, HCE_CMD_MRCSGET);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
  	}
  	$command_category=1;
  	break;
  }
  case HCE_CLUSTER_CMD_NODE_MRCSSET        : {
  	if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
  	}else if(!isset($args['csize'])) {
      $aborted='--csize must be set as numeric value, "0" - unlimited size';
  	}else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_SERVER_PROXY, HCE_CMD_MRCSSET, $args['csize']);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
  	}
  	$command_category=1;
  	break;
  }
  case HCE_CLUSTER_CMD_NODE_TIME            :
  case HCE_CLUSTER_CMD_NODE_ECHO            : {
    //Map manager command to ACN node API command
    $manager_to_hce_commands_map=array(HCE_CLUSTER_CMD_NODE_TIME=>HCE_CMD_TIME, HCE_CLUSTER_CMD_NODE_ECHO=>HCE_CMD_ECHO);

    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
    }else{
      $nodes=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_ADMIN, $manager_to_hce_commands_map[$args['command']]);
      foreach($nodes as $node_key=>$node_data){
        if(isset($node_data[HCE_HANDLER_ADMIN])){
          $properties=hce_manage_node_get_handler_properties($node_data[HCE_HANDLER_ADMIN]);
          if($properties!==false){
            if($args['command']==HCE_CLUSTER_CMD_NODE_PROPERTIES){
              $properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_TIME]=date(HCE_CLUSTER_CMD_DATE_FORMAT, round($properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_TIME]/1000));
              $properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_NAME]=$properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_CIDENTITY];
              unset($properties[HCE_CLUSTER_CMD_PROPERTIES_FIELD_CIDENTITY]);
            }
            $nodes[$node_key]=$properties;
          }
        }
      }
      echo cli_prettyPrintJson(json_encode($nodes), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  case HCE_CLUSTER_CMD_NODE_LLGET           :
  case HCE_CLUSTER_CMD_NODE_LLSET           :
  case HCE_CLUSTER_CMD_NODE_PROPERTIES      : 
  case HCE_CLUSTER_CMD_NODE_RESOURCE_USAGE 	: 
  case HCE_CLUSTER_CMD_NODE_HB_DELAY_GET	:
  case HCE_CLUSTER_CMD_NODE_HB_DELAY_SET	:
  case HCE_CLUSTER_CMD_NODE_HB_TIMEOUT_GET	:
  case HCE_CLUSTER_CMD_NODE_HB_TIMEOUT_SET	: 
  case HCE_CLUSTER_CMD_NODE_HB_MODE_GET		:
  case HCE_CLUSTER_CMD_NODE_HB_MODE_SET		: 
  case HCE_CLUSTER_CMD_NODE_POLL_TIMEOUT_GET:
  case HCE_CLUSTER_CMD_NODE_POLL_TIMEOUT_SET:
  case HCE_CLUSTER_CMD_NODE_PROPERTY_INTERVAL_GET:
  case HCE_CLUSTER_CMD_NODE_PROPERTY_INTERVAL_SET: 
  case HCE_CLUSTER_CMD_NODE_DUMP_INTERVAL_GET:
  case HCE_CLUSTER_CMD_NODE_DUMP_INTERVAL_SET: 
  case HCE_CLUSTER_CMD_NODE_RESET_STAT_COUNTERS:{
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1 ';
      break;
    }
    if(!isset($args['handler'])){
      $aborted='--handler=<handler_name{ADMIN,ROUTERSERVER_PROXY,DATASERVER_PROXY,DATA_CLIENT_PROXY,DATAPROCESSOR_DATA,DATACLIENT_DATA,DATAREDUCER_PROXY,*}> ';
      break;
    }
    if($args['command']==HCE_CLUSTER_CMD_NODE_LLSET && !isset($args['level'])){
      $aborted='--level=<level(s)_value_csv> ';
      break;
    }
    //List of all supported handler names
    $handlers=array(HCE_HANDLER_ADMIN, HCE_HANDLER_ROUTER_SERVER_PROXY, HCE_HANDLER_DATA_SERVER_PROXY, HCE_HANDLER_DATA_CLIENT_PROXY, HCE_HANDLER_DATA_PROCESSOR_DATA,
                    HCE_HANDLER_DATA_CLIENT_DATA, HCE_HANDLER_DATA_REDUCER_PROXY);
    $handlers_list=explode(',', $args['handler']);
    //Extend all handlers value "*" to exact handlers list
    if($handlers_list[0]=='*'){
      $handlers_list=$handlers;
    }
    //Set levels list
    if($args['command']==HCE_CLUSTER_CMD_NODE_LLSET){
      $levels_list=explode(',', $args['level']);
      if((count($levels_list)>count($handlers_list)) ||
         ((count($handlers_list)>1) && (count($levels_list)>1) && (count($levels_list)!=count($handlers_list)))
        ){
        $aborted='handler and level value mismatch by items number, --handler and --level > ';
        break;
      }
      //Extend levels list to have the same items as handlers
      if(count($levels_list)==1 && count($handlers_list)>1){
        for($i=0; $i<count($handlers_list)-1; $i++){
          $levels_list[]=$levels_list[0];
        }
      }
    }else{
      $levels_list=array();
    }
    foreach($handlers_list as $handler_item){
      if(!in_array($handler_item, $handlers)){
        $aborted='Handler name "'.$handler_item.'" not supported, --handler ';
        break 2;
      }
    }
    //Map manager command to ACN node API command
    $mgr_to_hce_cmd_map=array(HCE_CLUSTER_CMD_NODE_LLSET=>HCE_CMD_LLSET, HCE_CLUSTER_CMD_NODE_LLGET=>HCE_CMD_LLGET, 
    		HCE_CLUSTER_CMD_NODE_PROPERTIES=>HCE_CMD_PROPERTIES, HCE_CLUSTER_CMD_NODE_RESOURCE_USAGE=>HCE_CMD_NODE_RESOURCE_USAGE, 
    		HCE_CLUSTER_CMD_NODE_HB_DELAY_SET=>HCE_CMD_HEARTBEAT_DELAY_SET, HCE_CLUSTER_CMD_NODE_HB_DELAY_GET=>HCE_CMD_HEARTBEAT_DELAY_GET, 
    		HCE_CLUSTER_CMD_NODE_HB_TIMEOUT_SET=>HCE_CMD_HEARTBEAT_TIMEOUT_SET, HCE_CLUSTER_CMD_NODE_HB_TIMEOUT_GET=>HCE_CMD_HEARTBEAT_TIMEOUT_GET, 
    		HCE_CLUSTER_CMD_NODE_HB_MODE_SET=>HCE_CMD_HEARTBEAT_MODE_SET, HCE_CLUSTER_CMD_NODE_HB_MODE_GET=>HCE_CMD_HEARTBEAT_MODE_GET,
    		HCE_CLUSTER_CMD_NODE_POLL_TIMEOUT_SET=>HCE_CMD_POLL_TIMEOUT_SET, HCE_CLUSTER_CMD_NODE_POLL_TIMEOUT_GET=>HCE_CMD_POLL_TIMEOUT_GET,
    		HCE_CLUSTER_CMD_NODE_PROPERTY_INTERVAL_SET=>HCE_CMD_PROPERTY_INTERVAL_SET, HCE_CLUSTER_CMD_NODE_PROPERTY_INTERVAL_GET=>HCE_CMD_PROPERTY_INTERVAL_GET,
            HCE_CLUSTER_CMD_NODE_DUMP_INTERVAL_SET=>HCE_CMD_DUMP_INTERVAL_SET, HCE_CLUSTER_CMD_NODE_DUMP_INTERVAL_GET=>HCE_CMD_DUMP_INTERVAL_GET,
            HCE_CLUSTER_CMD_NODE_RESET_STAT_COUNTERS=>HCE_CMD_RESET_STAT_COUNTERS);
    //Get nodes info
    $node_info=hce_manage_nodes_get_info($args);
       
    $ret=array();
    //For each detected node
    foreach($node_info as $node=>$node_data){
      //For each of possible handlers
      for($i=0; $i<count($handlers_list); $i++){      	
        if($node_data['error']==0 && isset($node_data['data'][$handlers_list[$i]])){
          $properties=hce_manage_node_get_handler_properties($node_data['data'][$handlers_list[$i]]);
                   
          if($properties!==false){
          	//Init params value
          	$param_value='';
          	switch ($args['command']){
			    case HCE_CLUSTER_CMD_NODE_LLSET:
			        $param_value=$levels_list[$i];
			        break;
			    case HCE_CLUSTER_CMD_NODE_HB_DELAY_SET:{
				    	if($args['scan']==1 && count($hosts)!=count($ports)){
				    		$aborted='--host and --port must to list the same number of items if --scan=1';
				    	}else if(!isset($args['hbdelay'])) {
				    		$aborted='--hbdelay must be set im sec';
	  					}else{
				    		$param_value=$args['hbdelay'];
	  					}
			    	}			        
			        break;
			    case HCE_CLUSTER_CMD_NODE_HB_TIMEOUT_SET:{
					  	if($args['scan']==1 && count($hosts)!=count($ports)){
					  		$aborted='--host and --port must to list the same number of items if --scan=1';
					  	}else if(!isset($args['hbtimeout'])) {
					  		$aborted='--hbtimeout must be set in sec';
					  	}else{
					  		$param_value=$args['hbtimeout'];
					  	}
				  	}			        
			        break;
			    case HCE_CLUSTER_CMD_NODE_HB_MODE_SET:{
					  	if($args['scan']==1 && count($hosts)!=count($ports)){
					  		$aborted='--host and --port must to list the same number of items if --scan=1';
					  	}else if(!isset($args['hbmode'])) {
					  		$aborted='--hbmode must be set in numeric value';
					  	}else{
					  		$param_value=$args['hbmode'];
					  	}
				  	}			        
			        break;
			    case HCE_CLUSTER_CMD_NODE_POLL_TIMEOUT_SET:{
					  	if($args['scan']==1 && count($hosts)!=count($ports)){
					  		$aborted='--host and --port must to list the same number of items if --scan=1';
					  	}else if(!isset($args['ptimeout'])) {
					  		$aborted='--ptimeout must be set in numeric value';
					  	}else{
					  		$param_value=$args['ptimeout'];
					  	}
				  	}			        
			        break;
			    case HCE_CLUSTER_CMD_NODE_PROPERTY_INTERVAL_SET:{
					  	if($args['scan']==1 && count($hosts)!=count($ports)){
					  		$aborted='--host and --port must to list the same number of items if --scan=1';
					  	}else if(!isset($args['interval'])) {
					  		$aborted='--interval must be set in numeric value';
					  	}else{
					  		$param_value=$args['interval'];
					  	}
				  	}			        
			        break;
			    case HCE_CLUSTER_CMD_NODE_DUMP_INTERVAL_SET:{
					  	if($args['scan']==1 && count($hosts)!=count($ports)){
					  		$aborted='--host and --port must to list the same number of items if --scan=1';
					  	}else if(!isset($args['interval'])) {
					  		$aborted='--interval must be set in numeric value';
					  	}else{
					  		$param_value=$args['interval'];
					  	}
				  	}			        
			        break;
			    case HCE_CLUSTER_CMD_NODE_PROPERTIES:{
				    	if($args['scan']==1 && count($hosts)!=count($ports)){
				    		$aborted='--host and --port must to list the same number of items if --scan=1';
				    	}else{
				    		if(isset($args['realtime'])) {
				    			$param_value=$args['realtime'];	
				    		}else{
				    		  $param_value='';
				    		}				    		
				    	}
			    	}
			    	break;   
			    case HCE_CLUSTER_CMD_NODE_RESET_STAT_COUNTERS:{
    			        if($args['scan']==1 && count($hosts)!=count($ports)){
    			            $aborted='--host and --port must to list the same number of items if --scan=1';
    			        }else{
    			            $param_value='';
    			        }    			        
    			    }
    			    break;
          	}
          	         	
			//Execution command with parameters		         	
            $ret[$node][$handlers_list[$i]]=hce_manage_node_handler_command($node_data['host'], $node_data['port'], $handlers_list[$i], $mgr_to_hce_cmd_map[$args['command']],
                                                                            $param_value, $args['timeout']);              
            if($ret[$node][$handlers_list[$i]]['error']==0){  	
              $properties=hce_manage_node_get_handler_properties($ret[$node][$handlers_list[$i]]['data'][$handlers_list[$i]], HCE_ADMIN_CMD_DELIMITER, $args['tformat']);
              
              if(isset($properties['clients'])) {
                $properties['clients'] = json_decode($properties['clients'], true);
                  
                if(is_array($properties['clients']['clients']) && $args['tformat']!==null){
               	  //$properties['clients']['expiry']=date($args['tformat'], ceil($properties['clients']['expiry']/1000));
                  foreach($properties['clients']['clients'] as $key=>$client){
                    if(is_array($client)){
                  	  $properties['clients']['clients'][$key]['expiry']=date($args['tformat'], ceil($client['expiry']/1000));
                    }
                  }                  	
                }                  
              }
              
              if($properties!==false){
                if($args['command']==HCE_CLUSTER_CMD_NODE_PROPERTIES){
                  //Extended format of Sphinx FO properties as key-value array
                  if(isset($args['sphinx_properties_formatted']) && $args['sphinx_properties_formatted']=='yes' && isset($properties['sphinxDataStorageProperties'])){
                    $props=explode(',', $properties['sphinxDataStorageProperties']);
                    $properties['sphinxDataStorageProperties']=array();
                    foreach($props as $value){
                      $props2=explode(':', $value);
                      //$properties['sphinxDataStorageProperties'][$props2[0]]=$props2[1];
                      if($props2[0]=='ranker_expression'){
                        $properties['sphinxDataStorageProperties'][$props2[0]]=rawurldecode($props2[1]);
                      }else{
                        $properties['sphinxDataStorageProperties'][$props2[0]]=$props2[1];
                      }
                    }
                  }
                  //Extended format of DRCE FO properties as key-value array
                  if(isset($args['sphinx_properties_formatted']) && $args['sphinx_properties_formatted']=='yes' && isset($properties['drceDataStorageProperties'])){
                    $props=explode(',', $properties['drceDataStorageProperties']);
                    $properties['drceDataStorageProperties']=array();
                    foreach($props as $value){
                      $props2=explode(':', $value);
                      $properties['drceDataStorageProperties'][$props2[0]]=$props2[1];
                    }
                  }
                  $ret[$node][$handlers_list[$i]]=$properties;
                }else{
                  if(isset($properties[HCE_CLUSTER_CMD_PROPERTY_NAME_LOG])){
                    $ret[$node][$handlers_list[$i]]=$properties[HCE_CLUSTER_CMD_PROPERTY_NAME_LOG];
                  }else{

                  }
                }
              }else{

              }
              
            }else{
              $ret[$node][$handlers_list[$i]]='Error : '.$ret[$node][$handlers_list[$i]]['error'];
            }
          }else{

          }
        }else{
          $ret[$node][$handlers_list[$i]]='Error : Node not found at '.$node.' or connection timeout.';
        }
      }
    }
    echo cli_prettyPrintJson(json_encode($ret), ' ').PHP_EOL;

    $command_category=1;
    break;
  }
  case HCE_CLUSTER_CMD_NODE_DRCE            : {
    require_once '../inc/hce_drce_api.inc.php';
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
    }else{
      if(!isset($args['request']) || !isset($args['id']) || !isset($args['json'])){
        $aborted='--request, --json and --id is mandatory options for this command!';
        break;
      }
      $REQUEST_TYPE=isset($args['request']) ? $args['request'] : 'CHECK';
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
          $REQUEST_ID=crc32(hce_unique_message_id(1, microtime(true)));
        }
      }
      $input_json=trim(file_get_contents($args['json']));
      if($args['log']>2){
        echo 'Input file json: "'.$input_json.'"'.PHP_EOL;
      }
      $params_array=hce_drce_exec_create_parameters_array($input_json, $REQUEST_TYPE);
      if($args['log']>2){
        echo 'Parameters array: "'.var_export($params_array, TRUE).'"'.PHP_EOL;
      }
      $parameters=hce_drce_exec_prepare_request_admin($params_array, $REQUEST_TYPE, $REQUEST_ID);
      if($args['log']>2){
        echo 'DRCE reques json: "'.$parameters.'"'.PHP_EOL.PHP_EOL;
      }
      $nodes=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_PROCESSOR_DATA, HCE_CLUSTER_CMD_NODE_DRCE, $parameters);
      //Parse responses jsons           
      foreach($nodes as $node_key=>$node_data){       	     	
        if(isset($node_data[HCE_HANDLER_DATA_PROCESSOR_DATA])){
          $node_data[HCE_HANDLER_DATA_PROCESSOR_DATA]=explode(HCE_ADMIN_CMD_DELIMITER, $node_data[HCE_HANDLER_DATA_PROCESSOR_DATA]);
          if(isset($node_data[HCE_HANDLER_DATA_PROCESSOR_DATA][1])){     	
            $node_data[HCE_HANDLER_DATA_PROCESSOR_DATA][1]=json_decode($node_data[HCE_HANDLER_DATA_PROCESSOR_DATA][1], true);
            $node_data[HCE_HANDLER_DATA_PROCESSOR_DATA][1][0]['stdout']=base64_decode($node_data[HCE_HANDLER_DATA_PROCESSOR_DATA][1][0]['stdout']);
            $node_data[HCE_HANDLER_DATA_PROCESSOR_DATA][1][0]['stderror']=base64_decode($node_data[HCE_HANDLER_DATA_PROCESSOR_DATA][1][0]['stderror']);
          }
          $nodes[$node_key]=$node_data[HCE_HANDLER_DATA_PROCESSOR_DATA];
        }
      }

      echo cli_prettyPrintJson(json_encode($nodes), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  case HCE_CMD_DRCE_SET_HOST       : {
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
		}else if(!isset($args['host'])){
      $aborted='--host must be set value different from zero';
    }else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_PROCESSOR_DATA, HCE_CMD_DRCE_SET_HOST, $args['host']);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  case HCE_CMD_DRCE_GET_HOST       : {
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
    }else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_PROCESSOR_DATA, HCE_CMD_DRCE_GET_HOST);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  case HCE_CMD_DRCE_SET_PORT       : {
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
		}else if(!isset($args['port'])){
      $aborted='--port must be set value different from zero';
    }else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_PROCESSOR_DATA, HCE_CMD_DRCE_SET_PORT, $args['port']);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  case HCE_CMD_DRCE_GET_PORT       : {
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
    }else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_PROCESSOR_DATA, HCE_CMD_DRCE_GET_PORT);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  case HCE_CMD_DRCE_GET_TASKS        : {
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
    }else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_PROCESSOR_DATA, HCE_CMD_DRCE_GET_TASKS);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  case HCE_CMD_DRCE_GET_TASKS_INFO			: {
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
    }else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_PROCESSOR_DATA, HCE_CMD_DRCE_GET_TASKS_INFO);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  case HCE_CMD_NODE_RECOVER_NOTIFICATION_CONNECTION			: {
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
    }else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_PROCESSOR_DATA, HCE_CMD_NODE_RECOVER_NOTIFICATION_CONNECTION);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  case HCE_CMD_NODE_ROUTES			: {
    if($args['scan']==1 && count($hosts)!=count($ports)){
      $aborted='--host and --port must to list the same number of items if --scan=1';
    }else{
      $r=hce_manage_command_cluster_node_handler_command($args, HCE_HANDLER_DATA_SERVER_PROXY, HCE_CMD_NODE_ROUTES);
      echo cli_prettyPrintJson(json_encode($r), ' ').PHP_EOL;
    }
    $command_category=1;
    break;
  }
  default : {
    $aborted='command "'.$args['command'].'" not supported';    
    break;
  }
}

if($aborted=='' && $command_category==0){
  $connection_array=hce_connection_create(array('host'=>$args['host'], 'port'=>$args['port'], 'type'=>HCE_CONNECTION_TYPE_ADMIN, 'identity'=>hce_unique_client_id()));
  if($connection_array['error']==0){
    $ret=hce_sphinx_exec($args['command'], $options_array, $connection_array, $args['timeout']);
    if(!is_array($ret)){
      echo 'Error of command execution '.$ret.PHP_EOL;
      switch($ret){
        case HCE_PROTOCOL_ERROR_TIMEOUT      : {
          echo 'Timeout '.$args['timeout'].' ms, or connection error!'.PHP_EOL;
          break;
        }
        case HCE_SPHINX_ERROR_PARSE_RESPONSE : {
          echo 'Wrong response format!'.PHP_EOL;
          break;
        }
      }
    }else{
      echo 'Command executed '.PHP_EOL;
      if($ret['error_code']!=HCE_SPHINX_ERROR_OK){
        echo 'Returned error '.$ret['error_code'].' : '.$ret['error_message'].PHP_EOL;
        if(!empty($ret['data'])){
          if(SPHINX_JSON_USE_BASE64){
            echo 'data: '.base64_decode($ret['data']).PHP_EOL;
          }else{
            echo 'data: '.$ret['data'].PHP_EOL;
          }
        }
      }else{
        switch($args['command']){
          case HCE_SPHINX_CMD_INDEX_DATA_LIST         :
          case HCE_SPHINX_CMD_INDEX_MERGE             :
          case HCE_SPHINX_CMD_INDEX_PACK_DOC_DATA     :
          case HCE_SPHINX_CMD_INDEX_DELETE_DOC_NUMBER :
          case HCE_SPHINX_CMD_INDEX_STATUS_SEARCHD    :
          case HCE_SPHINX_CMD_INDEX_STATUS            :
          case HCE_SPHINX_CMD_INDEX_MAX_DOC_ID        :
          case HCE_SPHINX_CMD_INDEX_CHECK             : {
            if(SPHINX_JSON_USE_BASE64){
              echo 'data: '.base64_decode($ret['data']).PHP_EOL;
            }else{
              echo 'data: '.$ret['data'].PHP_EOL;
            }
          }
        }
      }
      echo 'time: '.$ret['time'].' ms'.PHP_EOL;
    }
    hce_connection_delete($connection_array);
  }else{
    echo 'Error create acn connection '.$connection_array['error'].$ret.PHP_EOL;
  }
}else if($aborted!==''){
  echo $aborted.' required'.PHP_EOL;
}

exit();

?>
