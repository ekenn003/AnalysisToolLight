#!/bin/sh

BASEDIR=$CMSSW_BASE/src/AnalysisToolLight

cd $BASEDIR
eval `scramv1 ru -sh`

#########################################
# Analysis to run #######################
#########################################
ANALYSIS="template"
#ANALYSIS="VH4Mu"

#########################################
# Dataset to run analysis on ############
#########################################
#DATASET="testing"
#DATASET="DYJetsToLL"
#DATASET="GF125HToMuMu"
#DATASET="TTJets"
#DATASET="TTZToLLNuNu"
#DATASET="VBF125HToMuMu"
#DATASET="WWTo2L2Nu"
#DATASET="WZTo2L2q"
#DATASET="WZTo3LNu"
#DATASET="ZZTo2L2Nu"
#DATASET="ZZTo2L2q"
#DATASET="ZZTo4L"

DATASET="SingleMuon2015C"
#DATASET="SingleMuon2015D"


#########################################
# Location of pileup files ##############
#########################################
PILEUPDIR="$BASEDIR/AnalysisTool/data/pileup"




#########################################
# Set up rest of running ################
#########################################
INPUTFILE=$BASEDIR/AnalysisTool/data/inputfiles_$DATASET.txt
LOGFILE=$BASEDIR/log_$ANALYSIS_$DATASET.log

if [ "$ANALYSIS" == "template" ]; then
    OUTPUTFILE=$BASEDIR/ana_2mu_$DATASET.root
    ANALYSISCODE=$BASEDIR/AnalysisTool/templates/FinalState_2mu_template.py

elif [ "$ANALYSIS" == "VH4Mu" ]; then
    OUTPUTFILE=$BASEDIR/VH/VH_4mu_$DATASET.root
    ANALYSISCODE=$BASEDIR/VH/python/FinalState_4mu.py

else
    echo "ERROR: analysis choice  not found :("
    exit 1
fi

# check for input list
if [ ! -f "$INPUTFILE" ]; then
    echo "Input file $INPUTFILE not found."
    exit 1
fi

# check for analysis code
if [ ! -f "$ANALYSISCODE" ]; then
    echo "Analysis $ANALYSISCODE not found."
    exit 1
fi


# run analysis
eosmount ~/eos
python $ANALYSISCODE $INPUTFILE $OUTPUTFILE $PILEUPDIR > $LOGFILE 2>&1

rfcp $LOGFILE $BASEDIR/results/
rfcp $OUTPUTFILE $BASEDIR/results/

