###############################################
# Functions to read in pickled scope traces
# and perform standard measurements.
# 
# Will calculate: Integrated area, rise time,
# fall time, pulse width, peak voltage and
# the jitter on two signals. 
# 
# Author: Ed Leming
# Date: 17/03/2015
################################################
import pickle
import utils
import time
import sys
import calc_utils as calc
import matplotlib.pyplot as plt
import numpy as np 

def plot_trig_sig_ph_corr(y1, y2, fname=None,show=False):
    """Plot pulse height correlations between trigger and signal"""
    trig = np.zeros( len(y1[:,0]) )
    sig = np.zeros( len(y1[:,0]) )
    for i in range(len(y1[:,0])):
        trig[i] = max(y1[i,:])
        sig[i] = min(y2[i,:])

    plt.figure()
    plt.plot(trig, sig, '.')
    plt.title( "Trig_out and pmt signal pulse height correlations" )
    plt.xlabel("Peak Trigger voltage (V)")
    plt.ylabel("Peak Signal voltage (V)")
    txt_str = "Entries: %s" % (len(y1[:,0])-1)
    ax=plt.gca()
    plt.text(0.75, 0.92, txt_str, transform=ax.transAxes, bbox={'facecolor':'white', 'pad':10}, fontsize=14)
    if fname is not None:
        plt.savefig(fname)
    if show == True:
        plt.show()
    plt.clf()

def plot_trig_sig_area_corr(x1, y1, x2, y2, fname=None, show=False):
    """Plot correlations of """
    trig = np.zeros( len(y1[:,0]) )
    sig = np.zeros( len(y2[:,0]) )
    for i in range(len(y1[:,0])):
        trig[i] = np.trapz(y1[i,:],x1)
        sig[i] = np.trapz(y2[i,:],x2)

    plt.figure()
    plt.plot(trig, sig, '.')
    plt.title( "Trig_out and pmt signal pulse integral correlations" )
    plt.xlabel("Trigger integral (Vs)")
    plt.ylabel("Signal integral (Vs)")
    txt_str = "Entries: %s" % (len(y1[:,0])-1)
    ax=plt.gca()
    plt.text(0.75, 0.92, txt_str, transform=ax.transAxes, bbox={'facecolor':'white', 'pad':10}, fontsize=14)
    if fname is not None:
        plt.savefig(fname)
    if show == True:
        plt.show()
    plt.clf()

def plot_eg_pulses(x1,y1,x2,y2,n,fname=None,show=False):
    """Plot example pulse pairs""" 
    plt.figure()
    for i in range(n):
        plt.plot(x1*1e9,y1[i,:])
        plt.plot(x2*1e9,y2[i,:])
    plt.title( "Example pulses from: %s"%(fileName) )
    plt.xlabel("Time (ns)")
    plt.ylabel("Amplitude (V)")
    if fname is not None:
        plt.savefig(fname)
    if show == True:
        plt.show()
    plt.clf()

if __name__ == "__main__":

    ## File path
    dataPath = "./results/"
    runs = [1,2,3,4,5]
    for i in runs:
        run = "run_%i" % i
        fileName = "%s%s.pkl" % (dataPath, run)
    
        # Read data
        fileRead = time.time()
        x1,y1 = calc.readPickleChannel(fileName, 1)
        x2,y2 = calc.readPickleChannel(fileName, 2)
        print "Reading %d pulses from %s took %1.2f s" % ( len(y1[:,0]), fileName, (time.time()-fileRead) )
        
        # Calculate and print parameters
        calc.printParams(x1, y1, "Trigger")
        calc.printParams(x2, y2, "Signal")
        separation, Jitter, JittErr = calc.calcJitter(x1,y1,x2,y2)
        print "\nJitter = %1.2f +/- %1.2f ps\n" % (Jitter*1e12, JittErr*1e12)
        
        print "Reading + calcs on %d pulses from file took %1.2f s" % ( len(y1[:,0]), (time.time()-fileRead) )

        plot_eg_pulses(x1, y1, x2, y2, 5, fname="results/plots/EgPulses_%s.png" % run)
        plot_trig_sig_ph_corr(y1, y2, fname="results/plots/PH_corr_%s.png" % run)
        plot_trig_sig_area_corr(x1, y1, x2, y2, fname="results/plots/Area_corr_%s.png" % run)
