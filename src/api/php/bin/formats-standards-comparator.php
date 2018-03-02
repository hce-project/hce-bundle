#!/usr/bin/php
<?php

if(php_sapi_name()!=='cli' || !defined('STDIN')){
    echo "Only cli execution mode supported\n";
    exit(1);
}

$args=cli_parse_arguments($argv);

$originalFile = isset($args['original']) ? $args['original'] : null;
$compareFile = isset($args['compare']) ? $args['compare'] : null;
$format = isset($args['format']) ? $args['format'] : 'json';
$type = isset($args['input_type']) ? $args['input_type'] : 'news';
$compareType = isset($args['type']) ? $args['type'] : 'text';

$fieldPath = isset($args['path']) ? $args['path'] : null;

$ignoredPaths = array('0:crawler_time', 'crawler_time', '0:scraper_time', 'scraper_time', '0:pubdate', 'pubdate', 'pubdate:', '0:dc_date', 'dc_date:', 'dc_date', 'dbFields:ProcessingTime');

if (isset($args['h']) or isset($args['help']) or !$originalFile or !$compareFile){
    echo "Usage: ".$argv[0]." --original=<json_file_1> --compare=<json_file_1> [--path=<custom field_path for check>] [--format=<answer format (json, csv, xml, html, sql, text), default=json>] [--type=<compare type (text, md5 or text), default=text>] [--input_type=<type of input format (news or rss), default=news>]\n";
    exit(1);
}

if (!file_exists($originalFile)) {
    echo "File ".$originalFile." not found. Exit.\n";
    die();
}
if (!file_exists($compareFile)){
    echo "File ".$compareFile." not found. Exit.\n";
    die();
}

function errHandle($errNo, $errStr, $errFile, $errLine) {
    $msg = "Error $errNo: $errStr in $errFile on line $errLine";
    if ($errNo == E_WARNING or $errNo == UPLOAD_ERR_EXTENSION) {
        exitScript( "Wrong format or wrong validation of input data\n");
    } else {
        echo $msg;
    }
}

set_error_handler('errHandle');

function checkCrc($first, $second) {
    if (crc32(serialize($first)) === crc32(serialize($second))) return true;
    else return false;
}

function checkMd5($first, $second) {
    if (md5(serialize($first)) === md5(serialize($second))) return true;
    else return false;
}

function checkText($first, $second) {
    if ($first === $second) return true;
    else return false;
}

function check($first, $second){
    global $compareType;
    switch ($compareType) {
        case 'text':
            return checkText($first, $second);
            break;
        case 'md5':
            return checkMd5($first, $second);
            break;
        case 'crc32':
            return checkCrc($first, $second);
            break;
        default:
            return checkText($first, $second);
            break;
    }
}

function getPathValue ($array) {
    if (!is_array($array)) return false;
    $ritit = new RecursiveIteratorIterator(new RecursiveArrayIterator($array));
    $results = array();
    foreach ($ritit as $leafValue) {
        $path = array();
        foreach (range(0, $ritit->getDepth()) as $depth) {
            $path[] = $ritit->getSubIterator($depth)->key();
        }
        $results[join(':', $path)] = $leafValue;
    }
    return $results;
}

function getData4Path ($input_json, $field_path){
    if(is_array($input_json)){
        $field_path=explode(':', $field_path);
        foreach($field_path as $dir){
            $dir=rawurldecode($dir);
            if(isset($input_json[$dir])){
                $input_json=$input_json[$dir];
            }
        }
        return $input_json;
    }
    return null;
}

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

