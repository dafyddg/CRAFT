# modggraphics.py

import numpy as np
# Import this before importing pyplot:
import matplotlib as mpl
mpl.use('Agg')   # WWW and saved graphics files
import matplotlib.pyplot as plt
import matplotlib.cm as cm


#===================================================================
#===================================================================
# Main wrapper for display output

def callgraphics(selectionparams, figureparams,signalparams, spectrumparams, f0params, aemsparams, femsparams):

#======== Fixed values for display settings

	fontsize = 8
	fontsizebig = 16

	fignum = 1

	rowinc = 1
	rowdec = 1
	normalrowspan = 4
	rownum = 0
	rowspan=normalrowspan
	colnum = 0
	colspan = 3	# Exceptions for aems and fems currently hard-wired

# Figure grid: 23 rows + 3 columns
# Waveform: 2 rows, the other 4 rows 4 each
	figrows = 23
	figcols = 3
	
	jassemxtickcount = 5

#======== Variable values for display settings

	algorithm = selectionparams #, waveform, spectro, f0track, amspect, fmspect = selectionparams
	
	waveform = spectro = f0track = amspect = fmspect = True

	figwidth, figheight, localfigfile = figureparams

	filebase, selectsignal, samprate, rectifiedselectsignal, selectenvelope, samprate, secstart, seclen = signalparams

	spectmin, spectmax, spectwin = spectrumparams

	f0list, framerate, secstart, seclen, f0min, f0max, f0switch, localpolyline, globalpolyline = f0params

	frequenciessegment, magnitudessegment, amspectrumpolyline, aemshzmin, aemshzmax, f0frequenciessegment, amabsmagnitudediffs = aemsparams

	f0frequenciessegment, f0magnitudessegment, fmspectrumpolyline, fmabsmagnitudediffs = femsparams

	fig = plt.figure(1,figsize=(figwidth,figheight))

	plt.suptitle("AM & FM signals and spectra: "+filebase+"\n\n",fontsize=fontsizebig)

#===================================================================
#======== Plot waveform

	if waveform:

		ax1 = plt.subplot2grid((figrows,figcols), (rownum,0),rowspan=rowspan,colspan=colspan)

	 	title = "\n\nAM carrier with amplitude envelope"
		xlabel = ""
		ylabel = 'Amplitude\n\n'
		colspan = 3
		waveformplot(ax1, selectsignal, rectifiedselectsignal, selectenvelope, samprate, secstart, title, xlabel, ylabel, fontsize)

#===================================================================
#======== Plot spectrogram

	if spectro:
		rownum += rowspan; rowspan=normalrowspan+rowinc	
		ax2 = plt.subplot2grid((figrows,figcols),(rownum,0),rowspan=rowspan,colspan=colspan)

		title = 'Spectrogram (win = '+str(spectwin)+', sampling rate = '+str(samprate)+'), time axis from zero.'
		xlabel = ""
		ylabel = 'Freq [Hz]'
		colspan = 3
		spectrogramplot(ax2, selectsignal, samprate, spectmin, spectmax, spectwin, title, xlabel, ylabel, fontsize)

#===================================================================
#======== Plot f0

	if f0track:
		rownum += rowspan; rowspan=normalrowspan+rowinc
		ax3 = plt.subplot2grid((figrows,figcols),(rownum,0),rowspan=rowspan,colspan=colspan)

		if len(globalpolyline) > 0:
			title = 'FM envelope (aka pitch track: '+algorithm+', framerate='+str(framerate)+'s) with local and global polynomial models\nGlobal model: green dotted, out of bounds values (e.g. unvoiced) reset to median of in-bounds values.'
		else:
			title = 'FM envelope (aka pitch track: '+algorithm+', framerate='+str(framerate)+'s)'
		xlabel = ""
		ylabel = 'Freq [Hz]'
		f0plot(ax3, f0list, framerate, secstart, seclen, f0min, f0max, f0switch, localpolyline, globalpolyline, title, xlabel, ylabel, fontsize)

