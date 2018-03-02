<?php
/**
 * HCE project key-value db manager API.
 * Samples of implementation of basic client-side API for highlighter manager.
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
 * Define and init highlighter http request timeout ms.
 */
defined('HCE_HLTR_TIMEOUT') or define('HCE_HLTR_TIMEOUT', 1500);
defined('HCE_HLTR_INPUT_STREAM_END_CHAR') or define('HCE_HLTR_INPUT_STREAM_END_CHAR', chr(7));

/**
 * Define and init highlighter error codes.
 */
defined('HCE_HLTR_ERROR_OK') or define('HCE_HLTR_ERROR_OK', 0);
defined('HCE_HLTR_ERROR_CREATE_MESSAGE') or define('HCE_HLTR_ERROR_CREATE_MESSAGE', -100);
defined('HCE_HLTR_ERROR_PARSE_RESPONSE') or define('HCE_HLTR_ERROR_PARSE_RESPONSE', -101);
defined('HCE_HLTR_ERROR_COMMAND_EXEC') or define('HCE_HLTR_ERROR_COMMAND_EXEC', -102);
defined('HCE_HLTR_ERROR_WRONG_REQUEST_ARRAY') or define('HCE_HLTR_ERROR_WRONG_REQUEST_ARRAY', -103);
defined('HCE_HLTR_ERROR_RESPONSE_JSON') or define('HCE_HLTR_ERROR_RESPONSE_JSON', -104);
defined('HCE_HLTR_ERROR_WRONG_PARAMETERS') or define('HCE_HLTR_ERROR_WRONG_PARAMETERS', -105);
defined('HCE_HLTR_ERROR_COMMAND_NOT_FOUND') or define('HCE_HLTR_ERROR_COMMAND_NOT_FOUND', -106);

/**
 * Define and init highlighter request message protocol json fields names
 */
defined('HCE_HLTR_FIELD_QUERY_STRING') or define('HCE_HLTR_FIELD_QUERY_STRING', 'q');
defined('HCE_HLTR_FIELD_RETURN_HASH') or define('HCE_HLTR_FIELD_RETURN_HASH', 'return_hash');
defined('HCE_HLTR_FIELD_CONTENTS') or define('HCE_HLTR_FIELD_CONTENTS', 'contents');
defined('HCE_HLTR_FIELD_PARAMETERS') or define('HCE_HLTR_FIELD_PARAMETERS', 'parameters');
defined('HCE_HLTR_FIELD_BEGIN_MARKER') or define('HCE_HLTR_FIELD_BEGIN_MARKER', 'begin_marker');
defined('HCE_HLTR_FIELD_END_MARKER') or define('HCE_HLTR_FIELD_END_MARKER', 'end_marker');
defined('HCE_HLTR_FIELD_MAX_NUMBER') or define('HCE_HLTR_FIELD_MAX_NUMBER', 'max_number');
defined('HCE_HLTR_FIELD_DELIMITERS') or define('HCE_HLTR_FIELD_DELIMITERS', 'delimiters');
defined('HCE_HLTR_FIELD_ACRONYMS') or define('HCE_HLTR_FIELD_ACRONYMS', 'acronyms');
defined('HCE_HLTR_FIELD_NUMBERS_AS_WORDS') or define('HCE_HLTR_FIELD_NUMBERS_AS_WORDS', 'numbers_as_words');
defined('HCE_HLTR_FIELD_USE_SINGLE_CHARS') or define('HCE_HLTR_FIELD_USE_SINGLE_CHARS', 'use_single_chars');
defined('HCE_HLTR_FIELD_ERROR_CODE') or define('HCE_HLTR_FIELD_ERROR_CODE', 'error_code');
defined('HCE_HLTR_FIELD_ERROR_MSG') or define('HCE_HLTR_FIELD_ERROR_MSG', 'error_msg');
defined('HCE_HLTR_FIELD_HIGHLIGHTED') or define('HCE_HLTR_FIELD_HIGHLIGHTED', 'highlighted');
defined('HCE_HLTR_FIELD_FOUND') or define('HCE_HLTR_FIELD_FOUND', 'found');
defined('HCE_HLTR_FIELD_TIME') or define('HCE_HLTR_FIELD_TIME', 'time');
defined('HCE_HLTR_FIELD_STD_ERROR') or define('HCE_HLTR_FIELD_STD_ERROR', 'std_error');
defined('HCE_HLTR_FIELD_RESPONSE_JSON_TEXT') or define('HCE_HLTR_FIELD_RESPONSE_JSON_TEXT', 'JSON_TEXT');