function base64Check($data) {
    if (is_array($data)) return array('type'=> 'array', 'data' => $data);
    if (base64_encode(base64_decode($data)) === $data){
        if (json_decode(base64_decode($data), true)) return array('type'=> 'array', 'data' => json_decode(base64_decode($data), true));
        else return array('type'=> 'data', 'data' => base64_decode($data));
    } else {
        if (json_decode($data, true)) return array('type'=> 'json', 'data' => json_decode($data, true));
        else return array('type'=> 'data', 'data' => $data);
    }
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

function csv_to_array_simple($filename='', $delimiter=',') {
    if(!file_exists($filename) || !is_readable($filename)) return false;
    $data = array();
    if (($handle = fopen($filename, 'r')) !== FALSE) {
        while (($row = fgetcsv($handle, 0, $delimiter)) !== FALSE) {
            $data[] = $row;
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

function exitScript($msg) {
    global $tempfile;
    if ($tempfile) unlink($tempfile);
    echo $msg;
    exit(1);
}

function prepare($file, $fieldPath){
    $json = json_decode(file_get_contents($file), true);

    if ($fieldPath) {
        $json = getData4Path($json, $fieldPath);
    }

    return base64Check($json);
}

function formatJson($originalFile, $compareFile, $fieldPath) {
    global $ignoredPaths;
    $originalJson = prepare($originalFile, $fieldPath);
    $compareJson = prepare($compareFile, $fieldPath);

    if ($originalJson['type'] == 'array' and $compareJson['type'] == 'array') {
        $originalNewArray = getPathValue($originalJson['data']);
        $compareNewArray = getPathValue($compareJson['data']);

        if ($originalNewArray == false or $compareNewArray == false) {
            exitScript("Wrong json\n");
        }

        if (count($originalNewArray) != count($compareNewArray)) {
            exitScript("Number of elements of array not compare\n");
        }
        foreach ($originalNewArray as $key => $value) {
            if (array_key_exists($key, $compareNewArray)) {
                if (in_array($key, $ignoredPaths)){
                    if (stripos('%', trim($value)) or stripos('%', trim($compareNewArray[$key]))){
                        $check = check(trim($value), trim($compareNewArray[$key]));
                        if ($check == false) print "Error in path '".$key."'. Original value: '".$value."', compare value: '".$compareNewArray[$key]."'\n\n";
                    }
                } else {
                    $check = check(trim($value), trim($compareNewArray[$key]));
                    if ($check == false) print "Error in path '".$key."'. Original value: '".$value."', compare value: '".$compareNewArray[$key]."'\n\n";
                }
            } else {
                print "Error. Key ".$key." not exist in compare file\n";
            }
        }
    } elseif ($originalJson['type'] == 'data' and $compareJson['type'] == 'data') {
        exitScript("Wrong json\n");
    } else {
        exitScript("Wrong json\n");
    }
}

function formatCsv($originalFile, $compareFile, $fieldPath){
    global $ignoredPaths;
    global $type;
    $originalCsv = prepare($originalFile, $fieldPath);
    $compareCsv = prepare($compareFile, $fieldPath);

    if(empty($compareCsv['data'])) {
        exitScript("Csv, compare content is null\n");
    };

    if ($originalCsv['type'] == 'array' or $compareCsv['type'] == 'array') {
        exitScript("Csv is wrong\n");
    }

    $tempfile = tempnam("/tmp", pathinfo(__FILE__,PATHINFO_FILENAME));

    if ($type == 'rss') {
        file_put_contents($tempfile, str_replace(array("\"\r\n,\"", "\"\r,\"", "\"\n,\""), '","', $originalCsv['data']));
        $originalNewArray = getPathValue(csv_to_array_rss($tempfile));

        file_put_contents($tempfile, str_replace(array("\"\r\n,\"", "\"\r,\"", "\"\n,\""), '","', $compareCsv['data']));
        $compareNewArray = getPathValue(csv_to_array_rss($tempfile));
    } else {
        file_put_contents($tempfile, str_replace(array("\"\r\n,\"", "\"\r,\"", "\"\n,\""), '","', $originalCsv['data']));
        #$originalNewArray = getPathValue(csv_to_array($tempfile));
        $originalNewArray = getPathValue(csv_to_array_simple($tempfile));

        file_put_contents($tempfile, str_replace(array("\"\r\n,\"", "\"\r,\"", "\"\n,\""), '","', $compareCsv['data']));
        #$compareNewArray = getPathValue(csv_to_array($tempfile));
        $compareNewArray = getPathValue(csv_to_array_simple($tempfile));
    }

    unlink($tempfile);

    if ($originalNewArray == false or $compareNewArray == false) {
        exitScript("Csv is wrong\n");
    }

    if (count($originalNewArray) != count($compareNewArray)) {
        exitScript("Number of elements of csv not compare");
    }

    foreach ($originalNewArray as $key => $value) {
        if (array_key_exists($key, $compareNewArray)) {
            if (array_key_exists($key, $compareNewArray)) {
                if (in_array($key, $ignoredPaths)){
                    if (stripos('%', trim($value)) or stripos('%', trim($compareNewArray[$key]))){
                        $check = check(trim($value), trim($compareNewArray[$key]));
                        if ($check == false) print "Error in path '".$key."'. Original value: '".$value."', compare value: '".$compareNewArray[$key]."'\n\n";
                    }
                } else {
                    $check = check(trim($value), trim($compareNewArray[$key]));
                    if ($check == false) print "Error in path '".$key."'. Original value: '".$value."', compare value: '".$compareNewArray[$key]."'\n\n";
                }
            } else {
                print "Error. Key ".$key." not exist in compare file\n";
            }
        } else {
            print "Error. Key ".$key." not exist in compare file\n";
        }
    }
}

function formatXml($originalFile, $compareFile, $fieldPath){
    global $ignoredPaths;
    $originalCsv = prepare($originalFile, $fieldPath);
    $compareCsv = prepare($compareFile, $fieldPath);

    if ($originalCsv['type'] == 'array' or $compareCsv['type'] == 'array' or stripos($originalCsv['data'], '<?xml version=') === false or stripos($compareCsv['data'], '<?xml version=') === false) {
        exitScript("XML is wrong\n");
    }

    $xmlOriginal = simplexml_load_string($originalCsv['data'], 'SimpleXMLElement', LIBXML_NOCDATA);
    $originalArray = (array)$xmlOriginal->item;
    $xmlCompare = simplexml_load_string($compareCsv['data'], 'SimpleXMLElement', LIBXML_NOCDATA);
    $compareArray = (array)$xmlCompare->item;

    if ($xmlOriginal === false or $xmlCompare === false) {
        exitScript("XML is wrong\n");
    } else {
        if (count($originalArray) != count($compareArray)) {
            exitScript("Number of elements of array not compare\n");
        }
        foreach ($originalArray as $key => $value) {
            if (array_key_exists($key, $compareArray)) {
                if (in_array($key, $ignoredPaths)){
                    if (stripos('%', trim($value)) or stripos('%', trim($compareArray[$key]))){
                        $check = check(trim($value), trim($compareArray[$key]));
                        if ($check == false) print "Error in path '".$key."'. Original value: '".$value."', compare value: '".$compareArray[$key]."'\n\n";
                    }
                } else {
                    $check = check(trim($value), trim($compareArray[$key]));
                    if ($check == false) print "Error in path '".$key."'. Original value: '".$value."', compare value: '".$compareArray[$key]."'\n\n";
                }
            } else {
                print "Error. Key ".$key." not exist in compare file\n";
            }
        }
    }
}

function formatHtml($originalFile, $compareFile, $fieldPath){
    global $ignoredPaths;
    $originalHtml = prepare($originalFile, $fieldPath);
    $compareHtml = prepare($compareFile, $fieldPath);

    if ($originalHtml['type'] == 'array' or $compareHtml['type'] == 'array') {
        exitScript("HTML is wrong\n");
    }

    #$originalArray = htmlParse(str_replace(array("\r\n", "\r", "\n"), '', $originalHtml['data']));
    #$compareArray = htmlParse(str_replace(array("\r\n", "\r", "\n"), '', $compareHtml['data']));
    $originalArray = htmlParse($originalHtml['data']);
    $compareArray = htmlParse($compareHtml['data']);

    if ($originalArray === false or $compareArray === false) {
        exitScript("HTML is wrong\n");
    } else {
        if (count($originalArray) != count($compareArray)) {
            exitScript("Number of elements of array not compare\n");
        }
        foreach ($originalArray as $key => $value) {
            if (array_key_exists($key, $compareArray)) {
                if (in_array($key, $ignoredPaths)){
                    if (stripos('%', trim($value)) or stripos('%', trim($compareArray[$key]))){
                        $check = check(trim($value), trim($compareArray[$key]));
                        if ($check == false) print "Error in path '".$key."'. Original value: '".$value."', compare value: '".$compareArray[$key]."'\n\n";
                    }
                } else {
                    $check = check(trim($value), trim($compareArray[$key]));
                    if ($check == false) print "Error in path '".$key."'. Original value: '".$value."', compare value: '".$compareArray[$key]."'\n\n";
                }
            } else {
                print "Error. Key ".$key." not exist in compare file\n";
            }
        }
    }
}

function formatSql($originalFile, $compareFile, $fieldPath){
    $originalSql = prepare($originalFile, $fieldPath);
    $compareSql = prepare($compareFile, $fieldPath);

    if ($originalSql['type'] == 'array' or $compareSql['type'] == 'array') {
        exitScript("SQL query is wrong\n");
    }
    if (stripos($originalSql['data'], 'INSERT INTO') === false or stripos($compareSql['data'], 'INSERT INTO') === false) {
        exitScript("SQL query is wrong\n");
    }

    preg_match('/INSERT INTO.*\((.*)\).*VALUES \n(.*).*/', $originalSql['data'], $originalOut);
    preg_match('/INSERT INTO.*\((.*)\).*VALUES \n\((.*)\).*/', $compareSql['data'], $compareOut);

    $originalOutHeader = $originalOut[1];
    $originalCsvHeader = explode(",", $originalOutHeader);
    $originalOut = ltrim($originalOut[2], '(');
    $originalOut = rtrim($originalOut, ');');
    $originalCsvVal = explode('), (', $originalOut);

    $compareOutHeader = $compareOut[1];
    $compareCsvHeader = explode(",", $compareOutHeader);
    $compareOut = ltrim($compareOut[2], '(');
    $compareOut = rtrim($compareOut, ');');
    $compareCsvVal = explode('), (', $compareOut);

    if (count($originalCsvHeader) != count($compareCsvHeader)) {
        exitScript("Number of elements in INSERT not compare\n");
    }

    if (count($originalCsvVal) != count($compareCsvVal)) {
        exitScript("Number of elements in VALUE not compare\n");
    }

    $check = check($originalCsvHeader, $compareCsvHeader);
    if ($check == false) exitScript("Not compare INSERT");

    $check = check($originalCsvVal, $compareCsvVal);
    if ($check == false) exitScript("Not compare VALUE");
}

function formatText($originalFile, $compareFile, $fieldPath){
    $originalText = prepare($originalFile, $fieldPath);
    $compareText = prepare($compareFile, $fieldPath);

    if ($originalText['type'] == 'array' or $compareText['type'] == 'array') {
        exitScript("Text is wrong\n");
    }
    $check = check($originalText, $compareText);
    if ($check == false) exitScript("Not compare");
}

switch($format) {
    case 'json':
        formatJson($originalFile, $compareFile, $fieldPath);
        break;
    case 'csv':
        formatCsv($originalFile, $compareFile, $fieldPath);
        break;
    case 'xml':
        formatXml($originalFile, $compareFile, $fieldPath);
        break;
    case 'html':
        formatHtml($originalFile, $compareFile, $fieldPath);
        break;
    case 'sql':
        formatSql($originalFile, $compareFile, $fieldPath);
        break;
    case 'text':
        formatText($originalFile, $compareFile, $fieldPath);
        break;
    default:
        print "Wrong format\n";
        exit(1);
}

