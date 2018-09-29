# modgs0ftio.py
# D. Gibbon, 2018-09-01

#=================================================================

import cgi, cgitb; cgitb.enable()
from cgi import escape

#=================================================================

print "Content-type: text/html\n\n"
print '<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01 Transitional//EN\" \"http://www.w3.org/TR/html4/loose.dtd\">'

def inithtml():
	print '<html><head><title>CRAFT - Demodulation and Reconstruction of Amplitude and Frequency Tracks. D. Gibbon</title>'
	print """
	<style type="text/css">
		tdp {font-size:14}
		td {font-size:14}
		p {font-size:14}
		li {font-size:14}
		small {font-size:14}
		big {font-size:18;font-weight:bold}
		verybig {font-size:24;font-weight:bold}
	</style>
	"""
	print '</head><body>'
	return

def terminatehtml():
	print "</body></html>"
	return


def definecgifields():
	return [
# External user and admin information
	'metadata',
  'filebase',

# S0FT
	'voicetype',

# Waveform
	'wavemedianfilt',
	'secstart',
	'seclen',

# Waveform handling:  downsampling, centre-clipping, Butterworth filters
###	'downsample', ### Use this???

	'cutofflo','orderlo','cutoffhi','orderhi','centreclip',

# F0 basics
	'algorithm',
	'f0min', 'f0max',
	'framerate', 'freqweight',	# Maybe make these fixed?
	'hilbertflag',
	'fft', 'zerox', 'peaks',

# Not used in CRAFT:	's0ftflag','raptflag', 'pyraptflag', 'praatflag','spectrogramflag',

# Outlier handling
	'f0clipmin','f0clipmax','f0medianfilt',

# Modelling: Polynomial; AEMS / FEMS
	'polydegreeglobal',	# Note that < 1 means no polynomial
	'polydegreelocal',
	'polydegreespectrum',
	'f0switch',

	'spectmin', 'spectmax',
	'spectwinfactor',

	'aemshzmin', 'aemshzmax',
	'amdiffspectpower', 'fmdiffspectpower',

# Noise/voicing filter (negative effect on current examples)
# Not used:	'voicewin','voicediff',

# Display dimensions
	'figwidth', 'figheight'

	]

def convertcgiparams(cgiparams):

	metadata = cgiparams['metadata']
	filebase = cgiparams['filebase']

# Waveform
# Signal subsequence

	secstart = float(cgiparams['secstart'])	# In HTML: clipstart, clipend
	seclen = float(cgiparams['seclen'])

	centreclip = float(cgiparams['centreclip'])
	wavemedianfilt = int(cgiparams['wavemedianfilt'])		# Not really necessary because of Butterworth
# Butterworth
	cutoffhi = int(cgiparams['cutoffhi'])
	orderhi = int(cgiparams['orderhi'])
	cutofflo = int(cgiparams['cutofflo'])
	orderlo = int(cgiparams['orderlo'])

# S0FT shortcut
	voicetype = cgiparams['voicetype']

# F0
	algorithm = cgiparams['algorithm']

	f0min = int(cgiparams['f0min'])	# For RAPT, PyRapt, Praat and plot display height
	f0max = int(cgiparams['f0max'])

	framerate = float(cgiparams['framerate'])
# RAPT
	freqweight = float(cgiparams['freqweight'])

	fft = cgiparams['fft']
	zerox = cgiparams['zerox']
	peaks = cgiparams['peaks']
	hilbertflag = cgiparams['hilbertflag']
	f0medianfilt = int(cgiparams['f0medianfilt'])	# After clipping?
	polydegreeglobal = int(cgiparams['polydegreeglobal'])	# Also for AEMS/FEMS spectra
	polydegreelocal = int(cgiparams['polydegreelocal'])
	polydegreespectrum = int(cgiparams['polydegreespectrum'])
	f0switch = cgiparams['f0switch']
	
# Spectrum display
	f0clipmin = int(cgiparams['f0clipmin'])	# As a final filter prior to display
	f0clipmax = int(cgiparams['f0clipmax'])	# As a final filter prior to display

	spectmin = int(cgiparams['spectmin'])
	spectmax = int(cgiparams['spectmax'])
	spectwinfactor = float(cgiparams['spectwinfactor'])

	aemshzmin = int(cgiparams['aemshzmin'])
	aemshzmax = int(cgiparams['aemshzmax'])

	amdiffspectpower = int(cgiparams['amdiffspectpower'])
	fmdiffspectpower = int(cgiparams['fmdiffspectpower'])

	figwidth = float(cgiparams['figwidth'])
	figheight = float(cgiparams['figheight'])

	sharedparams = metadata, filebase, secstart, seclen, centreclip, wavemedianfilt, cutoffhi, orderhi, cutofflo, orderlo, algorithm, f0min, f0max, framerate, freqweight, polydegreeglobal,polydegreelocal,polydegreespectrum,f0switch

	s0ftparams = fft, zerox, peaks, hilbertflag, f0medianfilt, voicetype

	displayparams = f0clipmin, f0clipmax, spectmin, spectmax, spectwinfactor, aemshzmin, aemshzmax, amdiffspectpower, fmdiffspectpower, figwidth, figheight

	return sharedparams, s0ftparams, displayparams

#======================
# Fetch CGI parameters as dictionary

def cgitransferlines(cgifields):
	fieldstorage = cgi.FieldStorage()
	fieldvalues = []
	for field in cgifields:
		if fieldstorage.has_key(field):
			fieldname = fieldstorage[field].value
		else:
			fieldname = '1066'
		fieldvalues = fieldvalues + [(field,fieldname)]
	return dict(fieldvalues)

#=================================================================

#===================================================================

def htmloutput(webaudioclip, webfigfile, filebase, samprate, signalduration, signalsamples, secstart, seclen, framerate):

	print '<table align="center"><tr align="center">'
	print '<td valign="bottom">'
	print '<audio controls="controls" preload="metadata" style="width: 90%;" src="'+webaudioclip+'" type="audio/wav">'
	print 'Your browser does not support the audio element.</audio>'
	print '</td></tr>'
	print '<tr align="center"><td>'
	print '<p align=center><img src='+webfigfile+'></p>'

	print "</td></tr></table>"

	print '<table><tr><td width=25% valign=\"top\" rowspan=\"2\"><table>'
	print '<tr><td><b>Selected settings</b></td></tr>'
	print '<tr><td></td><td>Signal filename:</td><td>'+filebase+'</td></tr>'
	print '<tr><td></td><td>Sampling rate:</td><td>'+str(samprate)+'</td></tr>'
	print '<tr><td></td><td>Total duration:</td><td>'+str(signalduration)+'</td></tr>'
	print '<tr><td></td><td>Total samples:</td><td>'+str(signalsamples)+'</td></tr>'
	print '<tr><td></td><td>Segment start:</td><td>'+str(secstart)+'</td></tr>'
	print '<tr><td></td><td>Segment duration:</td><td>'+str(seclen)+'</td></tr>'

	print '<tr><td></td><td>Segment first:</td><td>'+str(secstart*samprate)+'</td></tr>'
	print '<tr><td></td><td>Segment samples:</td><td>'+str(seclen*samprate)+'</td></tr>'
	print '<tr><td></td><td>Selected end:</td><td>'+str(secstart+seclen)+'</td></tr>'

	print '<tr><td></td><td>F0 frame rate:</td><td>'+str(framerate)+'</td></tr>'

	print '</table>'

	return

#=================================================================
