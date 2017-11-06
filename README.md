# AnalysisToolLight

RECIPE

    # set up scram area
    cmsrel CMSSW_7_6_5
    cd CMSSW_7_6_5/src/
    cmsenv
    
    # check out code
    git clone https://github.com/ektylr/AnalysisToolLight.git 
    
    # compile
    scram b -j 8
