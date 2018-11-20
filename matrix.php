<?php include 'layout.html' ?>
<?php include('gw_dir.php'); ?>

<?php
session_start();
$_SESSION['_type']='matrix';?>

<html>
<li><a href='matrix.php?number=1&trigger=<?php echo $_SESSION["trigger"]?>'>show in order</a></li>
<li><a href='matrixr.php?number=<?php echo $_SESSION["number"]?>&trigger=<?php echo $_SESSION["trigger"]?>'>show randomly</a></li>
</html>
