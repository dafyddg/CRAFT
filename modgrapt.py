# modgf0.py

import os
import numpy as np

"""
David Talkin's RAPT (get_f0 in ESPS) algorithm: David Talkin "A Robust Algorithm for Pitch Tracking (RAPT) in Speech Coding and Synthesis". In W. B. Kleijn and K. K. Palatal (eds), pages 497-518, Elsevier Science B.V., 1995
Debian distribution obtained from:
http://www.phon.ox.ac.uk/releases
"""

#================================================================
#======== F0 estimation

def rapt(filebase,f0min,f0max,framerate,freqweight):

#	filebase is fullfilebase, i.e. containing directory prefix.
	wavfilename = filebase + ".wav"
	f0filename = filebase + ".f0"
	f0csvfilename = filebase + ".csv"
	f0logfilename = filebase + ".f0log"
	paramfilename = "raptparams"
	paramstring = "float min_f0 = "+str(f0min)+";\nfloat max_f0 = " + str(f0max)+";\nfloat frame_step = " + str(framerate) + ";\nfloat freq_weight = " + str(freqweight) + ";\n"

#======== Write params file with either command line or default option
	handle = open(paramfilename, "w")
	handle.write(paramstring)
	handle.close()

#======== Define f0 command names
	getf0filename = "/opt/esps/bin/get_f0"
	getpplainfilename = "/opt/esps/bin/pplain"

#======== Define f0 and run estimation and conversion commands
	getf0command = getf0filename+" -P "+paramfilename+" "+wavfilename + " " + f0filename
	getcsvcommand = getpplainfilename+" "+f0filename + " > " + f0csvfilename
	os.system(getf0command + " 2> " + f0logfilename)
	os.system(getcsvcommand + " 2> " + f0logfilename)

#===== Deletion of temporary F0 files (see note above) - blocked for tests
	cleanf0filescommand = "rm -f *.f0 *.csv *log"
#	os.system(cleanf0filescommand)

#====== Read CSV file for F0 graphics
	handle = open(f0csvfilename,"r")
	csvlines = handle.readlines()
	handle.close()
	csvtable = [ line.split(" ")[:-1] for line in csvlines if line != '' ]
	if len(csvtable) < 1:
        	print "No f0 output detected."
        	exit()

#================================================================
#======== F0 data format conversion

	csvarray = np.array([ map(float,x) for x in csvtable])
	f0list = csvarray[:,0]
	voicelist = csvarray[:,1]

	return f0list,voicelist
