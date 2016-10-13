#v="76X"
v="80X"

##############################
# Common                     #
##############################
pileupdir=$CMSSW_BASE/src/AnalysisToolLight/AnalysisTool/data/pileup



##############################
# 76X                        #
##############################
if [ $v == "76X" ]; then

    # Data ###
    lumimask="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Reprocessing/Cert_13TeV_16Dec2015ReReco_Collisions15_25ns_JSON_v2.txt"
    pileupjson="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/PileUp/pileup_latest.txt"

    # MC #####
    # 76X samples with pileup matching data
    mixurl="https://raw.githubusercontent.com/cms-sw/cmssw/CMSSW_7_6_X/SimGeneral/MixingModule/python/"
    mixfile="mix_2015_25ns_FallMC_matchData_PoissonOOTPU_cfi.py"

##############################
# 80X                        #
##############################
elif [ $v == "80X" ]; then

    # Data ###
    lumimask="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-275783_13TeV_PromptReco_Collisions16_JSON.txt"
    pileupjson="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/pileup_latest.txt"

    # MC #####
    # 80X sample with startup pileup
    mixurl="https://raw.githubusercontent.com/cms-sw/cmssw/CMSSW_8_0_X/SimGeneral/MixingModule/python/"
    mixfile="mix_2016_25ns_SpringMC_PUScenarioV1_PoissonOOTPU_cfi.py"

##############################
# Those are the only choices #
##############################
else
    echo "wtf is $v supposed to be ?"
    exit 1
fi


# check if the file exists
if [ ! -f "${pileupdir}/${mixfile}" ]; then
    echo "Can't find ${pileupdir}/${mixfile}, will download from github..."
    echo "wget ${mixurl}${mixfile}"
    wget ${mixurl}${mixfile}
    echo "mv ${mixfile} ${pileupdir}/${mixfile}"
    mv ${mixfile} ${pileupdir}/${mixfile}
    echo
fi


# make files
#for xsec in [68000 68500 69000 69500 70000 70500 71000 71500 72000 72500 73000, 74000]; do
for xsec in [68000, 68500, 69000, 69500, 70000, 70500, 71000, 71500, 72000, 72500, 73000]; do
    echo $xsec
    #pileupCalc.py -i $lumimask --inputLumiJSON $pileupjson --calcMode true  --minBiasXsec $xsec --maxPileupBin 80 --numPileupBins 80 $pileupdir/PileUpData_$xsec.root
    pileupCalc.py -i $lumimask --inputLumiJSON $pileupjson --calcMode true  --minBiasXsec $xsec --maxPileupBin 80 --numPileupBins 80 $pileupdir/PileUpData${v}_${xsec}.root
done














