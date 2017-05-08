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
from collections import namedtuple

## _____________________________________________________________________________
EventWeight = namedtuple('EventWeight', 
    'full base_event_weight pileup_factor trigger_factor lepton_factor')

## _____________________________________________________________________________
class AnalysisBase(object):
    '''
    You should derive your own class from AnalysisBase
    '''
    ## _________________________________________________________________________
    def __init__(self, args):
        # set up logging info
        logging.getLogger('Analysis')
        logging.basicConfig(level=logging.INFO, stream=sys.stderr,
            format='[%(asctime)s]   %(message)s', datefmt='%Y-%m-%d %H:%M')
        logging.info('Beginning job...')

        # set defaults. These can be overridden with command line arguments
        # inputs
        self.filenames = []
        self.treedir  = 'makeroottree'
        self.infoname = 'AC1Binfo'
        self.luminame = 'AC1Blumi'
        self.treename = 'AC1B'
        input_file_list = args.input_file_list
        self.max_events = args.nevents
        self.skip_events = args.skipevents
        self.whichfile = args.whichfile
        self.data_dir   = ('{0}/src/AnalysisToolLight/AnalysisTool'
            '/data'.format(os.environ['CMSSW_BASE']))
        # outputs
        self.output = args.output_filename

        # put file names into a list called self.filenames
        with open(input_file_list,'r') as f:
            for line in f.readlines():
                fname_ = line.strip()
                if fname_.startswith('#'): continue
                if not fname_: continue

                # personal storage options
                if fname_.startswith('T2_CH_CERN'):
                    fname_ = 'root://eoscms.cern.ch/{0}'.format(fname_[10:])
                elif fname_.startswith('T2_US_UCSD'):
                    fname_ = 'root://xrootd.t2.ucsd.edu/{0}'.format(fname_[10:])

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
        self.dataset_source = ''.join(c for c in str(infotree.source_dataset)
            if c not in '"/')

        tfile0.Close('R')

        # get short CMSSW version that was used to produce these
        self.cmsswversion = ''.join(self.cmsswversion.split('_')[1:3] + ['X'])
        # get dataset cross section
        try:
            self.nom_xsec = xsecs[self.dataset_source]
        except:
            logging.info('       *   ')
            logging.info('    *******')
            logging.info('    No cross section information found for source:')
            logging.info('        "{0}".'.format(self.dataset_source))
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
        # iterate over lumis to find total number of events
        #     and summed event weights
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

        logging.info(('    Number of events found: {0} in {1} lumi sections '
            'in {2} files').format(self.nevents_to_process, self.numlumis, 
            len(self.filenames)))
        logging.info('Sample will be processed as '
            '{0}'.format('DATA' if self.isdata else 'MC'))
        logging.info('Sample has been identified as coming from:')
        logging.info('    {0}'.format(self.dataset_source))
        if self.ismc:
            logging.info('  with a nominal cross section of:')
            logging.info('    {0} pb.'.format(self.nom_xsec))




        # initialize map of histograms as empty
        self.histograms = histograms
        self.extra_histogram_map = {}

        # initialise list of category trees
        self.category_trees = []
        # initialise some other options that will be overridden
        #     in the derived class
        self.path_for_trigger_scale_factors = ''
        self.do_pileup_reweighting         = False
        self.include_trigger_scale_factors = False
        self.include_lepton_scale_factors  = False
        self.use_rochester_corrections     = False

        # summary tree
        self.summary_tree = TTree('Summary', 'Summary')
        # branches of summary tree
        # python array: 'L' = unsigned long, 'l' = signed long, 'f' = float
        # TBranch: 'l' = unsigned long, 'L' = signed long, 'F' = float
        self.nevents_a    = array('L', [self.nevents])
        self.summary_tree.Branch('tNumEvts', self.nevents_a, 'tNumEvts/l')
        self.sumweights_a = array('f', 
            [self.sumweights if self.sumweights != 0. else self.nevents])
        self.summary_tree.Branch('tSumWts', self.sumweights_a, 'tSumWts/F')
        self.nom_xsec_a   = array('f', [self.nom_xsec])
        self.summary_tree.Branch('tCrossSec', self.nom_xsec_a, 'tCrossSec/F')

        self.summary_tree.Fill()


        # initialize output file
        self.outfile = TFile(self.output,'RECREATE')

        # initialize event counters
        self.cutflow = initialize_cutflow(self)


    ## _________________________________________________________________________
    def analyze(self):
        '''
        The primary analysis loop.
        Iterate over each input file and row in trees.
        Calls the per_event_action method (which is overridden
        in the derived class).
        '''

        ##########################################################
        #                                                        #
        # load pileup info and other scale factors               #
        #                                                        #
        ##########################################################
        if self.ismc:
            # pileup
            if self.do_pileup_reweighting:
                logging.info('')
                logging.info('Loading pileup info...')
                self.puweights = PileupWeights(self.cmsswversion, self.data_dir)

            # trigger scale factors
            if self.include_trigger_scale_factors:
                logging.info('')
                logging.info('Loading trigger scale factor info...')
                self.hltweights = HLTScaleFactors(self.cmsswversion,
                    self.data_dir, self.path_for_trigger_scale_factors)

            # lepton scale factors
            if self.include_lepton_scale_factors:
                logging.info('')
                logging.info('Loading lepton scale factor info...')
                self.muonweights = MuonScaleFactors(self.cmsswversion,
                    self.data_dir)

        ##########################################################
        #                                                        #
        # get ready...                                           #
        #                                                        #
        ##########################################################
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

            if self.whichfile != -1 and f+1 != self.whichfile: continue

            logging.info('')
            logging.info('Processing file {0} of {1}:'.format(f+1,
                len(self.filenames)))
            # open the file and get the AC1B tree
            tfile = TFile.Open(fname)
            tree = tfile.Get('{0}/{1}'.format(self.treedir, self.treename))

            # loop over each event (row)
            for row in tree:
                # debug
                if (self.skip_events != -1
                    and self.eventsprocessed < self.skip_events):
                    continue
                if (self.max_events is not -1
                    and self.eventsprocessed >= self.max_events):
                    break

                self.eventsprocessed += 1

                # progress updates
                if self.eventsprocessed == 2:
                    starttime = time.time()
                elif self.eventsprocessed == updateevery:
                    logging.info('  Processing event '
                        '{0}/{1} ({2:0.0f}%) '.format(
                            self.eventsprocessed,
                            self.nevents_to_process,
                            (100.*self.eventsprocessed)/self.nevents_to_process)
                    )
                if (self.eventsprocessed > updateevery
                    and self.eventsprocessed % updateevery == 0):
                    currenttime = time.time()
                    timeelapsed = currenttime - starttime
                    timeleft = ((float(self.nevents_to_process)
                        - float(self.eventsprocessed)) * (float(timeelapsed)
                        / float(self.eventsprocessed)))
                    minutesleft, secondsleft = divmod(int(timeleft), 60)
                    hoursleft, minutesleft = divmod(minutesleft, 60)
                    logging.info('  Processing event '
                        '{0}/{1} ({2:0.0f}%) [{3}:{4:02d}:{5:02d}]'.format(
                            self.eventsprocessed,
                            self.nevents_to_process,
                            (100.*self.eventsprocessed)/self.nevents_to_process,
                            hoursleft,
                            minutesleft,
                            secondsleft)
                    )


                # load required collections
                self.event     = Event(row, self.sumweights)
                self.vertices  = ([Vertex(row, i)
                    for i in range(row.primvertex_count)])
                self.muons     = ([Muon(row, i, self.use_rochester_corrections)
                    for i in range(row.muon_count)]
                    if hasattr(row,'muon_count') else [])
                if self.use_rochester_corrections:
                    self.muons.sort(key=lambda m: m.pt_roch(), reverse=True)
                self.electrons = ([Electron(row, i)
                    for i in range(row.electron_count)]
                    if hasattr(row,'electron_count') else [])
                # load optional collections
                self.photons   = ([Photon(row, i)
                    for i in range(row.photon_count)]
                    if hasattr(row,'photon_count') else [])
                self.taus      = ([Tau(row, i)
                    for i in range(row.tau_count)]
                    if hasattr(row,'tau_count') else [])
                self.jets      = ([Jet(row, i)
                    for i in range(row.ak4pfchsjet_count)]
                    if hasattr(row,'ak4pfchsjet_count') else [])
                # MET is a vector of size 1
                self.met       = (PFMETTYPE1(row, 0)
                    if hasattr(row,'pfmettype1_count') else [])

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

                self.cutflow.increment('nEv_Skim')

                # check basic event selection
                passes_event_selection = check_event_selection(self)
                if not passes_event_selection: continue

                # check all-category preselection
                passes_preselection = check_preselection(self)
                if not passes_preselection: pass
             #   if not passes_preselection: continue

                # call the per_event_action method
                #     (which is overridden in the derived class)
                self.per_event_action()

            if (self.max_events is not -1
                and self.eventsprocessed >= self.max_events):
                break



        ##########################################################
        #                                                        #
        # end job (fill cutflow, write histograms in appropriate #
        #     directories, and write/close output file)          #
        #                                                        #
        ##########################################################
        self.end_job()


    ## _________________________________________________________________________
    def per_event_action(self):
        '''
        Dummy function for action taken every event. Must be overriden.
        Each physics object is available via:
            self.muons
            self.electrons
            etc.
        '''
        pass


    ## _________________________________________________________________________
    def fill_efficiencies(self):
        '''
        At the end of the job, fill efficiencies histogram.
        '''
        # initialise cutflow histogram
        self.histograms['hEfficiencies'] = TH1F('hEfficiencies',
            'hEfficiencies', self.cutflow.num_bins(), 0,
            self.cutflow.num_bins())
        self.histograms['hEfficiencies'].GetXaxis().SetTitle('')
        self.histograms['hEfficiencies'].GetYaxis().SetTitle('Events')
        # fill histogram
        for i, name in enumerate(self.cutflow.get_names()):
            # 0 is the underflow bin in root: first bin to fill is bin 1
            self.histograms['hEfficiencies'].SetBinContent(i+1,
                self.cutflow.count(name))
            self.histograms['hEfficiencies'].GetXaxis().SetBinLabel(i+1, name)

        # print cutflow table
        efftable = PrettyTable(['Selection', 'Events',
            'Eff.(Orig) [%]', 'Rel.Eff. [%]'])
        efftable.align = 'r'
        efftable.align['Selection'] = 'l'
        skimnevents = self.cutflow.count(self.cutflow.get_names()[0])

        for i, name in enumerate(self.cutflow.get_names()):
            efftable.add_row([self.cutflow.get_pretty(name),
                format(self.cutflow.count(name), '0.0f'),
                self.cutflow.get_eff(i),
                self.cutflow.get_rel_eff(i)])

        logging.info('')
        logging.info('Cutflow summary:\n\n' + efftable.get_string() + '\n')



    ## _________________________________________________________________________
    def end_of_job_action(self):
        '''
        Dummy function for action taken at the end of the job. Can be overriden,
        but does not have to be.
        '''
        pass


    ## _________________________________________________________________________
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

        #for hist in self.histograms:
        for hist in sorted(self.histograms):
            self.histograms[hist].Write()

        # make a directory and go into it
        for dirname in self.extra_histogram_map.keys():
            tdir = self.outfile.mkdir(dirname)
            tdir.cd()
            # write the histograms
            # self.extra_histogram_map is a map of string:histogram map
            # self.extra_histogram_map[dirname] is a map 
            #     in the same form as self.histograms
            for hist in self.extra_histogram_map[dirname]:
                # only write histograms that aren't empty
                if (self.extra_histogram_map[dirname][hist].GetEntries()
                    or dirname=='categories'):
                    self.extra_histogram_map[dirname][hist].Write()
            tdir.cd('../')

        # finish up
	logging.info('')
	logging.info('Created the following file:')
        logging.info('    {0}'.format(self.output))
        self.outfile.Close()

    ## _________________________________________________________________________
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
            logging.info('    NOM XSEC : '
                '{0} pb'.format(self.nom_xsec if self.nom_xsec != -1. else '--'))
        logging.info('    NEVENTS (skim) : {0}'.format(self.nevents_to_process))
        logging.info('    NEVENTS (orig) : {0}'.format(self.nevents))
        logging.info('    SUMWEIGHTS     : {0}'.format(self.sumweights))


    ## _________________________________________________________________________
    def calculate_event_weight(self):
        '''
        Returns the following named tuple:
            EventWeight = (base_event_weight, pileup_factor,
                trigger_factor, lepton_factor)
        Final event weight can be calculated by
        multiplying all 4 numbers together.
        '''
        if self.isdata: return EventWeight(1., 1., 1., 1., 1.)

        # lepton scale factors
        base_event_weight = self.event.gen_weight()

        pileup_factor = self.puweights.get_weight(
            self.event.num_true_pileup_interactions(),
            self.cuts['PU_scheme']
        ) if self.do_pileup_reweighting else 1.

        trigger_factor = self.hltweights.get_scale(
            self.good_muons,
            self.cuts['SF_scheme']
        ) if self.include_trigger_scale_factors else 1.

        lepton_factor = self.muonweights.get_id_scale(
            self.good_muons,
            self.cuts['cMuID'],
            self.cuts['SF_scheme']
        ) if self.include_lepton_scale_factors else 1.
        lepton_factor *= self.muonweights.get_iso_scale(
            self.good_muons, self.cuts['cMuID'],
            self.cuts['cMuIsoType'],
            self.cuts['cMuIsoLevel'],
            self.cuts['SF_scheme']
        ) if self.include_lepton_scale_factors else 1.

        full = base_event_weight * pileup_factor * trigger_factor * lepton_factor

        return EventWeight(full, base_event_weight, pileup_factor,
            trigger_factor, lepton_factor)


    ## _________________________________________________________________________
    def print_event_info(self, this_cat):
        '''
        Prints collection info after selection.
        '''
        thisrun = self.event.run()
        thislumi = self.event.lumi_block()
        thisevent = self.event.number()

        print '\n=================================================='
        print 'Event info for {0}:{1}:{2}'.format(thisrun, thislumi, thisevent)
        print '=================================================='
        print 'CAT{3} - {0}:{1}:{2}\n'.format(thisrun,
            thislumi, thisevent, this_cat)

        # print electron info
        print 'good electrons: {0}'.format(len(self.good_electrons)
            if self.good_electrons else 0)
        for i, e in enumerate(self.good_electrons):
            print '    Electron({0}):'.format(i)
            print '        pT = {0:0.4f}'.format(e.pt())
            print '        eta = {0:0.4f}'.format(e.eta())
            print '        phi = {0:0.4f}'.format(e.phi())
            print '        is_loose  = {0}'.format('True' if e.is_loose() else 'False')
            print '        is_medium = {0}'.format('True' if e.is_medium() else 'False')
            print '        is_tight  = {0}'.format('True' if e.is_tight() else 'False')
        print

        # print muon info
        print 'good muons: {0}'.format(len(self.good_muons)
            if self.good_muons else 0)
        for i, m in enumerate(self.good_muons):
            print '    Muon({0}):'.format(i)
            print '        pT(uncorr) = {0:0.4f}'.format(m.pt('uncorr'))
            print '        pT(corr)   = {0:0.4f}'.format(m.pt('corr'))
            print '        eta = {0:0.4f}'.format(m.eta())
            print '        phi = {0:0.4f}'.format(m.phi())
            print '        isoval = {0:0.4f}'.format(m.iso_PFr4dB_comb_rel())
            print '        is_loose  = {0}'.format('True' if m.is_loose() else 'False')
            print '        is_medium = {0}'.format('True' if m.is_medium() else 'False')
            print '        is_medium2016 = {0}'.format('True' if m.is_medium2016() else 'False')
            print '        is_tight  = {0}'.format('True' if m.is_tight() else 'False')
        print

        # print dimuon info
        print 'good dimuon cands: {0}'.format(len(self.dimuon_pairs)
            if self.dimuon_pairs else 0)
        for i, p in enumerate(self.dimuon_pairs):
            thisdimuon = self.good_muons[p[0]].p4() + self.good_muons[p[1]].p4()
            print '    Pair({0}):'.format(i)
            print '        dimuon inv mass = {0:0.4f}'.format(thisdimuon.M())
            print '        dimuon pt  = {0:0.4f}'.format(thisdimuon.Pt())
            print '        dimuon eta = {0:0.4f}'.format(thisdimuon.Eta())
            print '        Muon({0}):'.format(p[0])
            print '            pT = {0:0.4f}'.format(self.good_muons[p[0]].pt())
            print '        Muon({0}):'.format(p[1])
            print '            pT = {0:0.4f}'.format(self.good_muons[p[1]].pt())
        print

            # check effects of rochester corrections
            #thisdimuonuncorr_first  = self.good_muons[p[0]].p4('uncorr')
            #thisdimuonuncorr_second = self.good_muons[p[1]].p4('uncorr')
            #thisdimuonuncorr = thisdimuonuncorr_first + thisdimuonuncorr_second
            #thisdimuoncorr_first  = self.good_muons[p[0]].p4('corr')
            #thisdimuoncorr_second = self.good_muons[p[1]].p4('corr')
            #thisdimuoncorr = thisdimuoncorr_first + thisdimuoncorr_second
            #print 'uncor muon0 Pt, Eta, Phi, E =', thisdimuonuncorr_first.Pt(), \
            #thisdimuonuncorr_first.Eta(), thisdimuonuncorr_first.Phi(), \
            #thisdimuonuncorr_first.E()
            #print '  cor muon0 Pt, Eta, Phi, E =', thisdimuoncorr_first.Pt(), \
            #thisdimuoncorr_first.Eta(), thisdimuoncorr_first.Phi(), \
            #thisdimuoncorr_first.E()
            #print
            #print 'uncor muon0 Px, Py, Pz =', thisdimuonuncorr_first.Px(), \
            #thisdimuonuncorr_first.Py(), thisdimuonuncorr_first.Pz()
            #print '  cor muon0 Px, Py, Pz =', thisdimuoncorr_first.Px(), \
            #thisdimuoncorr_first.Py(), thisdimuoncorr_first.Pz()
            #print
            #print
            #print 'uncor muon1 Pt, Eta, Phi, E =', thisdimuonuncorr_second.Pt(), \
            #thisdimuonuncorr_second.Eta(), thisdimuonuncorr_second.Phi(), \
            #thisdimuonuncorr_second.E()
            #print '  cor muon1 Pt, Eta, Phi, E =', thisdimuoncorr_second.Pt(), \
            #thisdimuoncorr_second.Eta(), thisdimuoncorr_second.Phi(), \
            #thisdimuoncorr_second.E()
            #print
            #print 'uncor muon1 Px, Py, Pz =', thisdimuonuncorr_second.Px(), \
            #thisdimuonuncorr_second.Py(), thisdimuonuncorr_second.Pz()
            #print '  cor muon1 Px, Py, Pz =', thisdimuoncorr_second.Px(), \
            #thisdimuoncorr_second.Py(), thisdimuoncorr_second.Pz()
            #print '    corr dimuon mass = {0:0.4f}'.format(thisdimuoncorr.M())
            #print '    uncorr dimuon mass = {0:0.4f}'.format(thisdimuonuncorr.M())
            #print '    corr dimuon pt = {0:0.4f}'.format(thisdimuoncorr.Pt())
            #print '    uncorr dimuon pt = {0:0.4f}'.format(thisdimuonuncorr.Pt())
            #print '    dimuon eta = {0:0.4f}\n'.format(thisdimuonuncorr.Eta())


        # print jet info
        print 'good b jets: {0}'.format(len(self.good_bjets)
            if self.good_bjets else 0)
        for i, j in enumerate(self.good_bjets):
            print '    BJet({0}):'.format(i)
            print '        pT = {0:0.4f}'.format(j.pt())
            print '        eta = {0:0.4f}'.format(j.eta())
        print

        print 'good jets: {0}'.format(len(self.good_jets)
            if self.good_jets else 0)
        for i, j in enumerate(self.good_jets):
            print '    Jet({0}):'.format(i)
            print '        pT = {0:0.4f}'.format(j.pt())
            print '        eta = {0:0.4f}'.format(j.eta())
        print

        # print dijet info
        print 'dijet cands: {0}'.format(len(self.dijet_pairs)
            if self.dijet_pairs else 0)
        for i, p in enumerate(self.dijet_pairs):
            thisdijet = self.good_jets[p[0]].p4() + self.good_jets[p[1]].p4()
            print '    Pair({0}):'.format(i)
            print '        dijet inv mass = {0:0.4f}'.format(thisdijet.M())
            print '        dijet pt  = {0:0.4f}'.format(thisdijet.Pt())
            print '        dijet eta = {0:0.4f}'.format(thisdijet.Eta())
            print '        Jet({0}):'.format(p[0])
            print '            pT = {0:0.4f}'.format(self.good_jets[p[0]].pt())
            print '        Jet({0}):'.format(p[1])
            print '            pT = {0:0.4f}'.format(self.good_jets[p[1]].pt())
        print

        # print met info
        print 'MET: {0:0.4f}\n'.format(self.met.et())



## _____________________________________________________________________________
def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run analyzer')

    # line below is an example of a required argument
    parser.add_argument('-i', '--input_file_list', type=str,
        help='List of input files (AC1B*.root)')
    parser.add_argument('-o', '--output_filename', type=str,
        help='Output file name')

    # line below is an example of an optional argument
    parser.add_argument('-n', '--nevents', type=int, default=-1,
        help=('Max number of events to process (should be only used for '
            'debugging; results in incorrect sumweights)'))
    parser.add_argument('-s', '--skipevents', type=int, default=-1,
        help=('Number of events to skip before processing (should be only used '
            'for debugging; results in incorrect sumweights)'))
    parser.add_argument('-f', '--whichfile', type=int, default=-1,
        help=('Number of input file (should be only used '
            'for debugging; results in incorrect sumweights)'))

    return parser.parse_args(argv)

## _____________________________________________________________________________
def main(argv=None):
    if argv is None:
        # sys.argv[0:] is the python script itself;
        # sys.argv[1:] is the first argument
        argv = sys.argv[1:]
    args = parse_command_line(argv)
    return args

