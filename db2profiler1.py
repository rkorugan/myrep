from tkinter import * 
import tkinter as tk
import tkinter.messagebox as tkmsg
import ibm_db
import ibm_db_dbi
import sys
import sqlparse
import os
import pandas
import webbrowser
import pandas as pd
import shutil # for clearing test dir
import traceback
import logging
import subprocess
from datetime import	datetime
#put this part in main
def getsp():
	global op
	op=outpath.get()
	#clean up work dir
	msg='Cleaning the files in work directory'
	#log.info(fname+msg)
	for the_file in os.listdir(op):
		file_path = os.path.join(op, the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path): shutil.rmtree(file_path)
		except Exception as e:
			#print(e)
			msg=e
			log.error(msg)
	logname=datetime.now().strftime(spname.get()+'_%d_%m_%Y_%H_%M_%S.log')
	workdir=outpath.get()
	os.chdir(workdir)
	global alltable
	newdir='rpt'
	if not os.path.exists(newdir):
		os.makedirs(newdir)
	repdir = workdir+'\\'+newdir	
	newdir='log'
	if not os.path.exists(newdir):
		os.makedirs(newdir)
	logdir = workdir+'\\'+ newdir
	
	print(logdir)
	print(repdir)
	print(logname)
	log = Logger('DB2PY',logname,logdir)
	fname='getsp() -'
	msg= '*** Starting Getsp function()***'
	log.info(fname+msg)
	sp=spname.get()
	sch=schema.get()
	msg='SP Name: '+sp
	log.debug(fname+msg)
	msg='Schema Name: '+sch
	log.debug(fname+msg)
	msg='Work Directory: '+op
	log.debug(fname+msg)
	
	dsn_driver = "IBM DB2 ODBC DRIVER"
	dsn_database = dbname.get()      
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
	try:
		conn = ibm_db.connect(dsn, "", "")
	except:
		msg='B connection  failed'	
		msg=msg+'\n'+traceback.format_exc()
		log.error(fname+msg)
		popupmsg("DB connection  failed")
		
	con = ibm_db_dbi.Connection(conn)
	#Validate the SP  and schema before calling
	
	if conn:
		msg='Calling the SP- export_sp '
		log.info(fname+msg)
		try:
			stmt, sp, sch, op = ibm_db.callproc(conn, 'research.export_sp', (sp, sch, op))
		except:
			msg='Failed to fetch SP'
			log.error(fname+msg)
			popupmsg("Failed to fetch SP")
		sql_del="DELETE FROM RESEARCH.QUERY_COST;"
		msg='Deleting from Query Cost Table'
		log.info(fname+msg)
		try:
			c=con.cursor()
			#c.execute(sql_del)
		except:	
			msg="Delete from query_cost failed"
			log.error(fnam+msg)
			popupmsg(msg)
		#call parse function with inut as outfile
		msg='Calling parsesp function'	
		log.info(fname+msg)
		try:
			parsesp(op,log)
		except:
			msg='getsp() - Error in parsing - '+'\n'+traceback.format_exc()
			log.error(msg)
		msg=' getsp() - Calling explainselect function'	
		log.info(msg)
		try:	
			explainselect(op,dsn_database,conn,log,repdir)
		except:
			msg='getsp() - Error in explainselect - '+'\n'+traceback.format_exc()
			log.error(msg)
		msg='getsp() - Calling explainupdate function'	
		log.info(msg)
		explainupdate(op,dsn_database,conn,log,repdir)
		msg='getsp() - Calling explaininsert function'	
		log.info(msg)
		explaininsert(op,dsn_database,conn,log,repdir)
		msg='getsp() - Calling explaininsert function'	
		log.info(msg)
		explaindelete(op,dsn_database,conn,log,repdir)
		msg='****End of Getsp******'	
		log.info(msg)
		
		popupmsg("Completed")
		#logpath = os.path.join(logdir,logname)
		#log.closelog(logpath)	
		log.closelog()
		ibm_db.close(conn)
		
		
	else:
		print("errro")
def popupmsg(msg):
	popup=tk.Tk()
	popup.wm_title("test")
	label=tk.Label(popup,text=msg,font=8)
	label.pack(side="top",fill="x",pady=10)
	B1=tk.Button(popup,text="ok",command=popup.destroy)
	B1.pack()
	popup.mainloop()