/**
 * Define and init highlighter request message protocol json fields values defaults
 */
defined('HCE_HLTR_FIELD_BEGIN_MARKER_DEFAULT') or define('HCE_HLTR_FIELD_BEGIN_MARKER_DEFAULT', '<font color="red">');
defined('HCE_HLTR_FIELD_END_MARKER_DEFAULT') or define('HCE_HLTR_FIELD_END_MARKER_DEFAULT', '</font>');
defined('HCE_HLTR_FIELD_MAX_NUMBER_DEFAULT') or define('HCE_HLTR_FIELD_MAX_NUMBER_DEFAULT', 1000);
defined('HCE_HLTR_FIELD_TIMEOUT') or define('HCE_HLTR_FIELD_TIMEOUT', 'timeout');
defined('HCE_HLTR_FIELD_TIMEOUT_DEFAULT') or define('HCE_HLTR_FIELD_TIMEOUT_DEFAULT', 60000);


/*
 * @desc send highlighter cli request and parse result
 * @param $request_array - array with items defined by interation json protocol specification
 *        $command - command line to run highlighter utility
 *        $environment - OS environment variables array in name=>value format
 *
 * @return ACN highlighter manager API result array based on response protocol json object specification
 */
 function HCE_HLTR_request($request_array, $command, $environment=array('LANGUAGE'=>'utf-8', 'LANG'=>'en_US.UTF-8', 'LESSCHARSET'=>'utf-8')){
   //Init returned ACN API result array
   $ret=array(HCE_HLTR_FIELD_ERROR_CODE=>HCE_HLTR_ERROR_OK, HCE_HLTR_FIELD_ERROR_MSG=>'', HCE_HLTR_FIELD_CONTENTS=>array(), HCE_HLTR_FIELD_HIGHLIGHTED=>'0',
              HCE_HLTR_FIELD_FOUND=>'0', HCE_HLTR_FIELD_TIME=>'0', HCE_HLTR_FIELD_STD_ERROR=>'', HCE_HLTR_FIELD_RESPONSE_JSON_TEXT=>'');

   //TODO $request_array format and fields set check

   if(!file_exists($command)){
     //Highlghter executable not found
     $ret[HCE_HLTR_FIELD_ERROR_CODE]=HCE_HLTR_ERROR_COMMAND_NOT_FOUND;
     $ret[HCE_HLTR_FIELD_ERROR_MSG]='Command "'.$command.'" not found';
   }else{
     $descriptorspec=array(
       0 => array("pipe", "r"),        // stdin is a pipe that the child will read from
       1 => array("pipe", "w"),        // stdout is a pipe that the child will write to
       2 => array("pipe", "w")         // stderr is a file to write to
     );
     $path=pathinfo($command, PATHINFO_DIRNAME).'/';
     //Exec child process
     $process=proc_open($command, $descriptorspec, $pipes, $path, $environment);

     if(is_resource($process)){
       //Write to handle connected to child stdin
//file_put_contents('/var/www/_cluster_search01/_highlighter_json_A.txt', json_encode($request_array));
       fwrite($pipes[0], json_encode($request_array).HCE_HLTR_INPUT_STREAM_END_CHAR);
       fclose($pipes[0]);
       //Read from handle connected to child stdout     
       $out=stream_get_contents($pipes[1]);
//file_put_contents('/var/www/_cluster_search01/_highlighter_json_out_A.txt', $out);
       fclose($pipes[1]);
       //Read from handle connected to child stderror
       $err=stream_get_contents($pipes[2]);
       fclose($pipes[2]);
       //Close process in order to avoid a deadlock
       $return_value=proc_close($process);

       //Return response array
       $r=@json_decode($out, true);
       if(is_array($r)){
         $ret=$r;
         $ret[HCE_HLTR_FIELD_STD_ERROR]=$err;
       }else{
         $ret[HCE_HLTR_FIELD_ERROR_CODE]=HCE_HLTR_ERROR_RESPONSE_JSON;
         $ret[HCE_HLTR_FIELD_ERROR_MSG]='Response json wrong format';
         $ret[HCE_HLTR_FIELD_RESPONSE_JSON_TEXT]=$out;
       }
     }else{
       //Process execution error
       $ret[HCE_HLTR_FIELD_ERROR_CODE]=HCE_HLTR_ERROR_COMMAND_EXEC;
       $ret[HCE_HLTR_FIELD_ERROR_MSG]='Process execution error, command "'.$command.'"';
     }
   }

   return $ret;
 }


