<?php
function DoQuery($conn,$query) {  
  $result = mysqli_query($conn,$query);
  if (!$result) {
    die('Invalid query: ' . mysqli_error($conn));
  } else {
    return $result;
  }
}

function get_files1($dir) {
    $files = array();
 
    if(!is_dir($dir)) {
        return $files;
    }
 
    $handle = opendir($dir);
    if($handle) {
        while(false !== ($file = readdir($handle))) {
            if ($file != '.' && $file != '..') {
                $filename = $dir . "/"  . $file;
                if(is_file($filename)) {
                    $files[] = $filename;
                }else {
                    $files = array_merge($files, get_files($filename));
                }
            }
        }   //  end while
        closedir($handle);
    }
    return $files;
}   //  end function

function sort_files($files) {
  $newarr = [];
  foreach ($files as $x) 
    {       
      $p = explode(".png", $x);
      $p1 = explode("_", $p[0]);
      $newarr[end($p1)] = $x;     
    }
  return $newarr;
}


function recurse_copy($src,$dst) { 
    $dir = opendir($src); 
    @mkdir($dst); 
    while(false !== ( $file = readdir($dir)) ) { 
        if (( $file != '.' ) && ( $file != '..' )) { 
            if ( is_dir($src . '/' . $file) ) { 
                recurse_copy($src . '/' . $file,$dst . '/' . $file); 
            } 
            else { 
                copy($src . '/' . $file,$dst . '/' . $file); 
            } 
        } 
    } 
    closedir($dir); 
} 

function getPost($key, $default1, $default2) {
    if (isset($_POST[$key]))
        return $default1;
    return $default2;
}

function getPost_text($key) {
    if (isset($_POST[$key]))
        return $_POST[$key];
    return '';
}

function compare($key, $arr) {
    $nn = array_search($key, $arr);
    return $nn;
}
?>
