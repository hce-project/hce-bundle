<?php
/**
 * HCE project key-value db manager API.
 * Samples of implementation of basic client-side API for kv-db manager.
 *
 * @author bgv <bgv.hce@gmail.com>
 * @link http://hierarchical-cluster-engine.com/
 * @copyright Copyright &copy; 2013-2014 IOIX Ukraine
 * @license http://hierarchical-cluster-engine.com/license/
 * @package HCE tools utilities API
 * @since 0.1


/**
 * Define and init Sphinx FO encode base64 usage, 0 - not used, 1 - used
 */
defined('JSON_USE_BASE64') or define('JSON_USE_BASE64', 1);

/**
 * Define and init kv-db http request timeout ms.
 */
defined('HCE_KVDB_TIMEOUT') or define('HCE_KVDB_TIMEOUT', 1500);

/**
 * Define and init kv-db error codes.
 */
defined('HCE_KVDB_ERROR_OK') or define('HCE_KVDB_ERROR_OK', 0);
defined('HCE_KVDB_ERROR_CREATE_MESSAGE') or define('HCE_KVDB_ERROR_CREATE_MESSAGE', -100);
defined('HCE_KVDB_ERROR_PARSE_RESPONSE') or define('HCE_KVDB_ERROR_PARSE_RESPONSE', -101);
defined('HCE_KVDB_ERROR_WRONG_CONNECTION_ARRAY') or define('HCE_KVDB_ERROR_WRONG_CONNECTION_ARRAY', -102);
defined('HCE_KVDB_ERROR_WRONG_REQUEST_ARRAY') or define('HCE_KVDB_ERROR_WRONG_REQUEST_ARRAY', -103);
defined('HCE_KVDB_ERROR_WRONG_PARAMETERS') or define('HCE_KVDB_ERROR_WRONG_PARAMETERS', -105);

/**
 * Define and init kv-db http request names.
 */
defined('HCE_KVDB_CMD_PUT') or define('HCE_KVDB_CMD_PUT', '0');
defined('HCE_KVDB_CMD_GET') or define('HCE_KVDB_CMD_GET', '1');
defined('HCE_KVDB_CMD_DELETE') or define('HCE_KVDB_CMD_DELETE', '2');
defined('HCE_KVDB_CMD_CHECK') or define('HCE_KVDB_CMD_CHECK', '3');
defined('HCE_KVDB_CMD_MANAGE') or define('HCE_KVDB_CMD_MANAGE', '4');
defined('HCE_KVDB_CMD_NAME') or define('HCE_KVDB_CMD_NAME', '0');

/**
 * Define and init kv-db http request protocol json fields names
 */
defined('HCE_KVDB_FIELD_TYPE') or define('HCE_KVDB_FIELD_TYPE', 'type');
defined('HCE_KVDB_FIELD_DATA') or define('HCE_KVDB_FIELD_DATA', 'data');
defined('HCE_KVDB_FIELD_DOCUMENTS') or define('HCE_KVDB_FIELD_DOCUMENTS', 'documents');
defined('HCE_KVDB_FIELD_ERROR_CODE') or define('HCE_KVDB_FIELD_ERROR_CODE', 'error_code');
defined('HCE_KVDB_FIELD_ERROR_MSG') or define('HCE_KVDB_FIELD_ERROR_MSG', 'error_message');
defined('HCE_KVDB_FIELD_TIME') or define('HCE_KVDB_FIELD_TIME', 'time');

/**
 * Define and init kv-db http request connection array
 */
defined('HCE_KVDB_CA_URL') or define('HCE_KVDB_CA_URL', 'url');
defined('HCE_KVDB_CA_TIMEOUT') or define('HCE_KVDB_CA_TIMEOUT', 'timeout');
defined('HCE_KVDB_HTTP_POST_FIELD_NAME') or define('HCE_KVDB_HTTP_POST_FIELD_NAME', 'data');

/**
 * Define and init kv-db import functionality definitions
 */
defined('HCE_KVDB_IMPORT_TYPE_XML') or define('HCE_KVDB_IMPORT_TYPE_XML', 0);
defined('HCE_KVDB_IMPORT_TYPE_JSON') or define('HCE_KVDB_IMPORT_TYPE_JSON', 1);

/**
 * Define and init kv-db highlighter options
 */
defined('HCE_KVDB_HIGHLIGHTER_HASH_FIELD_SUFFIX') or define('HCE_KVDB_HIGHLIGHTER_HASH_FIELD_SUFFIX', '_HIGHLIGHTER_HASH');

