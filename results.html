<?php include 'layout.html' ?>
<?php include 'arrfunc.php' ?>

<?php
session_start();
include_once 'dbconnect.php';

if(!isset($_SESSION['user']))
{
 header("Location: index.php");
}
$res=mysqli_query($conn,"SELECT * FROM users WHERE user_id=".$_SESSION['user']);
$userRow=mysqli_fetch_array($res);
?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Welcome - <?php echo $userRow['email']; ?></title>
<link rel="stylesheet" href="style.css" type="text/css" />
</head>
<body>
<div id="header">
 <div id="left">
    <label>Account Info.</label>
    </div>
    <div id="right">
     <div id="content">
         <br>
         hi <?php echo $userRow['username'];?>&nbsp;<a href="logout.php?logout">Sign Out</a>
          <?php
            echo '<br><br>';                 
            echo date("Y/m/d,l h:i:s"); ?>           
	  <br>
	  <br>
	<?php 
	  $res1=mysqli_query($conn,"SELECT * FROM GW_classify_".
			     $userRow['username']);
          if(!$res1 )
	    { Doquery($conn,"CREATE TABLE GW_classify_".
		      $userRow['username'].
		      "( id INT NOT NULL AUTO_INCREMENT, ".		      
           	      "triggername text, ".
          	      "number INT DEFAULT NULL, ".
                      "SN INT DEFAULT NULL, ".
		      "AGN INT DEFAULT NULL, ".
		      "VAR INT DEFAULT NULL, ".
		      "MOV INT DEFAULT NULL, ".
		      "OGOOD INT DEFAULT NULL, ".
		      "DIPOLE INT DEFAULT NULL, ".
		      "BAD INT DEFAULT NULL, ".
		      "LMT INT DEFAULT NULL, ".
		      "OBAD INT DEFAULT NULL, ".
		      "SKIP INT DEFAULT NULL, ".
		      "NOTE text, ".
                      "PRIMARY KEY (id)) ".
		      "ENGINE=InnoDB DEFAULT CHARSET=utf8; ");
	    }              

	  echo "<table width='80%' border=1 align='center' cellpadding=5 cellspacing=0>";
          echo '<tr align="center"><td>trigger</td><td>number</td><td>sn</td><td>agn</td><td>var</td><td>mov</td><td>other good</td><td>dipole</td><td>bad subtraction</td><td>limit</td><td>other bad</td><td>skip</td><td>comment</td><td></td><td></td></tr>';
          while ($rows = mysqli_fetch_assoc($res1)) {
	    echo '<tr align="center">';
	    echo '<td>' . $rows['triggername'] .'</td>';
	    echo '<td>' . $rows['number'] .'</td>';
	    echo '<td>' . $rows['SN'] .'</td>';  
	    echo '<td>' . $rows['AGN'] .'</td>';
	    echo '<td>' . $rows['VAR'] .'</td>';
	    echo '<td>' . $rows['MOV'] .'</td>';
	    echo '<td>' . $rows['OGOOD'] .'</td>';
	    echo '<td>' . $rows['DIPOLE'] .'</td>';
	    echo '<td>' . $rows['BAD'] .'</td>';
	    echo '<td>' . $rows['LMT'] .'</td>';
	    echo '<td>' . $rows['OBAD'] .'</td>';
	    echo '<td>' . $rows['SKIP'] .'</td>';
            echo '<td>' . $rows['NOTE'] .'</td>';
	    echo '<td><a href='.'showpic.php?number='.$rows['number'].
	      '&trigger='.$rows['triggername'].
	      '>display</a></td>';
	    echo '<td><a href='.'delete.php?id='.$rows['id'].
	     '>delete</a></td>';}
	     ?>
        </div>
    </div>
</div>
</body>
</html>
