#!/usr/bin/env python
import os, sys
import math
import subprocess

# Analysis to run #######################
ANALYSIS='template'
#ANALYSIS='VH4Mu'


# Options ###############################
BASEDIR='{0}/src/AnalysisToolLight'.format(os.environ['CMSSW_BASE'])
RESULTSDIR='{0}/AnalysisTool/batch/results'.format(BASEDIR)
EOSDIR='/afs/cern.ch/user/e/ekennedy/eos'
DATADIR='{0}/AnalysisTool/data'.format(BASEDIR)

# Datasets ##############################
datasets = {
    'SingleMuon2015C' : { 'njobs' : 1 },
    'SingleMuon2015D' : { 'njobs' : 4 },
    'DYJetsToLL'  : { 'njobs' : 4 },
    'TTJets'      : { 'njobs' : 2 },
    'TTZToLLNuNu' : { 'njobs' : 1 },
    'WWTo2L2Nu'   : { 'njobs' : 1 },
    'WZTo2L2q'    : { 'njobs' : 3 },
    'WZTo3LNu'    : { 'njobs' : 1 },
    'ZZTo2L2Nu'   : { 'njobs' : 2 },
    'ZZTo2L2q'    : { 'njobs' : 3 },
    'ZZTo4L'      : { 'njobs' : 2 },
}

## ___________________________________________________________
def createSubmissionScript(dset, njob, njobs):
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


## ___________________________________________________________
# "main"

# Select analysis code ##################
if ANALYSIS=='template':
    ANALYSISCODE = '{0}/AnalysisTool/templates/FinalState_2mu_template.py'.format(BASEDIR)
elif ANALYSIS=='VH4Mu':
    ANALYSISCODE = '{0}/VH/python/FinalState_4mu.py'.format(BASEDIR)
else:
    raise ValueError('Analysis choice "{0}" not recognised.'.format(ANALYSIS))

# clear tmp directory and start over
if os.path.exists('tmp/'): 
    os.system('rm tmp/*.sh')
    os.chdir('tmp/')
else:
    os.system('mkdir tmp/')
    os.chdir('tmp/')

# loop over datasets and make input files lists, sub scripts
for dset in datasets:
    print '{0}:'.format(dset)
    # calculate number of jobs to run
    print '    calculating number of jobs and creating inputs'
    datasets[dset]['inputlist'] = '{0}/AnalysisTool/data/inputfiles_{1}.txt'.format(BASEDIR, dset)
    datasets[dset]['output']    = '{0}/ana_{1}_{2}.root'.format(RESULTSDIR, ANALYSIS, dset)
    datasets[dset]['logfile']   = '{0}/log_{1}_{2}.log'.format(RESULTSDIR, ANALYSIS, dset)
    # create input file lists
    with open(datasets[dset]['inputlist'], 'r') as f:
        for i, line in enumerate(f):
            pass
    i+=1
    njobs = datasets[dset]['njobs']
    nlinesperjob = int(math.ceil(float(i)/njobs))
    nlineslastjob = i - (njobs-1)*nlinesperjob
    # print a warning if the last job is <15% the size of the others
    if (float(nlineslastjob)/float(nlinesperjob)) < 0.15:
        print 'Warning: last job is disproportionately small (NJOBS: {0}, NLINES/JOB: {1}, NLINES/LASTJOB: {2}'.format(njobs, nlinesperjob, nlineslastjob)
    splitInputFile(datasets[dset]['inputlist'], njobs, nlinesperjob)

    print '    creating {0} submission script{1}'.format(njobs, '' if njobs==1 else 's')
    # create submission scripts
    for n in xrange(0, njobs):
        createSubmissionScript(dset, n, njobs)

os.chdir('../')

# submit jobs
print '\nSubmitting jobs...'
for dset in datasets:
    njobs = datasets[dset]['njobs']
    for n in xrange(0, njobs):
        scriptname = 'tmp/job_{0}_{1}_{2}of{3}.sh'.format(dset, ANALYSIS, n+1, njobs)
        jobname = '{0}{1}'.format(dset, '' if njobs==1 else '_{0}'.format(n+1))
        #print 'bsub -q 1nd -J {0} < {1}'.format(jobname, scriptname)
        #subprocess.check_call('bsub -q 1nd -J {0} < {1}'.format(jobname, scriptname))
        os.system('bsub -q 1nd -J {0} < {1}'.format(jobname, scriptname))




