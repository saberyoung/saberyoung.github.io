<?php include 'layout.html' ?>
<?php include('gw_dir.php'); ?>

<?php 
session_start();
if ($_SESSION['_type']=='images'){
  $dir = array(gw_dir_i1, gw_dir_i2);
} elseif ($_SESSION['_type']=='candidates'){
  $dir = array(gw_dir_c1, gw_dir_c2);
}

foreach ($dir as $dir1){
  if (!in_array($dir1,array(".","..","...")))
    {     
      $list1 = scandir($dir1);
      $type = explode("/",$dir1)[0];     
      foreach ($list1 as $y){
	if (!in_array($y,array(".","..","...")))
	  {	  
	    $list2 = scandir($dir1.$y);
	    $run = explode("/",$y)[0];	  	  
	    foreach ($list2 as $x) 
	      {
		$z = explode("/",$x)[0];	
		if (!in_array($z,array(".","..","...")))
		  {     
		    if (in_array($z,array($_POST["trigger"])))
		      if ($type == 'images_public' or $type == 'candidates_public') {
			$_SESSION['trigger'] = $z;
			$_SESSION['type'] = $type;
			$_SESSION['run'] = $run;		
			header("Location: transients_public.php");
		      } elseif ($type == 'images_private' or $type == 'candidates_private') {
		      $_SESSION['trigger'] = $z;
		      $_SESSION['type'] = $type;
		      $_SESSION['run'] = $run;
		      header("Location: transients_private.php");}
		  }}}}}}
?>