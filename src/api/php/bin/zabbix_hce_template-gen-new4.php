#!/usr/bin/php
<?php
/**
 * HCE project node Zabbix template generator from logs in json format
 * cli argument --l=<parameter_name> is a path to a log.
 * --node=<> consists of two parts - hostname and port, delimited by a colon, 
 * enclosed in double quotes, for example: "admindc03-10.snatz.com:5546"
 *
 * @author bgv <bgv.hce@gmail.com>
 * @author valerius <valerius2k7@gmail.com>
 * @link http://hierarchical-cluster-engine.com/
 * @copyright Copyright &copy; 2013-2014 IOIX Ukraine
 * @license http://hierarchical-cluster-engine.com/license/
 * @package HCE project node API
 * @since 0.1
 */

//Set default timezone if not set in host environment
@date_default_timezone_set(@date_default_timezone_get());

$LOG_FILE = '../log/properties.sh.m0.log';

require_once '../inc/hce_cli_api.inc.php';

// recursively build full keys 
// to values in nested arrays
// returns: $a is an array of $keystr
// where $keystr are keys delimited by '%'
// $key is the same only not a string but an array(...)
// $hparams is a subtree of a parsed JSON
function buildkey (& $a, $key, $hparams) {
    $PARAMETER_NAME_DELIMITER = '%';

    if (isset($hparams) && is_array($hparams)) {
      foreach($hparams as $pname => $pval) {
         // change handler name according the 'name field'
         if ($pname == 'name') {
           //array_pop($key);
           //array_push($key, $pval);
           continue;
         }

         if (! is_numeric($pval) && ! is_array($pval)) {
           // skip a subarray name
           continue;
         }

         array_push($key, $pname);
         $keystr = join(htmlspecialchars($PARAMETER_NAME_DELIMITER), $key);

         if (! isset($pval) || ! is_array($pval)) {
           array_push($a, $keystr);
         }
         else {
             buildkey($a, $key, $pval);
         }
         array_pop($key);
       }
     }
}

//Parse cli arguments
$args = cli_parse_arguments($argv);

// which hce-node to use for generating a template
if(!isset($args['node']) || empty($args['node'])){
  // whole cluster
  $node = '';
}
else {
  // specific node
  $node = $args['node'];
}

//Check optional arguments
if(isset($args['l']) && !empty($args['l'])){

    $LOG_FILE = $args['l'];

    //Relative path
    if (substr($args['l'], 0, 3) != '../') {
      $LOG_FILE = '../log/' . $args['l'];
    }
}

if(!file_exists($LOG_FILE)){
  echo 'ERROR: data file not found: ' . $LOG_FILE  . PHP_EOL;
  exit(1);
}

//Fetch log file
$data = array(json_decode(file_get_contents($LOG_FILE), true));

// the header
print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"  . PHP_EOL;
print "<zabbix_export>"  . PHP_EOL;
print "  <version>2.0</version>"  . PHP_EOL;
print "  <date>" . date("Y-m-d") . 'T' . date("H:i") . 'Z' . "</date>" . PHP_EOL;
print "  <groups>" . PHP_EOL;
print "    <group>" . PHP_EOL;
print "      <name>Templates</name>" . PHP_EOL;
print "    </group>" . PHP_EOL;
print "  </groups>" . PHP_EOL;
print "  <templates>" . PHP_EOL;
print "    <template>" . PHP_EOL;
print "      <template>Template_HCE</template>" . PHP_EOL;
print "      <name>Template_HCE</name>" . PHP_EOL;
print "      <groups>" . PHP_EOL;
print "        <group>" . PHP_EOL;
print "          <name>Templates</name>" . PHP_EOL;
print "        </group>" . PHP_EOL;
print "      </groups>" . PHP_EOL;

print "      <applications>" . PHP_EOL;

