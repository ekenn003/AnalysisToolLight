#!/bin/bash

#lumimask=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Cert_246908-260627_13TeV_PromptReco_Collisions15_25ns_JSON_v2.txt
lumimask=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/Reprocessing/Cert_13TeV_16Dec2015ReReco_Collisions15_25ns_JSON_v2.txt
pileupjson=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions15/13TeV/PileUp/pileup_latest.txt
pileupdir=$CMSSW_BASE/src/AnalysisToolLight/AnalysisTool/data/pileup

# make pileupdir if it doesn't exist
if [ ! -d "$pileupdir" ]; then
    mkdir -p $pileupdir
fi

for xsec in 71000; do
    up=$(echo "$xsec*1.05" | bc)
    down=$(echo "$xsec*0.95" | bc)
    echo $xsec
    pileupCalc.py -i $lumimask --inputLumiJSON $pileupjson --calcMode true  --minBiasXsec $xsec --maxPileupBin 80 --numPileupBins 80 $pileupdir/PileUpData76X.root
    echo $up
    pileupCalc.py -i $lumimask --inputLumiJSON $pileupjson --calcMode true  --minBiasXsec $up --maxPileupBin 80 --numPileupBins 80 $pileupdir/PileUpData76X_up.root
    echo $down
    pileupCalc.py -i $lumimask --inputLumiJSON $pileupjson --calcMode true  --minBiasXsec $down --maxPileupBin 80 --numPileupBins 80 $pileupdir/PileUpData76X_down.root
done
#for xsec in 69000 71000; do
#    echo $xsec
#    pileupCalc.py -i $lumimask --inputLumiJSON $pileupjson --calcMode true  --minBiasXsec $xsec --maxPileupBin 80 --numPileupBins 80 $pileupdir/PileUpData_$xsec.root
#done
echo "done"
