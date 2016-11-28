f = 1


# Datasets ##############################
datasets76X = {
    # data
    'SingleMuon_Run2015C' : { 'njobs' : 1 },
    'SingleMuon_Run2015D' : { 'njobs' : 20 },
    # signal
    'GluGlu_HToMuMu' : { 'njobs' : 1 },
    'VBF_HToMuMu'    : { 'njobs' : 1 },
    # background
    'DYJetsToLL'  : { 'njobs' : 12 },
    'TTJets'      : { 'njobs' : 4 },
    'TTZToLLNuNu' : { 'njobs' : 2 },
    'WWTo2L2Nu'   : { 'njobs' : 4 },
    'WZTo2L2Q'    : { 'njobs' : 16 },
    'WZTo3LNu'    : { 'njobs' : 2 },
    'ZZTo2L2Nu'   : { 'njobs' : 4 },
    'ZZTo2L2Q'    : { 'njobs' : 8 },
    'ZZTo4L'      : { 'njobs' : 8 },
}

datasets80X = {
    # data
    'SingleMuon_Run2016B' : { 'njobs' : 5*f },
    'SingleMuon_Run2016Bv3' : { 'njobs' : 3*f },
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
    #'TTZJets'     : { 'njobs' : 5*f },
    #'TTWJets'     : { 'njobs' : 3*f },
    #'tZq_ll_4f'   : { 'njobs' : 2*f },
    'WJetsToLNu' : { 'njobs' : 4*f },
    'WWTo2L2Nu'  : { 'njobs' : 1*f },
    'WZTo2L2Q'   : { 'njobs' : 2*f },
    'WZTo3LNu'   : { 'njobs' : 2*f },
    'ZZTo2L2Nu' : { 'njobs' : 2*f },
    'ZZTo2L2Q'  : { 'njobs' : 3*f },
    'ZZTo4L'    : { 'njobs' : 6*f },
    'WWW' : { 'njobs' : 1*f },
    'WWZ' : { 'njobs' : 1*f },
    'WZZ' : { 'njobs' : 1*f },
    'ZZZ' : { 'njobs' : 1*f },
}

