#!/usr/bin/env python
# AnalysisTool/scripts/collectTriggerScaleFactors80X.py
import os, sys, math
import ROOT

def main():
    '''
    This creates a 2D histograms of efficiencies for the 2016 RunF+GH IsoMu24_OR_IsoTkMu24 path,
    weighted by the integrated lumi for each period. To find the scale factor for this path,
    for i muons:
        sf(IsoMu24_OR_IsoTkMu24) = [1-eff(data, mu(i))*eff(data, mu(i+1))*...]
    where eff(data, mu(i)) is the bin content of the DAhist at the appropriate bins based on
    the pt and eta of mu(i):
        eff(data, mu) = DAhist.GetBinContent( DAhist.FindBin(mu.pt, mu.AbsEta) )

    See https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffsRun2
        https://twiki.cern.ch/twiki/bin/viewauth/CMS/MuonWorkInProgressAndPagResults
    '''

    cmsswversion = '80X'
    pog_filename3 = 'EfficienciesAndSF_Period3.root'
    pog_filename4 = 'EfficienciesAndSF_Period4.root'

    sf_dir = '{0}/src/AnalysisToolLight/AnalysisTool/data/scalefactors'.format(os.environ['CMSSW_BASE'])
    output_filename = '{0}/singlemuontrigger_{1}.root'.format(sf_dir, cmsswversion)

    lumi_Bv2 = 5.855
    lumi_C   = 2.646
    lumi_D   = 4.353
    lumi_E   = 4.050
    lumi_F   = 3.157
    lumi_G   = 7.261
    lumi_Hv2 = 8.285
    lumi_Hv3 = 0.217

    # Period1

    # Period2

    # Period3
    lumi_3 = lumi_F
    # Period4
    lumi_4 = lumi_G + lumi_Hv2 + lumi_Hv3
    # totals
    lumi_tot = lumi_3 + lumi_4


    pog_file3 = ROOT.TFile('{0}/{1}'.format(sf_dir, pog_filename3))
    pog_file4 = ROOT.TFile('{0}/{1}'.format(sf_dir, pog_filename4))
    outfile = ROOT.TFile(output_filename,'recreate')

    # find lumi with eg:
    # brilcalc lumi --normtag <my normtag> -i <my json> --hltpath "HLT_IsoMu20_v*"
    # see comments at end of this file
    singlemuoneffs = {
        'IsoMu24_OR_IsoTkMu24' : {
            'hdir' : 'IsoMu24_OR_IsoTkMu24'
        },
    }

    totlumi = 0.

    for path in singlemuoneffs:
        hdir = '{0}_PtEtaBins'.format(path)
        singlemuoneffs[path]['DATA'] = '{0}/efficienciesDATA/pt_abseta_DATA'.format(hdir)
        singlemuoneffs[path]['MC']   = '{0}/efficienciesMC/pt_abseta_MC'.format(hdir)

    # get hist for each path
    #for path in singlemuoneffs:
    path24 = 'IsoMu24_OR_IsoTkMu24'
    dahist3 = ROOT.TH2F(pog_file3.Get(singlemuoneffs[path24]['DATA']))
    mchist3 = ROOT.TH2F(pog_file3.Get(singlemuoneffs[path24]['MC']))
    weight3 = lumi_3 / lumi_tot

    dahist4 = ROOT.TH2F(pog_file4.Get(singlemuoneffs[path24]['DATA']))
    mchist4 = ROOT.TH2F(pog_file4.Get(singlemuoneffs[path24]['MC']))
    weight4 = lumi_4 / lumi_tot


    # create result hists
    MChist = mchist3.Clone('effMC')
    DAhist = dahist3.Clone('effDA')
    nbinsx = dahist3.GetNbinsX()
    nbinsy = dahist3.GetNbinsY()

    for bx in range(0, nbinsx):
        for by in range(0, nbinsy):
            # get average value of eff for data for this bin
            daeff3 = dahist3.GetBinContent(bx, by)
            daeff4 = dahist4.GetBinContent(bx, by)
            dabincontent = daeff3*weight3 + daeff4*weight4
            # get errors
            daerr3 = dahist3.GetBinError(bx, by)
            daerr4 = dahist4.GetBinError(bx, by)
            dabinerror = math.sqrt( pow(daerr3*weight3, 2) + pow(daerr4*weight4, 2) )
            # get average value of eff for mc for this bin
            mceff3 = mchist3.GetBinContent(bx, by)
            mceff4 = mchist4.GetBinContent(bx, by)
            mcbincontent = mceff3*weight3 + mceff4*weight4
            # get errors
            mcerr3 = mchist3.GetBinError(bx, by)
            mcerr4 = mchist4.GetBinError(bx, by)
            mcbinerror = math.sqrt( pow(mcerr3*weight3, 2) + pow(mcerr4*weight4, 2) )
            # fill result hists
            DAhist.SetBinContent(bx, by, dabincontent)
            DAhist.SetBinError(bx, by, dabinerror)
            MChist.SetBinContent(bx, by, mcbincontent)
            MChist.SetBinError(bx, by, mcbinerror)

    # save result
    outfile.cd()
    MChist.Write()
    DAhist.Write()
    outfile.Close()
    print '\nCreated file {0}'.format(output_filename)
    pog_file3.Close()
    pog_file4.Close()


if __name__ == "__main__":
    status = main()
    sys.exit(status)


# the info below is now obsolete
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
