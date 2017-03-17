#!/usr/bin/env python
import os, sys
#import time
#import math
#import subprocess
from AnalysisToolLight.AnalysisTool.tools.batch_helper import basedir as BASEDIR
#from AnalysisToolLight.AnalysisTool.datasets import *


head = 'ana_VH2Mu'

#version = '76X'
version = '80X'

resultsdir = '{0}/VH/batch/results{1}'.format(BASEDIR, version)

## ___________________________________________________________
def main():

    # get all the filenames
    fnames = os.listdir(resultsdir)
    datasets = []
    # get the dataset names
    for f in fnames:
        if not f.startswith(head): continue
        f = f[len(head)+1:]
        f = ('_').join(f.split('_')[:-1])
        datasets += [f]
    # remove duplicates
    datasets = sorted(set(datasets))


    commands = []
    outfiles = []
    for d in datasets:
        print d 
        bigfile = '{0}/{1}_{2}.root'.format(resultsdir, head, d)
        smolfile = '{0}/{1}_{2}_*of*.root'.format(resultsdir, head, d)
        haddcommand = 'hadd -f {0} {1} && rm {1}'.format(bigfile, smolfile)
        commands += [haddcommand]
        outfiles += [bigfile]

    for c in commands:
#        print c
        os.system(c)
        print
        print

    print '\nCreated the following files:'
    for f in outfiles:
        print '    ' + f


## ___________________________________________________________
if __name__ == "__main__":
    main()
