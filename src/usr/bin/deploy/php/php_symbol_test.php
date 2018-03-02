#! /usr/bin/php
<?php

function chk_class_exist($inc, $cla) {
  $incpath = getenv('HOME') . "/hce-node-tests/api/php/inc";
  
  require_once($incpath . '/' . $inc);
  
  if (class_exists($cla))
    echo "yes";
  else
    echo "no";
}

function chk_func_exist($inc, $func) {
  $incpath = getenv('HOME') . "/hce-node-tests/api/php/inc";
  
  require_once($incpath . '/' . $inc);
  
  if (function_exists($func))
    echo "yes";
  else
    echo "no";
}

if ($argc < 3) {
  echo "$argv[0]: Incorrect syntax!";
  echo "need to be:";
  echo "";
  echo "$argv[0] <header> \[\"func\"\|\"class\"\] <func|class>";
  exit(1);
}

switch ($argv[2])
{
  case 'class':
    chk_class_exist($argv[1], $argv[3]);
    break;

  case 'func':
  default:
    chk_func_exist($argv[1], $argv[3]);
}

exit(0);

?>
