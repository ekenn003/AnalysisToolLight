#!/usr/bin/env python
import os, sys
import math
from AnalysisToolLight.AnalysisTool.datasets import datasets76X, datasets80X

scram = os.environ['CMSSW_BASE']
basedir = scram + '/src/AnalysisToolLight'
datadir = basedir + '/AnalysisTool/data'



## ___________________________________________________________
def find_analysis_code(analysisname):
    '''Select analysis code'''
    if analysisname=='PU':
        tail = 'AnalysisTool/pileupstudy/FinalState_2mu.py'
    elif analysisname=='2Mu':
        tail = '2Mu/python/FinalState_2mu.py'
    elif analysisname=='VH4Mu':
        tail = 'VH/python/FinalState_4mu.py'
    elif analysisname=='VH2Mu':
        tail = 'VH/python/FinalState_2mu.py'
    elif analysisname=='ZH2J2Mu':
        tail = 'ZH/python/FinalState_2j2mu.py'
    else:
        raise ValueError('Analysis choice "{0}" not recognised.'.format(analysisname))
    return '{0}/{1}'.format(basedir, tail)



def fill_datasets_map(v, ana, dsets, resultsdir):

    dsetmap = datasets76X if v=='76X' else datasets80X

    # make sure they will be submitted
    for d in dsets:
        if d not in dsetmap:
            raise ValueError('"{0}" won\'t be submitted'.format(d))


    # set up infos
    for dname, d in dsetmap.iteritems():
        d['inputlist'] = '{0}/{1}/inputfiles_{2}.txt'.format(datadir, v, dname)
        d['output']    = '{0}/ana_{1}_{2}.root'.format(resultsdir, ana, dname)
        d['logfile']   = '{0}/log_{1}_{2}.log'.format(resultsdir, ana, dname)

        # get number of lines per job
        njobs = d['njobs']
        # get total number of inputs
        with open(d['inputlist'], 'r') as f:
            for totallines, line in enumerate(f):
                pass
        totallines += 1
        # if we asked for more jobs than input files, just do one job per file
        if njobs >= totallines: njobs = totallines
        nlinesperjob = int(math.ceil(float(totallines)/njobs))
        d['nlinesperjob'] = nlinesperjob

    return dsetmap



## ___________________________________________________________
def split_input_file(d, tmpdir):
    inputfile = d['inputlist']
    njobs = d['njobs']
    nlinesperjob = d['nlinesperjob']
    input_head = '{tmpdir}/job_{0}'.format(os.path.split(inputfile)[1][:-4], tmpdir=tmpdir)

    with open(inputfile, 'r') as fin:
        n = 1
        # open the first output file
        fout = open('{0}_01of{1}.txt'.format(input_head, n2d(njobs)), 'w')
        # loop over all lines in the input file, and number them
        for i, line in enumerate(fin):
            # every time the current line number can be divided by nlinesperjob,
            # close the output file and open a new one
            if i>0 and i%nlinesperjob==0:
                n += 1
                fout.close()
                fout = open('{0}_{1}of{2}.txt'.format(input_head, n2d(n), n2d(njobs)), 'w')
            # write line to fout
            fout.write(line)
        fout.close()



## ___________________________________________________________
def create_submission_scripts(d, dname, **kwargs):
    analysis     = kwargs['analysis']
    analysiscode = kwargs['analysiscode']
    resultsdir = kwargs['resultsdir']
    tmpdir     = kwargs['tmpdir']

    njobs = d['njobs']
    # these heads contain the full path prefix
    input_head  = tmpdir + '/job_' + os.path.split(d['inputlist'])[1][:-4]
    output_head = resultsdir + '/' + os.path.split(d['output'])[1][:-5]
    log_head    = resultsdir + '/' + os.path.split(d['logfile'])[1][:-4]

    for n in range(njobs):
        # define this sub script name
        this_scriptname = '{tmpdir}/job_{0}_{1}_{2}of{3}.sh'.format(analysis, dname, n2d(n+1), n2d(njobs), tmpdir=tmpdir)
        # find input files
        this_inputfile  = '{0}_{1}of{2}.txt'.format(input_head, n2d(n+1), n2d(njobs))
        # define output files
        this_outputfile = '{0}_{1}of{2}.root'.format(output_head, n2d(n+1), n2d(njobs))
        this_logfile    = '{0}_{1}of{2}.log'.format(d['logfile'][:-4], n2d(n+1), n2d(njobs))

        # write it
        with open(this_scriptname, 'w') as fout:
            fout.write('#!/bin/sh\n')
            fout.write('\n')
            fout.write('BASEDIR="{0}"\n'.format(basedir))
            fout.write('TMPDIR="{0}"\n'.format(tmpdir))
            fout.write('DATASET="{0}"\n'.format(dname))
            fout.write('ANALYSIS="{0}"\n'.format(analysis))
            fout.write('ANALYSISCODE="{0}"\n'.format(analysiscode))
            fout.write('INPUTFILE="{0}"\n'.format(this_inputfile))
            fout.write('OUTPUTFILE="{0}"\n'.format(this_outputfile))
            fout.write('LOGFILE="{0}"\n'.format(this_logfile))
            fout.write('\n')
            fout.write('cd $BASEDIR\n')
            fout.write('eval `scramv1 runtime -sh`\n')
            fout.write('export XRD_NETWORKSTACK=IPv4\n')
            fout.write('\n')
            fout.write('# go to working directory\n')
            fout.write('cd $TMPDIR\n')
            fout.write('cmsenv\n')
            fout.write('# copy grid auth\n')
            fout.write('find /tmp/x5* -user ekennedy -exec cp -f {} . \;\n')
            fout.write('\n')
            fout.write('# submit job\n')
            fout.write('python $ANALYSISCODE -i $INPUTFILE -o $OUTPUTFILE > $LOGFILE 2>&1\n')
            fout.write('\n')

        os.system('chmod +x {0}'.format(this_scriptname))



## ___________________________________________________________
def n2d(n):
    return str(n).zfill(2)
