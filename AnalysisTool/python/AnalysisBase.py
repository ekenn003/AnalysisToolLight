import logging
import argparse
import glob
import os, sys, time
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
        self.treedir  = 'makeroottree'
        self.infoname = 'AC1Binfo'
        self.luminame = 'AC1Blumi'
        self.treename = 'AC1B'
        self.output = args.outputFileName
        inputFileList = args.inputFileList
        self.pileupDir = args.pileupDir


        # put file names into a list called self.filenames
        with open(inputFileList,'r') as f:
            for line in f.readlines():
                # glob.glob returns the list of files with their full path
                self.filenames += glob.glob(line.strip())


        logging.info('Assembling job information...')
        # things we will check in the first file
        self.cmsswversion = ''
        self.isdata = None

        # set up lumi info and see how many events we have to process
        lumichain = ROOT.TChain('{0}/{1}'.format(self.treedir, self.luminame))
        self.numlumis   = 0
        self.sumweights = 0
        self.nevents    = 0
        for f, fname in enumerate(self.filenames):
            tfile = ROOT.TFile(self.filenames[f])
            infotree = tfile.Get('{0}/{1}'.format(self.treedir, self.infoname))
            infotree.GetEntry(0)
            self.isdata = bool(infotree.isdata)
            self.cmsswversion = str(infotree.CMSSW_version)
            tfile.Close('R')
            logging.info('Adding file {0}: {1}'.format(f+1, fname))
            lumichain.Add(fname)
        # iterate over lumis to find total number of events and summed event weights
        logging.info('Counting events and lumiblocks...')
        self.numlumis = lumichain.GetEntries()
        for entry in xrange(self.numlumis):
            lumichain.GetEntry(entry)
            self.nevents += lumichain.lumi_nevents
            self.sumweights += lumichain.lumi_sumweights


        logging.info('Number of events found: {0} in {1} lumi sections in {2} files'.format(self.nevents, self.numlumis, len(self.filenames)))
        logging.info('Sample will be processed as {0}'.format('DATA' if self.isdata else 'MC'))




        # initialize map of histograms as empty
        self.histograms = {}

        # initialize output file
        self.outfile = ROOT.TFile(self.output,'RECREATE')


    ## _______________________________________________________
    def analyze(self):
        '''
        The primary analysis loop.
        Iterate over each input file and row in trees.
        Calls the perEventAction method (which is overridden in the derived class).
        '''


        # load pileup info and other scale factors
        logging.info('Loading pileup info...')

        # set up pileup reweighting
        self.pileupScale = []
        self.pileupScale_up = []
        self.pileupScale_down = []

        logging.info('version = "{0}"'.format(self.cmsswversion))
        # get short CMSSW version that was used to produce these
        version = '{0}{1}X'.format(self.cmsswversion.split('_')[1], self.cmsswversion.split('_')[2])

	# now we look for a file called pileup_76X.root or pileup_80X.root in the pileupDir
        pufile = ROOT.TFile('{0}/pileup_{1}.root'.format(self.pileupDir, version))
        logging.info('  Looking for pileup file at {0}/pileup_{1}.root'.format(self.pileupDir, version))

        # save scale factors in vectors where each index corresponds to the NumTruePileupInteractions
        scalehist_ = pufile.Get('pileup_scale')
        for b in range(scalehist_.GetNbinsX()):
            # set (b)th entry in self.pileupScale to bin content of (b+1)th bin
            # (0th bin is underflow)
            self.pileupScale.append(scalehist_.GetBinContent(b+1))
        scalehist_ = pufile.Get('pileup_scale_up')
        for b in range(scalehist_.GetNbinsX()):
            self.pileupScale_up.append(scalehist_.GetBinContent(b+1))
        scalehist_ = pufile.Get('pileup_scale_down')
        for b in range(scalehist_.GetNbinsX()):
            self.pileupScale_down.append(scalehist_.GetBinContent(b+1))
        pufile.Close()

        eventsprocessed = 0
        # how often (in number of events) should we print out progress updates?
        # this can't be 1!
        updateevery = 1000

        # loop over each input file
        for f, fname in enumerate(self.filenames):
            logging.info('Processing file {0} of {1}:'.format(f+1, len(self.filenames)))
            # open the file and get the AC1B tree
            tfile = ROOT.TFile(fname)
            tree = tfile.Get('{0}/{1}'.format(self.treedir,self.treename))

            # loop over each event (row)
            for row in tree:
                eventsprocessed += 1

                # progress updates
                if eventsprocessed==2:
                    starttime = time.time()
                elif eventsprocessed==updateevery:
                    logging.info('  Processing event {0}/{1} ({2:0.0f}%) [est. time remaining]'.format(eventsprocessed, self.nevents, (100.*eventsprocessed)/self.nevents))
                if eventsprocessed > updateevery and eventsprocessed % updateevery == 0:
                    currenttime = time.time()
                    timeelapsed = currenttime - starttime
                    timeleft = (float(self.nevents) - float(eventsprocessed)) * (float(timeelapsed) / float(eventsprocessed))
                    minutesleft, secondsleft = divmod(int(timeleft), 60)
                    hoursleft, minutesleft = divmod(minutesleft, 60)
                    logging.info('  Processing event {0}/{1} ({2:0.0f}%) [{3}:{4:02d}:{5:02d}]'.format(eventsprocessed, self.nevents, (100.*eventsprocessed)/self.nevents, hoursleft, minutesleft, secondsleft))


                # load collections
                self.event     = Event(row, self.sumweights)
                self.vertices  = [Vertex(row, i) for i in range(row.primvertex_count)]
                self.muons     = [Muon(row, i) for i in range(row.muon_count)]
                self.electrons = [Electron(row, i) for i in range(row.electron_count)]
                self.photons   = [Photon(row, i) for i in range(row.photon_count)]
                self.taus      = [Tau(row, i) for i in range(row.tau_count)]
                self.jets      = [Jet(row, i) for i in range(row.ak4pfchsjet_count)]
                self.met       = PFMETTYPE1(row, 0) # MET is a vector of size 1

                # do the event analysis!
                # call the perEventAction method (which is overridden in the derived class)
                self.perEventAction()

        # end job and write histograms to output file
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
    def endJob(self):
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
        logging.info('Job complete.')
        logging.info('NEVENTS:    {0}'.format(self.nevents))
        logging.info('SUMWEIGHTS: {0}'.format(self.sumweights))

        efftable = PrettyTable(['Selection', 'Events', 'Eff.(Skim) [%]', 'Rel.Eff. [%]'])
        efftable.align = 'r'
        efftable.align['Selection'] = 'l'
        skimnevents = self.cutflow.count(self.cutflow.getNames()[0])

        for i, name in enumerate(self.cutflow.getNames()):
            efftable.add_row([self.cutflow.getPretty(name), format(self.cutflow.count(name), '0.0f'), self.cutflow.getSkimEff(i), self.cutflow.getRelEff(i)])

        logging.info('Cutflow summary:\n\n' + efftable.get_string() + '\n')


        # write histograms to output file
        self.outfile.cd()
        for hist in self.histograms:
            self.histograms[hist].Write()
        logging.info('Output file {0} created.'.format(self.output))
        self.outfile.Close()

    ## _______________________________________________________
    def GetPileupWeight(self, numtrueinteractions):
        return self.pileupScale[int(round(numtrueinteractions))] if len(self.pileupScale) > numtrueinteractions else 0.




## ___________________________________________________________
def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run analyzer')

    # line below is an example of a required argument
    parser.add_argument('inputFileList', type=str, help='List of input files (AC1B*.root)')
    parser.add_argument('outputFileName', type=str, help='Output file name')
    parser.add_argument('pileupDir', type=str, help='Pileup files directory (usually AnalysisTool/data/pileup)')
    # line below is an example of an optional argument
    #parser.add_argument('--outputFileName', type=str, default='ana.out', help='Output file name')

    return parser.parse_args(argv)

## ___________________________________________________________
def main(argv=None):
    if argv is None:
        # sys.argv[0:] is the python script itself, sys.argv[1:] is the first argument
        argv = sys.argv[1:]
    args = parse_command_line(argv)
    return args
