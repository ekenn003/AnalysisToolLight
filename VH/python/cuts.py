
# bjet algorithm choices:
#     '[CSVv2,JP,CMVAv2][loose,medium,tight]'
# muon isolation choices:
#     'loose', 'tight', 'tkloose', 'tktight'
#     https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2#Muon_Isolation
# muon id choices: 
#     'loose', 'medium', 'tight'
# electron ID choices:
#     'cbloose', 'cbmedium', 'cbtight', 'mva80', 'mva90'



vh_cuts = {
    # event selection
    'cVtxNdf' : 4
    'cVtxZ'   : 24. # cm

    # preselection
    'cBJetAlg' : 'CSVv2medium',
    'cBJetPt'  : 30., # GeV
    'cBJetEta' : 2.4,
    # delta R to clean jets
    'cDeltaR' : 0.4

    # MET cut
    'cMET' : 40.,

    # regular mu cuts
    'cMuDxy' : 0.02 # cm
    'cMuDz'  : 0.14 # cm
    'cMuPt'  : 10., # GeV
    'cMuEta' : 2.4,
    'cMuIsoMax' : 'tight',
    'cMuID'  : 'medium',

    # trigger-matched mu cuts
    'cMuPtMax'  : 24., # GeV
    'cMuEtaMax' : 2.4,
    'cMuIsoMax' : 'tight',
    'cMuIDMax'  : 'medium',

    # electron cuts
    'cEPt' : 10., # GeV
    'cEID' : 'cbmedium',

    # h candidate cuts
    'cDiMuInvMass' : 60., # GeV
    'cDiMuPt' : 30., # GeV



}
