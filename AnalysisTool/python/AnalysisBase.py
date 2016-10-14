# AnalysisToolLight/AnalysisTool/python/AnalysisBase.py
import logging
import argparse
import glob
import os, sys, time
import ROOT
from array import array
from prettytable import PrettyTable
from Dataform import *
from ScaleFactors import *

## ___________________________________________________________
class AnalysisBase(object):
    '''
    You should derive your own class from AnalysisBase
    '''
    ## _______________________________________________________
    def __init__(self, args):
        # set up logging info
        logging.getLogger('Analysis')
        logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='[%(asctime)s]   %(message)s', datefmt='%Y-%m-%d %H:%M')
        logging.info('Beginning job...')

        # set defaults. These can be overridden with command line arguments (after adding to Base)
        # inputs
        self.filenames = []
        self.treedir  = 'makeroottree'
        self.infoname = 'AC1Binfo'
        self.luminame = 'AC1Blumi'
        self.treename = 'AC1B'
        input_file_list = args.input_file_list
        self.data_dir   = args.data_dir
        # outputs
        self.output = args.output_filename
        self.dimuon_tree_name = 'dimuon'

        # put file names into a list called self.filenames
        with open(input_file_list,'r') as f:
            for line in f.readlines():
                fname_ = line.strip()
                if fname_.startswith('#'): continue

                # personal storage options
                if fname_.startswith('T2_CH_CERN'): fname_ = 'root://eoscms.cern.ch/{0}'.format(fname_[10:])
                # use global redirector for UCSD until I learn the real one
                elif fname_.startswith('T2_US_UCSD'): fname_ = 'root://cms-xrd-global.cern.ch/{0}'.format(fname_[10:])

                self.filenames += [fname_]


        logging.info('Assembling job information...')
        # things we will check in the first file
        self.cmsswversion = ''
        self.isdata = None
        # open first file and load info tree
        tfile0 = ROOT.TFile.Open(self.filenames[0])
        infotree = tfile0.Get('{0}/{1}'.format(self.treedir, self.infoname))
        infotree.GetEntry(0)
        self.isdata = bool(infotree.isdata)
        self.ismc = not self.isdata
        self.cmsswversion = str(infotree.CMSSW_version)
        tfile0.Close('R')
        # get short CMSSW version that was used to produce these
        self.cmsswversion = ''.join(self.cmsswversion.split('_')[1:3] + ['X'])


        # set up lumi info and see how many events we have to process
        lumichain = ROOT.TChain('{0}/{1}'.format(self.treedir, self.luminame))
        self.numlumis   = 0
        self.sumweights = 0
        self.nevents    = 0
        for f, fname in enumerate(self.filenames):
            logging.info('Adding file {0}: {1}'.format(f+1, fname))
            lumichain.Add(fname)
        # iterate over lumis to find total number of events and summed event weights
        logging.info('Counting events and lumiblocks...')
        self.numlumis = lumichain.GetEntries()
        for entry in xrange(self.numlumis):
            lumichain.GetEntry(entry)
            self.nevents += lumichain.lumi_nevents
            self.sumweights += lumichain.lumi_sumweights

        logging.info('    Number of events found: {0} in {1} lumi sections in {2} files'.format(self.nevents, self.numlumis, len(self.filenames)))
        logging.info('Sample will be processed as {0}'.format('DATA' if self.isdata else 'MC'))




        # initialize map of histograms as empty
        self.histograms = {}
        self.extraHistogramMap = {}
        # initialise some other options that will be overridden in the derived class
        self.pathForTriggerScaleFactors = ''
        self.doPileupReweighting = False
        self.includeTriggerScaleFactors = False
        self.includeLeptonScaleFactors = False
        self.useRochesterCorrections = False
        # initialise cutflow object to None... why
        self.cutflow = None

        # initialize output file and create tree to save wum of weights
        self.outfile = ROOT.TFile(self.output,'RECREATE')


        # initialise dimuon mass tree we will use for limit calculations
        self.dimuon_mass_tree = ROOT.TTree(self.dimuon_tree_name, self.dimuon_tree_name)


    ## _______________________________________________________
    def analyze(self):
        '''
        The primary analysis loop.
        Iterate over each input file and row in trees.
        Calls the perEventAction method (which is overridden in the derived class).
        '''

        ##########################################################
        #                                                        #
        # load pileup info and other scale factors               #
        #                                                        #
        ##########################################################
        # pileup
        if self.doPileupReweighting:
            logging.info('Loading pileup info...')
            self.puweights = PileupWeights(self.cmsswversion, self.data_dir)

        # trigger scale factors
        if self.includeTriggerScaleFactors:
            logging.info('Loading trigger scale factor info...')
            self.hltweights = HLTScaleFactors(self.cmsswversion, self.data_dir, self.pathForTriggerScaleFactors)

        # lepton scale factors
        if self.includeLeptonScaleFactors:
            logging.info('Loading lepton scale factor info...')
            self.muonweights = MuonScaleFactors(self.cmsswversion, self.data_dir)

        self.eventsprocessed = 0
        # how often (in number of events) should we print out progress updates?
        updateevery = 1000

        ##########################################################
        #                                                        #
        # do the analysis loop                                   #
        #                                                        #
        ##########################################################
        # loop over each input file
        for f, fname in enumerate(self.filenames):
            logging.info('Processing file {0} of {1}:'.format(f+1, len(self.filenames)))
            # open the file and get the AC1B tree
            tfile = ROOT.TFile.Open(fname)
            tree = tfile.Get('{0}/{1}'.format(self.treedir,self.treename))

            # loop over each event (row)
            for row in tree:
                self.eventsprocessed += 1

                # progress updates
                if self.eventsprocessed==2:
                    starttime = time.time()
                elif self.eventsprocessed==updateevery:
                    logging.info('  Processing event {0}/{1} ({2:0.0f}%) [est. time remaining]'.format(self.eventsprocessed, self.nevents, (100.*self.eventsprocessed)/self.nevents))
                if self.eventsprocessed > updateevery and self.eventsprocessed % updateevery == 0:
                    currenttime = time.time()
                    timeelapsed = currenttime - starttime
                    timeleft = (float(self.nevents) - float(self.eventsprocessed)) * (float(timeelapsed) / float(self.eventsprocessed))
                    minutesleft, secondsleft = divmod(int(timeleft), 60)
                    hoursleft, minutesleft = divmod(minutesleft, 60)
                    logging.info('  Processing event {0}/{1} ({2:0.0f}%) [{3}:{4:02d}:{5:02d}]'.format(self.eventsprocessed, self.nevents, (100.*self.eventsprocessed)/self.nevents, hoursleft, minutesleft, secondsleft))
                if self.eventsprocessed > 50000: break


                # load required collections
                self.event     = Event(row, self.sumweights)
                self.vertices  = [Vertex(row, i) for i in range(row.primvertex_count)]
                self.muons     = [Muon(row, i, self.useRochesterCorrections) for i in range(row.muon_count)]
                # load optional collections
                self.electrons = [Electron(row, i) for i in range(row.electron_count)] if hasattr(row,'electron_count') else []
                self.photons   = [Photon(row, i) for i in range(row.photon_count)] if hasattr(row,'photon_count') else []
                self.taus      = [Tau(row, i) for i in range(row.tau_count)] if hasattr(row,'tau_count') else []
                self.jets      = [Jet(row, i) for i in range(row.ak4pfchsjet_count)] if hasattr(row,'ak4pfchsjet_count') else []
                self.met       = PFMETTYPE1(row, 0) if hasattr(row,'pfmettype1_count') else [] # MET is a vector of size 1

                # do the event analysis!
                # call the perEventAction method (which is overridden in the derived class)
                self.perEventAction()

        ##########################################################
        #                                                        #
        # end job (fill cutflow, write histograms in appropriate #
        #     directories, and write/close output file)          #
        #                                                        #
        ##########################################################
        self.endJob()


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
    def fillEfficiencies(self):
        '''
        At the end of the job, fill efficiencies histogram.
        '''
        # initialise cutflow histogram
        self.histograms['hEfficiencies'] = ROOT.TH1F('hEfficiencies', 'hEfficiencies', self.cutflow.numBins(), 0, self.cutflow.numBins())
        self.histograms['hEfficiencies'].GetXaxis().SetTitle('')
        self.histograms['hEfficiencies'].GetYaxis().SetTitle('Events')
        # fill histogram
        for i, name in enumerate(self.cutflow.getNames()):
            # 0 is the underflow bin in root: first bin to fill is bin 1
            self.histograms['hEfficiencies'].SetBinContent(i+1, self.cutflow.count(name))
            self.histograms['hEfficiencies'].GetXaxis().SetBinLabel(i+1, name)

        # print cutflow table
        efftable = PrettyTable(['Selection', 'Events', 'Eff.(Skim) [%]', 'Rel.Eff. [%]'])
        efftable.align = 'r'
        efftable.align['Selection'] = 'l'
        skimnevents = self.cutflow.count(self.cutflow.getNames()[0])

        for i, name in enumerate(self.cutflow.getNames()):
            efftable.add_row([self.cutflow.getPretty(name), format(self.cutflow.count(name), '0.0f'), self.cutflow.getSkimEff(i), self.cutflow.getRelEff(i)])

        logging.info('Cutflow summary:\n\n' + efftable.get_string() + '\n')



    ## _______________________________________________________
    def endOfJobAction(self):
        '''
        Dummy function for action taken at the end of the job. Can be overriden,
        but does not have to be.
        '''
        pass


    ## _______________________________________________________
    def write(self):
        '''
        Writes histograms to output file and closes it.
        '''
        # write histograms to output file
        self.outfile.cd()
        sumw_ = self.sumweights if self.sumweights != 0. else self.eventsprocessed

        #sumwts = array('f', [sumwts_])
        #testtree = ROOT.TTree('testtree', 'testtree')
        #testtree.Branch('sumw', sumwts, 'sumw/F')
        #testtree.Write()
        self.dimuon_mass_tree.Write()

        sumw = ROOT.TH1F('hSumWeights', 'hSumWeights', 3, 0, 3)
        sumw.SetBinContent(1, sumw_)
        sumw.Write()

        #for hist in self.histograms:
        for hist in sorted(self.histograms):
            self.histograms[hist].Write()

        # make a directory and go into it
        for dirname in self.extraHistogramMap.keys():
            tdir = self.outfile.mkdir(dirname)
            tdir.cd()
            # write the histograms
            # self.extraHistogramMap is a map of string:histogram map
            # self.extraHistogramMap[dirname] is a map in the same form as self.histograms
            for hist in self.extraHistogramMap[dirname]:
                # only write histograms that aren't empty
                if self.extraHistogramMap[dirname][hist].GetEntries():
                    self.extraHistogramMap[dirname][hist].Write()
            tdir.cd('../')

        self.dimuon_mass_tree.Write()

        logging.info('Output file {0} created.'.format(self.output))
        self.outfile.Close()

    ## _______________________________________________________
    def endJob(self):
        '''
        Finishes job:
            fillEfficiencies
            endOfJobAction
            write
        '''
        if self.cutflow: self.fillEfficiencies()
        self.endOfJobAction()
        self.write()
        logging.info('Job complete.')
        logging.info('NEVENTS:    {0}'.format(self.eventsprocessed))
        logging.info('SUMWEIGHTS: {0}'.format(self.sumweights))



## ___________________________________________________________
def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run analyzer')

    # line below is an example of a required argument
    parser.add_argument('input_file_list', type=str, help='List of input files (AC1B*.root)')
    parser.add_argument('output_filename', type=str, help='Output file name')
    parser.add_argument('data_dir', type=str, help='Data directory (usually AnalysisTool/data/)')
    # line below is an example of an optional argument
    #parser.add_argument('--output_filename', type=str, default='ana.out', help='Output file name')

    return parser.parse_args(argv)

## ___________________________________________________________
def main(argv=None):
    if argv is None:
        # sys.argv[0:] is the python script itself, sys.argv[1:] is the first argument
        argv = sys.argv[1:]
    args = parse_command_line(argv)
    return args