def parsesp(outdirname,log):
	fname='parsesp() - '
	msg = 'parsesp()- Parse SP started'
	log.info(fname+msg)
	for filename in os.listdir(outdirname):
		if filename.endswith(".lob"):
			msg='file to be parsed - '+filename
			log.info(fname+msg)
			os.chdir(outdirname)
			with open (filename, "r") as myfile:
				sql=myfile.read()
				formattedSQL = sqlparse.format(sql, reindent=True, keyword_case='upper',strip_comments=True)
				formatted_file_name=filename+'_'+'formatted.sql'
				f = open(formatted_file_name,"w")
				print (formattedSQL,file=f)
				#msg = 'formatted SQL-'+'\n'+formattedSQL
				#log.info(msg)				
				f.close()
			with open (formatted_file_name, "r" )as myfile1:
				sql = myfile1.read()	
				words = " ".join(sql.split()).replace('; ', ';\n')
				split_file_name=filename+'_'+'split.sql'
				f = open(split_file_name,"w")
				print(words,file=f)
				f.close()
			#Extract ONLY SELECT,INSERT,UPDATE,DELETE  queries.	
			with open (split_file_name, "r") as myfile:
				select_file_name=filename+'_'+'select.sql'
				update_file_name=filename+'_'+'update.sql'
				insert_file_name=filename+'_'+'insert.sql'
				delete_file_name=filename+'_'+'delete.sql'
				uf=open(update_file_name,"w")
				sf=open(select_file_name,"w")
				inf=open(insert_file_name,"w")
				df=open(delete_file_name,"w")
				read_flag=0
				for line in myfile:	
					if line.find('UPDATE')!=-1:
						upos=line.find('UPDATE' )
						print(line[upos:],file=uf)
						continue
					if line.find('INSERT')!=-1:
						inpos=line.find('INSERT' )
						print(line[inpos:],file=inf)
						continue	
					if line.find('DELETE')!=-1:		
						dpos=line.find('DELETE')
						print(line[dpos:],file=df)
						continue
					if line.find('SELECT')!=-1:	
						spos=line.find('SELECT' )#there is a possibility that update,delete,insert will have select in them.so once the update/delete/insert is read mark it with * so select will not read that line
						print(line[spos:],file=sf)
				sf.close()
				uf.close()
				inf.close()	
				df.close()
			#Removing blank linese
			msg='Removing blank lines'
			log.info(fname+msg)
			select_file_name_final=select_file_name+'_'+'final.sql'
			#print(select_file_name_final)
			update_file_name_final=update_file_name+'_'+'final.sql'
			insert_file_name_final=insert_file_name+'_'+'final.sql'
			delete_file_name_final=delete_file_name+'_'+'final.sql'	
			with open(select_file_name_final,"w") as sout:
				with open(select_file_name,"r") as rf:
					for line in rf:
						if not line.isspace():
							sout.write(line)
							#print(line,file=f)
			with open(update_file_name_final,"w") as uout:				
				with open(update_file_name,"r") as f:
					for line in f:
						if not line.isspace():
							uout.write(line)	
			with open(insert_file_name_final,"w") as iout:
				with open(insert_file_name,"r") as f:
					for line in f:
						if not line.isspace():
							iout.write(line)
			with open(delete_file_name_final,"w") as dout:
				with open(delete_file_name,"r") as f:
					for line in f:
						if not line.isspace():
							dout.write(line)
				sout.close()
				uout.close()
				iout.close()
				dout.close()
			msg='Removing Into clause in SELECT queries'
			log.info(fname+msg)	
			#Remove INTO clause in SELECT statements .if there is no INTO clause just print the select as it is.
			select_file_name_into=select_file_name_final+'_'+'into.sql'
			sf=open(select_file_name_into,"w")
			with open (select_file_name_final, "r") as myfile:
				for line in myfile:	
					if line.find('INTO')!=-1:
						ipos=line.find('INTO' )
						fpos=line.find('FROM')
						print(line[:ipos]+line[fpos:],file=sf)
					else:
						print(line,file=sf)
			sf.close()

			#Replace variables with ?  in SELECT  file
			msg='Replace variables with ?  in SELECT  file'
			log.info(fname+msg)
			vlist=[]
			select_file_name_varrem=select_file_name_into+'_'+'varrem.sql'
			sf=open(select_file_name_varrem,"w")
			with open (select_file_name_into, "r") as f:
				for line in f:
					x=[m.start() for m in re.finditer('[vV]_',line)]#list containing the starting positions of the variable in the line 
					for i in x:
						pos=i
						z=i
						#print(pos)
						while (pos>0):
							pos=pos+1
							#print(pos)
							if (line[pos]== ' ' or line[pos]=='\n' or line[pos]==';' or line[pos]==')' or line[pos]==',') :
								p=line[z:pos]
								#print(p)p
								vlist.append(p)
								break
				newlist=list(set(vlist))#Remove duplicates
				print(newlist)	
			f.close()	
			#with open (r"c:\temp\TAECHECKEXHAUSTION.001.lob_select.sql_final.sql_into.sql","r")  as f:	
			with open (select_file_name_into,"r")  as f:	 
				line=f.read()
				for l in vlist:
					#print(list(set(vlist)))
					#print(line)
					if line.find(l)!=-1:
						line=line.replace(l,'\'?\'')
				print (line,file=sf)#should be outside for loop
			f.close()
			sf.close()
		
			#Replace variables with ?  in UPDATE  file
			msg='Replace variables with ?  in UPDATE  file'
			log.info(fname+msg)
			vlist=[]
			update_file_name_varrem=update_file_name_final+'_'+'varrem.sql'
			sf=open(update_file_name_varrem,"w")
			with open (update_file_name_final, "r") as f:
				for line in f:
					#print(re.findall(r'v_',line))
					x=[m.start() for m in re.finditer('[vV]_',line)]#list containing the starting positions of the variable in the line 
					for i in x:
						pos=i
						z=i
						#print(pos)
						while (pos>0):
							pos=pos+1
							#print(pos)
							if (line[pos]== ' ' or line[pos]=='\n' or line[pos]==';' or line[pos]==')' or line[pos]==',') :
								p=line[z:pos]
								#print(p)p
								vlist.append(p)
								break
				newlist=list(set(vlist))#Remove duplicates
				print(newlist)	
			f.close()	
			#with open (r"c:\temp\TAECHECKEXHAUSTION.001.lob_select.sql_final.sql_into.sql","r")  as f:	
			with open (update_file_name_final,"r")  as f:	 
				line=f.read()
				for l in vlist:
					#print(list(set(vlist)))
					#print(line)
					if line.find(l)!=-1:
						line=line.replace(l,'\'?\'')
				print (line,file=sf)#should be outside for loop
			f.close()
			sf.close()
			#Replace variables with ?  in INSERT  file
			msg='Replace variables with ?  in INSERT  file'
			log.info(fname+msg)
			vlist=[]
			insert_file_name_varrem=insert_file_name_final+'_'+'varrem.sql'
			sf=open(insert_file_name_varrem,"w")
			with open (insert_file_name_final, "r") as f:
				for line in f:
					#print(re.findall(r'v_',line))
					x=[m.start() for m in re.finditer('[vV]_',line)]#list containing the starting positions of the variable in the line 
					for i in x:
						pos=i
						z=i
						#print(pos)
						while (pos>0):
							pos=pos+1
							#print(pos)
							if (line[pos]== ' ' or line[pos]=='\n' or line[pos]==';' or line[pos]==')' or line[pos]==',') :
								p=line[z:pos]
								#print(p)p
								vlist.append(p)
								break
				newlist=list(set(vlist))#Remove duplicates
				print(newlist)	
			f.close()	
			#with open (r"c:\temp\TAECHECKEXHAUSTION.001.lob_select.sql_final.sql_into.sql","r")  as f:	
			with open (insert_file_name_final,"r")  as f:	 
				line=f.read()
				for l in vlist:
					#print(list(set(vlist)))
					#print(line)
					if line.find(l)!=-1:
						line=line.replace(l,'\'?\'')
				print (line,file=sf)#should be outside for loop
			f.close()
			sf.close()
			#Replace variables with ?  in DELETE  file
			msg='Replace variables with ?  in DELETE  file'
			log.info(fname+msg)
			vlist=[]
			delete_file_name_varrem=delete_file_name_final+'_'+'varrem.sql'
			sf=open(delete_file_name_varrem,"w")
			with open (delete_file_name_final, "r") as f:
				for line in f:
					#print(re.findall(r'v_',line))
					x=[m.start() for m in re.finditer('[vV]_',line)]#list containing the starting positions of the variable in the line 
					for i in x:
						pos=i
						z=i
						#print(pos)
						while (pos>0):
							pos=pos+1
							#print(pos)
							if (line[pos]== ' ' or line[pos]=='\n' or line[pos]==';' or line[pos]==')' or line[pos]==',') :
								p=line[z:pos]
								#print(p)p
								vlist.append(p)
								break
				newlist=list(set(vlist))#Remove duplicates
				print(newlist)	
			f.close()	
			#with open (r"c:\temp\TAECHECKEXHAUSTION.001.lob_select.sql_final.sql_into.sql","r")  as f:	
			with open (delete_file_name_final,"r")  as f:	 
				line=f.read()
				for l in vlist:
					#print(list(set(vlist)))
					#print(line)
					if line.find(l)!=-1:
						line=line.replace(l,'\'?\'')
				print (line,file=sf)#should be outside for loop
			f.close()
			sf.close()	
			
			
