import logging
import argparse
import glob
import os
import sys
import ROOT
from Candidates import Muon, Electron

## ___________________________________________________________
class AnalysisBase(object):
    '''
    You should derive your own class from AnalysisBase
    '''
    ## _______________________________________________________
    def __init__(self, **kwargs):
        # set defaults. These can be overridden with command line arguments
        self.filenames = kwargs.pop('filenames', [])
        self.treedir   = kwargs.pop('treedir', 'makeroottree')
        self.treename  = kwargs.pop('treename', 'AC1B')
        self.luminame  = kwargs.pop('luminame', 'AC1Blumi')
        self.output    = kwargs.pop('output', 'ana.root')

        inputFileList = kwargs.pop('inputFileList', '')
        with open(inputFileList,'r') as f:
            for line in f.readlines():
                self.filenames += glob.glob(line.strip())

        # get the summed weights of processed entries (add up all lumi_sumweights in AC1Blumi)
        self.sumweight = 0
        for f, fname in enumerate(self.filenames):
            tfile = ROOT.TFile(fname)
            print 'Adding file(s) ' + fname
            tree = tfile.Get('{0}/{1}'.format(self.treedir, self.luminame))
            self.sumweight += tree.lumi_sumweights

        # initialize output file
        self.outfile = ROOT.TFile(self.output,'RECREATE')

        # initialize list of histograms as empty
        self.histograms = {}

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
                self.muons = [Muon(row,i) for i in range(row.muon_count)]
                self.electrons = [Electron(row,i) for i in range(row.electron_count)]
                # Calls the perEventAction method (overridden in the derived class)
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
    # line below is an example of an optional argument
    parser.add_argument('--outputFileName', type=str, default='ana.out', help='Output file name')
    # line below is an example of a required argument
    parser.add_argument('inputFileList', type=str, help='List of input files (AC1B*.root)')
    return parser.parse_args(argv)

## ___________________________________________________________
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = parse_command_line(argv)
    return args
