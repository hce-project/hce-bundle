<?php

 function redirect($url, $statusCode = 303){
   header('Location: '.$url, true, $statusCode);
   die();
 }

 $url=(isset($_GET['u']) && $_GET['u']!='') ? $_GET['u'] : 'http://127.0.0.1/';
 $code=(isset($_GET['c']) && $_GET['c']!='') ? $_GET['c'] : 303;
 $number=(isset($_GET['n']) && $_GET['n']!='') ? $_GET['n'] : 1;

 if($number>1){
   $number--;
   $url='http://127.0.0.1/redirect.php?c='.$code.'&n='.$number.'&u='.urlencode($url);
 }

 redirect($url, $code);

?>