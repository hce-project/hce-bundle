<?php
 $executable='c112_localhost_drce_json01b.sh';

 exec('chmod 777 '.$executable.'&./'.$executable, $out);

 $out=implode(PHP_EOL, $out);

 var_dump($out);

?>