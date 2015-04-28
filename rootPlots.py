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
import ROOT
import readPklWaveFile as pklfuncs
import array

def fit_gauss(hist):
    """Fit generic gaussian to histogram"""
    f = ROOT.TF1("f1","gaus")
    f.SetLineColor(1)
    p = hist.Fit(f, "S")

    # Write to canvas
    #stats = c1.GetPrimitive("stats")
    #stats.SetTextColor(1)
    #c1.Modified(); c1.Update()

    return f.GetParameters(), f.GetParErrors()

def print_hist(hist, savename):
    """Function to print histogram to png"""
    c1.Clear()
    hist.Draw("")
    c1.Update()
    stats = c1.GetPrimitive("stats")
    stats.SetTextSize(0.04)
    c1.Modified(); c1.Update()
    c1.Print("%s" % savename, "pdf")

def plot_area(x, y, name):
    """Calc area of pulses"""
    area, areaErr = pklfuncs.calcArea(x,y)
    bins = np.arange((area-8*areaErr)*1e9, (area+8*areaErr)*1e9, (areaErr/5)*1e9)
    hist = ROOT.TH1D("%s" % name,"%s" % name, len(bins), bins[0], bins[-1])
    hist.SetTitle("Pulse integrals of %s pulses" % name)
    hist.GetXaxis().SetTitle("Integrated area (V.ns)")
    for i in range(len(y[:,0])-1):
        hist.Fill(np.trapz(y[i,:],x)*1e9)
    return hist, area, areaErr

def plot_rise(x, y, name):
    """Calc and plot rise time of pulses"""
    rise, riseErr = pklfuncs.calcRise(x,y)
    bins = np.arange((rise-8*riseErr)*1e9, (rise+8*riseErr)*1e9, (riseErr/5.)*1e9)
    hist = ROOT.TH1D("%s" % name,"%s" % name, len(bins), bins[0], bins[-1])
    hist.SetTitle("Rise times of %s pulses" % name)
    hist.GetXaxis().SetTitle("Rise time (ns)")
    f = pklfuncs.positive_check(y)
    if f == True:
        for i in range(len(y[:,0])-1):
            m = max(y[i,:])
            lo_thresh = m*0.1
            hi_thresh = m*0.9
            lo_index = np.where( y[i,:] > lo_thresh )[0][0]
            hi_index = np.where( y[i,:] > hi_thresh )[0][0]
            hist.Fill((x[hi_index] - x[lo_index])*1e9)
    else:
        for i in range(len(y[:,0])-1):
            m = min(y[i,:])
            lo_thresh = m*0.1
            hi_thresh = m*0.9
            lo_index = np.where( y[i,:] < lo_thresh )[0][0]
            hi_index = np.where( y[i,:] < hi_thresh )[0][0]
            hist.Fill((x[hi_index] - x[lo_index])*1e9)
    return hist, rise, riseErr

def plot_fall(x, y, name):
    """Calc and plot fall time of pulses"""
    fall, fallErr = pklfuncs.calcFall(x,y)
    bins = np.arange((fall-8*fallErr)*1e9, (fall+8*fallErr)*1e9, (fallErr/5.)*1e9)
    hist = ROOT.TH1D("%s" % name,"%s" % name, len(bins), bins[0], bins[-1])
    hist.SetTitle("Fall times of %s pulses" % name)
    hist.GetXaxis().SetTitle("Fall time (ns)")
    f = pklfuncs.positive_check(y)
    if f == True:
        for i in range(len(y[:,0])-1):
            m = max(y[i,:])
            m_index = np.where(y[i,:] == m)[0][0]
            lo_thresh = m*0.1
            hi_thresh = m*0.9
            lo_index = np.where( y[i,m_index:] < lo_thresh )[0][0]
            hi_index = np.where( y[i,m_index:] < hi_thresh )[0][0]
            hist.Fill((x[lo_index] - x[hi_index])*1e9)
    else:
        for i in range(len(y[:,0])-1):
            m = min(y[i,:])
            m_index = np.where(y[i,:] == m)[0][0]
            lo_thresh = m*0.1
            hi_thresh = m*0.9
            lo_index = np.where( y[i,m_index:] > lo_thresh )[0][0]
            hi_index = np.where( y[i,m_index:] > hi_thresh )[0][0]
            hist.Fill((x[lo_index] - x[hi_index])*1e9)
    return hist, fall, fallErr