/*
 * @desc send kv-db manager http request and parse result
 * @param $request_array - array with command code and items defined by interation json protocol specification
 *        $connection_array - connection array for http-based request array('host'=>'localhost', 'port'=>'2222', 'timeout'=>HCE_KVDB_TIMEOUT)
 *
 * @return ACN kv-db manager API result array based on response protocol json object specification
 */
 function HCE_KVDB_request($request_array, $connection_array=null){
   //Init returned ACN KV_DB API result array
   $ret=array('error'=>HCE_KVDB_ERROR_OK, 'error_msg'=>'', 'response'=>null);

   if(!isset($connection_array['url'], $connection_array['timeout'])){
     //Wrong connection array
     $ret['error']=HCE_KVDB_ERROR_WRONG_CONNECTION_ARRAY;
   }else{
     if(!isset($request_array['type'], $request_array['data'])){
       //The command json is empty or not set
       $ret['error']=HCE_KVDB_ERROR_WRONG_REQUEST_ARRAY;
     }else{
       //HTTP request POST method using curl
       $ch=curl_init();

       curl_setopt($ch, CURLOPT_URL, $connection_array['url']);
       curl_setopt($ch, CURLOPT_POST, true);
       curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, $connection_array['timeout']);
       curl_setopt($ch, CURLOPT_TIMEOUT, $connection_array['timeout']);
       curl_setopt($ch, CURLOPT_POSTFIELDS, HCE_KVDB_prepare_post_request($request_array));
       curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

       $ret['response']=curl_exec($ch);
       $ret['error']=curl_errno($ch);
       $ret['error_msg']=curl_error($ch);

       curl_close($ch);
     }
   }

   return $ret;
 }

/*
 * @desc create ACN kv-db manager request in HTTP POST format
 * @param $request_array - array of items to construct json request object according with protocol specification;
 *
 * @return ACN HTTP POST request string
 */
 function HCE_KVDB_prepare_post_request($request_array){
   //Encode for POCO json implementation compatibility reason
   return http_build_query(array(HCE_KVDB_HTTP_POST_FIELD_NAME=>json_encode($request_array)));
 }

/*
 * @desc parse ACN kv-db manager response in json format
 * @param $response_body - content of response json string
 *
 * @return ACN ACN kv-db manager request response array
 */
 function HCE_KVDB_parse_response($response_body){
   return json_decode($response_body, true);
 }

/*
 * @desc create ACN kv-db manager request array
 * @param $type - request type {'0' - put, '1' - get, '2' - delete, '3' - check}
 *        $documents - array of items, depends on type
 *
 * @return ACN request array
 */
 function HCE_KVDB_prepare_request_array($type, $documents){
   $ret=array(HCE_KVDB_FIELD_TYPE=>HCE_KVDB_CMD_PUT, HCE_KVDB_FIELD_DATA=>null);

   switch($type){
     case HCE_KVDB_CMD_GET     : {
       $ret[HCE_KVDB_FIELD_TYPE]=HCE_KVDB_CMD_GET;
       $ret[HCE_KVDB_FIELD_DATA]=array(HCE_KVDB_FIELD_DOCUMENTS=>json_encode($documents));
       break;
     }
     case HCE_KVDB_CMD_DELETE  : {
       $ret[HCE_KVDB_FIELD_TYPE]=HCE_KVDB_CMD_DELETE;
       $ret[HCE_KVDB_FIELD_DATA]=array(HCE_KVDB_FIELD_DOCUMENTS=>json_encode($documents));
       break;
     }
     case HCE_KVDB_CMD_CHECK   : {
       $ret[HCE_KVDB_FIELD_TYPE]=HCE_KVDB_CMD_CHECK;
       $ret[HCE_KVDB_FIELD_DATA]=array(HCE_KVDB_FIELD_DOCUMENTS=>json_encode($documents));
       break;
     }
     case HCE_KVDB_CMD_MANAGE  : {
       $ret[HCE_KVDB_FIELD_TYPE]=HCE_KVDB_CMD_MANAGE;
       $ret[HCE_KVDB_FIELD_DATA]=array(HCE_KVDB_FIELD_DOCUMENTS=>json_encode($documents));
       break;
     }
     case HCE_KVDB_CMD_PUT     :
     default : {
       $ret[HCE_KVDB_FIELD_TYPE]=HCE_KVDB_CMD_PUT;
       $ret[HCE_KVDB_FIELD_DATA]=array(HCE_KVDB_FIELD_DOCUMENTS=>json_encode($documents));
       break;
     }
   }

   return $ret;
 }

