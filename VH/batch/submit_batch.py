#!/usr/bin/env python
import os, sys
import time
import math
import subprocess
from AnalysisToolLight.AnalysisTool.batch.batch_helper import *
from AnalysisToolLight.AnalysisTool.datasets import *


#SENDEMAIL = True
SENDEMAIL = False

# Analysis to run #######################
ANALYSIS = 'VH2Mu'

#version = '76X'
version = '80X'

dsetstouse = [

#### 76X ####
#    # data
#    'SingleMuon_Run2015C',
#    'SingleMuon_Run2015D',
#    # signal
#    'GluGlu_HToMuMu',
#    'VBF_HToMuMu',
#    # background
#    'DYJetsToLL',
#    'TTJets',
#    'TTZToLLNuNu',
#    'WWTo2L2Nu',
#    'WZTo2L2Q',
#    'WZTo3LNu',
#    'ZZTo2L2Nu',
#    'ZZTo2L2Q',
#    'ZZTo4L',

#### 80X ####
##### data
    'SingleMuon_Run2016B',
    'SingleMuon_Run2016C',
    'SingleMuon_Run2016D',
    'SingleMuon_Run2016E',
    'SingleMuon_Run2016F',
    'SingleMuon_Run2016G',
##### signal
    #'GluGlu_HToMuMu',
    #'WMinusH_HToMuMu',
    #'WPlusH_HToMuMu',
    #'VBF_HToMuMu',
    #'ZH_HToMuMu',
##### background
    'DYJetsToLL',
    'TTJets',
    #'WWTo2L2Nu',
    #'WZTo2L2Q',
    #'WZTo3LNu',
    #'ZZTo2L2Nu',
    #'ZZTo2L2Q',
    #'ZZTo4L',
    #'WWW',
    #'WWZ',
    #'WZZ',
    #'ZZZ',

]

# Options ###############################
RESULTSDIR='{0}/VH/batch/results{1}'.format(BASEDIR, version)

## ___________________________________________________________
def main():
    print '\n\n***********************'
    print '* Did you setupgrid ? *'
    print '***********************\n'
    tmpdir = 'tmp{0}'.format(version)
    # clear tmp directory and start over
    if os.path.exists(tmpdir): 
        os.system('rm {0}/*'.format(tmpdir))
    else:
        os.system('mkdir {0}/'.format(tmpdir))
    os.chdir(tmpdir)
    # build options map
    options = {
        'ANALYSIS' : ANALYSIS,
        'BASEDIR' : BASEDIR,
        'RESULTSDIR' : RESULTSDIR,
        'tmpdir' : 'VH/batch/'+tmpdir,
    }
    
    if '76X' in version: options['datasets'] = datasets76X
    elif '80X' in version: options['datasets'] = datasets80X
    datasets = options['datasets']

    for d in dsetstouse:
        if d not in datasets:
            raise ValueError('"{0}" won\'t be submitted'.format(d))


    # loop over datasets and make input files lists, sub scripts
    for dset in datasets:
        print 'checking ' + str(dset)
        if not (dset in dsetstouse): continue
        print '{0}:'.format(dset)

        # calculate number of jobs to run
        print '    calculating number of jobs and creating inputs'
        datasets[dset]['inputlist'] = '{0}/AnalysisTool/data/{2}/inputfiles_{1}.txt'.format(BASEDIR, dset, version)
        datasets[dset]['output']    = '{0}/ana_{1}_{2}.root'.format(RESULTSDIR, ANALYSIS, dset)
        datasets[dset]['logfile']   = '{0}/log_{1}_{2}.log'.format(RESULTSDIR, ANALYSIS, dset)

        # create input file lists
        # count total input files
        with open(datasets[dset]['inputlist'], 'r') as f:
            for totallines, line in enumerate(f):
                pass
        totallines += 1
        njobs = datasets[dset]['njobs']
        # if we asked for more jobs than input files, just do one job per file
        if njobs >= totallines: njobs = totallines
        nlinesperjob = int(math.floor(float(totallines)/njobs))
        nlineslastjob = totallines - (njobs-1)*nlinesperjob

        # print a warning if the last job is <15% the size of the others
        if (float(nlineslastjob)/float(nlinesperjob)) < 0.15:
            print 'Warning: last job is disproportionately small (NJOBS: {0}, NLINES/JOB: {1}, NLINES/LASTJOB: {2}'.format(njobs, nlinesperjob, nlineslastjob)
        splitInputFile(datasets[dset]['inputlist'], njobs, nlinesperjob)
    
        print '    creating {0} submission script{1}'.format(njobs, '' if njobs==1 else 's')

        # create submission scripts
        for n in xrange(0, njobs):
            createSubmissionScript(dset, n, njobs, **options)
    
    os.chdir('../')
    
    # submit jobs
    print '\nSubmitting jobs...'
    for dset in datasets:
        if not (dset in dsetstouse): continue
        njobs = datasets[dset]['njobs']
        for n in xrange(0, njobs):
            scriptname = '{4}/job_{0}_{1}_{2}of{3}.sh'.format(dset, ANALYSIS, n+1, njobs, tmpdir)
            jobname = '{3}-{0}_{2}{1}'.format(dset, '' if njobs==1 else '_{0}'.format(n+1), version[:-1], ANALYSIS)
            submitcommand = '{2}bsub -q 8nh -J {0} < {1}'.format(jobname, scriptname, '' if SENDEMAIL else 'LSB_JOB_REPORT_MAIL=N ')
            print submitcommand

            os.system(submitcommand)

            print
            time.sleep(1)




if __name__ == "__main__":
    main()