def plot_peak(x, y, name):
    """Plot pulse heights for array of pulses"""
    peak, peakErr = pklfuncs.calcPeak(x,y)
    bins = np.arange((peak-8*peakErr), (peak+8*peakErr), (peakErr/5.))
    hist = ROOT.TH1D("%s" % name,"%s" % name, len(bins), bins[0], bins[-1])
    hist.SetTitle("Pulse hieghts of %s pulses" % name)
    hist.GetXaxis().SetTitle("Pulse height (V)")
    f = pklfuncs.positive_check(y)
    if f == True:
        for i in range(len(y[:,0])-1):
            hist.Fill(max(y[i,:]))
    else:
        for i in range(len(y[:,0])-1):
            hist.Fill(min(y[i,:]))
    return hist, peak, peakErr

def plot_jitter(x1, y1, x2, y2, name):
    """Calc and plot jitter of pulse pairs"""
    sep, jitter, jittErr = pklfuncs.calcJitter(x1, y1, x2, y2)
    bins = np.arange((sep-8*jitter)*1e9, (sep+8*jitter)*1e9, (jitter/5.)*1e9)
    hist = ROOT.TH1D("%s" % name,"%s" % name, len(bins), bins[0], bins[-1])
    hist.SetTitle("Jitter between signal and trigger out")
    hist.GetXaxis().SetTitle("Pulse separation (ns)")
    p1 = pklfuncs.positive_check(y1)
    p2 = pklfuncs.positive_check(y2)
    for i in range(len(y1[:,0])-1):
        m1 = pklfuncs.calcSinglePeak(p1, y1[i,:])
        m2 = pklfuncs.calcSinglePeak(p2, y2[i,:])
        time_1 = pklfuncs.calcTimeStamp(p1, x1, y1[i,:], 0.1*m1)
        time_2 = pklfuncs.calcTimeStamp(p2, x2, y2[i,:], 0.1*m2)
        hist.Fill((time_1 - time_2)*1e9)
    return hist, jitter, jittErr


if __name__ == "__main__": 

    # ROOT stuff
    ROOT.gROOT.Reset()
    ROOT.gStyle.SetOptStat(1)
    c1 = ROOT.TCanvas("c1")

    # File stuff
    dataPath = "./results/"
    runs = [1,2,3,4,5]
    for i in runs:
        run = "run_%i" % i
        fileName = "%s%s.pkl" % (dataPath, run)
        plotPath = "./results/plots/run_%i/" % i
        f = ROOT.TFile("%sresults.root" % plotPath, "RECREATE")

        # Read in data file
        x1, y1 = pklfuncs.readPickleChannel(fileName, 1)
        x2, y2 = pklfuncs.readPickleChannel(fileName, 2)

        # Make plots and save 
        area_trig, aT_mean, aT_Err = plot_area(x1, y1, "trigger")
        area_sig, aS_mean, aS_Err = plot_area(x2, y2, "signal")
        area_trig.Write(); area_sig.Write()
        print_hist(area_trig, "%sArea_trig.pdf" % plotPath)
        print_hist(area_sig, "%sArea_sig.pdf" % plotPath)

        rise_trig, rT_mean, rT_Err = plot_rise(x1, y1, "trigger")
        rise_sig, rS_mean, rS_Err = plot_rise(x2, y2, "signal")
        rise_trig.Write(), rise_sig.Write()
        print_hist(rise_trig, "%sRise_trig.pdf" % plotPath)
        print_hist(rise_sig, "%sRise_sig.pdf" % plotPath)

        fall_trig, fT_mean, fT_Err = plot_fall(x1, y1, "trigger")
        fall_sig, fS_mean, fS_Err = plot_fall(x2, y2, "signal")
        fall_trig.Write(), fall_sig.Write()
        print_hist(fall_trig, "%sFall_trig.pdf" % plotPath)
        print_hist(fall_sig, "%sFall_sig.pdf" % plotPath)

        peak_trig, pT_mean, pT_Err = plot_peak(x1, y1, "trigger")
        peak_sig, pS_mean, pS_Err = plot_peak(x2, y2, "signal")
        peak_trig.Write(), peak_sig.Write()
        print_hist(peak_trig, "%sPH_trig.pdf" % plotPath)
        print_hist(peak_sig, "%sPH_sig.pdf" % plotPath)

        jitter_hist, jitt_mean, jitt_Err = plot_jitter(x1, y1, x2, y2, "Pulse sep")
        jitter_hist.Write()
        print_hist(jitter_hist, "%sJitter.pdf" % plotPath)

