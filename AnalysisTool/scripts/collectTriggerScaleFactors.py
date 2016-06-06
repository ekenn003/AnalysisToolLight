#!/usr/bin/env python
# AnalysisTool/scripts/collectTriggerScaleFactors.py
import os, sys, math
import ROOT

def main():
    '''
    This creates a 2D histograms of efficiencies for the RunC+D IsoMu20_OR_IsoTkMu20 path,
    weighted by the integrated lumi for each period. To find the scale factor for this path,
    for i muons:
        sf(IsoMu20_OR_IsoTkMu20) = [1-eff(data, mu(i))*eff(data, mu(i+1))*...] / [1-eff(MC, mu(i))*eff(MC, mu(i+1))*...]
    where eff(data, mu(i)) is the bin content of the DAhist at the appropriate bins based on
    the pt and eta of mu(i):
        eff(data, mu) = DAhist.GetBinContent( DAhist.FindBin(mu.pt, mu.AbsEta) )

    See https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffsRun2
    '''

    cmsswversion = '76X'
    pogFileName = 'SingleMuonTrigger_Z_RunCD_Reco76X_Feb15.root'

    sfDir = '{0}/src/AnalysisToolLight/AnalysisTool/data/scalefactors'.format(os.environ['CMSSW_BASE'])
    outputFileName = '{0}/singlemuontrigger_{1}.root'.format(sfDir, cmsswversion)


    pogFile = ROOT.TFile('{0}/{1}'.format(sfDir, pogFileName))
    outfile = ROOT.TFile(outputFileName,'recreate')

    # find lumi with eg:
    # brilcalc lumi --normtag <my normtag> -i <my json> --hltpath "HLT_IsoMu20_v*"
    # see comments at end of this file
    singlemuoneffs = {
        'runC_IsoMu20_OR_IsoTkMu20' : {
            'lumi' : 16.689, # inv pb
        },
        'runD_IsoMu20_OR_IsoTkMu20_HLTv4p2' : {
            'lumi' : 399.990, # inv pb
        },
        'runD_IsoMu20_OR_IsoTkMu20_HLTv4p3' : {
            'lumi' : 1871.952, # inv pb
        },
    }

    totlumi = 0.

    for path in singlemuoneffs:
        hdir = '{0}_PtEtaBins'.format(path)
        singlemuoneffs[path]['MC']   = '{0}/efficienciesMC/pt_abseta_MC'.format(hdir)
        singlemuoneffs[path]['DATA'] = '{0}/efficienciesDATA/pt_abseta_DATA'.format(hdir)
        totlumi += singlemuoneffs[path]['lumi']

    # get hist for each path
    mchist0 = ROOT.TH2F(pogFile.Get(singlemuoneffs['runC_IsoMu20_OR_IsoTkMu20']['MC']))
    dahist0 = ROOT.TH2F(pogFile.Get(singlemuoneffs['runC_IsoMu20_OR_IsoTkMu20']['DATA']))
    weight0 = singlemuoneffs['runC_IsoMu20_OR_IsoTkMu20']['lumi'] / totlumi

    mchist1 = ROOT.TH2F(pogFile.Get(singlemuoneffs['runD_IsoMu20_OR_IsoTkMu20_HLTv4p2']['MC']))
    dahist1 = ROOT.TH2F(pogFile.Get(singlemuoneffs['runD_IsoMu20_OR_IsoTkMu20_HLTv4p2']['DATA']))
    weight1 = singlemuoneffs['runD_IsoMu20_OR_IsoTkMu20_HLTv4p2']['lumi'] / totlumi

    mchist2 = ROOT.TH2F(pogFile.Get(singlemuoneffs['runD_IsoMu20_OR_IsoTkMu20_HLTv4p3']['MC']))
    dahist2 = ROOT.TH2F(pogFile.Get(singlemuoneffs['runD_IsoMu20_OR_IsoTkMu20_HLTv4p3']['DATA']))
    weight2 = singlemuoneffs['runD_IsoMu20_OR_IsoTkMu20_HLTv4p3']['lumi'] / totlumi

    # create result hists
    MChist = mchist0.Clone('effMC')
    DAhist = dahist0.Clone('effDA')
    nbinsx = mchist0.GetNbinsX()
    nbinsy = mchist0.GetNbinsY()

    for bx in range(0, nbinsx):
        for by in range(0, nbinsy):
            # get average value of eff for data for this bin
            daeff0 = dahist0.GetBinContent(bx, by)
            daeff1 = dahist1.GetBinContent(bx, by)
            daeff2 = dahist2.GetBinContent(bx, by)
            dabincontent = daeff0*weight0 + daeff1*weight1 + daeff2*weight2
            # get errors
            daerr0 = dahist0.GetBinError(bx, by)
            daerr1 = dahist1.GetBinError(bx, by)
            daerr2 = dahist2.GetBinError(bx, by)
            dabinerror = math.sqrt( pow(daerr0*weight0, 2) + pow(daeff1*weight1, 2) + pow(daeff2*weight2, 2) )
            # get average value of eff for mc for this bin
            mceff0 = mchist0.GetBinContent(bx, by)
            mceff1 = mchist1.GetBinContent(bx, by)
            mceff2 = mchist2.GetBinContent(bx, by)
            mcbincontent = mceff0*weight0 + mceff1*weight1 + mceff2*weight2
            # get errors
            mcerr0 = mchist0.GetBinError(bx, by)
            mcerr1 = mchist1.GetBinError(bx, by)
            mcerr2 = mchist2.GetBinError(bx, by)
            mcbinerror = math.sqrt( pow(mcerr0*weight0, 2) + pow(mceff1*weight1, 2) + pow(mceff2*weight2, 2) )
            # fill result hists
            DAhist.SetBinContent(bx, by, dabincontent)
            DAhist.SetBinError(bx, by, dabinerror)
            MChist.SetBinContent(bx, by, mcbincontent)
            MChist.SetBinError(bx, by, mcbinerror)

    # save result
    outfile.cd()
    MChist.Write()
    DAhist.Write()
    outfile.Write()
    outfile.Close()
    pogFile.Close()


