#!/usr/bin/php
<?php
/**
 * DTM/DC Zabbix template generator from stat output in json format
 * cli argument --l=<parameter_name> is a path to a log.
 * --node=<> consists of two parts - hostname and port, delimited by a colon, 
 * enclosed in double quotes, for example: "admindc03-10.snatz.com:5546"
 *
 * @author valerius <valerius2k7@gmail.com>
 * @link http://hierarchical-cluster-engine.com/
 * @copyright Copyright &copy; 2013-2014 IOIX Ukraine
 * @license http://hierarchical-cluster-engine.com/license/
 * @package HCE project node API
 * @since 0.1
 */

/* 
 * Global variables
 */

// templates
$xml_header_template = 
	"<?xml version=\"1.0\" encoding=\"UTF-8\"?>"  . PHP_EOL .
	"<zabbix_export>"  . PHP_EOL .
	"	<version>2.0</version>"  . PHP_EOL .
	"	<date>" . date("Y-m-d") . 'T' . date("H:i") . 'Z' . "</date>" . PHP_EOL .
	"	<groups>" . PHP_EOL .
	"		<group>" . PHP_EOL .
	"			<name>Templates</name>" . PHP_EOL .
	"    		</group>" . PHP_EOL .
	"	</groups>" . PHP_EOL;

$xml_templates_header_template =
	"	<templates>" . PHP_EOL .
	"		<template>" . PHP_EOL .
	"			<template>Template_%TEMPLATE_NAME%</template>" . PHP_EOL .
	"			<name>Template_%TEMPLATE_NAME%</name>" . PHP_EOL .
	"			<groups>" . PHP_EOL .
	"				<group>" . PHP_EOL .
	"					<name>Templates</name>" . PHP_EOL .
	"				</group>" . PHP_EOL .
	"			</groups>" . PHP_EOL ;

$xml_templates_footer_template = 
	"		<discovery_rules/>" . PHP_EOL .
	"		<macros/>" . PHP_EOL .
	"		<templates/>" . PHP_EOL .
	"		<screens/>" . PHP_EOL .
	"		</template>" . PHP_EOL .
	"	</templates>" . PHP_EOL;

$xml_item_template =  
	"				<item>" . PHP_EOL .
	"					<name>%ITEM_NAME%</name>" . PHP_EOL .
	"					<type>0</type>" . PHP_EOL .
	"					<snmpcommunity/>" . PHP_EOL .
	"					<multiplier>0</multiplier>" . PHP_EOL .
	"					<snmp_oid/>" . PHP_EOL .
	"					<key>%KEY%[%KEY_PARAMETER%]</key>" . PHP_EOL .
	"					<delay>300</delay>" . PHP_EOL .
	"					<history>30</history>" . PHP_EOL .
	"					<trends>30</trends>" . PHP_EOL .
	"					<status>0</status>" . PHP_EOL .
	"					<value_type>0</value_type>" . PHP_EOL .
	"					<allowed_hosts/>" . PHP_EOL .
	"					<units/>" . PHP_EOL .
	"					<delta>0</delta>" . PHP_EOL .
	"					<snmpv3_securityname/>" . PHP_EOL .
	"					<snmpv3_securitylevel>0</snmpv3_securitylevel>" . PHP_EOL .
	"					<snmpv3_authpassphrase/>" . PHP_EOL .
	"					<snmpv3_privpassphrase/>" . PHP_EOL .
	"					<formula>1</formula>" . PHP_EOL .
	"					<delay_flex/>" . PHP_EOL .
	"					<params/>" . PHP_EOL .
	"					<ipmi_sensor/>" . PHP_EOL .
	"					<data_type>0</data_type>" . PHP_EOL .
	"					<authtype>0</authtype>" . PHP_EOL .
	"					<username/>" . PHP_EOL .
	"					<password/>" . PHP_EOL .
	"					<publickey/>" . PHP_EOL .
	"					<privatekey/>" . PHP_EOL .
	"					<port/>" . PHP_EOL .
	"					<description/>" . PHP_EOL .
	"					<inventory_link>0</inventory_link>" . PHP_EOL .
	"					<applications>" . PHP_EOL .
	"						<application>" . PHP_EOL .
	"							<name>%APPLICATION%</name>" . PHP_EOL .
	"						</application>" . PHP_EOL .
	"					</applications>" . PHP_EOL .
	"					<valuemap/>" . PHP_EOL .
	"				</item>" . PHP_EOL;

$xml_application_template = 
	"				<application>" . PHP_EOL .
	"					<name>%APPLICATION%</name>" . PHP_EOL .
	"				</application>" . PHP_EOL;