#==============================================================================
#======== Plot AM envelope modulation spectrum

	if amspect:
		rownum += rowspan; rowspan = normalrowspan
		ax4 = plt.subplot2grid((figrows,figcols), (rownum,0), rowspan=rowspan, colspan=1)
		title = "AM Envelope Spectrum\n(0.0,...,"+str(aemshzmax)+"Hz)"
		xlabel = ""
		ylabel = ""
		envelopespectrumplot(ax4, frequenciessegment, magnitudessegment, amspectrumpolyline, title, xlabel, ylabel, fontsize)

#======== Heatmap of envelope spectrum
# length = samprate * seclen

		ax4b = plt.subplot2grid((figrows,figcols), (rownum,1), rowspan=rowspan, colspan=1)
		title = "Heatmap of AM Envelope Spectrum\n(0.0,...,"+str(aemshzmax)+"Hz)"
		xlabel = ""
		ylabel = ""
		envelopeheatmapplot(ax4b, frequenciessegment, magnitudessegment, title, xlabel, ylabel, fontsize)

#======== Jassem spectrum

		ax4c = plt.subplot2grid((figrows,figcols),(rownum,2), rowspan=rowspan, colspan=1)
		title = "Jassem Edge Detector\n(AM rhythm zones)"
		xlabel = ""
		ylabel = ""
		jassemdiffspectplot(ax4c, frequenciessegment, amabsmagnitudediffs, aemshzmin, aemshzmax, title, xlabel, ylabel, fontsize, jassemxtickcount)

#==================================================================
#======== Plot FM envelope modulation spectrum

	if fmspect:
		rownum += rowspan; rowspan=normalrowspan
		ax5 = plt.subplot2grid((figrows,figcols), (rownum,0), rowspan=rowspan, colspan=1)
		title = "FM Envelope Spectrum\n(0.0,...,"+str(aemshzmax)+"Hz)"
		xlabel = ""
		ylabel = ""
		envelopespectrumplot(ax5, f0frequenciessegment, f0magnitudessegment, fmspectrumpolyline, title, xlabel, ylabel, fontsize)

#======== Heatmap of envelope spectrum
# length = samprate * seclen

		ax5b = plt.subplot2grid((figrows,figcols), (rownum,1), rowspan=rowspan, colspan=1)
		title = "Heatmap of FM Envelope Spectrum\n(0.0,...,"+str(aemshzmax)+"Hz)"
		xlabel = ""
		ylabel = ""
		envelopeheatmapplot(ax5b, f0frequenciessegment, f0magnitudessegment, title, xlabel, ylabel, fontsize)

#======== Jassem spectrum

		ax5c = plt.subplot2grid((figrows,figcols), (rownum,2), rowspan=rowspan, colspan=1)
		title = "Jassem Edge Detector\n(FM rhythm zones)"
		xlabel = ""
		ylabel = ""
		jassemdiffspectplot(ax5c, f0frequenciessegment, fmabsmagnitudediffs, aemshzmin, aemshzmax, title, xlabel, ylabel, fontsize, jassemxtickcount)

#===================================================================

	totalrowspan = rownum + rowspan

	plt.tight_layout(pad=0.8, w_pad=1, h_pad=0)

	plt.savefig(localfigfile)

	return

#===================================================================
#==============================================================================

def waveformplot(ax1, signal, rectifiedsignal, envelope, samprate, secstart, title, xlabel, ylabel, fontsize):
	
	ax1.set_title(title,fontsize=fontsize)
