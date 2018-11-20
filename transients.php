<?php include 'layout.html' ?>
<?php include('gw_dir.php'); ?>

<?php
#public
$dir1 = gw_dir_1;
$list1 = scandir(gw_dir_1);
$type1 = explode("/",$dir1)[4];
print_r("$type1:<br>");
foreach ($list1 as $x) 
{
  if (!in_array($x,array(".","..")))
    {     
      print_r("$x <br>");
}}

print_r("<br>");

#private
$dir2 = gw_dir_2;
$list2 = scandir(gw_dir_2);
$type2 = explode("/",$dir2)[4];
print_r("$type2:<br>");
foreach ($list2 as $x) 
{
  if (!in_array($x,array(".","..")))
    {     
      print_r("$x <br>");
}}
?>

<html>
<body>
<br>
<form action="choose.php" method="post">
type: <input type="text" name="trigger"><br>
<input type="submit">
</form>
</body>
</html>
