#!/bin/bash
# chmod me and run me with ./getPileupDists.sh

#v="76X"
v="80X"
#run="G"

##############################
# Common                     #
##############################
pileupdir=$CMSSW_BASE/src/AnalysisToolLight/AnalysisTool/data/pileup

maxpubin=100
maxnumbins=100

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
    minbias=69000

##############################
# 80X                        #
##############################
elif [ $v == "80X" ]; then

    # Data ###
    lumimask="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/ReReco/Final/Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt"
    #lumimask="/afs/cern.ch/work/e/ekennedy/work/fsanalysis/ana76/root6/CMSSW_7_6_5/src/AnalysisToolLight/AnalysisTool/scripts/json_${run}.json"
    pileupjson="/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/pileup_latest.txt"

    # MC #####
    mixurl="https://raw.githubusercontent.com/cms-sw/cmssw/CMSSW_8_0_X/SimGeneral/MixingModule/python/"
    # 80X sample with startup pileup
    #mixfile="mix_2016_25ns_SpringMC_PUScenarioV1_PoissonOOTPU_cfi.py"
    # moriond17 MC
    mixfile="mix_2016_25ns_Moriond17MC_PoissonOOTPU_cfi.py"
    minbias=69200

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
xsec=$minbias
echo "Making PU files for $v with min bias xsec ${minbias}."
up=$(echo "$xsec*1.025" | bc)
down=$(echo "$xsec*0.975" | bc)
echo $xsec
pileupCalc.py -i $lumimask --inputLumiJSON $pileupjson --calcMode true  --minBiasXsec $xsec --maxPileupBin ${maxpubin} --numPileupBins ${maxnumbins} $pileupdir/PileUpData${v}.root
echo "up = ${up}"
pileupCalc.py -i $lumimask --inputLumiJSON $pileupjson --calcMode true  --minBiasXsec $up   --maxPileupBin ${maxpubin} --numPileupBins ${maxnumbins} $pileupdir/PileUpData${v}_Up.root
echo "down = ${down}"
pileupCalc.py -i $lumimask --inputLumiJSON $pileupjson --calcMode true  --minBiasXsec $down --maxPileupBin ${maxpubin} --numPileupBins ${maxnumbins} $pileupdir/PileUpData${v}_Down.root

echo "done"
echo
echo "Created the following files:"
echo "${pileupdir}/PileUpData${v}.root"
echo "${pileupdir}/PileUpData${v}_Up.root"
echo "${pileupdir}/PileUpData${v}_Down.root"
echo
echo "Now you can run the following command:"
echo "    python generatePileupHist.py -version \"${v}\""