#	ax1.set_xlabel(xlabel,fontsize=fontsize)
	ax1.set_ylabel(ylabel,fontsize=fontsize)
	
	y = signal
	leny = len(y)
	x = range(leny)
	
	ey = envelope
	leney = len(ey)
	ex = range(leney)

	ax1.set_xlim(-leny*0.001,leny+leny*0.001)
	
	xticks = np.arange(0,leny+1,leny/5)
	ax1.set_xticks(xticks)
	ax1.tick_params(axis='both', labelsize=fontsize)
	xticklabels = [ "%.1f"%(secstart+float(l)/samprate) for l in xticks ]
	ax1.set_xticklabels(xticklabels,fontsize=fontsize)

	miny = np.min(y)
	maxy = np.max(y)
	yticks = np.linspace(miny,maxy,3)
	ax1.set_yticks(yticks)
	yticklabels = [ '-1','0','1' ]
	ax1.set_yticklabels(yticklabels,fontsize=fontsize)

	ax1.grid(which='both',axis='x',linewidth="1",linestyle='--')
	ax1.set_yticks([])

	plt.plot(x,y,color='green')
	plt.plot(x,rectifiedsignal,color='lightgreen')
	plt.plot(ex,ey,color='red')

#	if hilbertflag:
#		pey = envelopehilbert*1.1
#		pex = range(len(pey))
#		plt.plot(pex,pey,color='orange')
	return

#==============================================================================

def spectrogramplot(ax2, signal, samprate, spectmin, spectmax, spectwin, title, xlabel, ylabel, fontsize):

	plt.tick_params(axis='both', left='on', top='off', right='off', bottom='on', labelleft='on', labeltop='off', labelright='off', labelbottom='on')

	ax2.tick_params(axis='both', labelsize=fontsize)
	ax2.set_title(title,fontsize=fontsize)
#	plt.xlabel(xlabel,fontsize=fontsize)
	plt.ylabel(ylabel,fontsize=fontsize)

	NFFT = spectwin
	ax2.specgram(signal, NFFT=NFFT, Fs=samprate)
	plt.axis(ymin=spectmin, ymax=spectmax)
	ax2.grid(which='both',axis='both',linewidth="1",linestyle='--')
	return

#==============================================================================

def f0plot(ax, f0list, framerate, secstart, seclen, f0min, f0max, f0switch, localpolyline, globalpolyline, title, xlabel, ylabel, fontsize):

	ax.set_title(title,fontsize=fontsize)
	ax.set_ylabel(ylabel,fontsize=fontsize)
	ax.grid(which='both',axis='both', linewidth="1", linestyle='--')
	ax.tick_params(axis='both', labelsize=fontsize)

	y = f0list
	leny = len(y)
	x = np.linspace(0,leny,leny)
	displaybuffer = 0.0*seclen
	start = secstart-displaybuffer
	end = secstart+seclen+displaybuffer
	xtickcount = 11
	xticks = np.linspace(0,leny,xtickcount)
	xlabels = np.linspace(start,end,xtickcount)
	if seclen < 5:
		xlabels = [ "%.3f"%xx for xx in xlabels ]
	plt.xticks(xticks,xlabels)

	ax.set_xlim(0,leny)
	ax.set_ylim(f0min,f0max)

	"""
	ax3.tick_params(axis='both', labelsize=fontsize)
	xticks = np.arange(0,leny+1,leny/5)
	ax3.set_xticks(xticks)
	xticklabels = [ "%.1f"%(secstart+float(l)*framerate) for l in xticks ]
	ax3.set_xticklabels(xticklabels,fontsize=fontsize)
	"""

# Plot F0
	if f0switch == 'on':
		ax.scatter(x,y,s=6, color='blue')

