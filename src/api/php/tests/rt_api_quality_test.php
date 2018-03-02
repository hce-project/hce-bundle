#!/usr/bin/php
<?php

require_once '../inc/hce_cli_api.inc.php';

if(php_sapi_name()!=='cli' || !defined('STDIN')){
    echo 'Only cli execution mode supported'.PHP_EOL;
    exit(1);
}

$args=cli_parse_arguments($argv);

if(isset($args['h']) or isset($args['help'])){
    echo 'Usage: '.
        $argv[0].
        " --path=<path with json files> [--template=<template, default *>] [--bundle_path=<path to bundle, default=/home/hce/hce-node-bundle>]\n";
    exit(1);
}

$hce_path = isset($args['bundle_path']) ? $args['bundle_path'] : '/home/hce/hce-node-bundle';
$filesPath = isset($args['path']) ? $args['path'] : $hce_path.'/api/python/data/ftests/real_time_api_tests/';
$template = isset($args['template']) ? $args['template'] : '*';
$fieldPath = isset($args['field']) ? $args['field'] : 'itemsList:0:itemObject:0:processedContents:0:buffer';
$input_type = isset($args['input_type']) ? $args['input_type'] : 'news';

$failCount = 0;
$notTags = array('rss');

if (!is_dir($filesPath)) {
    echo "Directory ".$filesPath." not exist. Exit\n";
    exit(1);
}

function exitScript($msg) {
    global $tempfile, $failCount;
    if ($tempfile) unlink($tempfile);
    echo $msg;
    $failCount++;
}


function errHandle($errNo, $errStr, $errFile, $errLine) {
    global $failCount;
    $msg = "Error $errNo: $errStr in $errFile on line $errLine";
    if ($errNo == E_WARNING or $errNo == UPLOAD_ERR_EXTENSION) {
        echo "Wrong format or wrong validation of input data\n";
    } else {
        echo $msg;
    }
}

set_error_handler('errHandle');

function getJsonData($path2file, $field_path){
    $input_json=file_get_contents($path2file);
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
    return $input_json;
}

function runScrapping($json_file){
    global $hce_path;
    $bufferArray = array();
    $content = shell_exec("cd $hce_path/api/python/bin/; ./dc-client.py --config=../ini/dc-client.ini --command=BATCH --file=$json_file");
    $contentArray = json_decode($content, true);
    if (!isset($contentArray['itemsList'])) return false;
    if (!isset($contentArray['itemsList'][0]['itemObject'])) return false;
    foreach ($contentArray['itemsList'][0]['itemObject'] as $line) {
        foreach ($line['processedContents'] as $procedureContent) {
            if ($buffer = base64_decode($procedureContent['buffer'])) array_push($bufferArray, $buffer);
            else array_push($bufferArray, $procedureContent['buffer']);
        }
    }
    return $bufferArray;
}

function getTypes($json_file){
    $array = json_decode(file_get_contents($json_file), true);
    if (!$type = $array['items'][0]['properties']['template']['templates'][0]['output_format']['name']) return false;
    if ($type == 'json' or $type == 'csv' or $type == 'html' or $type == 'text' or $type == 'xml' or $type == 'sql') return $type;
    else return false;
}

function getInputType($json_file){
    $array = json_decode(file_get_contents($json_file), true);
    $type = $array['items'][0]['properties']['template']['templates'][0]['output_format'];
    if (array_key_exists('type', $type)) {
        return $array['items'][0]['properties']['template']['templates'][0]['output_format']['type'];
    }
    return 'news';
}

function getTags($json_file, $type){
    $array = json_decode(file_get_contents($json_file), true);
    if ($type == 'json') $tag = contentJson($array);
    elseif ($type == 'csv') $tag = contentCsv($array);
    elseif ($type == 'html') $tag = contentHtml($array);
    elseif ($type == 'text') $tag = contentText($array);
    elseif ($type == 'xml') $tag = contentXml($array);
    elseif ($type == 'sql') $tag = contentSql($array);
    else return false;
    return $tag;
}

function contentJson($array){
    if ($keys = array_keys(get_object_vars(json_decode($array['items'][0]['properties']['template']['templates'][0]['output_format']['item'])))) return $keys;
    return false;
}

function contentCsv($array){
    if ($keys = $array['items'][0]['properties']['template']['templates'][0]['output_format']['header']) {
        return str_getcsv($keys);
    }
    return false;
}

function contentHtml($array){
    if ($keys = $array['items'][0]['properties']['template']['templates'][0]['output_format']['item']) {
        preg_match_all('/\<tr\>\<td\>(.*?):\<\/td\>\<td\>/', $keys, $matches);
        return $matches[1];
    }
    return false;
}

function contentText($array){
    if ($keys = $array['items'][0]['properties']['template']['templates'][0]['output_format']['item']) {
        preg_match_all('/(.*?):/', $keys, $matches);
        return $matches[1];
    }
    return false;
}

