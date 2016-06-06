#!/usr/bin/env python
# AnalysisTool/scripts/collectTriggerScaleFactors.py
import os, sys, math
import ROOT

def main():
    '''
    This creates a 2D histograms of efficiencies for the Run2015C/D muon ID and isolation and
    collects them in one file for consistency. 
    See https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffsRun2
    '''

    cmsswversion = '76X'
    pogIdFileName  = 'MuonID_Z_RunCD_Reco76X_Feb15.root'
    pogIsoFileName = 'MuonIso_Z_RunCD_Reco76X_Feb15.root'

    sfDir = '{0}/src/AnalysisToolLight/AnalysisTool/data/scalefactors'.format(os.environ['CMSSW_BASE'])
    outputFileName = '{0}/muonidiso_{1}.root'.format(sfDir, cmsswversion)

    pogIdFile  = ROOT.TFile('{0}/{1}'.format(sfDir, pogIdFileName))
    pogIsoFile = ROOT.TFile('{0}/{1}'.format(sfDir, pogIsoFileName))
    outfile = ROOT.TFile(outputFileName,'recreate')

    muonideffs = {
        'looseID' : {
            'hdir' : 'LooseID'
        },
        'softID' : {
            'hdir' : 'SoftID'
        },
        'mediumID' : {
            'hdir' : 'MediumID'
        },
        'tightID' : {
            'hdir' : 'TightIDandIPCut'
        },
    }
    muonisoeffs = {
        'looseIso_looseID' : {
            'hdir' : 'LooseRelIso_DEN_LooseID'
        },
        'looseIso_mediumID' : {
            'hdir' : 'LooseRelIso_DEN_MediumID'
        },
        'looseIso_tightID' : {
            'hdir' : 'LooseRelIso_DEN_TightID'
        },
        'tightIso_mediumID' : {
            'hdir' : 'TightRelIso_DEN_MediumID'
        },
        'tightIso_tightID' : {
            'hdir' : 'TightRelIso_DEN_TightID'
        },
    }

    # get hist for each path
    for cut in muonideffs:
        muonideffs[cut]['hdir'] = 'MC_NUM_{0}_DEN_genTracks_PAR_pt_spliteta_bin1/pt_abseta_ratio'.format(muonideffs[cut]['hdir'])
        print 'trying to get hist at ' + muonideffs[cut]['hdir']
        muonideffs[cut]['RATIO'] = ROOT.TH2F(pogIdFile.Get(muonideffs[cut]['hdir']))
        muonideffs[cut]['RATIO'].SetName(cut)

    for cut in muonisoeffs:
        muonisoeffs[cut]['hdir'] = 'MC_NUM_{0}_PAR_pt_spliteta_bin1/pt_abseta_ratio'.format(muonisoeffs[cut]['hdir'])
        print 'trying to get hist at ' + muonisoeffs[cut]['hdir']
        muonisoeffs[cut]['RATIO'] = ROOT.TH2F(pogIsoFile.Get(muonisoeffs[cut]['hdir']))
        muonisoeffs[cut]['RATIO'].SetName(cut)

    # combine efficiencies for isolations on top of ids
    muonisoeffs['looseIso_looseID']['RATIO'].Multiply(muonideffs['looseID']['RATIO'])
    muonisoeffs['looseIso_mediumID']['RATIO'].Multiply(muonideffs['mediumID']['RATIO'])
    muonisoeffs['looseIso_tightID']['RATIO'].Multiply(muonideffs['tightID']['RATIO'])
    muonisoeffs['tightIso_mediumID']['RATIO'].Multiply(muonideffs['mediumID']['RATIO'])
    muonisoeffs['tightIso_tightID']['RATIO'].Multiply(muonideffs['tightID']['RATIO'])

    # write hists
    outfile.cd()
    for cut in muonideffs:
        muonideffs[cut]['RATIO'].Sumw2()
        muonideffs[cut]['RATIO'].Write()
    for cut in muonisoeffs:
        muonisoeffs[cut]['RATIO'].Sumw2()
        muonisoeffs[cut]['RATIO'].Write()

    outfile.Write()
    outfile.Close()
    pogIdFile.Close()
    pogIsoFile.Close()


if __name__ == "__main__":
    status = main()
    sys.exit(status)

