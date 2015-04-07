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
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import array

def readPickleChannel(file, channel_no):
    """Read data set as stored in pickle file"""
    # Make sure file path is correct format
    if file[-4:] == ".pkl":
        file = file[0:-4]
    ### READ Pickle File ###
    wave = utils.PickleFile(file, 4)
    wave.load()
    xRaw = wave.get_meta_data("timeform_%i" % channel_no)
    yRaw = wave.get_data(channel_no)
    # Correct for trigger offset in timestamps
    x = xRaw - xRaw[0]
    # Count how many pulses saved the file
    count = 0
    for i in yRaw:
        count = count + 1
    ### Make 2D array of pulse y values ###
    y = np.zeros( (count, len(xRaw)) )
    for i, ent in enumerate(yRaw):
        y[i, :] = ent  
    return x,y

def positive_check(y):
    if np.mean(y[1,:]) > 0:
        return True
    else:
        return False

def calcArea(x,y):
    """Calc area of pulses"""
    trapz = np.zeros( len(y[:,0]) )
    for i in range(len(y[:,0])):
        trapz[i] = np.trapz(y[i,:],x)
    return np.mean(trapz), np.std(trapz)


def calcRise(x,y):
    """Calc rise time of pulses"""
    rise = np.zeros( len(y[:,0]) )
    f = positive_check(y)
    if f == True:
        for i in range(len(y[:,0])):
            m = max(y[i,:])
            lo_thresh = m*0.1
            hi_thresh = m*0.9
            lo_index = np.where( y[i,:] > lo_thresh )[0][0]
            hi_index = np.where( y[i,:] > hi_thresh )[0][0]
            rise[i] = x[hi_index] - x[lo_index]
        return np.mean(rise), np.std(rise)
    else: 
        for i in range(len(y[:,0])):
            m = min(y[i,:])
            lo_thresh = m*0.1
            hi_thresh = m*0.9
            lo_index = np.where( y[i,:] < lo_thresh )[0][0]
            hi_index = np.where( y[i,:] < hi_thresh )[0][0]
            rise[i] = x[hi_index] - x[lo_index]
        return np.mean(rise), np.std(rise)

def calcFall(x,y):
    """Calc fall time of pulses"""
    fall = np.zeros( len(y[:,0]) )
    f = positive_check(y)
    if f == True:
        for i in range(len(y[:,0])):
            m = max(y[i,:])
            m_index = np.where(y[i,:] == m)[0][0]
            lo_thresh = m*0.1
            hi_thresh = m*0.9
            lo_index = np.where( y[i,m_index:] < lo_thresh )[0][0]
            hi_index = np.where( y[i,m_index:] < hi_thresh )[0][0]
            fall[i] = x[lo_index] - x[hi_index]
        return np.mean(fall), np.std(fall)
    else:
        for i in range(len(y[:,0])):
            m = min(y[i,:])
            m_index = np.where(y[i,:] == m)[0][0]
            lo_thresh = m*0.1
            hi_thresh = m*0.9
            lo_index = np.where( y[i,m_index:] > lo_thresh )[0][0]
            hi_index = np.where( y[i,m_index:] > hi_thresh )[0][0]
            fall[i] = x[lo_index] - x[hi_index]
        return np.mean(fall), np.std(fall)
        
def calcWidth(x,y):
    """Calc width of pulses"""
    width = np.zeros( len(y[:,0]) )
    f = positive_check(y)
    if f == True:
        for i in range(len(y[:,0])):
            m = max(y[i,:])
            thresh = m*0.5
            index_1 = np.where( y[i,:] > thresh )[0][0]
            index_2 = np.where( y[i,:] > thresh )[0][-1]
            width[i] = x[index_2] - x[index_1]
        return np.mean(width), np.std(width)
    else:
        for i in range(len(y[:,0])):
            m = min(y[i,:])
            thresh = m*0.5
            index_1 = np.where( y[i,:] < thresh )[0][0]
            index_2 = np.where( y[i,:] < thresh )[0][-1]
            width[i] = x[index_2] - x[index_1]
        return np.mean(width), np.std(width)