$xml_graph_template =
	"		<graph>" . PHP_EOL .
	"			<name>%GRAPH_NAME%</name>" . PHP_EOL .
	"			<width>1200</width>" . PHP_EOL .
	"			<height>200</height>" . PHP_EOL .
	"			<yaxismin>0.0000</yaxismin>" . PHP_EOL .
	"			<yaxismax>100.0000</yaxismax>" . PHP_EOL .
	"			<show_work_period>1</show_work_period>" . PHP_EOL .
	"			<show_triggers>1</show_triggers>" . PHP_EOL .
	"			<type>0</type>" . PHP_EOL .
	"			<show_legend>1</show_legend>" . PHP_EOL .
	"			<show_3d>0</show_3d>" . PHP_EOL .
	"			<percent_left>0.0000</percent_left>" . PHP_EOL .
	"			<percent_right>0.0000</percent_right>" . PHP_EOL .
	"			<ymin_type_1>0</ymin_type_1>" . PHP_EOL .
	"			<ymax_type_1>0</ymax_type_1>" . PHP_EOL .
	"			<ymin_item_1>0</ymin_item_1>" . PHP_EOL .
	"			<ymax_item_1>0</ymax_item_1>" . PHP_EOL .
	"			<graph_items>" . PHP_EOL .
	"				<graph_item>" . PHP_EOL .
	"					<sortorder>0</sortorder>" . PHP_EOL .
	"					<drawtype>0</drawtype>" . PHP_EOL .
	"					<color>C80000</color>" . PHP_EOL .
	"					<yaxisside>0</yaxisside>" . PHP_EOL .
	"					<calc_fnc>2</calc_fnc>" . PHP_EOL .
	"					<type>0</type>" . PHP_EOL .
	"					<item>" . PHP_EOL .
	"						<host>Template_%TEMPLATE_NAME%</host>" . PHP_EOL .
	"						<key>%KEY%[%KEY_PARAMETER%]</key>" . PHP_EOL .
	"					</item>" . PHP_EOL .
	"				</graph_item>" . PHP_EOL .
	"			</graph_items>" . PHP_EOL .
	"		</graph>" . PHP_EOL;

$xml_screen_header_template =
	"		<screens>" . PHP_EOL .
	"			<screen>" . PHP_EOL .
	"				<name>Template_%TEMPLATE_NAME%</name>" . PHP_EOL .
	"				<hsize>1</hsize>" . PHP_EOL .
	"				<vsize>%YSIZE%</vsize>" . PHP_EOL .
	"				<screen_items>" . PHP_EOL;

$xml_screen_footer_template =
	"				</screen_items>" . PHP_EOL .
	"			</screen>" . PHP_EOL .
	"		</screens>" . PHP_EOL;

$xml_screen_item_template =
	"					<screen_item>" . PHP_EOL .
	"						<resourcetype>0</resourcetype>" . PHP_EOL .
	"						<width>500</width>" . PHP_EOL .
	"						<height>100</height>" . PHP_EOL .
	"						<x>0</x>" . PHP_EOL .
	"						<y>%ROW%</y>" . PHP_EOL .
	"						<colspan>1</colspan>" . PHP_EOL .
	"						<rowspan>1</rowspan>" . PHP_EOL .
	"						<elements>0</elements>" . PHP_EOL .
	"						<valign>0</valign>" . PHP_EOL .
	"						<halign>0</halign>" . PHP_EOL .
	"						<style>0</style>" . PHP_EOL .
	"						<url/>" . PHP_EOL .
	"						<dynamic>0</dynamic>" . PHP_EOL .
	"						<sort_triggers>0</sort_triggers>" . PHP_EOL .
	"						<resource>" . PHP_EOL .
	"							<name>%KEY_PARAMETER%</name>" . PHP_EOL .
	"							<host>Template_%TEMPLATE_NAME%</host>" . PHP_EOL .
	"						</resource>" . PHP_EOL .
	"						<application/>" . PHP_EOL .
	"					</screen_item>" . PHP_EOL;

$xml_footer_template = 
	"</zabbix_export>" . PHP_EOL;

// get command line parameters
$params = array(
	''      => 'help',
	'k:'	=> 'key:',
	't:'	=> 'template-name:',
	'l:'	=> 'log-file:',
	'd:'	=> 'delimiter:',
	'g:'	=> 'graph-items:',
);
$errors     = array();

$options = getopt( implode('', array_keys($params)), $params );
 
if (isset($options['key']) || isset($options['k'])) {
	$zbx_key = isset( $options['key'] ) ? $options['key'] : $options['k'];
} else {
	$errors[] = 'zabbix item key is required';
}
 
if (isset($options['template-name']) || isset($options['t'])) {
	$zbx_template_name = isset( $options['template-name'] ) ? $options['template-name'] : $options['t'];
} else {
	$errors[] = 'zabbix template name is required';
}
 
if (isset($options['log-file']) || isset($options['l'])) {
	$log_file = isset( $options['log-file'] ) ? $options['log-file'] : $options['l'];
} else {
	$errors[] = 'log file is required';
}
 