function contentXml($array){
    if ($keys = $array['items'][0]['properties']['template']['templates'][0]['output_format']['item']) {
        preg_match_all('/\<((?!\/|\!).*?)\>/', $keys, $matches);
        return $matches[1];
    }
    return false;
}

function contentSql($array){
    if ($keys = $array['items'][0]['properties']['template']['templates'][0]['output_format']['header']) {
        preg_match('/INSERT INTO.*\((.*)\).*VALUES \n(.*).*/', $keys, $matches);
        return explode(',', $matches[1]);
    }
    return false;
}

function csv_to_array($filename='', $delimiter=',') {
    if(!file_exists($filename) || !is_readable($filename)) return false;
    $header = NULL;
    $data = array();
    if (($handle = fopen($filename, 'r')) !== FALSE) {
        while (($row = fgetcsv($handle, 0, $delimiter)) !== FALSE) {
            if(!$header)
                $header = $row;
            else {
                $data[] = array_combine($header, $row);
            }
        }
        fclose($handle);
    }
    if (!empty($data)) return $data;
    else return false;
}

function csv_to_array_rss($filename='', $delimiter=',') {
    if(!file_exists($filename) || !is_readable($filename)) return false;
    $data = array();
    if (($handle = fopen($filename, 'r')) !== FALSE) {
        while (($row = fgetcsv($handle, 0, $delimiter)) !== FALSE) {
            $num = count($row);
            for ($c=0; $c < $num; $c++) {
                array_push($data, $row[$c]);
            }
        }
        fclose($handle);
    }
    if (!empty($data)) return $data;
    else return false;
}

function htmlParse ($html){
    #if (stripos($html, '<!DOCTYPE html>') === false) return false;
    #print_r($html);
    $array = array();
    $dom = new domDocument;
    $dom->recover = true;
    $dom->strictErrorChecking = false;
    #libxml_use_internal_errors(true);
    #@$dom->loadHTML(rawurlencode($html));
    @$dom->loadHTML($html);
    #libxml_clear_errors();
    $dom->preserveWhiteSpace = false;
    $tables = $dom->getElementsByTagName('table');
    $rows = $tables->item(0)->getElementsByTagName('tr');
    if ($rows->length == 0) return false;
    foreach ($rows as $row) {
        $cols = $row->getElementsByTagName('td');
        $array[$cols->item(0)->textContent] = $cols->item(1)->textContent;
    }
    return $array;
}

function formatJson($buffer, $tags) {
    $bufferArray = get_object_vars(json_decode($buffer)[0]);
    if (is_array($tags)) {
        if (count($bufferArray) != count($tags)) return false;
        $tagsReverse = array_flip($tags);
        foreach ($bufferArray as $key => $value) {
            if (array_key_exists($key, $tagsReverse)) {
                if (checkJson($value) == false) return false;
            }
        }
    } else {
        foreach ($bufferArray as $key => $value) {
            if (checkJson($value) == false) return false;
        }
    }
    return true;
}

function checkJson($value){
    if (checkZero(trim($value)) == false) return false;
    if (checkWords(trim($value)) == false) return false;
    return true;
}

function formatCsv($buffer, $tags){
    $tempfile = tempnam("/tmp", pathinfo(__FILE__,PATHINFO_FILENAME));
    if ($tags == 'rss') {
        file_put_contents($tempfile, str_replace(array("\"\r\n,\"", "\"\r,\"", "\"\n,\""), '","', $buffer));
        $bufferArray = csv_to_array_rss($tempfile);
    } else {
        file_put_contents($tempfile, str_replace(array("\"\r\n,\"", "\"\r,\"", "\"\n,\""), '","', $buffer));
        $bufferArray = csv_to_array($tempfile)[0];
    }
    unlink($tempfile);
    if (is_array($tags)) {
        if (count($bufferArray) != count($tags)) return false;
        $tagsReverse = array_flip($tags);
        foreach ($bufferArray as $key => $value) {
            if (array_key_exists($key, $tagsReverse)) {
                if (checkCsv($value) == false) return false;
            }
        }
    } else {
        foreach ($bufferArray as $key => $value) {
            if (checkCsv($value) == false) return false;
        }
    }
    return true;
}

function checkCsv($value){
    if (checkZero(trim($value)) == false) return false;
    if (checkWords(trim($value)) == false) return false;
    return true;
}

function formatHtml($buffer, $tags){
    $bufferArray = htmlParse($buffer);
    if (is_array($tags)) {
        if (count($bufferArray) != count($tags)) return false;
        $tagsReverse = array_flip($tags);
        foreach ($bufferArray as $key => $value) {
            if (array_key_exists(rtrim($key, ":"), $tagsReverse)) {
                if (checkHtml($value) == false) return false;
            }
        }
    } else {
        foreach ($bufferArray as $key => $value) {
            if (checkHtml($value) == false) return false;
        }
    }
    return true;
}

