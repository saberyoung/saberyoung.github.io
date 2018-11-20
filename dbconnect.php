<?php include('config.php');

  $servername = $mysqlServername;
  $username   = $mysqlUsername;
  $password   = $mysqlPassword;
  $database   = $mysqlDB;
  $dbport     = $mysqlPort;
  $conn = mysqli_connect($servername,$username,$password);

if(!$conn)
{
     die('oops connection problem ! --> '.mysql_error());
}
if(!mysqli_select_db($conn,$database))
{
     die('oops database selection problem ! --> '.mysql_error());
}
?>