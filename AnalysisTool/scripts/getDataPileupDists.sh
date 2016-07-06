#!/bin/bash

lumimask=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/Cert_271036-275125_13TeV_PromptReco_Collisions16_JSON.txt
pileupjson=/afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions16/13TeV/PileUp/pileup_latest.txt
pileupdir=$CMSSW_BASE/src/AnalysisToolLight/AnalysisTool/data/pileup

# make pileupdir if it doesn't exist
if [ ! -d "$pileupdir" ]; then
    mkdir -p $pileupdir
fi

for xsec in 69000; do
    up=$(echo "$xsec*1.05" | bc)
    down=$(echo "$xsec*0.95" | bc)
    echo $xsec
    pileupCalc.py -i $lumimask --inputLumiJSON $pileupjson --calcMode true  --minBiasXsec $xsec --maxPileupBin 80 --numPileupBins 80 $pileupdir/PileUpData80X.root
    echo $up
    pileupCalc.py -i $lumimask --inputLumiJSON $pileupjson --calcMode true  --minBiasXsec $up --maxPileupBin 80 --numPileupBins 80 $pileupdir/PileUpData80X_up.root
    echo $down
    pileupCalc.py -i $lumimask --inputLumiJSON $pileupjson --calcMode true  --minBiasXsec $down --maxPileupBin 80 --numPileupBins 80 $pileupdir/PileUpData80X_down.root
done
echo "done"