function checkHtml($value){
    if (checkZero(trim($value)) == false) return false;
    if (checkWords(trim($value)) == false) return false;
    return true;
}

function formatText($buffer, $tags){
    $newBuffer = trim(str_replace('items:', '',$buffer));
    if (is_array($tags)) {
        foreach ($tags as $tag) {
            if (stripos($newBuffer, $tag) === false) return false;
        }
    }
    if (checkText($newBuffer) == false) return false;
    return true;
}

function checkText($value){
    if (checkZero(trim($value)) == false) return false;
    if (checkWords(trim($value)) == false) return false;
    return true;
}

function formatXml($buffer, $tags){
    if (stripos($buffer, '<?xml version=') === false) return false;
    #$xmlOriginal = simplexml_load_string(str_replace('&', '&amp;', $buffer), 'SimpleXMLElement', LIBXML_NOCDATA);
    $xmlOriginal = simplexml_load_string($buffer, 'SimpleXMLElement', LIBXML_NOCDATA);
    $bufferArray = (array)$xmlOriginal->item;
    if (is_array($tags)) {
        if (count($bufferArray) != count($tags)) return false;
        $tagsReverse = array_flip($tags);
        foreach ($bufferArray as $key => $value) {
            if (array_key_exists($key, $tagsReverse)) {
                if (checkXml($value) == false) return false;
            }
        }
    } else {
        foreach ($bufferArray as $key => $value) {
            if (checkXml($value) == false) return false;
        }
    }
    return true;
}

function checkXml($value){
    if (checkZero(trim($value)) == false) return false;
    if (checkWords(trim($value)) == false) return false;
    return true;
}

function formatSql($buffer, $tags){
    if (stripos($buffer, 'INSERT INTO') === false) return false;
    preg_match('/INSERT INTO.*\((.*)\).*VALUES \n\((.*)\).*/', $buffer, $bufferSql);
    $bufferHeader = explode(',', trim($bufferSql[1], '"'));
    $bufferValues = explode('","', trim($bufferSql[2], '"'));
    if (count($bufferHeader) != count($bufferValues)) return false;
    $bufferArray = array_combine($bufferHeader, $bufferValues);
    if (is_array($tags)) {
        if (count($bufferArray) != count($tags)) return false;
        $tagsReverse = array_flip($tags);
        foreach ($bufferArray as $key => $value) {
            if (array_key_exists($key, $tagsReverse)) {
                if (checkSql($value) == false) return false;
            }
        }
    } else {
        foreach ($bufferArray as $key => $value) {
            if (checkSql($value) == false) return false;
        }
    }
    return true;
}

function checkSql($value){
    if (checkZero(trim($value)) == false) return false;
    if (checkWords(trim($value)) == false) return false;
    return true;
}

function checkZero($string){
    if (is_null($string)) return false;
    return true;
}

function checkWords($string, $min=1){
    $check = str_word_count($string);
    if ($check < $min and $string != 0) return false;
    return true;
}

$files = ($template == "*") ? scandir($filesPath) : preg_grep("/$template/", scandir($filesPath));
$files = preg_grep("/.json$/", $files);

if (!isset($files)) {
    echo "Json files not found\n";
    exit(1);
}

foreach ($files as $json) {
    $file = rtrim($filesPath, "/")."/".$json;
    if (is_file($file)){
        if ($content = runScrapping($file)) {
            if ($type = getTypes($file)){
                $input_type = getInputType($file);
                $tags = (in_array($input_type, $notTags)) ? 'rss' : getTags($file, $type);
                if ($tags) {
                    foreach ($content as $buffer) {
                        if ($type == 'json') $checkContent = formatJson($buffer, $tags);
                        elseif ($type == 'csv') $checkContent = formatCsv($buffer, $tags);
                        elseif ($type == 'html') $checkContent = formatHtml($buffer, $tags);
                        elseif ($type == 'text') $checkContent = formatText($buffer, $tags);
                        elseif ($type == 'xml') $checkContent = formatXml($buffer, $tags);
                        elseif ($type == 'sql') $checkContent = formatSql($buffer, $tags);
                        else $checkContent = false;
                        if ($checkContent === false) exitScript($json.": check false\n");
                    }
                } else {
                    exitScript($json.": no tags\n");
                }
            } else {
                exitScript($json.": unknown type\n");
            }
        } else {
            exitScript($json.": no content\n");
        };
    } else {
        exitScript($json.": file not found\n");
    }
}

if ($failCount > 0) {
    echo "Number of fails: $failCount, from ".count($files)." jsons\n";
    exit($failCount);
} else {
    echo "Test is good from ".count($files)." jsons\n";
    exit(0);
}