def explainselect(op,dsn_database,conn,log,repdir):
	fname='explainselect() - '
	msg='*** Starting explainselect function()'
	log.info(fname+msg)
	print(repdir)
	for filename in os.listdir(op):
		if filename.endswith("select.sql_final.sql_into.sql_varrem.sql"):
			os.chdir(op)
			newdir='SELECT' 
			if not os.path.exists(newdir):
				os.makedirs(newdir)
			cmd='db2caem -d '+dsn_database+' -o '+newdir+' -u db2admin '+' -p python '+' -sf '+filename
			msg='Calling DB2CAEM for SELECT file ' + '\n' +cmd
			log.info(fname+msg)
			try:
				#os.system(cmd)
				proc = subprocess.Popen(cmd,stdout=subprocess.PIPE, shell=True)#capture the db2caemoutput in the log
				(out,err) = proc.communicate()
				if err:
					msg=err.decode("utf-8")
					msg = msg.rstrip('\n')
					msg = os.linesep.join([s for s in msg.splitlines() if s])#Remove blank lines in the output
					log.info(fname+msg)
					
				msg=out.decode("utf-8")
				msg = msg.rstrip('\n')
				msg = os.linesep.join([s for s in msg.splitlines() if s])#Remove blank lines in the output
				log.info(fname+msg)
			except OSError:
				msg=msg+'\n'+traceback.format_exc()
				log.error(fname+err)
				msg='Error while calling DB2CAEM'
				popupmsg(msg)
				#sys.exit(msg)	
				
			os.chdir(newdir)	
			selectlog=findfile('db2caem.log',newdir)#fetch db2caem directory based on the log file
			#msg='Explain location for SELECT -'+ selectlog
			#log.info(msg)
			if selectlog:
				currdir=os.path.dirname(os.path.abspath(selectlog))
				flag='SELECT'
				parsedb2caem(currdir,op,flag,conn,log,repdir)
				os.chdir(op)
			
