# modgdemodulation.py

"""
Amplitude envelope demodulation.
Amplitude envelope spectrum with heatmap and difference spectrum.

Frequency envelope demodulation (F0 estimation / pitch tracking)
Frequency envelope spectrum with heatmap and difference spectrum.
Global and polynomial models of F0 estimation.
Spectrum polynomial model.
Algorithm choice:
1. S0FT: Dafydd Gibbon
2. RAPT: David Talkin
3. PyRapt: Daniel Gaspari
4. Praat: Paul Boersma
	1. Default
	2. Autocorrelation
	3. Cross-correlation
"""

import numpy as np
from scipy.signal import medfilt
from scipy.signal.signaltools import hilbert
# from scipy.signal import spectrogram

# import modgrapt, modgpyrapt, modgs0ft, modgpraat, modgs0ftio
import modgpyrapt, modgs0ft, modgs0ftio

#======== Function definitions

def sqr(i): return i**2

#=====================================================================

def getregression(y,polynom):
	x = range(len(y))
	#===== Partial calculation
	# fit = np.polyfit(x,y,1)
	#==== Full calculation
	fit, res, _, _, _ = np.polyfit(x, y, polynom, full=True)
#	fit_fn = np.poly1d(fit)
	#====== Is m and b extraction correct for the full vector?
	m = fit[0]
	b = fit[1]
	m = round(1000*m)/1000.0
	b = round(1000*b)/1000.0
	#====== Reconstruct polynomial regression curve
	yfit = np.polyval(fit,x)
	yres = y-yfit
	# Round to 3 decimal places
	yresrms = round(100*np.mean(map(sqr,yres))**0.5)/100.0
	return m,b,yfit,yres,yresrms
#	fit = np.polyfit(x,y,1)			# (partial)

def polyregline(x,y,d):
	x = range(len(y))
	fit, res, _, _, _ = np.polyfit(x, y, d, full=True)
	yfit = np.polyval(fit,x)
	return yfit
# fit with np.polyfit; linear (degree 1) regression only

def polyregline2(x,y,d):
	m, b, _, _, _ = stats.linregress(x, y)
	poly = [ m * xx + b for xx in x]
	return poly

#================================================================
# Envelopes with peak-picking and Hilbert transform

def sigpeaks(x,k):
	signalabs = abs(x)
	peaksrange = range(len(signalabs)-k)
	signalpeaks = []
	for i in peaksrange:
		signalpeaks += [np.max(signalabs[i:i+k])]
	return signalpeaks

#========================================================================
# Calculate envelope spectrum

def fft1(e,period):
		w = np.abs(np.fft.fft(e))**2
		freqs = np.abs(np.fft.fftfreq(e.size,period))
		idx = np.argsort(freqs)
		return freqs,w,idx


def fftnew(signal,period):
	signal = np.array(signal)
	w = np.abs(np.fft.fft(signal))**2
	freqs = np.abs(np.fft.fftfreq(signal.size,period))
	idx = np.argsort(freqs)
	wlog = np.log10(w)
	spectrumlen = len(wlog)
	spectrumlenhalf = int(round(spectrumlen/2.0))
	frequencies = freqs[:spectrumlenhalf]
	magnitudes = wlog[:spectrumlenhalf]	# log magnitudes
	return frequencies,magnitudes

#=====================================
# Calculate AEMS or FEMS

def spectrumcalc(signal,samplingfrequency,aemshzmin,aemshzmax):

# Calculate FFT over the envelope
	period = 1.0/samplingfrequency
	frequencies, magnitudes = fftnew(signal,period)

# Collect FFT data
	spectrumlen = len(frequencies)
	freqmin = np.min(frequencies[0])
	freqmax = int(round(np.max(frequencies[-1])))

# Calculate top frequency (actually = int(round(frequencies[-1])))
# and coefficients per hertz
	topfreq = samplingfrequency/2
	coeffperhertz = spectrumlen/topfreq

# Convert selected spectrum segment to spectral points (coefficients)
	mincoeff = aemshzmin * coeffperhertz
	maxcoeff = aemshzmax * coeffperhertz
	frequenciessegment = frequencies[mincoeff:maxcoeff]
	magnitudessegment = magnitudes[mincoeff:maxcoeff]

	return frequenciessegment, magnitudessegment

#===========================================================================
# Polynomial models

def zeroandmedianise(f0list, f0min, f0max):

	f0squashvec = np.array([ x for x in f0list if x>f0min and x<f0max ])
	f0median = np.median(f0squashvec)

	f0medianised = np.array([ x if x>f0min and x<f0max else f0median  for x in f0list ])
	f0zeroed = np.array([ x if x>f0min and x<f0max else 0  for x in f0list ])

	return f0median, f0medianised, f0zeroed

#============================================

def f0polylines(f0list, f0min, f0max, polydegreelocal, polydegreeglobal):

	f0median, f0medianised, f0zeroed = zeroandmedianise(f0list, f0min, f0max)

	if polydegreelocal > 0:
		localpolyline = makelocalpolyline(f0zeroed, f0min, f0max, polydegreelocal)
	else: localpolyline = []

	if polydegreeglobal > 0:
		globalpolyline = makeglobalpolyline(f0medianised, polydegreeglobal)
	else:
		globalpolyline = []
			
	return localpolyline, globalpolyline, f0median, f0medianised, f0zeroed

