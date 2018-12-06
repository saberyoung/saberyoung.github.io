<?php
session_start();
include 'layout.html';
include_once 'dbconnect.php';
error_reporting(E_ALL ^ E_WARNING);

if(!isset($_SESSION['user']) and strpos($_SESSION["type"],'private'))
   {
     header("Location: index.php");
   }
   elseif (!isset($_SESSION['user']) and strpos($_SESSION["type"],'public'))
     {
       $_SESSION['user']='8';
	 }
$res=mysqli_query($conn,"SELECT * FROM users WHERE user_id=".$_SESSION['user']);
$userRow=mysqli_fetch_array($res);
?>

<HTML>
 <HEAD> 
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> 
<TITLE><?php echo $_SESSION["trigger"].'_'.$_SESSION["number"] ?></TITLE> 
<style> 
body,p{  
padding:0px;  
margin:0px;  
padding-top:20px;  
font-size:10pt;  
font-family:"  ";  
}  
.demo{  
position: absolute;
left: 50px;
top: 100px;
width:600px;  
height:700px;  
margin:0 auto;/*CSS          */  
border: 10px solid #999999;  
}  
.form{
   position: relative;
   left: 700px;
   top: 0px;
}
.run{  
position: relative;
left: 700px;
top: 100px;
width:90%;  
height:auto;  
margin:0px 0px 0px 0px;}  
</style> 
 </HEAD>


<!-- show the images -->
<div class="demo"> 
<?php
include('arrfunc.php');

if(isset($_GET['trigger'])){
  $_SESSION['number'] = $_GET['number'];
  $_SESSION["trigger"] = $_GET['trigger'];
} 
else{ 
  $_SESSION['number'] = $_SESSION['number'];
  $_SESSION["trigger"] = $_SESSION['trigger'];
}

# !!! important: use relavant path!!!
$ff = $_SESSION["type"] . DIRECTORY_SEPARATOR . $_SESSION["run"] . DIRECTORY_SEPARATOR . $_SESSION["trigger"]. DIRECTORY_SEPARATOR .basename($_SESSION["files"][(string)$_SESSION["number"]]); 
             
if (file_exists($ff)) {
  echo "<img widht=800 height=600 src=\"$ff\"><br>";
  echo "$ff<br>";
} else {
  echo "The file $ff does not exist<br>";
}

$num1=$_SESSION['number']+1;
$num2=$_SESSION['number']-1;
echo "<a href='showpic.php?number=".$num1."&trigger=".$_SESSION["trigger"]."'><H4>NEXT</H4></a>";              
echo "<a href='showpic.php?number=".$num2."&trigger=".$_SESSION["trigger"]."'><H4>PREVIOUS<H4></a><br>";?>
</div>

<!-- classification forum -->
<div class="form"> 
<form action="showpic.php?number=<?php echo $num1 ?>&trigger=<?php echo $_SESSION['trigger'] ?>" method="post">
  Classification:
  <hr>
  good:
  <input name="ctype" value="sn" type="radio" id="ctype_1" /> SN
  <input name="ctype" value="agn"  type="radio" id="ctype_2" /> AGN
  <input name="ctype" value="var" type="radio" id="ctype_3" /> VAR
  <input name="ctype" value="mov" type="radio" id="ctype_4" /> MOV
  <input name="ctype" value="ogood" type="radio" id="ctype_5" />other good
  <br>
  bad:
  <input name="ctype" value="dipole" type="radio" id="ctype_6" />dipole
  <input name="ctype" value="bad" type="radio" id="ctype_7" />bad subtraction
  <input name="ctype" value="limit" type="radio" id="ctype_8" />limit
  <input name="ctype" value="obad" type="radio" id="ctype_9" />other bad
  <br>  
  not sure:
  <input name="ctype" value="skip" type="radio" id="ctype_10" checked="y" />skip
  <br>
  <input name="cnote" size="50" type="text" placeholder="note"/>
  <input value="submit" type="submit" /> </br>
 
  <a href="transients.php" target="_top">Back</a>
 
  <?php 
  $default1 = 1;
  $default2 = 0;
  $arrc = ['sn','agn','var','mov','ogood','dipole','bad','limit','obad','skip'];
  $arrf = [$default2,$default2,$default2,$default2,$default2,$default2,$default2,$default2,$default2,$default2];

  if ($_SERVER['REQUEST_METHOD'] === 'POST') {      
    $nn = compare($_POST['ctype'],$arrc);
    $arrf[$nn] = $default1;   
    $cnote = getPost_text("cnote");
   
    DoQuery($conn,"INSERT INTO GW_classify_".
	    $userRow['username'].
	    "(triggername,number,SN,AGN,VAR,MOV,OGOOD,".
	    "DIPOLE,BAD,LMT,OBAD,SKIP,NOTE)".
	    " VALUES('".$_SESSION['trigger'].
	    "','".$num2.
	    "','".$arrf[0].
	    "','".$arrf[1].
	    "','".$arrf[2].
	    "','".$arrf[3].
	    "','".$arrf[4].
	    "','".$arrf[5].
	    "','".$arrf[6].
	    "','".$arrf[7].
	    "','".$arrf[8].
	    "','".$arrf[9].
	    "','".$cnote."')");
  }?>

</br>
</form>
</div>


<!-- machine learning and light curves -->
<div class="run">    
    <form method="get" action="showpic.php?number=<?php echo $_SESSION['number'] ?>&trigger=<?php echo $_SESSION['trigger'] ?>" >
    <input type="submit" value="run PSF lightcurves" name="lc"><br>
    <input type="submit" value="run limits" name="limit"><br>
    <input type="submit" value="run machine learning mode" name="ml">
    </form>
    <?php 
    if(isset($_GET['lc'])){
      header("Location: gw_lightcurve.php");
    }
if(isset($_GET['limit'])){    
  $_SESSION['p1'] = 1;
  $_SESSION['p2'] = 2;
  header("Location: try.php");
}
if(isset($_GET['ml'])){     
  header("Location: ml.php");
}
?>
</div>    
</HTML>