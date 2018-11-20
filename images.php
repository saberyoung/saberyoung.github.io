<?php include 'layout.html' ?>
<?php include('gw_dir.php'); ?>


<HTML>
 <HEAD> 
<style> 
.try{  
position: absolute;
left: 50px;
top: 100px;
width:25%;}  

.try1{  
position: relative;
left: 500px;
top: 50px;
width:50%;  
height:auto;  
margin:0px 0px 0px 0px;}  
</style> 
 </HEAD>

<body>
<div class="try"> 
<?php
session_start();
$_SESSION['_type']='images';

#public
$dir1 = gw_dir_i1;
$type1 = explode("/",$dir1)[0];
$list1 = scandir(gw_dir_i1);
print_r("<li>$type1:</li><br>");
foreach ($list1 as $x) 
  {
    if (!in_array($x,array(".","..")))
      {     
	$list11 = scandir(gw_dir_i1.$x);
	foreach ($list11 as $y) 
	  {
	    if (!in_array($y,array(".","..")))
	      {     
		echo '<pre>';
		print_r("   LIGO/VIRGO $x run - $y<br>");
		echo '</pre>';
	      }}
      }}

print_r("<br>");

#private
$dir2 = gw_dir_i2;
$type2 = explode("/",$dir2)[0];
$list2 = scandir(gw_dir_i2);
print_r("<li>$type2:</li><br>");
foreach ($list2 as $x) 
  {
    if (!in_array($x,array(".","..")))
      {     
	$list22 = scandir(gw_dir_i2.$x);
	foreach ($list22 as $y) 
	  {
	    if (!in_array($y,array(".","..")))
	      {     
		echo '<pre>';
		print_r("   LIGO/VIRGO $x run - $y<br>");
		echo '</pre>';
	      }}
      }}
?></div>

<div class="try1"> 
<?php
    echo 'Images were taken by VST telesope aiming to follow-up the LIGO/VIRGO Gravitational Wave localization triggers on behalf of GRAWITA project.<br><br>Considering the authority reason issued by the MoU, the images from the public LIGO/VIRGO trigger would be shown without need of login, otherwise, one should eyeball as login mode.';
?>
</div>

<br><br>

<div class="try1"> 
<form action="choose.php" method="post">
GW trigger: <input type="text" name="trigger"><br>
<input type="submit">
</form>
</div>
</body>

</HTML>