if (isset($options['delimiter']) || isset($options['d'])) {
	$delimiter = isset( $options['delimiter'] ) ? $options['delimiter'] : $options['d'];
} else {
	$errors[] = 'delimiter required';
}

if (isset($options['graph-items']) || isset($options['g'])) {
	$graphs = isset( $options['graph-items'] ) ? $options['graph-items'] : $options['g'];
	if (file_exists($graphs)) {
		$zbx_graph_items = file($graphs, FILE_IGNORE_NEW_LINES);
	} else {
		$zbx_graph_items = explode(",", $graphs); 
	}
}

if ( isset($options['help']) || count($errors) ) {
	$help = "Usage: php " . basename($argv[0])  . " [--help] [-k|--key=hce.check] [-d|--delimiter=%] [-l|--log-file=/path/to/log/file.log] [-t|--template-name=HCE]
 
Options:
	    --help			Show this message
	-k  --key			Zabbix item key
	-d  --delimiter		Delimiter wich will be used in item name and item key parameter
	-l  --log-file		Log file which will be parsed
	-t  --template-name	Zabbix template name
	-g  --graph-items	List of items or filename with items to create graphs, use '' if graphs not needed.

";
	if ( $errors ) {
		$help .= 'Errors:' . PHP_EOL . implode("\n", $errors) . PHP_EOL;
	}
	die( $help );
}

if(!file_exists($log_file)) {
	echo 'ERROR: data file not found: ' . $log_file  . PHP_EOL;
	exit(1);
}

// fetch data from log file and decode json
$data = array(json_decode(file_get_contents($log_file), true));

// print header template
print $xml_header_template;
print str_replace("%TEMPLATE_NAME%", $zbx_template_name, $xml_templates_header_template);

// the list of application objects
$zbx_applications = [];
array_walk_recursive($data, function($item, $key) use (&$zbx_applications) { if ('className' === $key) {$zbx_applications[] = $item; } });

// print list of applications
print "			<applications>" . PHP_EOL;
foreach ($zbx_applications as $app) {
	print str_replace('%APPLICATION%', $app, $xml_application_template);
}
print "			</applications>" . PHP_EOL;;

// process template and print
function print_template($data, $data_processing_func) {
	global $zbx_key, $zbx_graph_items, $zbx_template_name, $xml_graph_template, $xml_item_template, $delimiter, $xml_screen_item_template;

	$row = 0;
	foreach($data as $item) {
		if($item && is_array($item)) {
			foreach($item as $sitem) {
				if ($sitem && is_array($sitem)) {
					foreach($sitem as $ssitem) {
						if ($ssitem && is_array($ssitem)) {
							foreach ($ssitem as $key => $value) {
								if (('className' === $key) && ! is_array($value)) {
									$application = $value;
								} elseif (('fields' === $key) && is_array($value)) {
									foreach ($value as $key => $zbx_item_value) {
										if (! isset($key) || ! is_numeric($zbx_item_value)) {
											continue;
										}
										$key_parameter = "$application$delimiter$key";
										if ( 'item_processing' === $data_processing_func ) {
											print str_replace(array('%ITEM_NAME%', '%KEY%', '%KEY_PARAMETER%', '%APPLICATION%'), array($key_parameter, $zbx_key, $key_parameter, $application), $xml_item_template);
										} elseif ( 'graph_processing' === $data_processing_func ) {
											if (in_array($key_parameter, $zbx_graph_items))
												print str_replace(array('%GRAPH_NAME%', '%KEY%', '%KEY_PARAMETER%', '%TEMPLATE_NAME%'), array($key_parameter, $zbx_key, $key_parameter, $zbx_template_name), $xml_graph_template);	
										} elseif ( 'screen_processing' === $data_processing_func ) {
											if (in_array($key_parameter, $zbx_graph_items)) {
												print str_replace(array('%KEY_PARAMETER%', '%ROW%', '%TEMPLATE_NAME%'), array($key_parameter, $row, $zbx_template_name), $xml_screen_item_template);
												$row++;
											}
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
}

// print list of items
print "			<items>" . PHP_EOL;
print_template($data, 'item_processing');
print "                 </items>" . PHP_EOL;

if (isset($zbx_graph_items)) {
	// print list of screens
	print str_replace(array('%TEMPLATE_NAME%', '%YSIZE%'), array($zbx_template_name, count($zbx_graph_items)), $xml_screen_header_template);
	print_template($data, 'screen_processing');
	print $xml_screen_footer_template;
}

// the templates_footer
print $xml_templates_footer_template;

// graphs
if (isset($zbx_graph_items)) {
	print "	<graphs>" . PHP_EOL;
	print_template($data, 'graph_processing');
	print "	</graphs>" . PHP_EOL;
}

// xml footer
print $xml_footer_template;

exit(0);
