<?php
	function OpenCon() 
	{
		$dbhost = "192.168.86.134";
		$dbuser = "cep2";
		$dbpass = "cep2"; //or whatever you choose when you installed it
		$db = "KitchenGuardDB";
		$conn = new mysqli($dbhost, $dbuser, $dbpass,$db)
		or die("Connect failed: %s\n". $conn -> error);
		return $conn;
	}
	function CloseCon($conn)
	{
		$conn -> close();
	}
?>
