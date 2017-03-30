#!/usr/bin/env python
import argparse
import os, sys
import time
import math
import subprocess
from AnalysisToolLight.AnalysisTool.tools.batch_helper import *

## ___________________________________________________________
def wrapper(args):
    # define analysis
    #this_analysis = args.analysis
    this_analysis = '2Mu'
    #this_version = args.version
    this_version = '80X'
    # define working dirs
    tmpdir = basedir + '/2Mu/batch/tmp{0}'.format(this_version)
    resultsdir = basedir + '/2Mu/batch/results{0}'.format(this_version)
    # determine datasets
    dataset_list, dataset_map = get_datasets_to_use(args, resultsdir)

    # clear old contents
    if os.path.exists(tmpdir): 
        print 'Deleting contents of ' + tmpdir
        os.system('rm -r {0}/*'.format(tmpdir))
    else:
        print 'Creating working directory ' + tmpdir
        os.system('mkdir {0}/'.format(tmpdir))

    # split inputfile into temp input files
    for dname, d in dataset_map.iteritems():
        split_input_file(d, tmpdir)

    # build options map for sub scripts
    options = {
        'analysis'     : this_analysis,
        'analysiscode' : find_analysis_code(this_analysis),
        'resultsdir' : resultsdir,
        'tmpdir'     : tmpdir,
    }

    # create sub scripts in tmp dir
    for dname, d in dataset_map.iteritems():
        create_submission_scripts(d, dname, **options)


    # submit jobs
    # go to tmp dir
    os.chdir(tmpdir)



    print '\nSubmitting jobs...'
    for dname, d in dataset_map.iteritems():
        submit_dataset_jobs(d, dname, tmpdir, args)

    os.chdir('../')


## ___________________________________________________________
def get_datasets_to_use(args, resultsdir):
    #v = args.version
    v = '80X'
    #ana = args.analysis
    ana = '2Mu'
    # get template datasets
    #dsetmap = datasets76X if v=='76X' else datasets80X
    # get sets to use
    if v=='80X':
        dsets = (
        ##### data
            'SingleMuon_Run2016Bv2',
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
            'WWTo2L2Nu',
          #  'WZTo2L2Q',
            'WZTo3LNu',
            'ZZTo2L2Nu',
            'ZZTo2L2Q',
            'ZZTo4L',
            'WWW',
            'WWZ',
            'WZZ',
            'ZZZ',
        )
    else:
        dsets = ()

    return dsets, fill_datasets_map(v, ana, dsets, resultsdir)


## ___________________________________________________________
def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Submit jobs to lxplus batch')
    parser.add_argument('-a', '--analysis', type=str, help='Analysis to perform', choices=['2Mu'], required=True)
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
