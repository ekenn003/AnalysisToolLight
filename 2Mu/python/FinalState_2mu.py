# FinalState_2mu.py
import itertools
import argparse
import sys, logging
from ROOT import TTree, TH1F
from array import array
from AnalysisToolLight.AnalysisTool.tools.tools import delta_r, Z_MASS, event_is_on_list
from AnalysisToolLight.AnalysisTool.CutFlow import CutFlow
from AnalysisToolLight.AnalysisTool.AnalysisBase import AnalysisBase
from AnalysisToolLight.AnalysisTool.AnalysisBase import main as analysisBaseMain
from AnalysisToolLight.AnalysisTool.histograms import fill_base_histograms
from cuts import vh_cuts as cuts

## ___________________________________________________________
class Ana2Mu(AnalysisBase):
    def __init__(self, args):

        self.cuts = cuts

        super(Ana2Mu, self).__init__(args)

        ##########################################################
        #                                                        #
        # Sync and debugging                                     #
        #                                                        #
        ##########################################################
        self.debug = False

        self.nSyncEvents = 0
        self.sync_low = 100. # GeV
        self.sync_high = 110. # GeV

        # signal region for control plots
        self.sigLow = 120. # GeV
        self.sigHigh = 130. # GeV



        ##########################################################
        #                                                        #
        # Some run options (defaults are False)                  #
        #                                                        #
        ##########################################################
        self.do_pileup_reweighting = True
        self.include_trigger_scale_factors = True
        self.include_lepton_scale_factors = True

        self.use_rochester_corrections = True

        ##########################################################
        #                                                        #
        # Define event HLT requirement                           #
        #                                                        #
        ##########################################################
        self.hltriggers = cuts['HLT']
        self.path_for_trigger_scale_factors = cuts['HLTstring']



        ##########################################################
        #                                                        #
        # Initialize additional event counters                   #
        #                                                        #
        ##########################################################
        #self.cutflow.add('nEv_NoBJets', 'V(lep)h selection: Require 0 bjets')
        #self.cutflow.add('nEv_3or4Lep', 'V(lep)h selection: Require 1 or 2 extra isolated leptons')


        self.cutflow.add('nEv_NoElectrons', 'Require 0 electrons')
        self.cutflow.add('nEv_NoBJets', 'Require 0 bjets')
        self.cutflow.add('nEv_2Jets', 'Require 2 jets')
        self.cutflow.add('nEv_MET', 'Require <40 MET')




        ##########################################################
        #                                                        #
        # Book additional histograms                             #
        #                                                        #
        ##########################################################
        self.histograms['hNumDiMu'] = TH1F('hNumDiMu', 'hNumDiMu', 20, 0., 20.)
        self.histograms['hNumDiMu'].GetXaxis().SetTitle('N_{#mu^{+}#mu^{-}}')
        self.histograms['hNumDiMu'].GetYaxis().SetTitle('Candidates')

        self.histograms['hMetMtWithMu'] = TH1F('hMetMtWithMu', 'hMetMtWithMu', 500, 0., 1000.)
        self.histograms['hMetMtWithMu'].GetXaxis().SetTitle('M_{T}(#mu, MET)[GeV/c^{2}]')
        self.histograms['hMetMtWithMu'].GetYaxis().SetTitle('Candidates/2.0[GeV/c^{2}]')


        ##########################################################
        #                                                        #
        # Book control plot histograms                           #
        #                                                        #
        ##########################################################
        # make control versions of new the plots - they won't all be filled though
        self.histograms_ctrl = {}
        for name in self.histograms.keys():
            self.histograms_ctrl[name+'_ctrl'] = self.histograms[name].Clone(self.histograms[name].GetName()+'_ctrl')
        # add it to the extra histogram map
        self.extra_histogram_map['control'] = self.histograms_ctrl




        ##########################################################
        #                                                        #
        # Book category histograms                               #
        #                                                        #
        ##########################################################

        self.categories = [
            'Category0_All',
            'Category1_VBFTight',
            'Category2_GGFTight',
            'Category3_VBFLoose',
            'Category4_01JetTight',
            'Category5_01JetLoose',
        ]
        self.fnumCat0 = 0
        self.fnumCat1 = 0
        self.fnumCat2 = 0
        self.fnumCat3 = 0
        self.fnumCat4 = 0
        self.fnumCat5 = 0
        self.fnumBucket = 0

        category_hists = ['hVtxN', 'hMET', 'hDiMuPt', 'hDiMuInvMass', 'hNumMu', 'hMuPt']

        self.histograms_categories = {}
        for name in self.histograms.keys():
            if name not in category_hists: continue
            for cat in self.categories:
                self.histograms_categories[name+'_'+cat] = self.histograms[name].Clone(
                    (self.histograms[name].GetName()+'_'+cat))
        # add it to the extra histogram map
        self.extra_histogram_map['categories'] = self.histograms_categories



        ##########################################################
        #                                                        #
        # Set up trees for limit calculations                    #
        #                                                        #
        ##########################################################
        self.tEventNr = array('L', [0])
        self.tLumiNr  = array('L', [0])
        self.tRunNr   = array('L', [0])
        self.tInvMass = array('f', [0.])
        self.tEventWt = array('f', [0.])

        self.category_trees = []

        for i, cat in enumerate(self.categories):
            self.category_trees += [TTree(cat, cat)]
            self.category_trees[i].Branch('tEventNr', self.tEventNr, 'tEventNr/l')
            self.category_trees[i].Branch('tLumiNr', self.tLumiNr, 'tLumiNr/l')
            self.category_trees[i].Branch('tRunNr', self.tRunNr, 'tRunNr/l')
            self.category_trees[i].Branch('tInvMass', self.tInvMass, 'tInvMass/F')
            self.category_trees[i].Branch('tEventWt', self.tEventWt, 'tEventWt/F')


    ## _______________________________________________________
    def per_event_action(self):
        '''
        This is the core of the analysis loop. Selection is done here (not
        including event selection and preselection).
        This method only executes if the event passes event selection and
        preselection found in python/Preselection.
        '''

        thisrun = self.event.run()
        thislumi = self.event.lumi_block()
        thisevent = self.event.number()


        vbfevtlist = [
#            232626,
#            179489,
#            123462,

            53974,
            4115,
            188189,



 # rochester corrections
#            105005,
#            108654,
#            114785,
#            115239,
#            115434,
#            115889,
#            118885,
#            121125,
#            121943,
#            122467,
#            125021,
#            130950,
#            131273,
#            135799,
#            143943,
#            144680,
#            149966,
#            15013,
#            151679,
#            208643,
#            212737,
#            214687,
#            2196,
#            219650,
#            22591,
#            233563,
#            233980,
#            242424,
#            242832,
#            244524,
#            247428,
#            249270,
#            249940,
#            25061,
#            34777,
#            38193,
#            57881,
#            59611,
#            6742,
#            69989,
#            72317,
#            72463,
#            74008,
#            7459,
#            74870,
#            75424,
#            78132,
#            78153,
#            95103,
#            98351,



        ]


        # sync