def explainupdate(op,dsn_database,con,log,repdir):
	for filename in os.listdir(op):
		if filename.endswith("update.sql_final.sql_varrem.sql"):
			os.chdir(op)
			newdir='UPDATE' 
			if not os.path.exists(newdir):
				os.makedirs(newdir)
			cmd='db2caem -d '+dsn_database+' -o '+newdir+' -u db2admin '+' -p python '+' -sf '+filename
			os.system(cmd)
			os.chdir(newdir)
			updatelog=findfile('db2caem.log',newdir)
			if updatelog:
				currdir=os.path.dirname(os.path.abspath(updatelog))
				flag='UPDATE'
				parsedb2caem(currdir,op,flag,con,log,repdir)
				os.chdir(op)			
def explaininsert(op,dsn_database,con,log,repdir):
	for filename in os.listdir(op):
		if filename.endswith("insert.sql_final.sql_varrem.sql"):
			os.chdir(op)
			newdir='INSERT' 
			if not os.path.exists(newdir):
				os.makedirs(newdir)
			cmd='db2caem -d '+dsn_database+' -o '+newdir+' -u db2admin '+' -p python '+' -sf '+filename
			os.system(cmd)
			os.chdir(newdir)
			insertlog=findfile('db2caem.log',newdir)
			if insertlog:
				currdir=os.path.dirname(os.path.abspath(insertlog))
				flag='INSERT'
				parsedb2caem(currdir,op,flag,con,log,repdir)
				os.chdir(op)
					