// the list of application objects
$hnames = array();
foreach($data as $item) {
  if($item) {
    foreach($item as $host => $handlers) {
      if (empty($node) || ($host == $node)) {
        //foreach($handlers as $hname => $hparams) {
          // skip already existing application names
          //if (!in_array($hname, $hnames, true)) {
            // $hnames[] = $hname;
          //}
        //}
        //$host     = str_replace(':', '_', $host);
        $hnames[] = $host;
      }
    }
  }
}

// sort an array alphabetically
asort($hnames);

foreach ($hnames as $h) {
    print "        <application>" . PHP_EOL;
    printf("         <name>%s</name>" . PHP_EOL, $h);
    print "        </application>" . PHP_EOL;
}

print "      </applications>" . PHP_EOL;;

print "      <items>" . PHP_EOL;


$hnames2 = array();

// the indicators/items list
foreach($data as $item) {
  if($item) {
    foreach($item as $host => $handlers) {
      if (empty($node) || ($host == $node)) {
        foreach($handlers as $hname => $hparams) {

            $a = array();
            //$key = array($host, $hn);
            $key = array($host, $hname);
            buildkey($a, $key, $hparams);
            //$hnames[$host][$hname] = $a;

             foreach ($a as $keystr) {
                //$keystr = $e[0]; $key = $e[1]; $pname = $e[2];
                //$keystr = str_replace(':', '_', $keystr);
                //$host   = str_replace(':', '_', $host);
                print "        <item>" . PHP_EOL;
                print "          <name>" . $keystr . "</name>" . PHP_EOL;
                print "          <type>0</type>" . PHP_EOL;
                print "          <snmpcommunity/>" . PHP_EOL;
                print "          <multiplier>0</multiplier>" . PHP_EOL;
                print "          <snmp_oid/>" . PHP_EOL;
                print "          <key>hce.check[" . $keystr . "]</key>" . PHP_EOL;
                print "          <delay>30</delay>" . PHP_EOL;
                print "          <history>90</history>" . PHP_EOL;
                print "          <trends>365</trends>" . PHP_EOL;
                print "          <status>0</status>" . PHP_EOL;
                print "          <value_type>3</value_type>" . PHP_EOL;
                print "          <allowed_hosts/>" . PHP_EOL;
                print "          <units/>" . PHP_EOL;
                print "          <delta>0</delta>" . PHP_EOL;
                print "          <snmpv3_securityname/>" . PHP_EOL;
                print "          <snmpv3_securitylevel>0</snmpv3_securitylevel>" . PHP_EOL;
                print "          <snmpv3_authpassphrase/>" . PHP_EOL;
                print "          <snmpv3_privpassphrase/>" . PHP_EOL;
                print "          <formula>1</formula>" . PHP_EOL;
                print "          <delay_flex/>" . PHP_EOL;
                print "          <params/>" . PHP_EOL;
                print "          <ipmi_sensor/>" . PHP_EOL;
                print "          <data_type>0</data_type>" . PHP_EOL;
                print "          <authtype>0</authtype>" . PHP_EOL;
                print "          <username/>" . PHP_EOL;
                print "          <password/>" . PHP_EOL;
                print "          <publickey/>" . PHP_EOL;
                print "          <privatekey/>" . PHP_EOL;
                print "          <port/>" . PHP_EOL;
                print "          <description/>" . PHP_EOL;
                print "          <inventory_link>0</inventory_link>" . PHP_EOL;
                print "          <applications>" . PHP_EOL;
                print "            <application>" . PHP_EOL;
                print "              <name>" . $host . "</name>" . PHP_EOL;
                print "            </application>" . PHP_EOL;
                print "          </applications>" . PHP_EOL;
                print "          <valuemap/>" . PHP_EOL;
                print "        </item>" . PHP_EOL;
          }
        }
      }
    }
  }
}

// the footer
print "      </items>" . PHP_EOL;

print "      <discovery_rules/>" . PHP_EOL;
print "      <macros/>" . PHP_EOL;
print "      <templates/>" . PHP_EOL;
print "      <screens/>" . PHP_EOL;
print "      </template>" . PHP_EOL;
print "    </templates>" . PHP_EOL;
print "</zabbix_export>" . PHP_EOL;

exit(0);

