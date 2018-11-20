import numpy as np
import pylab as pl
import subprocess
import string
import sys

####################################################
def getconnection(site):
   connection={#        CHANGE THIS LINE WITH THE INFO ON THE NEW DATABASE
               'GRAWITA':{}}

   connection[site]['database'] = 'gwpd'
   connection[site]['hostname'] = 'localhost'
   connection[site]['username'] = 'gwpadova'
   connection[site]['passwd']   = 'PDgw_2017'
   return  connection[site]['hostname'],connection[site]['username'],connection[site]['passwd'],connection[site]['database']

def getconnection2(site):
   connection={#        CHANGE THIS LINE WITH THE INFO ON THE NEW DATABASE
               'GRAWITA2':{}}

   connection[site]['database'] = 'GW'
   connection[site]['hostname'] = 'localhost'
   connection[site]['username'] = 'gwusr'
   connection[site]['passwd']   = 'GW2016'
   return  connection[site]['hostname'],connection[site]['username'],connection[site]['passwd'],connection[site]['database']

def dbConnect(lhost, luser, lpasswd, ldb):
   import sys
   import pymysql,os,string
   try:
      conn = pymysql.connect (host = lhost,
                              user = luser,
                            passwd = lpasswd,
                                db = ldb)
      conn.autocommit(True)
   except pymysql.Error as e:
      print(("Error %d: %s" % (e.args[0], e.args[1])))
      sys.exit (1)
   return conn

#try:
hostname, username, passwd, database = getconnection('GRAWITA')
conn = dbConnect(hostname, username, passwd, database)
#except:   
#   print('\### warning: problem with the database')
#   conn=''

def insert_values(connection,table,values):
    import sys,string,os,re
    import pymysql,os,string
    def dictValuePad(key):
        return '%(' + str(key) + ')s'

    def insertFromDict(table, dict):
        """Take dictionary object dict and produce sql for 
        inserting it into the named table"""
        sql = 'INSERT INTO ' + table
        sql += ' ('
        sql += ', '.join(dict)
        sql += ') VALUES ('
        sql += ', '.join(map(dictValuePad, dict))
        sql += ');'
        return sql

    sql = insertFromDict(table, values)
    try:
        cursor = connection.cursor (pymysql.cursors.DictCursor)
        cursor.execute(sql, values)
        resultSet = cursor.fetchall ()
        if cursor.rowcount == 0:
            pass
        cursor.close ()
    except pymysql.Error as e:
        print(("Error %d: %s" % (e.args[0], e.args[1])))
        sys.exit (1)
        
def query(command,connection):
   import pymysql,os,string,pymysql.cursors
   lista=''
   try:
        cursor = connection.cursor (pymysql.cursors.DictCursor)
        for i in command:
            cursor.execute (i)
            lista = cursor.fetchall ()
            if cursor.rowcount == 0:
                pass
        cursor.close ()
   except pymysql.Error as e: 
        print(("Error %d: %s" % (e.args[0], e.args[1])))
   return lista