def explaindelete(op,dsn_database,con,log,repdir):
	for filename in os.listdir(op):
		if filename.endswith("delete.sql_final.sql_varrem.sql"):
			os.chdir(op)
			newdir='DELETE' 
			if not os.path.exists(newdir):
				os.makedirs(newdir)
			cmd='db2caem -d '+dsn_database+' -o '+newdir+' -u db2admin '+' -p python '+' -sf '+filename
			os.system(cmd)
			os.chdir(newdir)
			deletelog=findfile('db2caem.log',newdir)
			if deletelog:
				currdir=os.path.dirname(os.path.abspath(deletelog))
				flag='DELETE'
				parsedb2caem(currdir,op,flag,con,log,repdir)
				os.chdir(op)			
						
				
			
			#sf.close()
			#uf.close()
			#inf.close()	
			#df.close()

def openselect():
	op=outpath.get()
	os.chdir(op)
	log
	for filename in os.listdir(op):
		if filename.endswith("select.sql_final.sql"):
			with open (filename, "r") as myfile:
				select_formatted=filename+'_fmt.sql'
				with open(select_formatted, "w") as f:
					for line in myfile: 			
						print (sqlparse.format(line, reindent=True, keyword_case='upper'),file=f)
					f.close()
					with open (select_formatted,"r") as contents:
						with open('SELECT.html',"w") as e:
							for lines in contents.readlines():
								e.write("<prev>" + lines + "</prev> <br>\n")
							url='select.html'
							webbrowser.open(url)
						e.close()	
def openupdate():
	op=outpath.get()
	for filename in os.listdir(op):
		if filename.endswith("update.sql_final.sql"):
			with open (filename, "r") as myfile:
				update_formatted=filename+'_fmt.sql'
				with open(update_formatted, "w") as f:
					for line in myfile: 			
						print (sqlparse.format(line, reindent=True, keyword_case='upper'),file=f)
					f.close()
					with open (update_formatted,"r") as contents:
						with open('UPDATE.html',"w") as e:
							for lines in contents.readlines():
								e.write("<prev>" + lines + "</prev> <br>\n")
							url='update.html'
							webbrowser.open_new_tab(url)
						e.close()	

def opendelete():
	op=outpath.get()
	for filename in os.listdir(op):
		if filename.endswith("delete.sql_final.sql"):
			with open (filename, "r") as myfile:
				delete_formatted=filename+'_fmt.sql'
				with open(delete_formatted, "w") as f:
					for line in myfile: 			
						print (sqlparse.format(line, reindent=True, keyword_case='upper'),file=f)
					f.close()
					with open (delete_formatted,"r") as contents:
						with open('delete.html',"w") as e:
							for lines in contents.readlines():
								e.write("<prev>" + lines + "</prev> <br>\n")
							url='delete.html'
							webbrowser.open_new_tab(url)
						e.close()	
						
def openinsert():
	op=outpath.get()
	for filename in os.listdir(op):
		if filename.endswith("insert.sql_final.sql"):
			with open (filename, "r") as myfile:
				insert_formatted=filename+'_fmt.sql'
				with open(insert_formatted, "w") as f:
					for line in myfile: 			
						print (sqlparse.format(line, reindent=True, keyword_case='upper'),file=f)
					f.close()
					with open (insert_formatted,"r") as contents:
						with open('insert.html',"w") as e:
							for lines in contents.readlines():
								e.write("<prev>" + lines + "</prev> <br>\n")
							url='insert.html'
							webbrowser.open_new_tab(url)
						e.close()
def findfile(filename,subdir):
	op=outpath.get()
	os.chdir(op)
	if subdir:
		path=subdir
		print(path)
	else:
		print('Sub directory is not present')
	for root, dirs, names in os.walk(path):
		if filename in names:
			print(filename)
			return os.path.join(root, filename)						
			
