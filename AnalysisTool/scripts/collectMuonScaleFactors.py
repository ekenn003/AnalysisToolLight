# AnalysisTool/scripts/collectTriggerScaleFactors.py
#
# Run me with:
#     python collectMuonScaleFactors.py -version "80X"
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
    cmsswversion = args.version


    if cmsswversion == '76X':
        pog_id_fileName  = 'MuonID_Z_RunCD_Reco76X_Feb15.root'
        pog_iso_fileName = 'MuonIso_Z_RunCD_Reco76X_Feb15.root'
    else: # if 80X
        pog_id_fileName  = 'MuonID_Z_RunBCD_prompt80X_7p65.root'
        pog_iso_fileName = 'MuonIso_Z_RunBCD_prompt80X_7p65.root'


    sf_dir = '{0}/src/AnalysisToolLight/AnalysisTool/data/scalefactors'.format(os.environ['CMSSW_BASE'])
    output_filename = '{0}/muonidiso_{1}.root'.format(sf_dir, cmsswversion)

    pog_id_file  = ROOT.TFile.Open('{0}/{1}'.format(sf_dir, pog_id_fileName))
    pog_iso_file = ROOT.TFile.Open('{0}/{1}'.format(sf_dir, pog_iso_fileName))
    outfile = ROOT.TFile(output_filename,'recreate')

    muonideffs = {
        'looseID' : {
            'hdir' : 'LooseID'
        },
        #'softID' : {
        #    'hdir' : 'SoftID'
        #},
        'mediumID' : {
            'hdir' : 'MediumID'
        },
        'tightID' : {
            'hdir' : 'TightIDandIPCut'
        },
    }
    muonisoeffs = {
    #    'looseIso_looseID' : {
    #        'hdir' : 'LooseRelIso_DEN_LooseID'
    #    },
    #    'looseIso_mediumID' : {
    #        'hdir' : 'LooseRelIso_DEN_MediumID'
    #    },
        'looseIso_tightID' : {
            'hdir' : 'LooseRelIso_DEN_TightID'
        },
    #    'tightIso_mediumID' : {
    #        'hdir' : 'TightRelIso_DEN_MediumID'
    #    },
        'tightIso_tightID' : {
            'hdir' : 'TightRelIso_DEN_TightID'
        },
    }
    # 80X only has tight/highpt ids available
    if cmsswversion=='76X':
        muonisoeffs['looseIso_looseID'] = {
            'hdir' : 'LooseRelIso_DEN_LooseID'
        }
        muonisoeffs['looseIso_mediumID'] = {
            'hdir' : 'LooseRelIso_DEN_MediumID'
        }
        muonisoeffs['tightIso_mediumID'] = {
            'hdir' : 'TightRelIso_DEN_MediumID'
        }

    # get hist for each path
    for cut in muonideffs:
        muonideffs[cut]['hdir'] = 'MC_NUM_{0}_DEN_genTracks_PAR_pt_spliteta_bin1/pt_abseta_ratio'.format(muonideffs[cut]['hdir'])
        print 'trying to get hist at ' + muonideffs[cut]['hdir']
        muonideffs[cut]['RATIO'] = ROOT.TH2F(pog_id_file.Get(muonideffs[cut]['hdir']))
        muonideffs[cut]['RATIO'].SetName(cut)

    for cut in muonisoeffs:
        muonisoeffs[cut]['hdir'] = 'MC_NUM_{0}_PAR_pt_spliteta_bin1/pt_abseta_ratio'.format(muonisoeffs[cut]['hdir'])
        print 'trying to get hist at ' + muonisoeffs[cut]['hdir']
        muonisoeffs[cut]['RATIO'] = ROOT.TH2F(pog_iso_file.Get(muonisoeffs[cut]['hdir']))
        muonisoeffs[cut]['RATIO'].SetName(cut)

    # combine efficiencies for isolations on top of ids
    #muonisoeffs['looseIso_looseID']['RATIO'].Multiply(muonideffs['looseID']['RATIO'])
    #muonisoeffs['looseIso_mediumID']['RATIO'].Multiply(muonideffs['mediumID']['RATIO'])
    muonisoeffs['looseIso_tightID']['RATIO'].Multiply(muonideffs['tightID']['RATIO'])
    #muonisoeffs['tightIso_mediumID']['RATIO'].Multiply(muonideffs['mediumID']['RATIO'])
    muonisoeffs['tightIso_tightID']['RATIO'].Multiply(muonideffs['tightID']['RATIO'])
    if cmsswversion=='76X':
        muonisoeffs['looseIso_looseID']['RATIO'].Multiply(muonideffs['looseID']['RATIO'])
        muonisoeffs['looseIso_mediumID']['RATIO'].Multiply(muonideffs['mediumID']['RATIO'])
        muonisoeffs['tightIso_mediumID']['RATIO'].Multiply(muonideffs['mediumID']['RATIO'])

    # write hists
    outfile.cd()
    for cut in muonideffs:
        muonideffs[cut]['RATIO'].Sumw2()
        muonideffs[cut]['RATIO'].Write()
    for cut in muonisoeffs:
        muonisoeffs[cut]['RATIO'].Sumw2()
        muonisoeffs[cut]['RATIO'].Write()

    print '\nCreated file {0}'.format(output_filename)

    outfile.Write()
    outfile.Close()
    pog_id_file.Close()
    pog_iso_file.Close()




## ___________________________________________________________
def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-version',type=str,help='Version of CMSSW. Options: "76X" or "80X"')
    args = parser.parse_args(argv)
    return args

if __name__ == "__main__":
    status = main()
    sys.exit(status)

