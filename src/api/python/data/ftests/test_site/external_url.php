<?php
 $paramName = 'url';
 $header = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; rv:1.7.3) Gecko/20041001 Firefox/0.10.1';
 $method = 0;

 $url=(isset($_GET[$paramName]) && $_GET[$paramName]!='') ? $_GET[$paramName] : '';

 $ret = 'External wrapper error';
 switch($method){
   case 0 : {
     $ret = file_get_contents($url);
     break;
   }
   case 1 : {
     $ch = curl_init();
     curl_setopt($ch, CURLOPT_USERAGENT, $header);
     curl_setopt($ch, CURLOPT_URL, $url);
     curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
     $ret = curl_exec($ch);
     curl_close($ch);
     break;
   }
   case 2 : {
     $r = new HttpRequest($url, HttpRequest::METH_GET);
     $r->send();
     if ($r->getResponseCode() == 200){
       $ret = $r->getBody();
     }
     break;
   }
 }

 echo $ret;
?>