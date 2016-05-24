import logging
import argparse
import glob
import os
import sys
import ROOT
from Dataform import *

## ___________________________________________________________
class AnalysisBase(object):
    '''
    You should derive your own class from AnalysisBase
    '''
    ## _______________________________________________________
    def __init__(self, args):
        # set defaults. These can be overridden with command line arguments (after adding to Base)
        self.filenames = []
        self.treedir   = 'makeroottree'
        self.treename  = 'AC1B'
        self.luminame  = 'AC1Blumi'
        self.infoname  = 'AC1Binfo'

        self.output    = args.outputFileName

        # put file names into a list called self.filenames
        inputFileList = args.inputFileList
        with open(inputFileList,'r') as f:
            for line in f.readlines():
                self.filenames += glob.glob(line.strip())




        self.sumweight = 0
        self.nevents   = 0
        # things we will check in the first file
        self.isdata = True
        self.tauDiscrims = []
        # get the summed weights of processed entries (add up all lumi_sumweights in AC1Blumi)
        for f, fname in enumerate(self.filenames):
            tfile = ROOT.TFile(fname)
            print 'Adding file ' + str(f+1) + ': ' + fname
            lumitree = tfile.Get('{0}/{1}'.format(self.treedir, self.luminame))
            self.sumweight += lumitree.lumi_sumweights
            self.nevents   += lumitree.lumi_eventsprocessed
            if f == 0:
                infotree = tfile.Get('{0}/{1}'.format(self.treedir, self.infoname))
                self.isdata = infotree.isdata
                tauDiscList = str(infotree.taudiscriminators)
                print str(tauDiscList)
#                self.tauDiscrims = tauDiscList.split()



#        for disc in self.tauDiscrims: print disc

        # initialize output file
        self.outfile = ROOT.TFile(self.output,'RECREATE')

        # initialize list of histograms as empty
        self.histograms = {}

        print 

    ## _______________________________________________________
    def analyze(self):
        '''
        The primary analysis loop.
        Iterate over each input file and row in trees.
        Calls the perEventAction method (which is overridden in the derived class).
        '''
        # Iterate over each input file
        for f,fname in enumerate(self.filenames):
            tfile = ROOT.TFile(fname)
            tree = tfile.Get('{0}/{1}'.format(self.treedir,self.treename))
            # Iterate over each event
            for row in tree:
                # Load collections
                #self.vertices  = [Vertex(row, i) for i in range(row.primvertex_count)]
                self.muons     = [Muon(row, i) for i in range(row.muon_count)]
                self.electrons = [Electron(row, i) for i in range(row.electron_count)]

                # Calls the perEventAction method (which is overridden in the derived class)
                self.perEventAction()

        self.endJob()
        self.write()


    ## _______________________________________________________
    def perEventAction(self):
        '''
        Action taken every event. Must be overriden.
        Each physics object is available via:
               self.muons
               self.electrons
               ...
        Call the fill method to store the event.
        '''

        self.fill()


    ## _______________________________________________________
    def fill(self):
        '''
        Determines the event weight and fills the histogram accordingly. (overridden in derived class)
        '''
        weight = 1.

    ## _______________________________________________________
    def endJob(self):
        ''' 
        Dummy function overridden in derived class
        '''
        pass

    ## _______________________________________________________
    def write(self):
        self.outfile.cd()
        for hist in self.histograms:
            self.histograms[hist].Write()

        self.outfile.Close()



## ___________________________________________________________
def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run analyzer')

    # line below is an example of a required argument
    parser.add_argument('inputFileList', type=str, help='List of input files (AC1B*.root)')
    # line below is an example of an optional argument
    parser.add_argument('--outputFileName', type=str, default='ana.out', help='Output file name')

    return parser.parse_args(argv)

## ___________________________________________________________
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = parse_command_line(argv)
    return args
