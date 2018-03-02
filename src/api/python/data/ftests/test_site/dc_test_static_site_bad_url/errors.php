<?php
if (array_key_exists('error', $_GET)){
	$error = $_GET['error'];
	http_response_code($error);
}
?>
