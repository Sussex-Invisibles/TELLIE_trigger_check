##########################################################
# Script to generate root plots of standard measurements
# to recorded trigger and signals pulses using root_utils.py
# functions available in the AcquireTek package from 
# https://github.com/Sussex-Invisibles/AcquireTek
#
# Will calculate: Integrated area, rise time,
# fall time, pulse width, peak voltage and
# the jitter on two signals. 
#
# Author: Ed Leming
# Date: 17/03/2015
#########################################################
import utils
import calc_utils as calc
import root_utils as rootu
import ROOT

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
        x1, y1 = calc.readPickleChannel(fileName, 1)
        x2, y2 = calc.readPickleChannel(fileName, 2)

        # Make plots and save 
        area_trig, aT_mean, aT_Err = rootu.plot_area(x1, y1, "trigger")
        area_sig, aS_mean, aS_Err = rootu.plot_area(x2, y2, "signal")
        area_trig.Write(); area_sig.Write()
        rootu.print_hist(area_trig, "%sArea_trig.pdf" % plotPath, c1)
        rootu.print_hist(area_sig, "%sArea_sig.pdf" % plotPath, c1)

        rise_trig, rT_mean, rT_Err = rootu.plot_rise(x1, y1, "trigger")
        rise_sig, rS_mean, rS_Err = rootu.plot_rise(x2, y2, "signal")
        rise_trig.Write(), rise_sig.Write()
        rootu.print_hist(rise_trig, "%sRise_trig.pdf" % plotPath, c1)
        rootu.print_hist(rise_sig, "%sRise_sig.pdf" % plotPath, c1)

        fall_trig, fT_mean, fT_Err = rootu.plot_fall(x1, y1, "trigger")
        fall_sig, fS_mean, fS_Err = rootu.plot_fall(x2, y2, "signal")
        fall_trig.Write(), fall_sig.Write()
        rootu.print_hist(fall_trig, "%sFall_trig.pdf" % plotPath, c1)
        rootu.print_hist(fall_sig, "%sFall_sig.pdf" % plotPath, c1)

        peak_trig, pT_mean, pT_Err = rootu.plot_peak(x1, y1, "trigger")
        peak_sig, pS_mean, pS_Err = rootu.plot_peak(x2, y2, "signal")
        peak_trig.Write(), peak_sig.Write()
        rootu.print_hist(peak_trig, "%sPH_trig.pdf" % plotPath, c1)
        rootu.print_hist(peak_sig, "%sPH_sig.pdf" % plotPath, c1)

        jitter_hist, jitt_mean, jitt_Err = rootu.plot_jitter(x1, y1, x2, y2, "Pulse sep")
        jitter_hist.Write()
        rootu.print_hist(jitter_hist, "%sJitter.pdf" % plotPath, c1)

