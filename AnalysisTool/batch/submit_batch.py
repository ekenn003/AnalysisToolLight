#!/usr/bin/env python
import os, sys
import math

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
#    'SingleMuon2015C' : { 'njobs' : 1 },
#    'SingleMuon2015D' : { 'njobs' : 4 },
#    'DYJets'      : { 'njobs' : 3 },
#    'TTJets'      : { 'njobs' : 1 },
#    'TTZToLLNuNu' : { 'njobs' : 1 },
#    'WWTo2L2Nu'   : { 'njobs' : 1 },
#    'WZTo2L2q'    : { 'njobs' : 3 },
#    'WZTo3LNu'    : { 'njobs' : 1 },
    'ZZTo2L2Nu'   : { 'njobs' : 2 },
#    'ZZTo2L2q'    : { 'njobs' : 1 },
#    'ZZTo4L'      : { 'njobs' : 1 },
}

# Make batch submit script ##############
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
        INPUTFILE  = '{0}_{1}of{2}.txt'.format(datasets[dset]['inputlist'][:-4], njob+1, njobs)
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


def splitInputFile(inputfile, njobs, linesperfile):
    datadir, inputfilename = os.path.split(inputfile)
    basename = 'job_{0}'.format(inputfilename[:-4])

    with open(inputfile, 'r') as fin:
        n = 1
        # open the first output file
        print 'try to open file ' + 'tmp/{0}_{1}of{2}.txt'.format(basename, n, njobs)
        fout = open('{0}_{1}of{2}.txt'.format(basename, n, njobs), 'w')
        # loop over all lines in the input file, and number them
        for i, line in enumerate(fin):
            # every time the current line number can be divided by linesperfile
            # close the output file and open a new one
            if i>0 and i%linesperfile==0:
                n += 1
                print 'close previous file and open file ' + 'tmp/{0}_{1}of{2}.txt'.format(basename, n, njobs)
                fout.close()
                fout = open('{0}_{1}of{2}.txt'.format(basename, n, njobs), 'w')
            # write line to fout
            fout.write(line)
        fout.close()


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



for dset in datasets:

    # calculate number of jobs to run
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


    for n in xrange(0, njobs):
        createSubmissionScript(dset, n, njobs)



os.chdir('../')






