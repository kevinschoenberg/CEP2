<?php
{
function PrintObj ($o) { echo "<pre>"; print_r($o); echo "</pre>"; }

// Load the POST.
$data = file_get_contents("php://input");

// ...and decode it into a PHP array.
$jsondata = json_decode($data);

// Do whatever with the array. 
//PrintObj($jsondata);

$servername = "localhost";
$username = "root";
$password = "cep2";
$dbname = "kitchenguearddb";

// Database connection
$conn = new mysqli($servername, $username, $password, $dbname);
// Insert data Query
$sql = "INSERT INTO events ( Timestamp, Eventtype, IdChain) 
VALUES ('$jsondata->Timestamp', '$jsondata->Event' , '$jsondata->IdChain')";
  
if ($conn->query($sql) === TRUE) {
  echo "Insert your JSON record successfully";
}
else
{
  echo "Error: " . $sql . "<br>" . mysqli_error($conn);
}

mysqli_close($conn); 
}
?>

