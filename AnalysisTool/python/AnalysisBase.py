import logging
import argparse
import glob
import os
import sys
import ROOT
from prettytable import PrettyTable
from Dataform import *

## ___________________________________________________________
class AnalysisBase(object):
    '''
    You should derive your own class from AnalysisBase
    '''
    ## _______________________________________________________
    def __init__(self, args):
        # set up logging info
        logging.getLogger('Analysis')
        #logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s: %(message)s', datefmt='%H:%M:%S')
        logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='[%(asctime)s]   %(message)s', datefmt='%Y-%m-%d %H:%M')


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

        lumichain = ROOT.TChain('{0}/{1}'.format(self.treedir, self.luminame))

        self.sumweights = 0
        self.numlumis   = 0
        self.nevents    = 0
        # things we will check in the first file
        self.isdata = True
        # get the summed weights of processed entries (add up all lumi_sumweights in AC1Blumi)
        for f, fname in enumerate(self.filenames):
            tfile = ROOT.TFile(fname)
            logging.info('Adding file {0}: {1}'.format(f+1, fname))
            lumitree = tfile.Get('{0}/{1}'.format(self.treedir, self.luminame))
            infotree = tfile.Get('{0}/{1}'.format(self.treedir, self.infoname))
            self.isdata = infotree.isdata
            tfile.Close('R')
            lumichain.Add(fname)

        logging.info('Assembling lumi information...')
        # iterate over lumis to find total number of events
        self.numlumis = lumichain.GetEntries()
        for entry in xrange(self.numlumis):
            lumichain.GetEntry(entry)
            self.sumweights += lumichain.lumi_sumweights
            self.nevents    += lumichain.lumi_nevents


        logging.info('Number of events found: {0} in {1} lumi sections in {2} files'.format(self.nevents, self.numlumis, len(self.filenames)))
        logging.info('Sample will be processed as {0}'.format('DATA' if self.isdata else 'MC'))

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
        eventsprocessed = 0
        # Iterate over each input file
        for f, fname in enumerate(self.filenames):
            logging.info('Processing file {0} of {1}:'.format(f+1, len(self.filenames)))

            tfile = ROOT.TFile(fname)
            tree = tfile.Get('{0}/{1}'.format(self.treedir,self.treename))

            # Iterate over each event
            for row in tree:
                eventsprocessed += 1
                if eventsprocessed%1000==0: logging.info('  Processing event {0}/{1}'.format(eventsprocessed, self.nevents))
                # Load collections
                self.event     = Event(row)
                self.vertices  = [Vertex(row, i) for i in range(row.primvertex_count)]
                self.muons     = [Muon(row, i) for i in range(row.muon_count)]
                self.electrons = [Electron(row, i) for i in range(row.electron_count)]
                self.taus      = [Tau(row, i) for i in range(row.tau_count)]

                # Calls the perEventAction method (which is overridden in the derived class)
                self.perEventAction()

        self.endJob()
        self.write()


    ## _______________________________________________________
    def perEventAction(self):
        '''
        Dummy function for action taken every event. Must be overriden.
        Each physics object is available via:
               self.muons
               self.electrons
               etc.
        '''
        pass



    ## _______________________________________________________
    def endJob(self):
        '''
        At the end of the job, fill efficiencies histogram.
        '''
        # initialise cutflow histogram
        self.histograms['hEfficiencies'] = ROOT.TH1F('hEfficiencies', 'hEfficiencies', self.cutflow.numBins(), 0, self.cutflow.numBins())
        self.histograms['hEfficiencies'].GetXaxis().SetTitle('')
        self.histograms['hEfficiencies'].GetYaxis().SetTitle('')
        # fill histogram
        for i, name in enumerate(self.cutflow.getNames()):
            # 0 is the underflow bin in root: first bin to fill is bin 1
            self.histograms['hEfficiencies'].SetBinContent(i+1, self.cutflow.count(name))
            self.histograms['hEfficiencies'].GetXaxis().SetBinLabel(i+1, name)

        # print cutflow table
        logging.info('Job complete.')
        logging.info('NEVENTS: {0}'.format(self.nevents))
        logging.info('SUMWEIGHTS: {0}'.format(self.sumweights))

        efftable = PrettyTable(['Selection', 'Events', 'Eff.(Skim) [%]', 'Rel.Eff. [%]'])
        efftable.align['Selection'] = 'l'
        efftable.align['Events'] = 'r'
        efftable.align['Eff.(Skim) [%]'] = 'r'
        efftable.align['Rel.Eff. [%]'] = 'r'
        skimnevents = self.cutflow.count(self.cutflow.getNames()[0])

        for i, name in enumerate(self.cutflow.getNames()):
            efftable.add_row([self.cutflow.getPretty(name), format(self.cutflow.count(name), '0.0f'), self.cutflow.getSkimEff(i), self.cutflow.getRelEff(i)])


         
        logging.info('Cutflow summary:\n\n' + efftable.get_string() + '\n')




    ## _______________________________________________________
    def write(self):
        '''
        Writes the histograms to the output file and saves it.
        '''
        self.outfile.cd()
        for hist in self.histograms:
            self.histograms[hist].Write()
        logging.info('Output file ' + self.output + ' created.')
        self.outfile.Close()


## ___________________________________________________________
def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run analyzer')

    # line below is an example of a required argument
    parser.add_argument('inputFileList', type=str, help='List of input files (AC1B*.root)')
    parser.add_argument('outputFileName', type=str, help='Output file name')
    # line below is an example of an optional argument
    #parser.add_argument('--outputFileName', type=str, default='ana.out', help='Output file name')

    return parser.parse_args(argv)

## ___________________________________________________________
def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    args = parse_command_line(argv)
    return args