# Plot in-bounds and out-of-bounds global polyline segments
	if globalpolyline != []:
		y = globalpolyline
		x = range(len(y))
		okwin = []
		notokwin = []
		xwin = []
		for i,p,f in zip(x,y,f0list):
			if f > f0min and f < f0max:
				if len(notokwin) > 0:
					notokwin = np.append(notokwin,[p])
					xwin = np.append(xwin,[i])
					ax.plot(xwin,notokwin,':',linewidth=2,color='g')
					notokwin = []
					okwin = [p]
					xwin = [i]
				else:
					okwin = np.append(okwin,[p])
					xwin = np.append(xwin,[i])
			else:
				if len(okwin) > 0:
					okwin = np.append(okwin,[p])
					xwin = np.append(xwin,[i])
					ax.plot(xwin,okwin,linewidth=2,color='r')
					okwin = []
					notokwin = [p]
					xwin = [i]
				else:
					notokwin = np.append(notokwin,[p])
					xwin = np.append(xwin,[i])
		if len(okwin) > 0:
			ax.plot(xwin,okwin,linewidth=2,color='r')
		if len(notokwin) > 0:
			ax.plot(xwin,notokwin,':',linewidth=2,color='g')

#	Plot voiced sections of local polyline
	if localpolyline != []:
		y = localpolyline
		x = range(len(y))
		tempwin = []
		xwin = []
		for i,f in zip(x,y):
			if f > f0min and f < f0max:
				tempwin = np.append(tempwin, [f])
				xwin = np.append(xwin,[i])
			else:										# i.e. if f is out of bounds
				if len(tempwin) > 0:
					ax.plot(xwin,tempwin,linewidth=3,color='orange')
				tempwin = xwin = []	

	return

#==============================================================================
# Plot envelope spectrum (AM and FM)

def	envelopespectrumplot(ax, frequenciessegment, magnitudessegment, polyline, title, xlabel, ylabel, fontsize):

	ax.set_title(title,fontsize=fontsize)
	ax.tick_params(axis='both', labelsize=fontsize)
	ax.set_yticks([])
	ax.grid(which='both',axis='x', linewidth=1, linestyle='--')

	plt.plot(frequenciessegment,magnitudessegment,linewidth=1)

	if polyline != []:
		plt.plot(frequenciessegment,polyline,color="r",linewidth=2)
		
	return

#==============================================================================
# Plot envelope heatmaps (AM and FM)

def envelopeheatmapplot(ax, frequenciessegment, magnitudessegment, title, xlabel, ylabel, fontsize):

	ax.set_title(title, fontsize=fontsize)
	ax.tick_params(axis='both', labelsize=fontsize)
	ax.set_yticks([])

	minfreq = np.floor(frequenciessegment[0])
	maxfreq = np.ceil(frequenciessegment[-1])
	if maxfreq < 5:
		xtickcount = 9
		xticks = np.linspace(0,len(frequenciessegment),xtickcount)
		xlabels = np.linspace(minfreq,maxfreq,xtickcount)
	else:
		xtickcount = 5
		xticks = np.linspace(0,len(frequenciessegment),xtickcount)
		xlabels = np.linspace(minfreq,maxfreq,xtickcount)
		xlabels = map(int,xlabels)
	
	plt.xticks(xticks,xlabels)

	hm = np.array([magnitudessegment,magnitudessegment])
	heatmap = ax.pcolormesh([magnitudessegment], cmap=cm.YlOrRd)

	return

#==============================================================================
# Plot Jassem difference spectrum (AM and FM)

def jassemdiffspectplot(ax, frequenciessegment, absmagnitudediffs, aemshzmin, aemshzmax, title, xlabel, ylabel, fontsize, tickcount):

	ax.set_title(title,fontsize=fontsize)
	ax.set_yticks([])
	ax.tick_params(axis='both', labelsize=fontsize)
	ax.grid(which='both',axis='x', linewidth="1", linestyle='--')
	minlen = min([len(frequenciessegment),len(absmagnitudediffs)])
	lenxticks = len(plt.xticks())
	xticks = np.linspace(0,len(absmagnitudediffs),lenxticks)
	xlabels = np.linspace(0.0,20.0,lenxticks)
#	plt.xticks(xticks,xlabels)
#	ax.plot(frequenciessegment[:minlen],absmagnitudediffs[:minlen])

	ax.plot(frequenciessegment,absmagnitudediffs)

	return

#==============================================================================
