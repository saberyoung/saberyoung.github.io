<?php
session_start();
include 'layout.html';

$n1 = $_SESSION['p1'];
$n2 = $_SESSION['p2'];
$cmd = '/usr/local/anaconda3/envs/sheng/bin/python /home/gwpadova/public_html/python/gw_limit.py '.$n1.' '.$n2;
echo $cmd,'<br><br>';
passthru($cmd);
?>