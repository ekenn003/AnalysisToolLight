
# bjet algorithm choices:
#     '[CSVv2,JP,CMVAv2][L,M,T]' (ie. Loose, Medium, Tight)
# muon isolation choices:
#     'loose', 'tight', 'tkloose', 'tktight'
#     https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2#Muon_Isolation
# muon id choices: 
#     'loose', 'medium', 'tight'
# electron ID choices:
#     'cbloose', 'cbmedium', 'cbtight', 'mva80', 'mva90'



vh_cuts = {
    # HLT
    'HLT' : (
        'IsoMu24',
        'IsoTkMu24', 
    ),
    # path for scale factors
    'HLTstring' : 'IsoMu20_OR_IsoTkMu20',

    # event selection
    'cVtxNdf' : 4,
    'cVtxZ'   : 24., # cm

    # preselection
    'cBJetAlg' : 'CMVAv2T',
    'cBJetPt'  : 30., # GeV
    'cBJetEta' : 2.4,

    # MET cut
    'cMET' : 40.,

    # regular jets
    'cJetPt'  : 30., # GeV
    'cJetEta' : 4.7,
    # delta R to clean jets
    'cDeltaR' : 0.4,

    # regular mu cuts
    'cMuPt'  : 10., # GeV
    'cMuEta' : 2.4,
    'cMuIso' : 'tight',
    #'cMuID'  : 'medium',
    'cMuID'  : 'medium2016',
    'cMuDxy' : 0.02, # cm
    'cMuDz'  : 0.14, # cm

    # trigger-matched mu cuts
    'cMuPtMax'  : 24., # GeV
    'cMuEtaMax' : 2.4,

    # electron cuts
    'cEPt'  : 10., # GeV
    'cEEta' : 2.5,
    'cEID'  : 'cbtight',

    # h candidate cuts
    'cDiMuInvMass' : 60., # GeV
    'cDiMuPt' : 30., # GeV

}

