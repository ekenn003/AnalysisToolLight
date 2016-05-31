#!/bin/sh

#BASEDIR=$CMSSW_BASE/src/AnalysisToolLight
BASEDIR=/afs/cern.ch/work/e/ekennedy/work/fsanalysis/ana76/root6/CMSSW_7_6_5/src/AnalysisToolLight
EOSDIR=/afs/cern.ch/user/e/ekennedy/eos

cd $BASEDIR
cmsenv
#eval `scramv1 ru -sh`
eval `scramv1 runtime -sh`
cd -

ANALYSIS="template"

#DATASET="SingleMuon2015C"
DATASET="SingleMuon2015D"

PILEUPDIR=$BASEDIR/AnalysisTool/data/pileup


#########################################

INPUTFILE=$BASEDIR/AnalysisTool/data/inputfiles_$DATASET.txt
LOGFILE=$BASEDIR/log_$ANALYSIS_$DATASET.log
OUTPUTFILE=$BASEDIR/ana_2mu_$DATASET.root
ANALYSISCODE=$BASEDIR/AnalysisTool/templates/FinalState_2mu_template.py

# mount eos
/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select -b fuse mount $EOSDIR

# run analysis
python $ANALYSISCODE $INPUTFILE $OUTPUTFILE $PILEUPDIR > $LOGFILE 2>&1

# move outputs
rfcp $LOGFILE $BASEDIR/results/
rfcp $OUTPUTFILE $BASEDIR/results/

# unmount eos
/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select -b fuse umount $EOSDIR
