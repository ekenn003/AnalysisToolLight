#!/usr/bin/env python
import argparse
import os, sys
import time
import math
import subprocess
from AnalysisToolLight.AnalysisTool.tools.batch_helper import *
#from AnalysisToolLight.AnalysisTool.tools.batch_helper import
#from AnalysisToolLight.AnalysisTool.datasets import datasets76X, datasets80X

def wrapper(args):
    # define analysis
    this_analysis = args.analysis
    # define working dirs
    tmpdir = basedir + '/VH/batch/tmp{0}'.format(args.version)
    resultsdir = basedir + '/VH/batch/results{0}'.format(args.version)
    # determine datasets
    dataset_list, dataset_map = get_datasets_to_use(args, resultsdir)

    #####################
    # write tmp scripts #
    #####################
    # clear old contents
    if os.path.exists(tmpdir): 
        print 'Deleting contents of ' + tmpdir
        os.system('rm {0}/*.*'.format(tmpdir))
    else:
        print 'Creating working directory ' + tmpdir
        os.system('mkdir {0}/'.format(tmpdir))

    # go to tmp dir
#    os.chdir(tmpdir)

########## still have to chdir for this now
    # split inputfile into temp input files
    for dname, d in dataset_map.iteritems():
        split_input_file(d, tmpdir)


    # build options map
    options = {
        'analysis'     : args.analysis,
        'analysiscode' : find_analysis_code(args.analysis),
        'resultsdir' : resultsdir,
        'tmpdir'     : tmpdir,
    }


    for dname, d in dataset_map.iteritems():
        create_submission_scripts(d, dname, **options)


#    # submit jobs
#    print '\nSubmitting jobs...'
#    for dset in datasets:
#        if not (dset in dsetstouse): continue
#        njobs = datasets[dset]['njobs']
#        for n in xrange(0, njobs):
#            scriptname = '{4}/job_{0}_{1}_{2}of{3}.sh'.format(dset, ANALYSIS, n+1, njobs, tmpdir)
#            jobname = '{3}-{0}_{2}{1}'.format(dset, '' if njobs==1 else '_{0}'.format(n+1), version[:-1], ANALYSIS)
#            submitcommand = '{2}bsub -q 8nh -J {0} < {1}'.format(jobname, scriptname, '' if args.mail else 'LSB_JOB_REPORT_MAIL=N ')
#
#
#            print submitcommand
#
##            os.system(submitcommand)
#
#            print
#            time.sleep(1)
#
#    os.chdir('../')


## ___________________________________________________________
def get_datasets_to_use(args, resultsdir):
    v = args.version
    ana = args.analysis
    # get template datasets
    #dsetmap = datasets76X if v=='76X' else datasets80X
    # get sets to use
    if v=='76X':
        dsets = (
        ##### data
            'SingleMuon_Run2015C',
            'SingleMuon_Run2015D',
        ##### signal
            'GluGlu_HToMuMu',
            'VBF_HToMuMu',
        ##### background
            'DYJetsToLL',
            'TTJets',
            'TTZToLLNuNu',
            'WWTo2L2Nu',
            'WZTo2L2Q',
            'WZTo3LNu',
            'ZZTo2L2Nu',
            'ZZTo2L2Q',
            'ZZTo4L',
        )
    elif v=='80X':
        dsets = (
        ##### data
            'SingleMuon_Run2016Bv3',
            'SingleMuon_Run2016C',
            'SingleMuon_Run2016D',
            'SingleMuon_Run2016E',
            'SingleMuon_Run2016F',
            'SingleMuon_Run2016G',
            'SingleMuon_Run2016Hv2',
            'SingleMuon_Run2016Hv3',
        ##### signal
#            'GluGlu_HToMuMu',
#            'WMinusH_HToMuMu',
#            'WPlusH_HToMuMu',
#            'VBF_HToMuMu',
#            'ZH_HToMuMu',
        ##### background
            'DYJetsToLL',
            'TTJets',
#            'WWTo2L2Nu',
#            'WZTo2L2Q',
#            'WZTo3LNu',
#            'ZZTo2L2Nu',
#            'ZZTo2L2Q',
#            'ZZTo4L',
#            'WWW',
#            'WWZ',
#            'WZZ',
#            'ZZZ',
        )
    else:
        dsets = ()

    return dsets, fill_datasets_map(v, ana, dsets, resultsdir)


## ___________________________________________________________
def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Submit jobs to lxplus batch')
    parser.add_argument('-a', '--analysis', type=str, help='Analysis to perform', choices=['VH2Mu'], required=True)
    parser.add_argument('-v', '--version',  type=str, help='CMSSW version used to make ntuples', choices=['76X','80X'], required=True)
    parser.add_argument('--mail', action='store_true', help='Send mail upon job completion')

    return parser.parse_args(argv)

## ___________________________________________________________
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = parse_command_line(argv)

    wrapper(args)
    return args


## ___________________________________________________________
if __name__ == '__main__':
    main()
