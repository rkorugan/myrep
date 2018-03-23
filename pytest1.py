# 
#  Licensed Materials - Property of IBM
#
#  (c) Copyright IBM Corp. 2007-2008
#

import unittest, sys
import ibm_db
import config
from testfunctions import IbmDbTestFunctions

class IbmDbTestCase(unittest.TestCase):

	def test_019_selectRowcountPrefetchPrepOpt(self):
		obj = IbmDbTestFunctions()
		obj.assert_expect(self.run_test_019)
	def run_test_019(self):
		dsn_driver = "IBM DB2 ODBC DRIVER"
		dsn_database = "JUPYTER"
		dsn_hostname = "localhost"
		dsn_port = "50000"
		dsn_protocol = "TCPIP"
		dsn_uid = "db2admin"
		dsn_pwd = "python"
		dsn = (
		"DRIVER={{IBM DB2 ODBC DRIVER}};"
		"DATABASE={0};"
		"HOSTNAME={1};"
		"PORT={2};"
		"PROTOCOL=TCPIP;"
		"UID={3};"
		"PWD={4};").format(dsn_database, dsn_hostname, dsn_port, dsn_uid, dsn_pwd)
		print ("Sp name : " , sp)
		print ("schema name is  : " ,sch)
		print ("outpath is : " , op)
		conn = ibm_db.connect(dsn, "", "")  
		#conn = ibm_db.connect(config.database, config.user, config.password)
		ibm_db.autocommit(conn, ibm_db.SQL_AUTOCOMMIT_ON)
		if conn:
			stmt = ibm_db.prepare(conn, "SELECT * from log ", {ibm_db.SQL_ATTR_ROWCOUNT_PREFETCH : ibm_db.SQL_ROWCOUNT_PREFETCH_ON} )
			result = ibm_db.execute(stmt)
			print("result" ,result)
			if result:
				rows = ibm_db.num_rows(stmt)
				print("affected row:", rows)
				ibm_db.free_result(stmt)
			else:
				print(ibm_db.stmt_errormsg())
			ibm_db.close(conn)
		else:
			print("no connection:", ibm_db.conn_errormsg())

#__END__
#__LUW_EXPECTED__
#affected row: 4
#__ZOS_EXPECTED__
#affected row: 4
#__SYSTEMI_EXPECTED__
#affected row: 4
#__IDS_EXPECTED__
#affected row: 4
