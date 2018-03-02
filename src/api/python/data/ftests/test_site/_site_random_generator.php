<?php
 @ini_set('max_execution_time', 120);
// @ini_set('memory_limit', '256M');

 @error_reporting(E_ALL);
 @ini_set('display_errors', 1);

// @error_reporting(0);
// @ini_set('display_errors', 0);

//Send cookie
 setcookie('TestCookie1', 'Value of cookie 1');
 setcookie('TestCookie2', 'Value of cookie 2', time()+3600);  /* expire in 1 hour */
 setcookie('TestCookie3', 'Value of cookie 3', time()+3600, "/dir1/", "127.0.0.1", 1);

 $LinksHREF='http://127.0.0.1/_site_random_generator.php?id=';

 $DataSourceType=1;         //0 - random generators, 1 - txt file lines
 $DataFilePath=dirname(__FILE__).'/_site_random_generator_data.txt';

 if($DataSourceType==0){    //0 - random generators, 1 - txt file
   $WordsBodyType=0;        //0 - numeric, 1 - alphabet, 2 - mixed, 3 - txt file lines
   $WordsTitleType=0;       //0 - numeric, 1 - alphabet, 2 - mixed, 3 - txt file lines

   $data_lines=array();

   $LinksMaxNumber=10;
   $LinksMaxWordsNumber=2;
   $LinksMinWordsNumber=1;
   $WordsLinksMaxChars=8;
   $WordsLinksMinChars=3;

   $WordsBodyMax=1024;
   $WordsBodyMin=512;
   $WordsBodyMaxChars=8;
   $WordsBodyMinChars=3;
   
   $WordsTitleMax=24;
   $WordsTitleMin=4;
   $WordsTitleMaxChars=8;
   $WordsTitleMinChars=3;
 }else{
   $WordsBodyType=3;
   $WordsTitleType=3;

   $data_lines=file($DataFilePath);
   $LinksMaxNumber=5;       //Max number of linked context block on page
   $LinksMaxWordsNumber=1;  //For file data source - max number of sets of lines
   $LinksMinWordsNumber=1;  //For file data source - min number of sets of lines
   $WordsLinksMaxChars=10;   //For file data source - max number of lines in set
   $WordsLinksMinChars=2;   //For file data source - min number of lines in set

   $WordsBodyMax=1;         //For file data source - max number of sets of lines
   $WordsBodyMin=1;
   $WordsBodyMaxChars=5;    //For file data source - max number of lines in set
   $WordsBodyMinChars=2;
   
   $WordsTitleMax=1;
   $WordsTitleMin=1;
   $WordsTitleMaxChars=5;
   $WordsTitleMinChars=3;
 }
 
 $ContextDataFiles['Title']=dirname(__FILE__).'/_site_random_generator_context_title.txt';
 $ContextDataFiles['Body']=dirname(__FILE__).'/_site_random_generator_context_body.txt';
 $ContextDataFiles['Links']=dirname(__FILE__).'/_site_random_generator_context_links.txt';
 $ContextDataFiles['WordsPerLineMin']=1;
 $ContextDataFiles['WordsPerLineMax']=3;
   
 $Delimiter=' ';
 $AcronimConcatChar=rawurldecode('%E2%88%A7');

 //Metadata set
 $MetadataBegin=rawurldecode('%E2%80%B9');
 $MetadataEnd=rawurldecode('%E2%80%BA');
 $MetadataText=' versioning'.$MetadataBegin.'{"normal":"VERSUS","pos":"2","lang":"33"}'.$MetadataEnd.' context aghtung'.$MetadataBegin.'{"normal":"FEUER","pos":"2","lang":"33"}'.$MetadataEnd.
               ' and based strings'.$MetadataBegin.'{"normal":"STR","pos":"2","lang":"1"}'.$MetadataEnd.' content ';

 $PageTemplate='<HTML><HEAD><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/><TITLE>test rest '.$MetadataText.' %TITLE%  And Legos. [Video] word'.$AcronimConcatChar.'test'.$AcronimConcatChar.'apple'.$AcronimConcatChar.'MAC '.$MetadataText.'</TITLE></HEAD><BODY><DIV>%LINKS%</DIV><P>%BODY%</P></BODY></HTML>';
 $LinkTemplate='<A href="%HREF%">%WORD%</A><BR>';

 function assign_rand_value($num){
  // accepts 1 - 36
  switch($num){
    case "1":
     $rand_value = "a";
    break;
    case "2":
     $rand_value = "b";
    break;
    case "3":
     $rand_value = "c";
    break;
    case "4":
     $rand_value = "d";
    break;
    case "5":
     $rand_value = "e";
    break;
    case "6":
     $rand_value = "f";
    break;
    case "7":
     $rand_value = "g";
    break;
    case "8":
     $rand_value = "h";
    break;
    case "9":
     $rand_value = "i";
    break;
    case "10":
     $rand_value = "j";
    break;
    case "11":
     $rand_value = "k";
    break;
    case "12":
     $rand_value = "l";
    break;
    case "13":
     $rand_value = "m";
    break;
    case "14":
     $rand_value = "n";
    break;
    case "15":
     $rand_value = "o";
    break;
    case "16":
     $rand_value = "p";
    break;
    case "17":
     $rand_value = "q";
    break;
    case "18":
     $rand_value = "r";
    break;
    case "19":
     $rand_value = "s";
    break;
    case "20":
     $rand_value = "t";
    break;
    case "21":
     $rand_value = "u";
    break;
    case "22":
     $rand_value = "v";
    break;
    case "23":
     $rand_value = "w";
    break;
    case "24":
     $rand_value = "x";
    break;
    case "25":
     $rand_value = "y";
    break;
    case "26":
     $rand_value = "z";
    break;
    case "27":
     $rand_value = "0";
    break;
    case "28":
     $rand_value = "1";
    break;
    case "29":
     $rand_value = "2";
    break;
    case "30":
     $rand_value = "3";
    break;
    case "31":
     $rand_value = "4";
    break;
    case "32":
     $rand_value = "5";
    break;
    case "33":
     $rand_value = "6";
    break;
    case "34":
     $rand_value = "7";
    break;
    case "35":
     $rand_value = "8";
    break;
    case "36":
     $rand_value = "9";
    break;
  }

  return $rand_value;
 }

 function get_rand_letters($length){
  if($length>0){ 
    $rand_id="";
    mt_srand((double)microtime() * 1000000);
    for($i=1; $i<=$length; $i++){
      $num=mt_rand(1, 26);
      $rand_id .= assign_rand_value($num);
    }
  }

  return $rand_id;
 }

 function get_rand_numbers($length){
  if($length>0){ 
    $rand_id="";
    mt_srand((double)microtime() * 1000000);
    for($i=1; $i<=$length; $i++){
      $num=mt_rand(27, 36);
      $rand_id .= assign_rand_value($num);
    }
  }

  return $rand_id;
 }

 function get_rand_mixed($length){
  if($length>0){ 
    $rand_id="";
    for($i=1; $i<=$length; $i++){
      mt_srand((double)microtime() * 1000000);
      $num=mt_rand(1, 36);
      $rand_id .= assign_rand_value($num);
    }
  }

  return $rand_id;
 }

 function get_rand_array_lines($data_lines, $lines_number, $delimiter="\n"){
  $ret='';

  $max_lines=count($data_lines);
  if($max_lines<$lines_number){
    $ret=implode($delimiter, $data_lines);
  }else{
    mt_srand((double)microtime() * 1000000);
    $max_lines--;
    for($i=0; $i<$lines_number; $i++){
      $ret.=$data_lines[mt_rand(0, $max_lines)].$delimiter;
    }
  }

  return trim($ret);
 }

 function get_rand_array_words($words, $words_min, $words_max, $delimiter=' '){
  $ret=array();

  $words_count=count($words);
  $word_index=0;
  mt_srand((double)microtime() * 1000000);
  do{
    $words_number=mt_rand($words_min, $words_max);
    if($word_index+$words_number>$words_count){
      $words_number=$words_count-$word_index;
    }
    $ret_line='';
    for($i=0; $i<$words_number; $i++){
      $ret_line.=$words[$word_index+$i].$delimiter;
    }
    $ret_line=trim($ret_line);
    if($ret_line!=''){
      $ret[crc32($ret_line)]=$ret_line;
    }
    $word_index+=$words_number;
  }while($word_index<$words_count);

  return $ret;
 }

 function getRandWords($MinNumber=8, $MaxNumber=128, $MinChars=3, $MaxChars=8, $Type=0, $Delimiter=' ', $data_lines=''){
   $ret='';
   $num=mt_rand($MinNumber, $MaxNumber);
   for($i=0; $i<$num; $i++){
     $chars_number=mt_rand($MinChars, $MaxChars);
     switch($Type){
       case 1  : {
         $word=get_rand_letters($chars_number);
         break;
       }
       case 2  : {
         $word=get_rand_mixed($chars_number);
         break;
       }
       case 3  : {
         $word=get_rand_array_lines($data_lines, $lines_number=$chars_number, $Delimiter);
         break;
       }
       case 0  :
       default : {
         $word=get_rand_numbers($chars_number);
       }
     }
     $ret.=$word.$Delimiter;
   }
   
   return trim($ret);
 }

 $Title=getRandWords($WordsTitleMin, $WordsTitleMax, $WordsTitleMinChars, $WordsTitleMaxChars, $WordsTitleType, $Delimiter, $data_lines);
 $Body=getRandWords($WordsBodyMin, $WordsBodyMax, $WordsBodyMinChars, $WordsBodyMaxChars, $WordsBodyType, $Delimiter, $data_lines);
 $Links='';
 $Links_words='';
 for($i=0; $i<$LinksMaxNumber; $i++){
   $words=getRandWords($LinksMinWordsNumber, $LinksMaxWordsNumber, $WordsLinksMinChars, $WordsLinksMaxChars, $WordsTitleType, $Delimiter, $data_lines);
   $Links_words.=$words.$Delimiter;
   $Links.=str_replace(array('%WORD%', '%HREF%'), array($words, $LinksHREF.rawurlencode($words)), $LinkTemplate).$Delimiter;
 }

 echo str_replace(array('%LINKS%', '%TITLE%', '%BODY%'), array($Links, $Title, $Body), $PageTemplate);
