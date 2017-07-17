#!/usr/bin/env python

import os, sys
from array import array
from ROOT import TH2F, gROOT, TFile
from ROOT import TCanvas

gROOT.SetBatch(True)

sys_dir = ('{0}/src/AnalysisToolLight/AnalysisTool/data/'
           'systematics/').format(os.environ['CMSSW_BASE'])

tfns = {'MC':{}, 'BCD':{}, 'EF':{}, 'G':{}, 'H':{}}
tfns['MC']['txt']  = sys_dir + 'Summer16_23Sep2016V4_MC_Uncertainty_AK4PFchs.txt'
tfns['BCD']['txt'] = sys_dir + 'Summer16_23Sep2016BCDV4_DATA_Uncertainty_AK4PFchs.txt'
tfns['EF']['txt'] = sys_dir + 'Summer16_23Sep2016EFV4_DATA_Uncertainty_AK4PFchs.txt'
tfns['G']['txt'] = sys_dir + 'Summer16_23Sep2016GV4_DATA_Uncertainty_AK4PFchs.txt'
tfns['H']['txt'] = sys_dir + 'Summer16_23Sep2016HV4_DATA_Uncertainty_AK4PFchs.txt'

outfile_name = 'jetshifts_80X.root'

hists = []

for key, s in tfns.iteritems():
    eta_bins = []
    pt_bins  = []

    with open(s['txt']) as f:
        next(f) # skip first line

        for line in f:
            l = line.split()
            eta_bins.append(float(l[0]))
    
        for n in range(int(len(l)/3)-1):
            pt_bins.append(float(l[3*(n+1)]))
    
        eta_bins.append(float(l[1]))
        pt_bins.append(10000.)
    
    nbinsx = len(pt_bins)-1
    xbins  = array('f', pt_bins)
    nbinsy = len(eta_bins)-1
    ybins  = array('f', eta_bins)
    dhn = 'hJetShift_' + key + '_Down'
    uhn = 'hJetShift_' + key + '_Up'


    hJetShiftDown = TH2F(dhn, dhn, nbinsx, xbins, nbinsy, ybins)
    hJetShiftUp   = TH2F(uhn, uhn, nbinsx, xbins, nbinsy, ybins)
    
    
    with open(s['txt']) as f:
        next(f) # skip first line
        for y_, line in enumerate(f):
            l = line.split()
            y = y_ + 1
            for x_, n in enumerate(range(int(len(l)/3)-1)):
                x = x_ + 1
                down = float(l[3*(n+1)+1])
                up   = float(l[3*(n+1)+2])
                hJetShiftDown.SetBinContent(x, y, down)
                hJetShiftUp.SetBinContent(x, y, up)

    hists.append(hJetShiftDown.Clone(dhn))
    hists.append(hJetShiftUp.Clone(uhn))
    
    canv_down = TCanvas(dhn,dhn,1100,900)
    canv_down.cd()
    hJetShiftDown.Draw()
    canv_down.SetLogx()
    canv_down.Print('canv_'+dhn+'.png')
    canv_up = TCanvas(uhn,uhn,1100,900)
    canv_up.cd()
    hJetShiftUp.Draw()
    canv_up.SetLogx()
    canv_up.Print('canv_'+uhn+'.png')

    hJetShiftDown.Delete()
    hJetShiftUp.Delete()



outfile = TFile('{0}/{1}'.format(sys_dir, outfile_name),'recreate')
outfile.cd()
for h in hists:
    h.Write()
outfile.Close()

print '\nCreated file {0}/{1}'.format(sys_dir, outfile_name)
