<?php
/**
 * HCE project minor php API for cli applications.
 *
 * @author bgv <bgv.hce@gmail.com>
 * @link http://hierarchical-cluster-engine.com/
 * @copyright Copyright &copy; 2013-2014 IOIX Ukraine
 * @license http://hierarchical-cluster-engine.com/license/
 * @package HCE php cli API
 * @since 0.1
*/

/**
 * Define and init cli request file i/o statement
 */
defined('HCE_CLI_READ_FROM_FILE_STATEMENT') or define('HCE_CLI_READ_FROM_FILE_STATEMENT', 'READ_FROM_FILE:');


function cli_parse_arguments($argv) {
  $_ARG = array();
  foreach ($argv as $arg) {
    if (preg_match('/--([^=]+)=(.*)/',$arg,$reg)) {
      $_ARG[$reg[1]] = $reg[2];
    } elseif(preg_match('/-([a-zA-Z0-9])/',$arg,$reg)) {
      $_ARG[$reg[1]] = 'true';
    }
  }

  return $_ARG;
}

function cli_prettyPrintJson( $json, $left_ident="\t" ){
  $result = '';
  $level = 0;
  $prev_char = '';
  $in_quotes = false;
  $ends_line_level = NULL;
  $json_length = strlen( $json );

  for( $i = 0; $i < $json_length; $i++ ) {
      $char = $json[$i];
      $new_line_level = NULL;
      $post = "";
      if( $ends_line_level !== NULL ) {
          $new_line_level = $ends_line_level;
          $ends_line_level = NULL;
      }
      if( $char === '"' && $prev_char != '\\' ) {
          $in_quotes = !$in_quotes;
      } else if( ! $in_quotes ) {
          switch( $char ) {
              case '}': case ']':
                  $level--;
                  $ends_line_level = NULL;
                  $new_line_level = $level;
                  break;

              case '{': case '[':
                  $level++;
              case ',':
                  $ends_line_level = $level;
                  break;

              case ':':
                  $post = " ";
                  break;

              case " ": case "\t": case "\n": case "\r":
                  $char = "";
                  $ends_line_level = $new_line_level;
                  $new_line_level = NULL;
                  break;
          }
      }
      if( $new_line_level !== NULL ) {
          $result .= PHP_EOL.str_repeat( $left_ident, $new_line_level );
      }
      $result .= $char.$post;
      $prev_char = $char;
  }

  return $result;
}

function cli_getScreenSize(){
 $ret=array('width'=>0, 'height'=>0);

 preg_match_all("/rows.([0-9]+);.columns.([0-9]+);/", strtolower(exec('stty -a | grep columns')), $output);

 if(sizeof($output) == 3) {
   $ret['width'] = $output[1][0];
   $ret['height'] = $output[2][0];
 }

 return $ret;
}

