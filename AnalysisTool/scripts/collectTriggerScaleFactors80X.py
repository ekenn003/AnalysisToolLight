#!/usr/bin/env python
# AnalysisTool/scripts/collectTriggerScaleFactors80X.py
import os, sys, math
import ROOT

def main():
    '''
    This creates a 2D histograms of efficiencies for the 2016 RunB+C+D IsoMu22_OR_IsoTkMu22 path,
    weighted by the integrated lumi for each period. To find the scale factor for this path,
    for i muons:
        sf(IsoMu20_OR_IsoTkMu20) = [1-eff(data, mu(i))*eff(data, mu(i+1))*...] / [1-eff(MC, mu(i))*eff(MC, mu(i+1))*...]
    where eff(data, mu(i)) is the bin content of the DAhist at the appropriate bins based on
    the pt and eta of mu(i):
        eff(data, mu) = DAhist.GetBinContent( DAhist.FindBin(mu.pt, mu.AbsEta) )

    See https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffsRun2
    '''

    cmsswversion = '80X'
    pog_filename = 'SingleMuonTrigger_Z_RunBCD_prompt80X_7p65.root'

    sf_dir = '{0}/src/AnalysisToolLight/AnalysisTool/data/scalefactors'.format(os.environ['CMSSW_BASE'])
    output_filename = '{0}/singlemuontrigger_{1}.root'.format(sf_dir, cmsswversion)


    pog_file = ROOT.TFile('{0}/{1}'.format(sf_dir, pog_filename))
    outfile = ROOT.TFile(output_filename,'recreate')

    # find lumi with eg:
    # brilcalc lumi --normtag <my normtag> -i <my json> --hltpath "HLT_IsoMu20_v*"
    # see comments at end of this file
    singlemuoneffs = {
        'IsoMu22_OR_IsoTkMu22_PtEtaBins_Run273158_to_274093' : {
            'lumi' : 621.512, # inv pb
        },
        'IsoMu22_OR_IsoTkMu22_PtEtaBins_Run274094_to_276097' : {
            'lumi' : 7033.818, # inv pb
        },
    }

    totlumi = 0.

    for path in singlemuoneffs:
        hdir = '{0}'.format(path)
        singlemuoneffs[path]['DATA'] = '{0}/efficienciesDATA/pt_abseta_DATA'.format(hdir)
        totlumi += singlemuoneffs[path]['lumi']

    # get hist for each path
    dahist0 = ROOT.TH2F(pog_file.Get(singlemuoneffs['IsoMu22_OR_IsoTkMu22_PtEtaBins_Run273158_to_274093']['DATA']))
    weight0 = singlemuoneffs['IsoMu22_OR_IsoTkMu22_PtEtaBins_Run273158_to_274093']['lumi'] / totlumi

    dahist1 = ROOT.TH2F(pog_file.Get(singlemuoneffs['IsoMu22_OR_IsoTkMu22_PtEtaBins_Run274094_to_276097']['DATA']))
    weight1 = singlemuoneffs['IsoMu22_OR_IsoTkMu22_PtEtaBins_Run274094_to_276097']['lumi'] / totlumi

    # create result hists
    #MChist = mchist0.Clone('effMC')
    DAhist = dahist0.Clone('effDA')
    nbinsx = dahist0.GetNbinsX()
    nbinsy = dahist0.GetNbinsY()

    for bx in range(0, nbinsx):
        for by in range(0, nbinsy):
            # get average value of eff for data for this bin
            daeff0 = dahist0.GetBinContent(bx, by)
            daeff1 = dahist1.GetBinContent(bx, by)
            dabincontent = daeff0*weight0 + daeff1*weight1
            # get errors
            daerr0 = dahist0.GetBinError(bx, by)
            daerr1 = dahist1.GetBinError(bx, by)
            dabinerror = math.sqrt( pow(daerr0*weight0, 2) + pow(daeff1*weight1, 2) )
            ## get average value of eff for mc for this bin
            #mceff0 = mchist0.GetBinContent(bx, by)
            #mceff1 = mchist1.GetBinContent(bx, by)
            #mceff2 = mchist2.GetBinContent(bx, by)
            #mcbincontent = mceff0*weight0 + mceff1*weight1 + mceff2*weight2
            ## get errors
            #mcerr0 = mchist0.GetBinError(bx, by)
            #mcerr1 = mchist1.GetBinError(bx, by)
            #mcerr2 = mchist2.GetBinError(bx, by)
            #mcbinerror = math.sqrt( pow(mcerr0*weight0, 2) + pow(mceff1*weight1, 2) + pow(mceff2*weight2, 2) )
            # fill result hists
            DAhist.SetBinContent(bx, by, dabincontent)
            DAhist.SetBinError(bx, by, dabinerror)
            #MChist.SetBinContent(bx, by, mcbincontent)
            #MChist.SetBinError(bx, by, mcbinerror)

    # save result
    outfile.cd()
    #MChist.Write()
    DAhist.Write()
    outfile.Close()
    print '\nCreated file {0}'.format(output_filename)
    pog_file.Close()


if __name__ == "__main__":
    status = main()
    sys.exit(status)


# How this file was created
#
# run 273158-274093:
# 
#     brilcalc lumi --normtag /afs/cern.ch/user/l/lumipro/public/normtag_file/normtag_DATACERT.json -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-276097_13TeV_PromptReco_Collisions16_JSON_NoL1T.txt --hltpath "HLT_Iso*Mu22_v*" -u /pb --begin 273158 --end 274093
# 
# +------------------+-------+------+-------+-------------------+------------------+
# | hltpath          | nfill | nrun | ncms  | totdelivered(/pb) | totrecorded(/pb) |
# +------------------+-------+------+-------+-------------------+------------------+
# | HLT_IsoMu22_v2   | 9     | 27   | 12422 | 647.570           | 621.512          |
# | HLT_IsoTkMu22_v2 | 9     | 27   | 12422 | 647.570           | 621.512          |
# +------------------+-------+------+-------+-------------------+------------------+
#  total lumi: 621.512
# 
# 
# run 274094-276097
#     brilcalc lumi --normtag /afs/cern.ch/user/l/lumipro/public/normtag_file/normtag_DATACERT.json -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-276097_13TeV_PromptReco_Collisions16_JSON_NoL1T.txt --hltpath "HLT_Iso*Mu22_v*" -u /pb --begin 274094 --end 276097
# +------------------+-------+------+-------+-------------------+------------------+
# | hltpath          | nfill | nrun | ncms  | totdelivered(/pb) | totrecorded(/pb) |
# +------------------+-------+------+-------+-------------------+------------------+
# | HLT_IsoMu22_v2   | 14    | 38   | 16760 | 2266.607          | 2174.505         |
# | HLT_IsoMu22_v3   | 18    | 69   | 34799 | 5061.596          | 4859.313         |
# | HLT_IsoTkMu22_v2 | 14    | 38   | 16760 | 2266.607          | 2174.505         |
# | HLT_IsoTkMu22_v3 | 11    | 37   | 23072 | 3219.888          | 3092.831         |
# | HLT_IsoTkMu22_v4 | 7     | 32   | 11727 | 1841.709          | 1766.482         |
# +------------------+-------+------+-------+-------------------+------------------+
# tot lumi: 2174.505 + 4859.313 = 7033.818
# 
