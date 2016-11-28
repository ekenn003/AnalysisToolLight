# AnalysisToolLight/AnalysisTool/python/AnalysisBase.py
import logging
import argparse
import re
import os, sys, time
from ROOT import TTree, TFile, TChain, TH1F
#import ROOT
from array import array
from Dataform import *
from ScaleFactors import *
from xsec import xsecs
from histograms import *
from Preselection import *
from prettytable import PrettyTable

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
        self.max_events = args.nevents
        self.data_dir   = '{0}/src/AnalysisToolLight/AnalysisTool/data'.format(os.environ['CMSSW_BASE'])
        # outputs
        self.output = args.output_filename

        # put file names into a list called self.filenames
        with open(input_file_list,'r') as f:
            for line in f.readlines():
                fname_ = line.strip()
                if fname_.startswith('#'): continue
                if not fname_: continue

                # personal storage options
                if fname_.startswith('T2_CH_CERN'):   fname_ = 'root://eoscms.cern.ch/{0}'.format(fname_[10:])
                elif fname_.startswith('T2_US_UCSD'): fname_ = 'root://xrootd.t2.ucsd.edu/{0}'.format(fname_[10:])
                #elif fname_.startswith('T2_US_UCSD'): fname_ = 'root://cms-xrd-global.cern.ch/{0}'.format(fname_[10:])

                self.filenames += [fname_]


        logging.info('Assembling job information...')
        # things we will check in the first file
        self.cmsswversion = ''
        self.dataset_source = ''
        self.isdata = None
        # open first file and load info tree
        tfile0 = TFile.Open(self.filenames[0])
        infotree = tfile0.Get('{0}/{1}'.format(self.treedir, self.infoname))
        infotree.GetEntry(0)
        self.isdata = bool(infotree.isdata)
        self.ismc = not self.isdata
        self.cmsswversion = str(infotree.CMSSW_version)
        # strip " and / from parent dataset name
        self.dataset_source = ''.join( c for c in str(infotree.source_dataset) if c not in '"/')

        tfile0.Close('R')

        # get short CMSSW version that was used to produce these
        self.cmsswversion = ''.join(self.cmsswversion.split('_')[1:3] + ['X'])
        # get dataset cross section
        try:
            self.nom_xsec = xsecs[self.dataset_source]
        except:
            logging.info('       *   ')
            logging.info('    *******')
            logging.info('    No cross section information found for source "{0}".'.format(self.dataset_source))
            logging.info('    *******')
            logging.info('       *   ')
            self.nom_xsec = -1.

        # set up lumi info and see how many events we have to process
        infochain = TChain('{0}/{1}'.format(self.treedir, self.infoname))
        self.nevents_to_process  = 0
        # find original sum weights
        lumichain = TChain('{0}/{1}'.format(self.treedir, self.luminame))
        self.numlumis   = 0
        self.sumweights = 0
        self.nevents    = 0
        for f, fname in enumerate(self.filenames):
            logging.info('Adding file {0}: {1}'.format(f+1, fname))
            lumichain.Add(fname)
            infochain.Add(fname)
        # iterate over lumis to find total number of events and summed event weights
        logging.info('')
        logging.info('Counting events and lumiblocks...')
        self.numlumis = lumichain.GetEntries()
        self.numinfos = infochain.GetEntries()
        for entry in xrange(self.numlumis):
            lumichain.GetEntry(entry)
            self.nevents += lumichain.lumi_nevents
            self.sumweights += lumichain.lumi_sumweights
        for entry in xrange(self.numinfos):
            infochain.GetEntry(entry)
            self.nevents_to_process += infochain.nevents_filled

        logging.info('    Number of events found: {0} in {1} lumi sections in {2} files'.format(self.nevents_to_process, self.numlumis, len(self.filenames)))
        logging.info('Sample will be processed as {0}'.format('DATA' if self.isdata else 'MC'))
        if self.ismc:
            logging.info('Sample has been identified as coming from {0} with a nominal cross section of {1} pb.'.format(self.dataset_source, self.nom_xsec))
        else:
            logging.info('Sample has been identified as coming from {0}'.format(self.dataset_source))




        # initialize map of histograms as empty
        self.histograms = histograms
        self.extraHistogramMap = {}

        # initialise list of category trees
        self.category_trees = []
        # initialise some other options that will be overridden in the derived class
        self.pathForTriggerScaleFactors = ''
        self.doPileupReweighting = False
        self.includeTriggerScaleFactors = False
        self.includeLeptonScaleFactors = False
        self.useRochesterCorrections = False

        # summary tree
        self.summary_tree = TTree('Summary', 'Summary')
        # branches of summary tree
        # python array: 'L' = unsigned long, 'l' = signed long, 'f' = float
        # TBranch: 'l' = unsigned long, 'L' = signed long, 'F' = float
        self.nevents_a    = array('L', [self.nevents])
        self.summary_tree.Branch('tNumEvts', self.nevents_a, 'tNumEvts/l')
        self.sumweights_a = array('f', [self.sumweights if self.sumweights != 0. else self.nevents])
        self.summary_tree.Branch('tSumWts', self.sumweights_a, 'tSumWts/F')
        self.nom_xsec_a   = array('f', [self.nom_xsec])
        self.summary_tree.Branch('tCrossSec', self.nom_xsec_a, 'tCrossSec/F')

        self.summary_tree.Fill()


        # initialize output file`
        self.outfile = TFile(self.output,'RECREATE')

        ##########################################################
        #                                                        #
        # Initialize event counters                              #
        #                                                        #
        ##########################################################
        self.cutflow = initialize_cutflow(self)


    ## _______________________________________________________
    def analyze(self):
        '''
        The primary analysis loop.
        Iterate over each input file and row in trees.
        Calls the per_event_action method (which is overridden in the derived class).
        '''

        

        ##########################################################
        #                                                        #
        # load pileup info and other scale factors               #
        #                                                        #
        ##########################################################
        # pileup
        if self.doPileupReweighting:
            logging.info('')
            logging.info('Loading pileup info...')
            self.puweights = PileupWeights(self.cmsswversion, self.data_dir)

        # trigger scale factors
        if self.includeTriggerScaleFactors:
            logging.info('')
            logging.info('Loading trigger scale factor info...')
            self.hltweights = HLTScaleFactors(self.cmsswversion, self.data_dir, self.pathForTriggerScaleFactors)

        # lepton scale factors
        if self.includeLeptonScaleFactors:
            logging.info('')
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
            logging.info('')
            logging.info('Processing file {0} of {1}:'.format(f+1, len(self.filenames)))
            # open the file and get the AC1B tree
            tfile = TFile.Open(fname)
            tree = tfile.Get('{0}/{1}'.format(self.treedir,self.treename))

            # loop over each event (row)
            for row in tree:
                self.eventsprocessed += 1

                # progress updates
                if self.eventsprocessed==2:
                    starttime = time.time()
                elif self.eventsprocessed==updateevery:
                    logging.info(
                        '  Processing event {0}/{1} ({2:0.0f}%) [est. time remaining]'.format(
                            self.eventsprocessed,
                            self.nevents_to_process,
                            (100.*self.eventsprocessed)/self.nevents_to_process
                        )
                    )
                if self.eventsprocessed > updateevery and self.eventsprocessed % updateevery == 0:
                    currenttime = time.time()
                    timeelapsed = currenttime - starttime
                    timeleft = (float(self.nevents_to_process) - float(self.eventsprocessed)) * (float(timeelapsed) / float(self.eventsprocessed))
                    minutesleft, secondsleft = divmod(int(timeleft), 60)
                    hoursleft, minutesleft = divmod(minutesleft, 60)
                    logging.info(
                        '  Processing event {0}/{1} ({2:0.0f}%) [{3}:{4:02d}:{5:02d}]'.format(
                            self.eventsprocessed,
                            self.nevents_to_process,
                            (100.*self.eventsprocessed)/self.nevents_to_process,
                            hoursleft,
                            minutesleft,
                            secondsleft
                        )
                    )


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

                # set up containers for good objects
                self.good_vertices  = []
                self.good_muons     = []
                self.good_electrons = []
                self.good_jets      = []
                self.good_bjets     = []

                self.dimuon_pairs     = []
                self.dielectron_pairs = []
                self.dijet_pairs      = []

                # do the event analysis!
                # call the per_event_action method (which is overridden in the derived class)
                self.cutflow.increment('nEv_Skim')
                passes_event_selection = check_event_selection(self)
                if not passes_event_selection: continue
                passes_preselection = check_preselection(self)
                if not passes_preselection: continue

                self.per_event_action()

                # debug
                if (self.max_events is not -1) and (self.eventsprocessed >= self.max_events): break

        ##########################################################
        #                                                        #
        # end job (fill cutflow, write histograms in appropriate #
        #     directories, and write/close output file)          #
        #                                                        #
        ##########################################################
        self.end_job()


    ## _______________________________________________________
    def per_event_action(self):
        '''
        Dummy function for action taken every event. Must be overriden.
        Each physics object is available via:
            self.muons
            self.electrons
            etc.
        '''
        pass


    ## _______________________________________________________
    def fill_efficiencies(self):
        '''
        At the end of the job, fill efficiencies histogram.
        '''
        # initialise cutflow histogram
        self.histograms['hEfficiencies'] = TH1F('hEfficiencies', 'hEfficiencies', self.cutflow.num_bins(), 0, self.cutflow.num_bins())
        self.histograms['hEfficiencies'].GetXaxis().SetTitle('')
        self.histograms['hEfficiencies'].GetYaxis().SetTitle('Events')
        # fill histogram
        for i, name in enumerate(self.cutflow.get_names()):
            # 0 is the underflow bin in root: first bin to fill is bin 1
            self.histograms['hEfficiencies'].SetBinContent(i+1, self.cutflow.count(name))
            self.histograms['hEfficiencies'].GetXaxis().SetBinLabel(i+1, name)

        # print cutflow table
        efftable = PrettyTable(['Selection', 'Events', 'Eff.(Orig) [%]', 'Rel.Eff. [%]'])
        efftable.align = 'r'
        efftable.align['Selection'] = 'l'
        skimnevents = self.cutflow.count(self.cutflow.get_names()[0])

        for i, name in enumerate(self.cutflow.get_names()):
            efftable.add_row([self.cutflow.get_pretty(name), format(self.cutflow.count(name), '0.0f'), self.cutflow.get_eff(i), self.cutflow.get_rel_eff(i)])

        logging.info('')
        logging.info('Cutflow summary:\n\n' + efftable.get_string() + '\n')



    ## _______________________________________________________
    def end_of_job_action(self):
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
        sumw_ = self.sumweights if self.sumweights != 0. else self.nevents

        self.summary_tree.Write()

        for tree in self.category_trees:
            tree.Write()

        sumw = TH1F('hSumWeights', 'hSumWeights', 3, 0, 3)
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
                if self.extraHistogramMap[dirname][hist].GetEntries() or dirname=='categories':
                    self.extraHistogramMap[dirname][hist].Write()
            tdir.cd('../')


	logging.info('')
	logging.info('Created the following file:')
        logging.info('    {0}'.format(self.output))
        self.outfile.Close()

    ## _______________________________________________________
    def end_job(self):
        '''
        Finishes job:
            fill_efficiencies
            end_of_job_action
            write
        '''
        self.fill_efficiencies()
        self.end_of_job_action()
        self.write()
        logging.info('')
        logging.info('Job complete.')
        logging.info(
            '    NEVENTS processed: {0}/{1} ({2}%)'.format(
                self.eventsprocessed,
                self.nevents_to_process,
                (100*self.eventsprocessed)/self.nevents_to_process
            )
        )
        logging.info('Sample information:')
        logging.info('    DATASET  : {0}'.format(self.dataset_source))
        if self.ismc:
            logging.info('    NOM XSEC : {0} pb'.format(self.nom_xsec if self.nom_xsec != -1. else '--'))
        logging.info('    NEVENTS (skim) : {0}'.format(self.nevents_to_process))
        logging.info('    NEVENTS (orig) : {0}'.format(self.nevents))
        logging.info('    SUMWEIGHTS     : {0}'.format(self.sumweights))


    ## _______________________________________________________
    def calculate_event_weight(self):
        ##########################################################
        # Include pileup reweighting                             #
        ##########################################################
        eventweight = 1.

        if not self.isdata:
            eventweight = self.event.GenWeight()
            if self.doPileupReweighting:
                eventweight *= self.puweights.getWeight(self.event.NumTruePileUpInteractions())


        ##########################################################
        # Update event weight (MC only)                          #
        ##########################################################
        if not self.isdata:
            if self.includeTriggerScaleFactors:
                eventweight *= self.hltweights.getScale(self.good_muons)
            #else: eventweight *= 0.93
            if self.includeLeptonScaleFactors:
                eventweight *= self.muonweights.getIdScale(self.good_muons, self.cuts['cMuID'])
                # NB: the below only works for PF w/dB isolation
                eventweight *= self.muonweights.getIsoScale(self.good_muons, self.cuts['cMuID'], self.cuts['cMuIso'])

        return eventweight



## ___________________________________________________________
def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run analyzer')

    # line below is an example of a required argument
    parser.add_argument('-i', '--input_file_list', type=str, help='List of input files (AC1B*.root)')
    parser.add_argument('-o', '--output_filename', type=str, help='Output file name')
    #parser.add_argument('data_dir', type=str, help='Data directory (usually AnalysisTool/data/)')
    # line below is an example of an optional argument
    parser.add_argument('-n', '--nevents', type=int, default=-1, help='Max number of events to process (should be only used for debugging; results in incorrect sumweights)')

    return parser.parse_args(argv)

## ___________________________________________________________
def main(argv=None):
    if argv is None:
        # sys.argv[0:] is the python script itself, sys.argv[1:] is the first argument
        argv = sys.argv[1:]
    args = parse_command_line(argv)
    return args