def parsedb2caem(currdir,op,flag,conn,log,repdir):# generic function to parse the given db2caem file and insert in db2 table				
	lookup = 'Original Statement:'
	lookup1 = 'Optimized Statement:'
	lookup2='Explain level:'
	lookup3='Extended Diagnostic Information:'
	lookup4='Total Cost:'
	fname='parsedb2caem() -'
	msg='*******parsedb2caem started*****'
	log.info(fname+msg)
	width = os.get_terminal_size().columns
	sp=spname.get()
	os.chdir(currdir)
	totcost=[]
	#c=con.cursor()
	if flag=='SELECT':
		msg='Parsing the DB2CAEM file for '+flag+' file'
		log.info(fname+msg)
		planfile=op+'/'+'selectplan.html'
		table=['<html><body><table border="1"><CAPTION><b>SELECT PERFORMANCE REPORT - '+sp+'</b></CAPTION><thead><th>Original Query</th><th>Optimized Query</th><th>Access Plan</th></thead>']
	if flag=='UPDATE':
		msg='Parsing the DB2CAEM file for '+flag+' file'
		log.info(fname+msg)
		planfile=op+'/'+'updateplan.html'
		table=['<html><body><table border="1"><CAPTION><b>UPDATE PERFORMANCE REPORT - '+sp+'</b></CAPTION><thead><th>Original Query</th><th>Optimized Query</th><th>Access Plan</th></thead>']
	if flag=='INSERT':
		msg='Parsing the DB2CAEM file for '+flag+' file'
		log.info(fname+msg)
		planfile=op+'/'+'insertplan.html'
		table=['<html><body><table border="1"><CAPTION><b>INSERT PERFORMANCE REPORT - '+sp+'</b></CAPTION><thead><th>Original Query</th><th>Optimized Query</th><th>Access Plan</th></thead>']
	if flag=='DELETE':
		msg='Parsing the DB2CAEM file for '+flag+' file'
		log.info(fname+msg)
		planfile=op+'/'+'deleteplan.html'
		table=['<html><body><table border="1"><CAPTION><b>DELETE PERFORMANCE REPORT - '+sp+'</b></CAPTION><thead><th>Original Query</th><th>Optimized Query</th><th>Access Plan</th></thead>']
	msg='flag -'+flag
	log.debug(fname+msg)
	allplanfile=op+'/'+'allplan.html'
	alltable=['<html><body><table border="1"><CAPTION><b>FINAL PERFORMANCE REPORT - '+sp+'</b></CAPTION><thead><th>Original Query</th><th>Optimized Query</th><th>Access Plan</th></thead>']
	#with open (planfile,"w") as sf:
		for filename in os.listdir(currdir):
			print(filename)	
			if filename.startswith("db2caem.exfmt."):
				caemplanfile=filename+'_'+flag+'.plan'	
				#with open (planfile,"w") as pf:
				with open(filename) as myFile: 	#open the  db2caem file and note the line numbers of lookup values
					for num, line in enumerate(myFile, 1):
						if lookup in line:
							start=num
						if lookup1 in line:
							end=num	
						if lookup1 in line:
							start1=num
						if lookup2 in line:
							end1=num
						if lookup2 in line:
							start2=num
						if lookup3 in line:
							end2=num
						if line.find(lookup4)!=-1:
							pos=line.find(lookup4)
							cost=line[pos+11:]
							totcost.append(cost)
							#print(totcost)	
				#myFile.close()			
				with open(filename) as fp: 
					final_line1=""
					final_line2=""
					final_line3=""
					with open (caemplanfile,"w") as pf:		#writing  access plan			
						for i, line in enumerate(fp):					
							if i > start and i<end-1:
								final_line1=final_line1 +' '+line					
							if i > start1 and i<end1-1 :
								final_line2=final_line2 +' '+line
								#print(line,file=sf)
							if i > start2 and i<end2-1 :
								print(line,end='',file=pf)# Remove blank lines
								#pf.write(line)
							#if line.find()	
				link=os.path.abspath(caemplanfile)
				shutil.copy(caemplanfile,repdir)
				hlink='<a href ='+link+'>Click to see Accessplan'+'</a>'
				#plan='<object data = '+ '"'+link +'"'+'height="200"'+'/>'
				plan='<object data = '+ '"'+caemplanfile+'"'+'height="200"'+'/>'
				print(plan)
				#fp.close()
				table.append(r'<tr><td align=left width=20% style="white-space:pre-wrap;white-space:-moz-pre-wrap;white-space:-pre-wrap;white-space:-o-pre-wrap;word-wrap:break-word">{}</td><td align=left width=40% style="white-space:pre-wrap;white-space:-moz-pre-wrap;white-space:-pre-wrap;white-space:-o-pre-wrap;word-wrap:break-word">{}</td><td align=left width=5% ">{}</td></tr>'.format(final_line1,final_line2,plan))
				#table.append(r'<tr><td align=center width=20% style="word-wrap:break-word">{}</td><td align=center idth=40% style="word-wrap:break-word">{}</td><td align=center width=20% style="word-wrap:break-word">{}</td></tr>'.format(final_line1,final_line2,plan))
				#print(totcost[0])
				#INSERT final_line1 and totcost[0] into DB
				#sl_ins="INSERT INTO RESEARCH.QUERY_COST (TYPE,QUERY,COST) VALUES ("+"'"+flag+"'"+","+"'"+final_line1+"'"+","+totcost[0]+");"
				qry="'"+final_line1+"'"
				tcost=totcost[0]
				#print(sql_ins)
				#logger.debug('flag=%s,query=%s,tcost=%d',flag,qry,tcost)
				msg='flag -'+flag
				log.debug(fname+msg)
				msg='Query-'+qry
				log.debug(fname+msg)
				msg='tcost -'+tcost
				log.debug(fname+msg)
				#try:					
				#	stmt1, flag, qry, tcost = ibm_db.callproc(conn, 'research.ins_query_cost', (flag,qry, tcost))
					#stmt, sp, sch, op = ibm_db.callproc(conn, 'research.export_sp', (sp, sch, op))
				#except:					
				#	msg="Failed to insert into query_cost"
					#msg=traceback.print_exc(limit=1,file=sys.stdout)
					#traceback.print_exc(limit=1,file=sys.stdout)
				#	msg=msg+'\n'+traceback.format_exc()
				#	log.error(msg)
				#	log.closelog()
					#close DB connection
				#	popupmsg(msg)
				#	sys.exit(1)
		totcost=[]
		with open (planfile,"w") as sf:
			print(''.join(table),file=sf)
		shutil.copy(planfile,repdir)
		with open (allplanfile,"a") as asf:
			print(''.join(table),file=asf)			
		shutil.copy(allplanfile,repdir)
		fp.close()
		myFile.close()
	sf.close
	asf.close
	msg='*******parsedb2caem() ended*****'
	log.info(fname+msg)
	