// echo $PageTemplate;

 $DelimitersToReplace=array("\r\n", "\n", "\r");
 if($ContextDataFiles['Title']!=''){
   file_put_contents($ContextDataFiles['Title'], implode(PHP_EOL, get_rand_array_words(explode($Delimiter, str_replace($DelimitersToReplace, $Delimiter, $Title)), $ContextDataFiles['WordsPerLineMin'], $ContextDataFiles['WordsPerLineMax'], $Delimiter)).PHP_EOL, FILE_APPEND);
 }
 if($ContextDataFiles['Body']!=''){
   file_put_contents($ContextDataFiles['Body'], implode(PHP_EOL, get_rand_array_words(explode($Delimiter, str_replace($DelimitersToReplace, $Delimiter, $Body)), $ContextDataFiles['WordsPerLineMin'], $ContextDataFiles['WordsPerLineMax'], $Delimiter)).PHP_EOL, FILE_APPEND);
 }
 if($ContextDataFiles['Links']!=''){
   file_put_contents($ContextDataFiles['Links'], implode(PHP_EOL, get_rand_array_words(explode($Delimiter, str_replace($DelimitersToReplace, $Delimiter, trim($Links_words))), $ContextDataFiles['WordsPerLineMin'], $ContextDataFiles['WordsPerLineMax'], $Delimiter)).PHP_EOL, FILE_APPEND);
 }

?>