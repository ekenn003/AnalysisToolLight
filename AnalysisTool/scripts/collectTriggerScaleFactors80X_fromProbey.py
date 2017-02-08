#!/usr/bin/env python
# AnalysisTool/scripts/collectTriggerScaleFactors80X_fromProbey.py
import os, sys, math
import ROOT

def main():
    '''
    for i muons:
        sf(IsoMu20_OR_IsoTkMu20) = [1-eff(data, mu(i))*eff(data, mu(i+1))*...]
    where eff(data, mu(i)) is the bin content of the DAhist at the appropriate bins based on
    the pt and eta of mu(i):
        eff(data, mu) = DAhist.GetBinContent( DAhist.FindBin(mu.pt, mu.AbsEta) )
    '''

    cmsswversion = '80X'
    probey_filename = 'efficiencies_muon_trigger.root'

    sf_dir = '{0}/src/AnalysisToolLight/AnalysisTool/data/scalefactors'.format(os.environ['CMSSW_BASE'])
    output_filename = '{0}/singlemuontrigger_{1}.root'.format(sf_dir, cmsswversion)



    probey_file = ROOT.TFile.Open('{0}/{1}'.format(sf_dir, probey_filename))
    outfile = ROOT.TFile(output_filename,'recreate')

    # create result hists
    dahist0 = probey_file.Get('passingIsoMu24ORIsoTkMu24/probe_pt_probe_abseta_PLOT')
    DAhist = dahist0.Clone('effDA')

    # save result
    outfile.cd()
    #MChist.Write()
    DAhist.Write('effDA')
    outfile.Close()
    print '\nCreated file {0}'.format(output_filename)
    probey_file.Close()


if __name__ == "__main__":
    status = main()
    sys.exit(status)
