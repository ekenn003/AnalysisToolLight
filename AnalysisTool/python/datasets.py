f = 1


# Datasets ##############################

datasets80X = {
    # data
    'SingleMuon_Run2016Bv2' : { 'njobs' : 4*f },
    'SingleMuon_Run2016C' : { 'njobs' : 5*f },
    'SingleMuon_Run2016D' : { 'njobs' : 5*f },
    'SingleMuon_Run2016E' : { 'njobs' : 5*f },
    'SingleMuon_Run2016F' : { 'njobs' : 7*f },
    'SingleMuon_Run2016G' : { 'njobs' : 7*f },
    'SingleMuon_Run2016Hv2' : { 'njobs' : 7*f },
    'SingleMuon_Run2016Hv3' : { 'njobs' : 2*f },
    # signal
    'GluGlu_HToMuMu'  : { 'njobs' : 1*f },
    'VBF_HToMuMu'     : { 'njobs' : 1*f },
    'WMinusH_HToMuMu' : { 'njobs' : 1*f },
    'WPlusH_HToMuMu'  : { 'njobs' : 1*f },
    'ZH_HToMuMu'      : { 'njobs' : 1*f },
    # background
    'DYJetsToLL'  : { 'njobs' : 10*f },
    'TTJets'      : { 'njobs' : 10*f },
    'WJetsToLNu' : { 'njobs' : 4*f },
    'WWTo2L2Nu'  : { 'njobs' : 1*f },
    'WZTo2L2Q'   : { 'njobs' : 3*f },
    'WZTo3LNu'   : { 'njobs' : 2*f },
    'ZZTo2L2Nu' : { 'njobs' : 2*f },
    'ZZTo2L2Q'  : { 'njobs' : 3*f },
    'ZZTo4L'    : { 'njobs' : 6*f },
    'WWW' : { 'njobs' : 1*f },
    'WWZ' : { 'njobs' : 1*f },
    'WZZ' : { 'njobs' : 1*f },
    'ZZZ' : { 'njobs' : 1*f },

    'ST_tW_antitop_5f' : { 'njobs' : 1*f },
    'ST_tW_top_5f'     : { 'njobs' : 1*f },
    'TTZToLLNuNu'      : { 'njobs' : 1*f },
    'TTWJetsToLNu'     : { 'njobs' : 2*f },
    'TZQ_ll_4f'        : { 'njobs' : 6*f },
}

