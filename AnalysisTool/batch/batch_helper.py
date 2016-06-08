#!/usr/bin/env python
import os, sys
import math

## ___________________________________________________________
def selectAnalysisCode(analysisname, basedir):
    '''Select analysis code'''
    if analysisname=='template':
        analysiscode = '{0}/AnalysisTool/templates/FinalState_2mu_template.py'.format(basedir)
    elif analysisname=='VH4Mu':
        analysiscode = '{0}/VH/python/FinalState_4mu.py'.format(basedir)
    else:
        raise ValueError('Analysis choice "{0}" not recognised.'.format(analysisname))
    return analysiscode


## ___________________________________________________________
def createSubmissionScript(dset, njob, njobs, **kwargs):
    ANALYSIS   = kwargs['ANALYSIS']
    BASEDIR    = kwargs['BASEDIR']
    RESULTSDIR = kwargs['RESULTSDIR']
    EOSDIR     = kwargs['EOSDIR']
    datasets   = kwargs['datasets']
    ANALYSISCODE = selectAnalysisCode(ANALYSIS, BASEDIR)

    DATADIR = '{0}/AnalysisTool/data'.format(BASEDIR)
    
    scriptname = 'job_{0}_{1}_{2}of{3}.sh'.format(dset, ANALYSIS, njob+1, njobs)

    with open(scriptname, 'w') as fout:
        fout.write('#!/bin/sh\n')
        fout.write('\n')
        fout.write('BASEDIR={0}\n'.format(BASEDIR))
        fout.write('RESULTSDIR={0}\n'.format(RESULTSDIR))
        fout.write('EOSDIR={0}\n'.format(EOSDIR))
        fout.write('DATADIR={0}\n'.format(DATADIR))
        fout.write('DATASET={0}\n'.format(dset))
        fout.write('ANALYSIS={0}\n'.format(ANALYSIS))
        fout.write('ANALYSISCODE={0}\n'.format(ANALYSISCODE))
        # find input files and define output files
        datadir, inputfilename = os.path.split(datasets[dset]['inputlist'])
        inputfilename = 'job_{0}_{1}of{2}.txt'.format(inputfilename[:-4], njob+1, njobs)
        INPUTFILE  = '{0}/AnalysisTool/batch/tmp/{1}'.format(BASEDIR, inputfilename)
        OUTPUTFILE = '{0}_{1}of{2}.root'.format(datasets[dset]['output'][:-5], njob+1, njobs)
        LOGFILE    = '{0}_{1}of{2}.log'.format(datasets[dset]['logfile'][:-4], njob+1, njobs)
        fout.write('INPUTFILE={0}\n'.format(INPUTFILE))
        fout.write('OUTPUTFILE={0}\n'.format(OUTPUTFILE))
        fout.write('LOGFILE={0}\n'.format(LOGFILE))
        fout.write('\n')
        fout.write('cd $BASEDIR\n')
        fout.write('eval `scramv1 runtime -sh`\n')
        fout.write('\n')
        fout.write('# go to working directory\n')
        fout.write('cd $RESULTSDIR\n')
        fout.write('\n')
        fout.write('# mount eos\n')
        fout.write('/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select -b fuse mount $EOSDIR\n')
        fout.write('\n')
        fout.write('# submit job\n')
        fout.write('python $ANALYSISCODE $INPUTFILE $OUTPUTFILE $DATADIR > $LOGFILE 2>&1\n')
        fout.write('\n')

    os.system('chmod +x {0}'.format(scriptname))

## ___________________________________________________________
def splitInputFile(inputfile, njobs, linesperfile):
    datadir, inputfilename = os.path.split(inputfile)

    basename = 'job_{0}'.format(inputfilename[:-4])

    with open(inputfile, 'r') as fin:
        n = 1
        # open the first output file
        fout = open('{0}_{1}of{2}.txt'.format(basename, n, njobs), 'w')
        # loop over all lines in the input file, and number them
        for i, line in enumerate(fin):
            # every time the current line number can be divided by linesperfile
            # close the output file and open a new one
            if i>0 and i%linesperfile==0:
                n += 1
                fout.close()
                fout = open('{0}_{1}of{2}.txt'.format(basename, n, njobs), 'w')
            # write line to fout
            fout.write(line)
        fout.close()
