#!/bin/bash
# This has to be run with ./run.sh instead of source or 
# errors will close the ssh session.
# This is an example of a script to run an analyis locally.
# See AnalysisTool/test/batch.sh for a script to run
# on the lxplus batch system.
set -e
BASEDIR=$CMSSW_BASE/src/AnalysisToolLight


maxevents=50000
#maxevents=-1

#########################################
# Analysis to run #######################
#########################################
#ANALYSIS="template"
ANALYSIS="2Mu"
#ANALYSIS="PU"
#ANALYSIS="VH4Mu"
#ANALYSIS="ZH2E2Mu"
#ANALYSIS="ZH2J2Mu"

v="76X"
#v="80X"
#########################################
# Dataset to run analysis on ############
#########################################
#DATASET="testingdata"
#DATASET="testingmc76"
#DATASET="testingmc80"
DATASET="DYJetsToLL"
#DATASET="DYJets"
#DATASET="TTJets"
#DATASET="TTZJets"
#DATASET="TTWJets"
#DATASET="TTZToLLNuNu"
#DATASET="WWTo2L2Nu"
#DATASET="WZTo2L2q"
#DATASET="WZTo3LNu"
#DATASET="ZZTo2L2Nu"
#DATASET="ZZTo2L2Q"
#DATASET="ZZTo4L"

#DATASET="SingleMuon2015C"
#DATASET="SingleMuon2015D"
#DATASET="SingleMuon2016B"
#DATASET="SingleMuon2016C"


#########################################
# Set up rest of running ################
#########################################
#DATADIR=$BASEDIR/AnalysisTool/data
INPUTFILE=$BASEDIR/AnalysisTool/data/${v}/inputfiles_${DATASET}.txt

if [ "$ANALYSIS" == "template" ]; then
    OUTPUTFILE=$BASEDIR/ana_2mu_$DATASET.root
    ANALYSISCODE=$BASEDIR/AnalysisTool/templates/FinalState_2mu_template.py

elif [ "$ANALYSIS" == "2Mu" ]; then
    OUTPUTFILE=$BASEDIR/2Mu/2mu_$DATASET.root
    ANALYSISCODE=$BASEDIR/2Mu/python/FinalState_2mu.py

elif [ "$ANALYSIS" == "VH4Mu" ]; then
    OUTPUTFILE=$BASEDIR/VH/VH_4mu_$DATASET.root
    ANALYSISCODE=$BASEDIR/VH/python/FinalState_4mu.py
 
elif [ "$ANALYSIS" == "ZH2E2Mu" ]; then
    OUTPUTFILE=$BASEDIR/ZH/ZH_2e2mu_$DATASET.root
    ANALYSISCODE=$BASEDIR/ZH/python/FinalState_2e2mu.py
 
elif [ "$ANALYSIS" == "ZH2J2Mu" ]; then
    OUTPUTFILE=$BASEDIR/ZH/ZH_2j2mu_$DATASET.root
    ANALYSISCODE=$BASEDIR/ZH/python/FinalState_2j2mu.py
 
elif [ "$ANALYSIS" == "PU" ]; then
    OUTPUTFILE=$BASEDIR/AnalysisTool/pileupstudy/PU_$DATASET.root
    ANALYSISCODE=$BASEDIR/AnalysisTool/pileupstudy/FinalState_2mu.py

else
    echo "ERROR: analysis choice " + $ANALYSIS + " not found :("
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

# debuggin
#echo
#echo "########################### PARAMETERS:"
#echo "ANALYSIS = $ANALYSIS"
#echo "DATASET  = $DATASET"
#echo "INPUTFILE    = $INPUTFILE"
#echo "OUTPUTFILE   = $OUTPUTFILE"
#echo "ANALYSISCODE = $ANALYSISCODE"
#echo "#######################################"
#echo

# run analysis
#python $ANALYSISCODE $INPUTFILE $OUTPUTFILE $DATADIR
if [ "$maxevents" == "-1" ]; then
    python $ANALYSISCODE -i $INPUTFILE -o $OUTPUTFILE 
else
    python $ANALYSISCODE -i $INPUTFILE -o $OUTPUTFILE -n $maxevents
fi