function cli_getASCIITreeFromArray($array, $params=null) {
 $res='';

 if($params==null){
   $params=array();
 }

 if(!isset($params['whitespace_char'])){
   //Space fill separator string
   $params['whitespace_char']=' ';
 }
 if(!isset($params['interrow_ident'])){
   //Inter row ident lines number
   $params['interrow_ident']=0;
 }
 if(!isset($params['hline_char'])){
   //Inter row ident lines number
   $params['hline_char']='_';
 }
 if(!isset($params['vline_char'])){
   //Inter row ident lines number
   $params['vline_char']='|';
 }
 if(!isset($params['max_width'])){
   //Max width in characters
   $params['max_width']=80;
 }
 if(!isset($params['item_hident'])){
   //Max width in characters
   $params['item_hident']=1;
 }

 //Get max number of items on one level
 $getMaxItems = function($arr) use(&$getMaxItems){
   $n=0;

   foreach($arr as $val){
     if(is_array($val)){
       $n+=$getMaxItems($val);
     }else{
       $n++;
     }
   }

   return $n;
 };

 $maxItemsOnOneLevel=$getMaxItems($array);

 //Get total width of titles items in characters on all levels
 $getTotalWidth = function($arr) use(&$getTotalWidth){
   $n=0;

   foreach($arr as $key=>$val){
     if(is_array($val)){
       $n+=$getTotalWidth($val);
     }else{
       $n+=strlen($key);
     }
   }

   return $n;
 };

 $totalWidth=$getTotalWidth($array);

 //Get max length of string array
 $getMaxLength = function($arr){
   if(!empty($arr)){
 	 $lengths=array_map('strlen', $arr);
   }else{
   	 $lengths=0;
   }

   return max($lengths);
 };

 //Space per item
 $params['max_space_per_item']=floor(($params['max_width']-$totalWidth)/($maxItemsOnOneLevel<1 ? 1 : $maxItemsOnOneLevel))-$params['item_hident'];
 $params['max_space_per_item']=($params['max_space_per_item']<1) ? 1: $params['max_space_per_item'];

 //Get max title width
 $getMaxTitleWidth = function($arr) use(&$getMaxTitleWidth){
  static $maxWidth=0;

  foreach($arr as $key=>$val){
  	$lines=explode(PHP_EOL, $key);
  	foreach($lines as $line){
      if(strlen($line)>$maxWidth){
  		$maxWidth=strlen($line);
  	  }
  	}

    if(is_array($val)){
 	  $getMaxTitleWidth($val);
    }
  }

  return $maxWidth;
 };

 //Get max title lines
 $getMaxTitleLines = function($arr) use(&$getMaxTitleLines){
  static $maxLines=0;

  foreach($arr as $key=>$val){
   	$lines=substr_count($key, PHP_EOL)+1;
  	if($lines>$maxLines){
      $maxLines=$lines;
  	}

    if(is_array($val)){
 	  $getMaxTitleLines($val);
    }
  }

  return $maxLines;
 };

 //Fix title lines number and width
 $fixTitleLinesWidth = function($arr, $titleLines, $titleWidth) use(&$fixTitleLinesWidth){
   $ret=array();

  if(is_array($arr)){
    foreach($arr as $key=>$val){
      $lines=explode(PHP_EOL, $key);
      //Fix lines lenght
      foreach($lines as $lineKey=>$line){
        if(strlen($line)<$titleWidth){
          $diff=$titleWidth-strlen($line);
          $lines[$lineKey]=str_repeat(' ', ceil($diff/2)).$line.str_repeat(' ', floor($diff/2));
  	    }
      }
      //Fix lines number
      for($i=0; $i<$titleLines-count($lines); $i++){
      	$lines[]=str_repeat(' ', $titleWidth);
      }
      //Pack lines
      $ret[implode(PHP_EOL, $lines)]=$fixTitleLinesWidth($val, $titleLines, $titleWidth);
    }
  }else{
  	$ret=$arr;
  }

  return $ret;
 };

 //Generate text stream
 $getTreeChartArray = function($arr, $params, $offset=0) use(&$getTreeChartArray, &$getMaxLength){
   static $level=0;

   $level++;

   $ret=array();

   if($level==1){
   	$first=true;
   }else{
   	$first=false;
   }

   $i=0;
   $lastNodeStrLen=0;
   $ret1=array();
   $titles=array();
   $vlines=str_repeat($params['whitespace_char'], $offset);
   $hlines=str_repeat($params['whitespace_char'], $offset);
   $vlines2=str_repeat($params['whitespace_char'], $offset);

   foreach($arr as $key=>$val){
     $lines=explode(PHP_EOL, $key);

     if(count($titles)==0){
       //Init titles lines array
       foreach($lines as $line){
         $titles[]=str_repeat($params['whitespace_char'], $offset);
       }
     }

     $lastNodeStrLen=count($ret1)>0 ? $getMaxLength($ret1) : strlen($titles[0]);
     if(is_array($val)){
       $ret1=array_merge($ret1, $getTreeChartArray($val, $params, $lastNodeStrLen));
     }
     if($i==0){
       $offset1=0;
     }else{
       $offset1=($lastNodeStrLen-strlen($titles[0]))>0 ? ($lastNodeStrLen-strlen($titles[0])) : $params['max_space_per_item'];
     }

     for($j=0; $j<count($lines); $j++){
       $titles[$j].=str_repeat($params['whitespace_char'], $offset1).$lines[$j];
     }

     if($val!==null){
       $vline_char=$params['vline_char'];
     }else{
       $vline_char=$params['whitespace_char'];
     }
     $chars=$offset1+((strlen($lines[0])/2)-1);
     if($chars<0){
       $chars=0;
     }
     $vlines.=str_repeat($params['whitespace_char'], $chars).$vline_char.str_repeat($params['whitespace_char'], ((strlen($lines[0])/2)));

     if(!$first){
       if(count($arr)>1){
       	 $vlines2.=str_repeat($params['whitespace_char'], $offset1+((strlen($lines[0])/2)-1)).$params['vline_char'].str_repeat($params['whitespace_char'], ((strlen($lines[0])/2)));

         if($i==0){
           $hlines.=str_repeat($params['whitespace_char'], $offset1+(strlen($lines[0])/2)).str_repeat($params['hline_char'], strlen($lines[0])/2);
         }else{
     	   $hlines.=str_repeat($params['hline_char'], strlen($vlines2)-strlen($hlines)-(strlen($lines[0])/2));
         }
         $hlines=substr($hlines, 0, strlen($hlines)-1);
       }else{
         //$hlines=$vlines;
       }
     }

     $i++;
   }

   $ret[]=$hlines;
   $ret[]=$vlines2;
   foreach($titles as $titles_key=>$titles_value){
   	 $titles[$titles_key]=rtrim($titles_value);
   }
   $ret[]=implode(PHP_EOL, $titles);
   $ret[]=$vlines;
   $ret=array_merge($ret, $ret1);

   return $ret;
 };

 $maxTitleWidth=$getMaxTitleWidth($array);
 if($maxTitleWidth%2>0){
   $maxTitleWidth++;
 }

 $maxTitleLines=$getMaxTitleLines($array);

 $array=$fixTitleLinesWidth($array, $maxTitleLines, $maxTitleWidth);

 $res=$getTreeChartArray($array, $params);

 //Trim lines
 for($i=0; $i<count($res); $i++){
   $res[$i]=rtrim($res[$i]);
 }

 //Add vlines for down nodes
 for($i=0; $i<count($res)-1; $i++){
   $p=0;
   while(($p=strpos($res[$i], $params['vline_char'], $p))!==false){
     if(strlen($res[$i+1])<$p){
       $res[$i+1].=str_repeat($params['whitespace_char'], $p-strlen($res[$i+1])).$params['vline_char'];
     }
     $p++;
   }
 }

 //Remove duplicated lines
 do{
   $new_res=array();
   $duplicates=0;
   for($i=0; $i<count($res)-1; $i++){
     if($res[$i]!=$res[$i+1]){
   	   $new_res[]=$res[$i];
     }else{
       $duplicates++;
     }
   }
   $new_res[]=$res[$i];
   $res=$new_res;
 }while($duplicates>0);

 return implode(PHP_EOL, $new_res);
}


function file_get_contents_json($input, $statement=HCE_CLI_READ_FROM_FILE_STATEMENT, $error_message='File not found:'){
  $content=$input;
  $statement_len=strlen($statement);

  if(is_string($input)){
    if(strlen($input)>$statement_len && substr($input, 0, $statement_len)==$statement){
      $file_name=substr($input, $statement_len);
      if(file_exists($file_name)){
        $content=file_get_contents($file_name);
        $content=@json_decode($content, true);
        $content=file_get_contents_json($content);
      }else{
        if(strlen($error_message)>0){
          $content=$error_message.$file_name;
        }
      }
    }
  }elseif(is_array($input)){
    foreach($input as $key=>$val){
      $input[$key]=file_get_contents_json($val);
    }
    $content=$input;
  }

  return $content;
}

?>