#        if thisevent not in vbfevtlist: return
        #printevtinfo = True
        printevtinfo = False


 #       if thisevent in vbfevtlist: printevtinfo = True



        ##########################################################
        #                                                        #
        # More channel-specific selections                       #
        #                                                        #
        ##########################################################
        ##########################################################
        #                                                        #
        # Calculate event weight                                 #
        #                                                        #
        ##########################################################
        eventweight_ = self.calculate_event_weight()
        #print 'eventweight_.base_event_weight =', eventweight_.base_event_weight
        #print 'eventweight_.pileup_factor =',     eventweight_.pileup_factor
        #print 'eventweight_.trigger_factor =',    eventweight_.trigger_factor
        #print 'eventweight_.lepton_factor =',     eventweight_.lepton_factor

        eventweight = eventweight_.full

        ##########################################################
        #                                                        #
        # Determine dimuon pairs                                 #
        #                                                        #
        ##########################################################
        self.histograms['hNumDiMu'].Fill(len(self.dimuon_pairs), eventweight)


        pairindex1, pairindex2 = self.dimuon_pairs[0]
        muon1 = self.good_muons[pairindex1]
        muon2 = self.good_muons[pairindex2]
        dimuonobj = muon1.p4() + muon2.p4()

        # pick which inv mass to put in limit tree

        mytInvMass = dimuonobj.M()

        # decide whether to fill control plots
        fill_control_plots = mytInvMass > self.sigHigh or mytInvMass < self.sigLow

        ##########################################################
        #                                                        #
        # Fill them histograms                                   #
        #                                                        #
        ##########################################################

        # fill base histograms
        fill_base_histograms(self, eventweight, fill_control_plots)

        # fill extra histograms
        #if len(self.good_muons)==3:
        #    self.histograms['hMetMtWithMu'].Fill(self.met.MtWith(mu), eventweight)


        ##########################################################
        #                                                        #
        # Determine category                                     #
        #                                                        #
        ##########################################################

        # 80X sync preselection: 0 bjets, at least 2 regular jets, leading/subleading jet 40/30 GeV

        this_cat = 999

        # 80X sync evt selection: exactly 2 muons, 0 electrons
        if (len(self.good_electrons) == 0 and len(self.good_muons) == 2):
            passes_sync_selection = True
        else:
            passes_sync_selection = False



        ###################################
        # Preselection                    #
        ###################################
        jet_count_is_ok = False
        jet_pts_are_ok = False

        if ((len(self.good_bjets) == 0) and (len(self.good_jets) >= 2)):
            jet_count_is_ok = True

        for i, p in enumerate(self.dijet_pairs):
            # should already be ordered by pT
            if ((self.good_jets[p[0]].pt() > 40.) and (self.good_jets[p[1]].pt() > 30.)):
                jet_pts_are_ok = True

        passes_sync_preselection = True if (jet_count_is_ok and jet_pts_are_ok) else False


        ###################################
        # VBFTight                        #
        ###################################