if __name__ == "__main__":
    status = main()
    sys.exit(status)




# How this file was created
#
# run c:
# 
#     brilcalc lumi --normtag /afs/cern.ch/user/l/lumipro/public/normtag_file/moriond16_normtag.json -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON_v2.txt --hltpath "HLT_Iso*Mu20_v*" -u /pb --begin 253659 --end 256464
# +------------------+-------+------+------+-------------------+------------------+
# | hltpath          | nfill | nrun | ncms | totdelivered(/pb) | totrecorded(/pb) |
# +------------------+-------+------+------+-------------------+------------------+
# | HLT_IsoMu20_v2   | 5     | 7    | 1045 | 17.134            | 16.689           |
# | HLT_IsoTkMu20_v2 | 5     | 7    | 1045 | 17.134            | 16.689           |
# +------------------+-------+------+------+-------------------+------------------+
# 
# run d
# check https://cmsweb-testbed.cern.ch/confdb/ to find the cutoff betweenHLTv4p2/3
# run range taken from https://twiki.cern.ch/twiki/bin/view/CMS/PdmV2015Analysis
#     brilcalc lumi --normtag /afs/cern.ch/user/l/lumipro/public/normtag_file/moriond16_normtag.json -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON_v2.txt --hltpath "HLT_Iso*Mu20_v*" -u /pb --begin 256630 --end 260627
# +------------------+-------+------+-------+-------------------+------------------+
# | hltpath          | nfill | nrun | ncms  | totdelivered(/pb) | totrecorded(/pb) |
# +------------------+-------+------+-------+-------------------+------------------+
# | HLT_IsoMu20_v2   | 16    | 30   | 7366  | 416.631           | 399.990          |
# | HLT_IsoMu20_v3   | 25    | 75   | 24366 | 1934.016          | 1871.952         |
# | HLT_IsoTkMu20_v3 | 16    | 30   | 7366  | 416.631           | 399.990          |
# | HLT_IsoTkMu20_v4 | 25    | 75   | 24366 | 1934.016          | 1871.952         |
# +------------------+-------+------+-------+-------------------+------------------+
# 
# runD_IsoMu20_OR_IsoTkMu20_HLTv4p2:
# 399.990 /pb
# 
# runD_IsoMu20_OR_IsoTkMu20_HLTv4p3:
# 1871.952 /pb
# 
