#!/usr/bin/env python
import os, sys
import math

BASEDIR='{0}/src/AnalysisToolLight'.format(os.environ['CMSSW_BASE'])

## ___________________________________________________________
def find_analysis_code(analysisname, basedir):
    '''Select analysis code'''
    if analysisname=='template':
        analysiscode = '{0}/AnalysisTool/templates/FinalState_2mu_template.py'.format(basedir)
    elif analysisname=='PU':
        analysiscode = '{0}/AnalysisTool/pileupstudy/FinalState_2mu.py'.format(basedir)
    elif analysisname=='2Mu':
        analysiscode = '{0}/2Mu/python/FinalState_2mu.py'.format(basedir)
    elif analysisname=='VH4Mu':
        analysiscode = '{0}/VH/python/FinalState_4mu.py'.format(basedir)
    elif analysisname=='VH2Mu':
        analysiscode = '{0}/VH/python/FinalState_2mu.py'.format(basedir)
    elif analysisname=='ZH2J2Mu':
        analysiscode = '{0}/ZH/python/FinalState_2j2mu.py'.format(basedir)
    else:
        raise ValueError('Analysis choice "{0}" not recognised.'.format(analysisname))
    return analysiscode


## ___________________________________________________________
def create_submission_script(dset, njob, njobs, **kwargs):
    ANALYSIS   = kwargs['ANALYSIS']
    BASEDIR    = kwargs['BASEDIR']
    RESULTSDIR = kwargs['RESULTSDIR']
    RESULTSDIR = kwargs['RESULTSDIR']
    tmpdir     = kwargs['tmpdir']
    datasets   = kwargs['datasets']
    ANALYSISCODE = find_analysis_code(ANALYSIS, BASEDIR)

    DATADIR = '{0}/AnalysisTool/data'.format(BASEDIR)
    
    scriptname = 'job_{0}_{1}_{2}of{3}.sh'.format(dset, ANALYSIS, n(njob+1), n(njobs))

    with open(scriptname, 'w') as fout:
        fout.write('#!/bin/sh\n')
        fout.write('\n')
        fout.write('BASEDIR="{0}"\n'.format(BASEDIR))
        fout.write('RESULTSDIR="{0}"\n'.format(RESULTSDIR))
        fout.write('DATASET="{0}"\n'.format(dset))
        fout.write('ANALYSIS="{0}"\n'.format(ANALYSIS))
        fout.write('ANALYSISCODE="{0}"\n'.format(ANALYSISCODE))
        # find input files and define output files
        datadir, inputfilename = os.path.split(datasets[dset]['inputlist'])
        inputfilename = 'job_{0}_{1}of{2}.txt'.format(inputfilename[:-4], n(njob+1), n(njobs))
        INPUTFILE  = '{0}/{1}/{2}'.format(BASEDIR, tmpdir, inputfilename)
        OUTPUTFILE = '{0}_{1}of{2}.root'.format(datasets[dset]['output'][:-5], n(njob+1), n(njobs))
        LOGFILE    = '{0}_{1}of{2}.log'.format(datasets[dset]['logfile'][:-4], n(njob+1), n(njobs))

        fout.write('INPUTFILE="{0}"\n'.format(INPUTFILE))
        fout.write('OUTPUTFILE="{0}"\n'.format(OUTPUTFILE))
        fout.write('LOGFILE="{0}"\n'.format(LOGFILE))
        fout.write('\n')
        fout.write('cd $BASEDIR\n')
        fout.write('eval `scramv1 runtime -sh`\n')
        fout.write('export XRD_NETWORKSTACK=IPv4\n')
        fout.write('\n')
        fout.write('# go to working directory\n')
        fout.write('cd $RESULTSDIR\n')
        fout.write('cmsenv\n')
        fout.write('# copy grid auth\n')
        fout.write('find /tmp/x5* -user ekennedy -exec cp -f {} . \;\n')
        fout.write('\n')
        fout.write('# submit job\n')
        fout.write('python $ANALYSISCODE -i $INPUTFILE -o $OUTPUTFILE > $LOGFILE 2>&1\n')
        fout.write('\n')

    os.system('chmod +x {0}'.format(scriptname))

## ___________________________________________________________
def split_input_file(inputfile, njobs, linesperfile):
    datadir, inputfilename = os.path.split(inputfile)

    basename = 'job_{0}'.format(inputfilename[:-4])

    with open(inputfile, 'r') as fin:
        n = 1
        # open the first output file
        fout = open('{0}_{1}of{2}.txt'.format(basename, n(n), n(njobs)), 'w')
        # loop over all lines in the input file, and number them
        for i, line in enumerate(fin):
            # every time the current line number can be divided by linesperfile
            # close the output file and open a new one
            if i>0 and i%linesperfile==0:
                n += 1
                fout.close()
                fout = open('{0}_{1}of{2}.txt'.format(basename, n(n), n(njobs)), 'w')
            # write line to fout
            fout.write(line)
        fout.close()

## ___________________________________________________________
def n(n):
    return str(n).zfill(2)