#        vbftight_dijet_mass_ok = False
#        vbftight_dijet_deta_ok = False
        have_vbftight_pair = False

        for i, p in enumerate(self.dijet_pairs):    
            vbftight_dijet_mass_ok = False
            vbftight_dijet_deta_ok = False

            if not (self.good_jets[p[0]].pt() > 40. and self.good_jets[p[1]].pt() > 30.): continue
            thisdijet = self.good_jets[p[0]].p4() + self.good_jets[p[1]].p4()

            if thisdijet.M() > 650.: vbftight_dijet_mass_ok = True
            if abs(self.good_jets[p[0]].eta() - self.good_jets[p[1]].eta()) > 3.5: vbftight_dijet_deta_ok = True

            if vbftight_dijet_mass_ok and vbftight_dijet_deta_ok:
                have_vbftight_pair = True
                break

        passes_sync_vbftight = have_vbftight_pair

        ###################################
        # GGFTight                        #
        ###################################
#        ggftight_dijet_mass_ok = False
#        ggftight_dimuon_pt_ok = False
        have_ggftight_pair = False

        for i, p in enumerate(self.dijet_pairs):    
            ggftight_dijet_mass_ok = False
            ggftight_dimuon_pt_ok = False
            if not (self.good_jets[p[0]].pt() > 40. and self.good_jets[p[1]].pt() > 30.): continue
            thisdijet = self.good_jets[p[0]].p4() + self.good_jets[p[1]].p4()
            if thisdijet.M() > 250.: ggftight_dijet_mass_ok = True
            if dimuonobj.Pt() > 50.: ggftight_dimuon_pt_ok = True
            if ggftight_dijet_mass_ok and ggftight_dimuon_pt_ok:
                have_ggftight_pair = True
                break

        passes_sync_ggftight = have_ggftight_pair







        #if dimuonobj.M() < self.sync_low or dimuonobj.M() > self.sync_high: return

        self.fnumCat0 += 1
        if passes_sync_selection and passes_sync_preselection:
            if passes_sync_vbftight:
                self.fnumCat1 += 1
                this_cat = 1
            elif passes_sync_ggftight:
                self.fnumCat2 += 1
                this_cat = 2
            else:
                self.fnumCat3 += 1
                this_cat = 3
        elif passes_sync_selection:
            if dimuonobj.Pt() >= 25.:
                self.fnumCat4 += 1
                this_cat = 4
            else:
                self.fnumCat5 += 1
                this_cat = 5
        else: this_cat = -1

        #if this_cat == 1: printevtinfo = True
   #     print 'CAT{3} - {0}:{1}:{2}\n'.format(thisrun, thislumi, thisevent, this_cat)

        if printevtinfo:
            print '\n=================================================='
            print 'Event info for {0}:{1}:{2}'.format(thisrun, thislumi, thisevent)
            print '=================================================='
            print 'CAT{3} - {0}:{1}:{2}\n'.format(thisrun, thislumi, thisevent, this_cat)
            # print muon info
            print 'good electrons: {0}'.format(len(self.good_electrons) if self.good_electrons else 0)
            for i, e in enumerate(self.good_electrons):
                print '  Electron({0}):'.format(i)
                print '    pT = {0:0.4f}\n    eta = {1:0.4f}'.format(e.pt(), e.eta())
                print '    is_veto   = {0}'.format('True' if e.is_veto() else 'False')
                print '    is_loose  = {0}'.format('True' if e.is_loose() else 'False')
                print '    is_medium = {0}'.format('True' if e.is_medium() else 'False')
                print '    is_tight  = {0}'.format('True' if e.is_tight() else 'False')
            print
            print 'good muons: {0}'.format(len(self.good_muons) if self.good_muons else 0)
            for i, m in enumerate(self.good_muons):
                print '  Muon({0}):'.format(i)
                print '    pT(corr) = {0:0.4f}\n    eta = {1:0.4f}'.format(m.pt('corr'), m.eta())
                print '    pT(uncorr) = {0:0.4f}\n    eta = {1:0.4f}'.format(m.pt('uncorr'), m.eta())
                print '    isoval = {0:0.4f}'.format(m.iso_PFr4dB_comb_rel())
            print
            print 'good dimuon cands: {0}'.format(len(self.dimuon_pairs) if self.dimuon_pairs else 0)
            for i, p in enumerate(self.dimuon_pairs):
                print '  Pair({0}):'.format(i)
                print '    Muon(0):\n      pT = {0:0.4f}\n      eta = {1:0.4f}'.format(self.good_muons[p[0]].pt(), self.good_muons[p[0]].eta())
                print '    Muon(1):\n      pT = {0:0.4f}\n      eta = {1:0.4f}'.format(self.good_muons[p[1]].pt(), self.good_muons[p[1]].eta())
                thisdimuon = self.good_muons[p[0]].p4() + self.good_muons[p[1]].p4()
                print '    dimuon mass = {0:0.4f}'.format(thisdimuon.M())
                print '    dimuon pt = {0:0.4f}'.format(thisdimuon.Pt())
                print '    dimuon eta = {0:0.4f}\n'.format(thisdimuon.Eta())
            print

            # print jet info
            print 'good b jets: {0}'.format(len(self.good_bjets) if self.good_bjets else 0)
            for i, j in enumerate(self.good_bjets):
                print '    Jet({2}):\n      pT = {0:0.4f}\n      eta = {1:0.4f}'.format(j.pt(), j.eta(), i)

            print 'good jets: {0}'.format(len(self.good_jets) if self.good_jets else 0)
            for i, j in enumerate(self.good_jets):
                print '    Jet({2}):\n      pT = {0:0.4f}\n      eta = {1:0.4f}'.format(j.pt(), j.eta(), i)
            print


            print 'dijet cands: {0}'.format(len(self.dijet_pairs) if self.dijet_pairs else 0)
            for i, p in enumerate(self.dijet_pairs):
                print '    Pair({0}):'.format(i)
                print '      Jet(0):\n        pT = {0:0.4f}\n        eta = {1:0.4f}'.format(self.good_jets[p[0]].pt(), self.good_jets[p[0]].eta())
                print '      Jet(1):\n        pT = {0:0.4f}\n        eta = {1:0.4f}'.format(self.good_jets[p[1]].pt(), self.good_jets[p[1]].eta())
                thisdijet = self.good_jets[p[0]].p4() + self.good_jets[p[1]].p4()
                print '      dijet mass = {0:0.4f}'.format(thisdijet.M())
                print '      dijet dEta = {0:0.4f}\n'.format(abs(self.good_jets[p[0]].eta() - self.good_jets[p[1]].eta()))




            #print '    dijet mass = {0:0.4f}'.format(dijetmass)
            #print '    dijet dEta = {0:0.4f}'.format(dijetdeta)
            print

            # print met info
            print 'MET: {0:0.4f}\n'.format(self.met.et())



        

        #############################################################
        ####                                                        #
        #### Fill limit trees                                       #
        ####                                                        #
        #############################################################
        ###self.tEventNr[0] = self.event.Number()
        ###self.tLumiNr[0]  = self.event.LumiBlock()
        ###self.tRunNr[0]   = self.event.Run()
        ###self.tInvMass[0] = mytInvMass
        ###self.tEventWt[0] = eventweight


        ###if this_cat: self.category_trees[this_cat-1].Fill()

        ###for cat in self.categories:
        ###    if 'Category{0}'.format(this_cat) not in cat: continue
        ###    self.histograms_categories['hDiMuInvMass_'+self.categories[this_cat-1]].Fill(mytInvMass, eventweight)


    ## _______________________________________________________
    def end_of_job_action(self):
#        logging.info('nSyncEvents = ' + str(self.nSyncEvents))
        logging.info('Category1 (VBFTight) events   = {0}'.format(self.fnumCat1))
        logging.info('Category2 (GGFTight) events   = {0}'.format(self.fnumCat2))
        logging.info('Category3 (VBFLoose) events   = {0}'.format(self.fnumCat3))
        logging.info('Category4 (01JetTight) events = {0}'.format(self.fnumCat4))
        logging.info('Category5 (01JetLoose) events = {0}'.format(self.fnumCat5))
        logging.info('')
        logging.info('Category0 (Total) events      = {0}'.format(self.fnumCat0))



## ___________________________________________________________
# actually execute the analysis
def main(argv=None):
#    try:
    Ana2Mu(analysisBaseMain(argv)).analyze()
#    except KeyboardInterrupt:
#        Ana2Mu(analysisBaseMain(argv)).end_job()

## ___________________________________________________________
# checks if this was run from the command line
if __name__ == '__main__':
    status = main()
    sys.exit(status)