/*
 * @desc imports documents from xml file prepared for Sphinx indexation
 * @param $file - xml file source
 *
 * @return documents array in format array('document_id'=>document_fields_array, ...)
 */
 function HCE_KVDB_import_from_xml_file($file){
   //Supported fields names
   $XML_DOC_FIELDS_NAMES=array('TITLE', 'H', 'ALT', 'BODYS', 'BODYN', 'META', 'REF', 'URL', 'CDATE', 'MMEDIA', 'CTYPES', 'BSEO', 'UID', 'SID', 'LANG');
   for($i=0; $i<8; $i++){
     $XML_DOC_FIELDS_NAMES[]='AFFLAGS'.$i;
   }
   for($i=0; $i<8; $i++){
     $XML_DOC_FIELDS_NAMES[]='AFFLAGS'.$i.'EX';
   }

   //Init returned documents array
   $ret=array();

   //Get documents from xmlstorage
   $p=xml_parser_create();
   xml_parse_into_struct($p, file_get_contents($file), $vals, $index);
   xml_parser_free($p);

   $resources=array();

   foreach($index['SPHINX:DOCUMENT'] as $doc_index){
     if(isset($vals[$doc_index]['attributes']['ID'])){
       $resources[]['Id']=$vals[$doc_index]['attributes']['ID'];
     }
   }
   foreach($XML_DOC_FIELDS_NAMES as $name){
     foreach($index[$name] as $item_index=>$doc_index){
       if(isset($vals[$doc_index]['value'])){
         $resources[$item_index][$name]=$vals[$doc_index]['value'];
       }else{
         $resources[$item_index][$name]='';
       }
     }
   }

   foreach($resources as $resource){
     $fields=array();
     foreach($XML_DOC_FIELDS_NAMES as $name){
       $fields[$name]=$resource[$name];
     }
     $ret[$resource['Id']]=$fields;
   }

   return $ret;
 }

/*
 * @desc imports documents from json file
 * @param $file - json file source
 *
 * @return documents array in format array('document_id'=>document_fields_array, ...)
 */
 function HCE_KVDB_import_from_json_file($file){
   //Init returned documents array
   $ret=array();

   //TODO: import from json file implementation

   return $ret;
 }

/*
 * @desc add highlight hashes to the document's fields sets by call highlighter utility for each document
 * @param $file - json file source
 *
 * @return documents array in format array('document_id'=>document_fields_array, ...)
 */
 function HCE_KVDB_highlight_hashes_add($documents, $command, $log=0, $timeout=HCE_HLTR_FIELD_TIMEOUT_DEFAULT, $fields_to_highlight=array('TITLE', 'H', 'ALT', 'BODYS', 'BODYN', 'META', 'REF', 'URL')){
   //Init returned documents array
   $ret=$documents;
   $time_start=microtime(true);

   $contents_to_highlight=array();
   foreach($documents as $id=>$document){
     //Collect all fields that need to be highlighted
     foreach($document as $field_name=>$field_value){
       //Collect only supported fields
       if(in_array($field_name, $fields_to_highlight)){
         //$contents_to_highlight[]=array((JSON_USE_BASE64 ? base64_encode($field_value) : $field_value), '');
         $contents_to_highlight[]=array($field_value, '');
       }
     }
   }

   if(count($contents_to_highlight)>0){
     //Prepare request to highlighter utility
     $params=array(HCE_HLTR_FIELD_RETURN_HASH=>true);
     $hrequest=HCE_HLTR_prepare_request_array($params, $contents_to_highlight);

     $time_start=microtime(true);
     //Call the highlighter
     $hresponse=HCE_HLTR_request($hrequest, $command);
//echo 'time:'.(microtime(true)-$time_start).PHP_EOL.'-------------'.PHP_EOL.var_dump($hresponse).PHP_EOL.'-------------'.PHP_EOL; flush();
     if($hresponse[HCE_HLTR_FIELD_ERROR_CODE]==HCE_HLTR_ERROR_OK){
       //Resource's fields decomposition
       $i=0;
       foreach($documents as $id=>$document){
         foreach($document as $field_name=>$field_value){
           //Set hash only for supported field
           if(in_array($field_name, $fields_to_highlight)){
             $document[$field_name.HCE_KVDB_HIGHLIGHTER_HASH_FIELD_SUFFIX]=$hresponse[HCE_HLTR_FIELD_CONTENTS][$i++][1];
           }
         }
         $documents[$id]=$document;
       }
       //Set document array with added field
       $ret[$id]=$document;
     }else{
       if($log>0){
         echo 'Highlight resource '.$id.' error'.$hresponse[HCE_HLTR_FIELD_ERROR_CODE].PHP_EOL.$hresponse[HCE_HLTR_FIELD_ERROR_MSG].PHP_EOL;
         flush();
       }
     }
   }

   return $ret;
 }

?>