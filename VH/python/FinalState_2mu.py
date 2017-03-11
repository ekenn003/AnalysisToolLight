# FinalState_2mu.py
#import glob
import itertools
import argparse
import sys, logging
#import ROOT
from ROOT import TTree, TH1F
from array import array
from AnalysisToolLight.AnalysisTool.tools.tools import DeltaR, Z_MASS, EventIsOnList
from AnalysisToolLight.AnalysisTool.CutFlow import CutFlow
from AnalysisToolLight.AnalysisTool.AnalysisBase import AnalysisBase
from AnalysisToolLight.AnalysisTool.AnalysisBase import main as analysisBaseMain
from AnalysisToolLight.AnalysisTool.Preselection import check_vh_preselection
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
        self.syncLow = 110. # GeV
        self.syncHigh = 130. # GeV

        # signal region for control plots
        self.sigLow = 120. # GeV
        self.sigHigh = 130. # GeV



        ##########################################################
        #                                                        #
        # Some run options                                       #
        #                                                        #
        ##########################################################
        self.do_pileup_reweighting = True
        self.include_trigger_scale_factors = True
        self.include_lepton_scale_factors = True

        # use rochester corrections (default is false)
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
        self.cutflow.add('nEv_NoBJets', 'V(lep)h selection: Require 0 bjets')
        self.cutflow.add('nEv_3or4Lep', 'V(lep)h selection: Require 1 or 2 extra isolated leptons')


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
        self.extraHistogramMap['control'] = self.histograms_ctrl




        ##########################################################
        #                                                        #
        # Book category histograms                               #
        #                                                        #
        ##########################################################

        self.categories = [
            'Category1_V_mu_h',
            'Category2_V_e_h',
            'Category3_Z_tau_h',
            'Category4_Z_mu_h',
            'Category5_Z_e_h',
        ]
        self.fnumCat1 = 0
        self.fnumCat2 = 0
        self.fnumCat3 = 0
        self.fnumCat4 = 0
        self.fnumCat5 = 0
        self.fnumBucket = 0

        category_hists = ['hVtxN', 'hMET', 'hDiMuPt', 'hDiMuInvMass', 'hNumMu', 'hNumE', 'hMuPt', 'hMuEt', 'hEPt']

        self.histograms_categories = {}
        for name in self.histograms.keys():
            if name not in category_hists: continue
            for cat in self.categories:
                self.histograms_categories[name+'_'+cat] = self.histograms[name].Clone(self.histograms[name].GetName()+'_'+cat)
        # add it to the extra histogram map
        self.extraHistogramMap['categories'] = self.histograms_categories



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
#        self.ftreeCat0 = TTree('Category0', 'Category0')
#        self.category_trees += [self.ftreeCat0]
#        self.ftreeCat0.Branch('tEventNr', self.tEventNr, 'tEventNr/l')
#        self.ftreeCat0.Branch('tLumiNr', self.tLumiNr, 'tLumiNr/l')
#        self.ftreeCat0.Branch('tRunNr', self.tRunNr, 'tRunNr/l')
#        self.ftreeCat0.Branch('tInvMass', self.tInvMass, 'tInvMass/F')
#        self.ftreeCat0.Branch('tEventWt', self.tEventWt, 'tEventWt/F')

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
        ##########################################################
        #                                                        #
        # Check VH preselection                                  #
        #                                                        #
        ##########################################################
#        passes_vh = check_vh_preselection(self)
#        if not passes_vh: return


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
        dimuonobj = muon1.P4() + muon2.P4()

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
        num_muons = len(self.good_muons)
        num_electrons = len(self.good_electrons)

        if self.met.Et() >= 40.:
            # V_mu_h
            if num_muons==3 and num_electrons==0:
                this_cat = 1
                self.fnumCat1 += 1
            # V_e_h
            elif num_muons==2 and num_electrons==1:
                this_cat = 2
                self.fnumCat2 += 1
            # Z_tau_h
            elif num_muons==3 and num_electrons==1:
                this_cat = 3
                self.fnumCat3 += 1
            # leftover
            else:
                this_cat = 0
                self.fnumBucket += 1
        else:
            # Z_mu_h
            if num_muons==4 and num_electrons==0:
                this_cat = 4
                self.fnumCat4 += 1
            # Z_e_h
            elif num_muons==2 and num_electrons==2:
                this_cat = 5
                self.fnumCat5 += 1
            # leftover
            else:
                this_cat = 0
                self.fnumBucket += 1

        #if this_cat: logging.info('THISCATEGORY = ' + str(this_cat))

        ##########################################################
        #                                                        #
        # Fill limit trees                                       #
        #                                                        #
        ##########################################################
        self.tEventNr[0] = self.event.Number()
        self.tLumiNr[0]  = self.event.LumiBlock()
        self.tRunNr[0]   = self.event.Run()
        self.tInvMass[0] = mytInvMass
        self.tEventWt[0] = eventweight
        if this_cat: self.category_trees[this_cat-1].Fill()
    #    self.ftreeCat0.Fill()
    #    self.fnumCat0 += 1


        for cat in self.categories:
            if 'Category{0}'.format(this_cat) not in cat: continue
            self.histograms_categories['hDiMuInvMass_'+self.categories[this_cat-1]].Fill(mytInvMass, eventweight)


    ## _______________________________________________________
    def end_of_job_action(self):
        logging.info('nSyncEvents = ' + str(self.nSyncEvents))
        logging.info('Category1 (V_mu_h) events  = {0}'.format(self.fnumCat1))
        logging.info('Category2 (V_e_h) events   = {0}'.format(self.fnumCat2))
        logging.info('Category3 (Z_tau_h) events = {0}'.format(self.fnumCat3))
        logging.info('Category4 (Z_mu_h) events  = {0}'.format(self.fnumCat4))
        logging.info('Category5 (Z_e_h) events   = {0}'.format(self.fnumCat5))
        logging.info('Bucket events = {0}'.format(self.fnumBucket))



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
