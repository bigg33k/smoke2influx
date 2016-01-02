#!/usr/bin/python
from datetime import datetime

import os
import time
import subprocess
import socket
import string
import ConfigParser

#---------------------------------------------------------
def get_filepaths(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.
#------------------------------------------------------

config = ConfigParser.ConfigParser()
config.readfp(open('/home/pi/s2i/s2i.conf'))

#print config.get('Smokeping','SMOKEPINGDATA')


#get files and directories
rrds = []
rrds = get_filepaths(config.get('Smokeping','SMOKEPINGDATA'))
 
#get tags
tags = []
for f in rrds:
	if f.endswith(".rrd"):
		try:
			if f.index('~'):
				thattag,thistag=f.split('~')
				tag,junk=thistag.split('.rrd')
				if not tag in tags:
					tags.append(tag)
		except ValueError:
			#don't care
			continue
		
#print tags
timestamp=0;
smokestr = []
smokedata = []
for f in rrds:
	if f.endswith(".rrd"):
		host = f.split('/')
		linesize=len(host)-1
		label = host[linesize].split('~')
		#check to se if the result came from the master
		if len(label) == 1:
			#print label
			#get last update from rrd file
			response=subprocess.Popen(['rrdtool', 'lastupdate',f], stdout=subprocess.PIPE).communicate()[0]
			results = response.split('\n')
		
			smokestr = results[0].split(' ')
			smokedata = results[2].split(' ')		

			count=0
			message=""
			timestamp=0
			for str in smokestr:
				
				if "uptime" in str:
					timestamp=smokedata[0][:-1]
				elif len(str)<1:
					continue
				else:
					message+=" " + str
					if "-" in smokedata[count]:
						number,junk=smokedata[count].split('e-')
						message+=" value=" + number
					elif "U" in smokedata[count]:
						message+=" value=0"
					else:
						message+=" value=" + smokedata[count]	
					
					#prepare for insertion, grab master from config
					menu = label[0].split('.')
					payload="'smokeping,host=%s,label=%s,point=%s'" % (config.get('Smokeping','SMOKEMASTER'),menu[0],message.lstrip())
					curlresult=subprocess.Popen("curl -s -i -XPOST http://192.168.1.121:8086/write?db=smokeping --data-binary " +payload, stdout=subprocess.PIPE,shell=True)
					#print payload
				message=""
				count+=1
		
		else:
		
		#must have been a slave then

			 #get last update from rrd file
                        response=subprocess.Popen(['rrdtool', 'lastupdate',f], stdout=subprocess.PIPE).communicate()[0]
                        results = response.split('\n')

              	        smokestr = results[0].split(' ')
                        smokedata = results[2].split(' ')

                        count=0
                        message=""
                        timestamp=0
                        for str in smokestr:
         
				
				if "uptime" in str:
					timestamp=smokedata[0][:-1]
				elif len(str)<1:
					continue
				else:
					message+=" " + str
					if "-" in smokedata[count]:
						number,junk=smokedata[count].split('e-')
						message+=" value=" + number
					elif "U" in smokedata[count]:
						message+=" value=0"
					else:
						message+=" value=" + smokedata[count]	
					
					#prepare for insertion, grab master from config
					menu = label[0].split('.')
					origin = label[1].split('.')
					payload="'smokeping,host=%s,label=%s,point=%s'" % (origin[0],menu[0],message.lstrip())
					curlresult=subprocess.Popen("curl -s -i -XPOST http://192.168.1.121:8086/write?db=smokeping --data-binary " +payload, stdout=subprocess.PIPE,shell=True)
					#print payload

                                     
                                message=""
                                count+=1



