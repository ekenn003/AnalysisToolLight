#!/usr/bin/env python
import sys, os, getopt
import ROOT

# don't forget to set cmssw version and check output file
def main(argv):
    argv = sys.argv[1:]

    cmsswversion = '76x'

    histName = 'pileup'
    fileName = '$CMSSW_BASE/src/AnalysisToolLight/AnalysisTool/data/pileup/testpileup.root'
    
    if cmsswversion == '76x':
        # 76X samples with pileup matching data
        from SimGeneral.MixingModule.mix_2015_25ns_FallMC_matchData_PoissonOOTPU_cfi import mix
        pileupDist = [float(x) for x in mix.input.nbPileupEvents.probValue]
    else:
        # 80X sample with startup pileup
        from SimGeneral.MixingModule.mix_2016_25ns_SpringMC_PUScenarioV1_PoissonOOTPU_cfi import mix
        pileupDist = [float(x) for x in mix.input.nbPileupEvents.probValue]

    rootfile = ROOT.TFile(fileName,'recreate')
    
    # create mc pileup dist
    histmc = ROOT.TH1D(histName+'_MC',histName+'_MC',len(pileupDist),0,len(pileupDist))
    for b,val in enumerate(pileupDist):
        histmc.SetBinContent(b+1,val)
    histmc.Scale(1./histmc.Integral())
    
    histmc.Write()
    
    # read data
    for datatype in ['','_up','_down','_69000','_71000','_80000']:
        dataFileName = '$CMSSW_BASE/src/AnalysisToolLight/AnalysisTool/data/pileup/PileUpData{0}.root'.format(datatype)
        datafile = ROOT.TFile(dataFileName)
        histdata = datafile.Get(histName)
        #histdata.SetTitle('{0}_Data{1}'.format(histName, datatype))
        histdata.SetName('{0}_Data{1}'.format(histName, datatype))
        histdata.Scale(1./histdata.Integral())
        rootfile.cd()
        histdata.Write()
    
        # now use the histograms to get scalefactors
        numbins = min([histdata.GetNbinsX(),histmc.GetNbinsX()])
        histscale = ROOT.TH1D(histName+'_scale'+datatype,histName+'_scale'+datatype,numbins,0,numbins)
        for b in range(numbins):
            d = histdata.GetBinContent(b+1)
            m = histmc.GetBinContent(b+1)
            sf = float(d)/m if m else 0.
            histscale.SetBinContent(b+1,sf)
        histscale.Write()
    
    rootfile.Write()
    rootfile.Close()


if __name__ == "__main__":
   main(sys.argv[1:])