#============================================

def makelocalpolyline(f0zeroed,f0min,f0max,polydegreelocal):

	localpoly = []
	tempwin = []

	for f in f0zeroed:
		if f > f0min and f < f0max:
			tempwin = np.append(tempwin, [f])
		else:										# i.e. if f is out of bounds
			if len(tempwin) > 1:
				xx = np.arange(len(tempwin))
				tempwin = polyregline(xx,tempwin,polydegreelocal)
			localpoly = np.append(localpoly,tempwin)
			localpoly = np.append(localpoly,[f])
			tempwin = []

	localpoly = np.asarray(localpoly)

	return localpoly

#============================================

def makeglobalpolyline(f0medianised, polydegree):

	xx = range(len(f0medianised))
	polymodels = np.array(polyregline(xx,f0medianised,polydegree))

	return polymodels

#========================================================================
# Jassem difference spectrum

def jassemdiffspectrum(magnitudessegment,diffspectpower):

	absmagnitudediffs = abs(np.diff(magnitudessegment))
	absmagnitudediffs[0] = 0
	absmagnitudediffs = np.append(absmagnitudediffs, [0])
	absmagnitudediffs = absmagnitudediffs**diffspectpower

	return absmagnitudediffs

#========================================================================
# AM demodulation

def amdemodulation(selectsignal, samprate, aemshzmin, aemshzmax, wavmedianfilt, amdiffspectpower, polydegreespectrum):

	rectifiedselectsignal = abs(selectsignal)

	peakwindow = int(round(samprate/100.0))
	peakpadding = [0]*(int(round(peakwindow/2.0)))
	selectenvelopepeaks = peakpadding + sigpeaks(rectifiedselectsignal, peakwindow) + peakpadding

	newmedianfilt = 2*int((samprate/2.0) / wavmedianfilt) + 1

#	if hilbertflag:
#		selectenvelopehilbert = abs(hilbert(selectsignal))**1.04
#		selectenvelopehilbert = medfilt(selectenvelopehilbert, kernel_size=newmedianfilt)

	selectenvelope = np.array(selectenvelopepeaks)

	frequenciessegment, magnitudessegment =	spectrumcalc(selectenvelope, samprate, aemshzmin, aemshzmax)
	amabsmagnitudediffs = jassemdiffspectrum(magnitudessegment,amdiffspectpower)
	if polydegreespectrum > 0:
		amspectrumpolyline = np.array(polyregline(frequenciessegment, magnitudessegment, polydegreespectrum))
	else:
		amspectrumpolyline = []

	return rectifiedselectsignal, selectenvelope, frequenciessegment, magnitudessegment, amabsmagnitudediffs, amspectrumpolyline

#========================================================================
# Estimate F0

def fmdemodulation(tempwavfilebase, selectsignal, samprate, algorithm, fft, zerox, peaks, polydegreeglobal, framerate, stepfactor, f0medianfilt, f0min, f0max, centreclip, f0clipmin, f0clipmax, cutoffhi, orderhi, cutofflo, orderlo):

	if algorithm == 'S0FT':
		try:
			f0list = modgs0ft.s0ft(selectsignal, samprate, fft, zerox, peaks, polydegreeglobal, framerate, stepfactor, f0medianfilt, f0min, f0max, centreclip, f0clipmin, f0clipmax, cutoffhi, orderhi, cutofflo, orderlo)
		except:
		 	print 'Error with S0FT.'; exit()

	elif algorithm == 'RAPT':
		if True:
			import modgrapt
			f0list,voicelist = modgrapt.rapt(tempwavfilebase, f0min, f0max, "0.01", "0.02")
		if False:
			print 'RAPT is not available on this server.'; exit()

	elif algorithm == 'PyRapt':
		try:
			f0list = modgpyrapt.rapt(tempwavfilebase)
		except:
			print 'Error with PyRapt.'; exit()

	elif algorithm[:5] in 'Praat':
		try:
			import modgpraat
			if algorithm == 'PraatAC':
				type = 'ac'
			elif algorithm == 'PraatCC':
				type = 'cc'
			else:
				type = 'default'
			praattimes,f0list = modgpraat.praatf0estimate(tempwavfilebase, 0.01, f0min, f0max, type)
#			print len(praattimes),
		except:
			print 'Praat is not available on this server.'; exit()

	else: print "Unknown F0 algorithm."; exit()

#	print len(f0list),"<br>"

	return np.array(f0list)

#========================================================================
# FM spectrum

def fmspectrum(f0medianised, secstart, seclen, framerate, aemshzmin, aemshzmax, fmdiffspectpower, polydegreespectrum):
	try:
# FEMS
		f0frequenciessegment, f0magnitudessegment =	spectrumcalc(f0medianised, 1/framerate, aemshzmin, aemshzmax)
		fmabsmagnitudediffs = jassemdiffspectrum(f0magnitudessegment, fmdiffspectpower)

		if polydegreespectrum > 0:
			fmspectrumpolyline = np.array(polyregline(f0frequenciessegment, f0magnitudessegment, polydegreespectrum))
		else:
			fmspectrumpolyline = []
	except:
		print "Error calculating FM envelope spectrum."; exit()

	return f0frequenciessegment, f0magnitudessegment, fmabsmagnitudediffs, fmspectrumpolyline

