#!/usr/bin/env python
import os, sys
import time
import math
import subprocess
from AnalysisToolLight.AnalysisTool.batch.batch_helper import *
from AnalysisToolLight.AnalysisTool.batch.datasets import *


# Analysis to run #######################
ANALYSIS = '2Mu'
#version = '76X'
version = '80X'

# Options ###############################
RESULTSDIR='{0}/2Mu/batch/results{1}'.format(BASEDIR, version)

## ___________________________________________________________
def main():
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
        'tmpdir' : '2Mu/batch/'+tmpdir,
    }
    
    if '76X' in version: options['datasets'] = datasets76X
    elif '80X' in version: options['datasets'] = datasets80X
    datasets = options['datasets']

    # loop over datasets and make input files lists, sub scripts
    for dset in datasets:
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
        nlinesperjob = int(math.ceil(float(totallines)/njobs))
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
        njobs = datasets[dset]['njobs']
        for n in xrange(0, njobs):
            scriptname = '{4}/job_{0}_{1}_{2}of{3}.sh'.format(dset, ANALYSIS, n+1, njobs, tmpdir)
            jobname = '2Mu-{0}_{2}{1}'.format(dset, '' if njobs==1 else '_{0}'.format(n+1), version[:-1])
            submitcommand = 'bsub -q 8nh -J {0} < {1}'.format(jobname, scriptname)
            print submitcommand

# debug
#            if 'SingleMuon' in jobname: os.system(submitcommand)
            os.system(submitcommand)

            print
            time.sleep(1)




if __name__ == "__main__":
    main()
