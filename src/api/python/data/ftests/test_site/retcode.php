<?php

 $code=(isset($_GET['c']) && $_GET['c']!='') ? $_GET['c'] : 500;

 http_response_code($code);

?>