def openselectp():#Select performance report
	op=outpath.get()
	dsn_dbname=dbname.get()
	os.chdir(op)
	url='selectplan.html'
	webbrowser.open(url)	
def openupdatep():#update performance report
	op=outpath.get()
	dsn_dbname=dbname.get()
	os.chdir(op)
	url='updateplan.html'
	webbrowser.open_new_tab(url)
def opendeletep():
	op=outpath.get()
	dsn_dbname=dbname.get()
	os.chdir(op)
	url='deleteplan.html'
	webbrowser.open_new_tab(url)
def openinsertp():
	op=outpath.get()
	dsn_dbname=dbname.get()
	os.chdir(op)
	url='insertplan.html'
	webbrowser.open_new_tab(url)
	
def clear():
	sp_box.delete(0,'end')
	schema_box.delete(0,'end')
	outpath_box.delete(0,'end')
def exit():
		root.destroy()
class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        self._geom='200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        master.bind('<Escape>',self.toggle_geom)            
    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom
class Logger(object):
		def __init__(self, name='logger',logname='log',logdir='c:\tmp', level=logging.DEBUG):
			self.logger = logging.getLogger(name)
			self.logger.setLevel(level)
			#logname=datetime.now().strftime('db2py_%d_%m_%Y_%H_%M_%S.log')
			logpath = os.path.join(logdir,logname)
			fh = logging.FileHandler('%s.log' % logpath, 'w')
			self.logger.addHandler(fh)
			
			sh = logging.StreamHandler()
			#self.logger.addHandler(sh)
			formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
			#sh.setFormatter(formatter)
			fh.setFormatter(formatter)

		def debug(self, msg):
			self.logger.debug(msg)

		def info(self, msg):
			self.logger.info(msg)

		def warning(self, msg):
			self.logger.warning(msg)

		def error(self, msg):
			self.logger.error(msg)		
		def closelog(self):
			for handler in self.logger.handlers[:]: 
				handler.close()
				self.logger.removeHandler(handler)
