
# bjet algorithm choices:
#     '[CSVv2,JP,CMVAv2][loose,medium,tight]'
# muon isolation choices:
#     'loose', 'tight', 'tkloose', 'tktight'
# muon id choices: 
#     'loose', 'medium', 'tight'
# electron ID choices:
#     'cbloose', 'cbmedium', 'cbtight', 'mva80', 'mva90'



vh_cuts = {
    # preselection
    cBJetAlg = 'CSVv2medium',
    cBJetPt  = 30., # GeV
    cBJetEta = 2.4,

    # MET cut
    cMET = 40.,

    # trigger-matched mu cuts
    cMuPtMax  = 24., # GeV
    cMuEtaMax = 2.4,
    cMuIsoMax = 'tight',
    cMuIDMax  = 'medium',

    # regular mu cuts
    cMuPt  = 10., # GeV
    cMuEta = 2.4,
    cMuIsoMax = 'tight',
    cMuID  = 'medium',

    # electron cuts
    cEPt = 10., # GeV
    cEID = 'cbmedium',

}
