#!/usr/bin/env python
#
# Run me with:
#     python generatePileupHist.py -version "80X"
#

import os, sys
import argparse
import ROOT

## ___________________________________________________________
def getMixingProb(version, pudir):
    pileup_dist = []
    if version == '76X': 
        mixfile = 'mix_2015_25ns_FallMC_matchData_PoissonOOTPU_cfi.py'
    elif version == '80X':
        mixfile = 'mix_2016_25ns_SpringMC_PUScenarioV1_PoissonOOTPU_cfi.py'
    else: raise ValueError('Choices for version are 76X and 80X')

    mixfile = '{0}/{1}'.format(pudir, mixfile)

    x, y = -1, -1
    with open(mixfile, 'r') as f:
        for line in f:
            # find numbins
            if 'probFunctionVariable' in line:
                for i, c in enumerate(line):
                    if c==',': x=i
                    if c==')':
                        y=i
                        break
                numbins = int(line[x+1:y]) + 1
            # fill bins
            if 'probValue' in line:
                for l, line in enumerate(f):
                    if l == numbins: 
                        #print 'reached bin {0}, breaking'.format(numbins)
                        break
                    thisbin = ''.join(c for c in line.rstrip() if (c.isdigit() or c in ['e', '-', '.']))
                    pileup_dist += [float(thisbin)]

    return pileup_dist


## ___________________________________________________________
def main(argv=None):
    if argv is None: argv = sys.argv[1:]
    args = parse_command_line(argv)
    cmsswversion = args.version

    print 'version = ' + cmsswversion

    histName = 'pileup'
    pileup_dir = '{0}/src/AnalysisToolLight/AnalysisTool/data/pileup'.format(os.environ['CMSSW_BASE'])
    output_filename = '{0}/pileup_{1}.root'.format(pileup_dir, cmsswversion)

    pileup_dist = getMixingProb(cmsswversion, pileup_dir)
    rootfile = ROOT.TFile(output_filename,'recreate')
    
    # create mc pileup dist
    histmc = ROOT.TH1D(histName+'_MC', histName+'_MC', len(pileup_dist), 0, len(pileup_dist))
    for b, val in enumerate(pileup_dist):
        histmc.SetBinContent(b+1,val)
    histmc.Scale(1./histmc.Integral())
    histmc.Write()
    
    # read data
    #for datatype in ['','_Up','_Down','_69000','_71000']:
    for datatype in ['','_Up','_Down']:
        data_filename = '{0}/PileUpData{1}{2}.root'.format(pileup_dir, cmsswversion, datatype)
        datafile = ROOT.TFile(data_filename)
        histdata = datafile.Get(histName)
        histdata.SetTitle('{0}_Data{1}'.format(histName, datatype))
        histdata.SetName('{0}_Data{1}'.format(histName, datatype))
        histdata.Scale(1./histdata.Integral())
        rootfile.cd()
        print 'Rewriting {0}'.format(data_filename)
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
    print
    print 'Created the following file:\n{0}'.format(output_filename)
    rootfile.Close()




## ___________________________________________________________
def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Devin is GREAT!')
    parser.add_argument('-version',type=str,help='Version of CMSSW to use for pu mixing. (Usually whichever version was used to produce the RootMaker ntuples.) Options: "76X" or "80X"')
    args = parser.parse_args(argv)
    return args



## ___________________________________________________________
if __name__ == "__main__":
    status = main()
    sys.exit(status)