def calcPeak(x,y):
    """Calc min amplitude of pulses"""
    peak = np.zeros( len(y[:,0]) )
    f = positive_check(y)
    if f == True:
        for i in range(len(y[:,0])):
            peak[i] = max(y[i,:])
        return np.mean(peak), np.std(peak)
    else:
        for i in range(len(y[:,0])):
            peak[i] = min(y[i,:])
        return np.mean(peak), np.std(peak)

def calcSinglePeak(pos_check, y_arr):
    """Calculate peak values for single trace inputs can be positive or negative."""
    if pos_check == True:
        m = max(y_arr)
    else:
        m = min(y_arr)
    return m

def calcTimeStamp(pos_check, x, y_arr, thresh):
    """Return timestamp of the first threshold crossing"""
    if pos_check == True:
        index = np.where(y_arr > thresh)[0][0]
    else:
        index = np.where(y_arr < thresh)[0][0]
    return x[index]

def calcJitter(x1, y1, x2, y2):
    """Calc jitter between trig and signal using CFD"""
    p1 = positive_check(y1)
    p2 = positive_check(y2)
    times = np.zeros(len(y1[:,0]))
    for i in range(len(y1[:,0])):
        m1 = calcSinglePeak(p1, y1[i,:])
        m2 = calcSinglePeak(p2, y2[i,:])
        time_1 = calcTimeStamp(p1, x1, y1[i,:], 0.1*m1)
        time_2 = calcTimeStamp(p2, x2, y2[i,:], 0.1*m2)
        times[i] = time_1 - time_2
    return np.mean(times), np.std(times), np.std(times)/np.sqrt(2*len(y1[:,0]))

def printParams(x,y, name):
    """Calculate standard parameters and print to screen"""
    area, areaStd = calcArea(x,y)
    rise, riseStd = calcRise(x,y)
    fall, fallStd = calcFall(x,y)
    width, widthStd = calcWidth(x,y)
    mini, miniStd = calcPeak(x,y)

    print "\n%s:" % name
    print "--------"
    print "Area \t\t= %1.2e +/- %1.2e Vs" % (area, areaStd)
    print "Fall time \t= %1.2f +/- %1.2f ns" % (fall*1e9, fallStd*1e9)
    print "Rise time \t= %1.2f +/- %1.2f ns" % (rise*1e9, riseStd*1e9)
    print "Width \t\t= %1.2f +/- %1.2f ns" % (width*1e9, widthStd*1e9)
    print "Peak \t\t= %1.2f +/- %1.2f V" % (mini, miniStd)

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

if __name__ == "__main__":

    ## File path
    dataPath = "./results/"
    runs = [1,2,3,4,5]
    for i in runs:
        run = "run_%i" % i
        fileName = "%s%s.pkl" % (dataPath, run)
    
        # Read data
        fileRead = time.time()
        x1,y1 = readPickleChannel(fileName, 1)
        x2,y2 = readPickleChannel(fileName, 2)
        print "Reading %d pulses from %s took %1.2f s" % ( len(y1[:,0]), fileName, (time.time()-fileRead) )
        
        # Correct for baseline offset in data files
        for i, ent in enumerate(y1):
            y1[i, :] = ent - np.mean(ent[0:20])
            y2[i, :] = y2[i, :] - np.mean(ent[0:20])

        # Calculate and print parameters
        printParams(x1, y1, "Trigger")
        printParams(x2, y2, "Signal")
        separation, Jitter, JittErr = calcJitter(x1,y1,x2,y2)
        print "\nJitter = %1.2f +/- %1.2f ps\n" % (Jitter*1e12, JittErr*1e12)
        
        print "Reading + calcs on %d pulses from file took %1.2f s" % ( len(y1[:,0]), (time.time()-fileRead) )

        plot_eg_pulses(x1, y1, x2, y2, 5, fname="results/plots/EgPulses_%s.png" % run)
        plot_trig_sig_ph_corr(y1, y2, fname="results/plots/PH_corr_%s.png" % run)
        plot_trig_sig_area_corr(x1, y1, x2, y2, fname="results/plots/Area_corr_%s.png" % run)