def	gitpush():
	print('Enter GIT repository URL')
				
		

if __name__ == '__main__':
	root=Tk()
	app=FullScreenApp(root)
	root.title("powered by P Y T H ON")
	root.iconbitmap(r'C:\Users\db2admin1\Desktop\icons\python.ico')
	#root.geometry("640*640+0+0") 
	heading = Label(root,text="DB2PY",font=("arial",30,"bold"),fg="steelblue").pack()
	label1 = Label(root,text=" SP name",font=("arial",15,"bold"),fg="steelblue").place(x=10,y=200)
	label2 = Label(root,text=" Schema name",font=("arial",15,"bold"),fg="steelblue").place(x=10,y=250)
	label3 = Label(root,text=" Work directory",font=("arial",15,"bold"),fg="steelblue").place(x=10,y=300)
	label4 = Label(root,text=" DB name",font=("arial",15,"bold"),fg="steelblue").place(x=10,y=350)
	#ADD boxes for DB Name,host,user,pw
	spname=StringVar()
	schema=StringVar()
	outpath=StringVar()
	dbname=StringVar()
	sp_box =Entry(root,textvariable=spname,width=35,bg="lightblue")
	sp_box.place(x=175,y=210)
	schema_box = Entry(root,textvariable=schema,width=35,bg="lightblue")
	schema_box.place(x=175,y=250)
	outpath_box = Entry(root,textvariable=outpath,width=35,bg="lightblue")
	outpath_box.place(x=175,y=300)
	dbname_box = Entry(root,textvariable=dbname,width=35,bg="lightblue")
	dbname_box.place(x=175,y=350)
	work=Button(root,text="OK",width=20,height=2,bg="lightblue",command=getsp).place(x=500,y=600)
	work=Button(root,text="Clear",width=20,height=2,bg="lightblue",command=clear).place(x=650,y=600)
	work=Button(root,text="Exit",width=20,height=2,bg="lightblue",command=exit).place(x=800,y=600)
	#Menu creation
	menu = Menu(root)
	root.config(menu=menu)
	filemenu = Menu(menu)
	menu.add_cascade(label="REPORTS",menu=filemenu)
	filemenu.add_command(label="SELECT",command=openselect)
	filemenu.add_command(label="UPDATE",command=openupdate)
	filemenu.add_command(label="DELETE",command=opendelete)
	filemenu.add_command(label="INSERT",command=openinsert)
	filemenu.add_command(label="Stored Procedure",command=openinsert)
	pfilemenu = Menu(menu)
	menu.add_cascade(label="PERFORMANCE REPORTS",menu=pfilemenu)
	pfilemenu.add_command(label="SELECT",command=openselectp)
	pfilemenu.add_command(label="UPDATE",command=openupdatep)
	pfilemenu.add_command(label="DELETE",command=opendeletep)
	pfilemenu.add_command(label="INSERT",command=openinsertp)
	pfilemenu.add_command(label="ALL",command=openinsertp)
	#pfilemenu.add_command(label="COMPARE PERFORMANCE",command=compare)
	#pfilemenu.add_command(label="Mail Report",command=compare)	
	pfilemenu.add_command(label="Top 5 fast SQL",command=openinsertp)
	pfilemenu.add_command(label="Top 5 slow SQL",command=openinsertp)
	dfilemenu = Menu(menu)
	menu.add_cascade(label="DATA VISUALIZATION",menu=dfilemenu)
	dfilemenu.add_command(label="QUERY GRAPH")
	dfilemenu.add_command(label="PERFORMANCE GRAPH")
	db2filemenu = Menu(menu)
	menu.add_cascade(label="TOOLS",menu=db2filemenu)
	db2filemenu.add_command(label="DB2 PROFILER")
	db2filemenu.add_command(label="DB2 ADVISOR")
	db2filemenu.add_command(label="OPTIMIZATION PROFILE")
	#GIT  Menu
	gitmenu = Menu(menu)
	menu.add_cascade(label="GIT",menu=gitmenu)
	gitmenu.add_command(label="GIT PUSH")
	
	
	
	#catch runttime errors
	#def show_error(self, *args):
	#	err = traceback.format_exception(*args)
	#	tkmsg.showerror('Exception',err)
	#tk.Tk.report_callback_exception = show_error
	
	
	
	
	root.mainloop()
	