/*
 * @desc create ACN highlighter utility request array
 * @param $parameters - request parameters fields array in format field_name=>value
 *        $contents - array of contents to highlight
 *
 * @return ACN request array
 */
 function HCE_HLTR_prepare_request_array($parameters, $contents=array()){
   //Init highlighter ACN API result array
   $ret=array(HCE_HLTR_FIELD_QUERY_STRING=>chr(7), HCE_HLTR_FIELD_RETURN_HASH=>false, HCE_HLTR_FIELD_CONTENTS=>array(), HCE_HLTR_FIELD_PARAMETERS=>array());

   //Check parameters fields
   if(!isset($parameters[HCE_HLTR_FIELD_RETURN_HASH])){
     $parameters[HCE_HLTR_FIELD_RETURN_HASH]=false;
   }
   if(!isset($parameters[HCE_HLTR_FIELD_BEGIN_MARKER])){
     $parameters[HCE_HLTR_FIELD_BEGIN_MARKER]=HCE_HLTR_FIELD_BEGIN_MARKER_DEFAULT;
   }
   if(!isset($parameters[HCE_HLTR_FIELD_END_MARKER])){
     $parameters[HCE_HLTR_FIELD_END_MARKER]=HCE_HLTR_FIELD_END_MARKER_DEFAULT;
   }
   if(!isset($parameters[HCE_HLTR_FIELD_MAX_NUMBER])){
     $parameters[HCE_HLTR_FIELD_MAX_NUMBER]=HCE_HLTR_FIELD_MAX_NUMBER_DEFAULT;
   }
   if(!isset($parameters[HCE_HLTR_FIELD_DELIMITERS])){
     $parameters[HCE_HLTR_FIELD_DELIMITERS]='';
   }
   if(!isset($parameters[HCE_HLTR_FIELD_ACRONYMS])){
     $parameters[HCE_HLTR_FIELD_ACRONYMS]='';
   }
   if(!isset($parameters[HCE_HLTR_FIELD_NUMBERS_AS_WORDS])){
     $parameters[HCE_HLTR_FIELD_NUMBERS_AS_WORDS]=true;
   }
   if(!isset($parameters[HCE_HLTR_FIELD_USE_SINGLE_CHARS])){
     $parameters[HCE_HLTR_FIELD_USE_SINGLE_CHARS]=true;
   }
   if(!isset($parameters[HCE_HLTR_FIELD_USE_SINGLE_CHARS])){
     $parameters[HCE_HLTR_FIELD_USE_SINGLE_CHARS]=true;
   }
   if(!isset($parameters[HCE_HLTR_FIELD_TIMEOUT])){
     $parameters[HCE_HLTR_FIELD_TIMEOUT]=HCE_HLTR_FIELD_TIMEOUT_DEFAULT;
   }

   if(isset($parameters[HCE_HLTR_FIELD_QUERY_STRING]) && $parameters[HCE_HLTR_FIELD_QUERY_STRING]!=''){
     $ret[HCE_HLTR_FIELD_QUERY_STRING]=$parameters[HCE_HLTR_FIELD_QUERY_STRING];
     unset($parameters[HCE_HLTR_FIELD_QUERY_STRING]);
   }
   if(isset($parameters[HCE_HLTR_FIELD_RETURN_HASH])){
     $ret[HCE_HLTR_FIELD_RETURN_HASH]=$parameters[HCE_HLTR_FIELD_RETURN_HASH];
     unset($parameters[HCE_HLTR_FIELD_RETURN_HASH]);
   }

   $ret[HCE_HLTR_FIELD_PARAMETERS]=$parameters;
   $ret[HCE_HLTR_FIELD_CONTENTS]=$contents;

   return $ret;
 }

?>