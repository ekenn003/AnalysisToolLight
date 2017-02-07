# AnalysisTool/scripts/collectTriggerScaleFactors.py
#
# Run me with:
#     python collectMuonScaleFactors.py
#
import os, sys, math
import argparse
import ROOT

def main(argv=None):
    '''
    This creates a 2D histograms of efficiencies for the Run2015C/D muon ID and isolation and
    collects them in one file for consistency. 
    See https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffsRun2
    '''
    if argv is None: argv = sys.argv[1:]
    args = parse_command_line(argv)
    cmsswversion = '80X'

    lumi_Bv2 = 5.855
    lumi_C   = 2.646
    lumi_D   = 4.353
    lumi_E   = 4.050
    lumi_F   = 3.157
    lumi_G   = 7.261
    lumi_Hv2 = 8.285
    lumi_Hv3 = 0.217

    pog_id_filename0  = 'EfficienciesAndSF_ID_BCDEF.root'
    pog_id_filename1  = 'EfficienciesAndSF_ID_GH.root'
    pog_iso_filename0 = 'EfficienciesAndSF_ISO_BCDEF.root'
    pog_iso_filename1 = 'EfficienciesAndSF_ISO_GH.root'


    sf_dir = '{0}/src/AnalysisToolLight/AnalysisTool/data/scalefactors'.format(os.environ['CMSSW_BASE'])
    output_filename = '{0}/muonidiso_{1}.root'.format(sf_dir, cmsswversion)

    pog_id_file0  = ROOT.TFile.Open('{0}/{1}'.format(sf_dir, pog_id_filename0))
    pog_id_file1  = ROOT.TFile.Open('{0}/{1}'.format(sf_dir, pog_id_filename1))
    pog_iso_file0 = ROOT.TFile.Open('{0}/{1}'.format(sf_dir, pog_iso_filename0))
    pog_iso_file1 = ROOT.TFile.Open('{0}/{1}'.format(sf_dir, pog_iso_filename1))
    outfile = ROOT.TFile(output_filename,'recreate')

    muonideffs = {
        'looseID' : {
            'hdir' : 'LooseID'
        },
        'mediumID' : {
            'hdir' : 'MediumID'
        },
        'mediumID2016' : {
            'hdir' : 'MediumID2016'
        },
        'tightID' : {
            'hdir' : 'TightID'
        },
    }
    muonisoeffs = {
        'looseIso_looseID' : {
            'hdir' : 'LooseISO_LooseID'
        },
        'looseIso_mediumID' : {
            'hdir' : 'LooseISO_MediumID'
        },
        'looseIso_tightID' : {
            'hdir' : 'LooseISO_TightID'
        },
        'tightIso_mediumID' : {
            'hdir' : 'TightISO_MediumID'
        },
        'tightIso_tightID' : {
            'hdir' : 'TightISO_TightID'
        },
    }

    # get hist for each path
    for cut in muonideffs:
        muonideffs[cut]['hdir'] = 'MC_NUM_{0}_DEN_genTracks_PAR_pt_eta/pt_abseta_ratio'.format(muonideffs[cut]['hdir'])
        print 'trying to get hist at ' + muonideffs[cut]['hdir']
        muonideffs[cut]['RATIO_BCDEF'] = ROOT.TH2F(pog_id_file0.Get(muonideffs[cut]['hdir']))
        muonideffs[cut]['RATIO_BCDEF'].SetName(cut)
        muonideffs[cut]['RATIO_GH'] = ROOT.TH2F(pog_id_file1.Get(muonideffs[cut]['hdir']))

    for cut in muonisoeffs:
        muonisoeffs[cut]['hdir'] = '{0}_pt_eta/pt_abseta_ratio'.format(muonisoeffs[cut]['hdir'])
        print 'trying to get hist at ' + muonisoeffs[cut]['hdir']
        muonisoeffs[cut]['RATIO_BCDEF'] = ROOT.TH2F(pog_iso_file0.Get(muonisoeffs[cut]['hdir']))
        muonisoeffs[cut]['RATIO_BCDEF'].SetName(cut)
        muonisoeffs[cut]['RATIO_GH'] = ROOT.TH2F(pog_iso_file1.Get(muonisoeffs[cut]['hdir']))

    # combine efficiencies for isolations on top of ids
    muonisoeffs['looseIso_looseID']['RATIO_BCDEF'].Multiply(muonideffs['looseID']['RATIO_BCDEF'])
    muonisoeffs['looseIso_looseID']['RATIO_GH'].Multiply(muonideffs['looseID']['RATIO_GH'])

    muonisoeffs['looseIso_mediumID']['RATIO_BCDEF'].Multiply(muonideffs['mediumID']['RATIO_BCDEF'])
    muonisoeffs['looseIso_mediumID']['RATIO_GH'].Multiply(muonideffs['mediumID']['RATIO_GH'])

    muonisoeffs['looseIso_tightID']['RATIO_BCDEF'].Multiply(muonideffs['tightID']['RATIO_BCDEF'])
    muonisoeffs['looseIso_tightID']['RATIO_GH'].Multiply(muonideffs['tightID']['RATIO_GH'])

    muonisoeffs['tightIso_mediumID']['RATIO_BCDEF'].Multiply(muonideffs['mediumID']['RATIO_BCDEF'])
    muonisoeffs['tightIso_mediumID']['RATIO_GH'].Multiply(muonideffs['mediumID']['RATIO_GH'])

    muonisoeffs['tightIso_tightID']['RATIO_BCDEF'].Multiply(muonideffs['tightID']['RATIO_BCDEF'])
    muonisoeffs['tightIso_tightID']['RATIO_GH'].Multiply(muonideffs['tightID']['RATIO_GH'])

    lumi_BCDEF = lumi_Bv2 + lumi_C + lumi_D + lumi_E + lumi_F
    lumi_GH    = lumi_G + lumi_Hv2 + lumi_Hv3
    nbinsx = muonisoeffs['tightIso_mediumID']['RATIO_GH'].GetNbinsX()
    nbinsy = muonisoeffs['tightIso_mediumID']['RATIO_GH'].GetNbinsY()

    # create template hists
    for cut in muonideffs:
        muonideffs[cut]['RATIO'] = muonideffs[cut]['RATIO_GH'].Clone(cut)
        muonideffs[cut]['RATIO'].SetName(cut)
    for cut in muonisoeffs:
        muonisoeffs[cut]['RATIO'] = muonisoeffs[cut]['RATIO_GH'].Clone(cut)
        muonisoeffs[cut]['RATIO'].SetName(cut)

    # weight efficiencies by lumi period
    for cut in muonideffs:
        for bx in range(0, nbinsx):
            for by in range(0, nbinsy):
                # get average value of eff for this bin
                eff0 = muonideffs[cut]['RATIO_BCDEF'].GetBinContent(bx, by)
                eff1 = muonideffs[cut]['RATIO_GH'].GetBinContent(bx, by)
                eff = (lumi_BCDEF/(lumi_BCDEF+lumi_GH))*eff0 + (lumi_GH/(lumi_BCDEF+lumi_GH))*eff1
                # get errors
                err0 = muonideffs[cut]['RATIO_BCDEF'].GetBinError(bx, by)
                err1 = muonideffs[cut]['RATIO_GH'].GetBinError(bx, by)
                err = math.sqrt( pow(err0*(lumi_BCDEF/(lumi_BCDEF+lumi_GH)), 2) + pow(err1*(lumi_GH/(lumi_BCDEF+lumi_GH)), 2) )

                muonideffs[cut]['RATIO'].SetBinContent(bx, by, eff)
                muonideffs[cut]['RATIO'].SetBinError(bx, by, err)


    for cut in muonisoeffs:
        for bx in range(0, nbinsx):
            for by in range(0, nbinsy):
                # get average value of eff for this bin
                eff0 = muonisoeffs[cut]['RATIO_BCDEF'].GetBinContent(bx, by)
                eff1 = muonisoeffs[cut]['RATIO_GH'].GetBinContent(bx, by)
                eff = (lumi_BCDEF/(lumi_BCDEF+lumi_GH))*eff0 + (lumi_GH/(lumi_BCDEF+lumi_GH))*eff1
                # get errors
                err0 = muonisoeffs[cut]['RATIO_BCDEF'].GetBinError(bx, by)
                err1 = muonisoeffs[cut]['RATIO_GH'].GetBinError(bx, by)
                err = math.sqrt( pow(err0*(lumi_BCDEF/(lumi_BCDEF+lumi_GH)), 2) + pow(err1*(lumi_GH/(lumi_BCDEF+lumi_GH)), 2) )

                muonisoeffs[cut]['RATIO'].SetBinContent(bx, by, eff)
                muonisoeffs[cut]['RATIO'].SetBinError(bx, by, err)


    # write hists
    outfile.cd()
    for cut in muonideffs:
        muonideffs[cut]['RATIO'].Write()
    for cut in muonisoeffs:
        muonisoeffs[cut]['RATIO'].Write()

    print '\nCreated file {0}'.format(output_filename)

    outfile.Close()
    pog_id_file0.Close()
    pog_iso_file0.Close()
    pog_id_file1.Close()
    pog_iso_file1.Close()




## ___________________________________________________________
def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='')
#    parser.add_argument('-version',type=str,help='Version of CMSSW. Options: "76X" or "80X"')
    args = parser.parse_args(argv)
    return args

if __name__ == "__main__":
    status = main()
    sys.exit(status)

