<?php include('gw_dir.php');
include('arrfunc.php'); 
include 'layout.html';
error_reporting(E_ALL ^ E_NOTICE);?>

<html>
<body>
<?php 
session_start();
if ($_SESSION['type'] == 'images_public') {
  $dir = gw_dir_i1;
} 
elseif ($_SESSION['type'] == 'images_private') {
  $dir = gw_dir_i2;
}
elseif ($_SESSION['type'] == 'candidates_public') {
  $dir = gw_dir_c1;
}
elseif ($_SESSION['type'] == 'candidates_private') {
  $dir = gw_dir_c2;
}

$filepath = $dir . 
  $_SESSION['run']  . DIRECTORY_SEPARATOR . 
  $_SESSION['trigger'];

$files = get_files1($filepath);
$files = sort_files($files);

$_SESSION["files"]=$files;
$_SESSION["trigger"]=$_SESSION['trigger'];
$_SESSION["filepath"]=$filepath;
$_SESSION["total_number"]=count($files);
$_SESSION['number']=rand(0,count($files));

if (count($files)>0) {
  echo count($files)," images in ",$filepath,"<br><br>";
} 
else{
  header("Location: page_not_found.php");
}
?>

</body>
<li><a href='showpic.php?number=1&trigger=<?php echo $_SESSION["trigger"]?>'>show in order</a></li>
<li><a href='showpicr.php?number=<?php echo $_SESSION["number"]?>&trigger=<?php echo $_SESSION["trigger"]?>'>show randomly</a></li>
</html>
