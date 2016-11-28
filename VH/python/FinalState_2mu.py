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
        self.doPileupReweighting = True
        #self.includeTriggerScaleFactors = True
        #self.includeLeptonScaleFactors = True

        ## use rochester corrections (default is false)
        self.useRochesterCorrections = True

        ##########################################################
        #                                                        #
        # Define event HLT requirement                           #
        #                                                        #
        ##########################################################
        self.hltriggers = cuts['HLT']
        self.pathForTriggerScaleFactors = cuts['HLTstring'] #'IsoMu20_OR_IsoTkMu20'



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

        eventweight = self.calculate_event_weight()

        self.histograms['hNumDiMu'].Fill(len(self.dimuon_pairs), eventweight)


#        # step1
#        self.histograms['hVtxN_step1'].Fill(len(goodVertices), eventweight)
#        self.histograms['hNumMu_step1'].Fill(len(goodMuons), eventweight)
#        for mu in goodMuons:
#            self.histograms['hMuPt_step1'].Fill(mu.Pt(), eventweight)
#        self.histograms['hNumE_step1'].Fill(len(goodElectrons), eventweight)
#        for e in goodElectrons:
#            self.histograms['hEPt_step1'].Fill(e.Pt(), eventweight)
#        self.histograms['hDiMuInvMass_step1'].Fill((diMuonPairs[0][0].P4() + diMuonPairs[0][1].P4() ).M() if diMuonPairs else 0., eventweight)
#
#
#
#        num_leptons = len(goodMuons) + len(goodElectrons)
#
#        if (num_leptons > 4): return
#        self.cutflow.increment('nEv_4Lep')
#        # step2
#        self.histograms['hVtxN_step2'].Fill(len(goodVertices), eventweight)
#        self.histograms['hNumMu_step2'].Fill(len(goodMuons), eventweight)
#        for mu in goodMuons:
#            self.histograms['hMuPt_step2'].Fill(mu.Pt(), eventweight)
#        self.histograms['hNumE_step2'].Fill(len(goodElectrons), eventweight)
#        for e in goodElectrons:
#            self.histograms['hEPt_step2'].Fill(e.Pt(), eventweight)
#        self.histograms['hDiMuInvMass_step2'].Fill((diMuonPairs[0][0].P4() + diMuonPairs[0][1].P4() ).M() if diMuonPairs else 0., eventweight)
#
#        if (len(goodBJets) > 0): return
#        self.cutflow.increment('nEv_NoBJets')
#        # step3
#        self.histograms['hVtxN_step3'].Fill(len(goodVertices), eventweight)
#        self.histograms['hNumMu_step3'].Fill(len(goodMuons), eventweight)
#        for mu in goodMuons:
#            self.histograms['hMuPt_step3'].Fill(mu.Pt(), eventweight)
#        self.histograms['hNumE_step3'].Fill(len(goodElectrons), eventweight)
#        for e in goodElectrons:
#            self.histograms['hEPt_step3'].Fill(e.Pt(), eventweight)
#        self.histograms['hDiMuInvMass_step3'].Fill((diMuonPairs[0][0].P4() + diMuonPairs[0][1].P4() ).M() if diMuonPairs else 0., eventweight)
#
#        # V(lep)h selection: 0 bjets, 1 or 2 extra leptons
#        if (num_leptons < 3): return
#        self.cutflow.increment('nEv_3or4Lep')
#        # step4
#        self.histograms['hVtxN_step4'].Fill(len(goodVertices), eventweight)
#        self.histograms['hNumMu_step4'].Fill(len(goodMuons), eventweight)
#        for mu in goodMuons:
#            self.histograms['hMuPt_step4'].Fill(mu.Pt(), eventweight)
#        self.histograms['hNumE_step4'].Fill(len(goodElectrons), eventweight)
#        for e in goodElectrons:
#            self.histograms['hEPt_step4'].Fill(e.Pt(), eventweight)
#        self.histograms['hDiMuInvMass_step4'].Fill((diMuonPairs[0][0].P4() + diMuonPairs[0][1].P4() ).M() if diMuonPairs else 0., eventweight)
#
#
#        ##########################################################
#        #                                                        #
#        # Fill histograms                                        #
#        #                                                        #
#        ##########################################################
#
#        # decide on control plots
#        # control region = events without dimuon in signal region
#        fillControlPlots = False
#        for mupair in diMuonPairs:
#            mupairP4 = mupair[0].P4() + mupair[1].P4()
#            if (mupairP4.M() < self.sigLow or mupairP4.M() > self.sigHigh): fillControlPlots = True
#
#        #############################
#        # PV after selection ########
#        #############################
#        # fill histograms with good pvs
#        self.histograms['hVtxN'].Fill(len(goodVertices), eventweight)
#
#        #############################
#        # Muons #####################
#        #############################
#        self.histograms['hNumMu'].Fill(len(goodMuons), eventweight)
#        for mu in goodMuons:
#            self.histograms['hMuPt'].Fill(mu.Pt(), eventweight)
#            self.histograms['hMuEta'].Fill(mu.Eta(), eventweight)
#            self.histograms['hMuPhi'].Fill(mu.Phi(), eventweight)
#            if len(goodMuons)==3:
#                self.histograms['hMetMtWithMu'].Fill(self.met.MtWith(mu), eventweight)
#            # fill comtrol plots
#            if fillControlPlots:
#                self.histograms_ctrl['hMuPt_ctrl'].Fill(mu.Pt(), eventweight)
#                self.histograms_ctrl['hMuEta_ctrl'].Fill(mu.Eta(), eventweight)
#                self.histograms_ctrl['hMuPhi_ctrl'].Fill(mu.Phi(), eventweight)
#                if len(goodMuons)==3:
#                    self.histograms_ctrl['hMetMtWithMu_ctrl'].Fill(self.met.MtWith(mu), eventweight)
#
#        #############################
#        # Dimuon ####################
#        #############################
#        for mupair in diMuonPairs:
#            self.histograms['hLeadMuPt'].Fill(mupair[0].Pt(), eventweight)
#            self.histograms['hSubLeadMuPt'].Fill(mupair[1].Pt(), eventweight)
#            diMuP4 = mupair[0].P4() + mupair[1].P4()
#            self.histograms['hDiMuPt'].Fill(diMuP4.Pt(), eventweight)
#            self.histograms['hDiMuEta'].Fill(diMuP4.Eta(), eventweight)
#            self.histograms['hDiMuPhi'].Fill(diMuP4.Phi(), eventweight)
#            self.histograms['hDiMuInvMass'].Fill(diMuP4.M(), eventweight)
#            self.histograms['hDiMuDeltaPt'].Fill(mupair[0].Pt() - mupair[1].Pt(), eventweight)
#            self.histograms['hDiMuDeltaEta'].Fill(mupair[0].Eta() - mupair[1].Eta(), eventweight)
#            self.histograms['hDiMuDeltaPhi'].Fill(mupair[0].Phi() - mupair[1].Phi(), eventweight)
#
#            # fill control plots
#            if fillControlPlots:
#                self.histograms_ctrl['hLeadMuPt_ctrl'].Fill(mupair[0].Pt(), eventweight)
#                self.histograms_ctrl['hSubLeadMuPt_ctrl'].Fill(mupair[1].Pt(), eventweight)
#                self.histograms_ctrl['hDiMuPt_ctrl'].Fill(diMuP4.Pt(), eventweight)
#                self.histograms_ctrl['hDiMuEta_ctrl'].Fill(diMuP4.Eta(), eventweight)
#                self.histograms_ctrl['hDiMuPhi_ctrl'].Fill(diMuP4.Phi(), eventweight)
#                self.histograms_ctrl['hDiMuInvMass_ctrl'].Fill(diMuP4.M(), eventweight)
#                self.histograms_ctrl['hDiMuDeltaPt_ctrl'].Fill(mupair[0].Pt() - mupair[1].Pt(), eventweight)
#                self.histograms_ctrl['hDiMuDeltaEta_ctrl'].Fill(mupair[0].Eta() - mupair[1].Eta(), eventweight)
#                self.histograms_ctrl['hDiMuDeltaPhi_ctrl'].Fill(mupair[0].Phi() - mupair[1].Phi(), eventweight)
#
#        # pick which inv mass to put in limit tree
#        mytInvMass = ( diMuonPairs[0][0].P4() + diMuonPairs[0][1].P4() ).M() if diMuonPairs else 0.
#
#        #############################
#        # Electrons #################
#        #############################
#        self.histograms['hNumE'].Fill(len(goodElectrons), eventweight)
#        for e in goodElectrons:
#            self.histograms['hEPt'].Fill(e.Pt(), eventweight)
#            self.histograms['hEEta'].Fill(e.Eta(), eventweight)
#            self.histograms['hEPhi'].Fill(e.Phi(), eventweight)
#        # leading electron
#        if len(goodElectrons) > 0:
#            self.histograms['hLeadEPt'].Fill(goodElectrons[0].Pt(), eventweight)
#        # subleading electron
#        if len(goodElectrons) > 1:
#            self.histograms['hSubLeadEPt'].Fill(goodElectrons[1].Pt(), eventweight)
#
#        #############################
#        # Dielectron ################
#        #############################
#        for epair in diElectronPairs:
#            diEP4 = epair[0].P4() + epair[1].P4()
#            self.histograms['hDiEPt'].Fill(diEP4.Pt(), eventweight)
#            self.histograms['hDiEEta'].Fill(diEP4.Eta(), eventweight)
#            self.histograms['hDiEPhi'].Fill(diEP4.Phi(), eventweight)
#            self.histograms['hDiEInvMass'].Fill(diEP4.M(), eventweight)
#            self.histograms['hDiEDeltaPt'].Fill(epair[0].Pt() - epair[1].Pt(), eventweight)
#            self.histograms['hDiEDeltaEta'].Fill(epair[0].Eta() - epair[1].Eta(), eventweight)
#            self.histograms['hDiEDeltaPhi'].Fill(epair[0].Phi() - epair[1].Phi(), eventweight)
#
#
#        #############################
#        # Jets ######################
#        #############################
#        self.histograms['hNumJets'].Fill(len(goodJets), eventweight)
#        self.histograms['hNumBJets'].Fill(len(goodBJets), eventweight)
#        for jet in goodJets:
#            self.histograms['hJetPt'].Fill(jet.Pt(), eventweight)
#            self.histograms['hJetEta'].Fill(jet.Eta(), eventweight)
#            self.histograms['hJetPhi'].Fill(jet.Phi(), eventweight)
#        # leading jet
#        if len(goodJets) > 0:
#            self.histograms['hLeadJetPt'].Fill(goodJets[0].Pt(), eventweight)
#        # subleading jet
#        if len(goodJets) > 1:
#            self.histograms['hSubLeadJetPt'].Fill(goodJets[1].Pt(), eventweight)
#
#        #############################
#        # Dijet #####################
#        #############################
#        for jetpair in diJetPairs:
#            diJetP4 = jetpair[0].P4() + jetpair[1].P4()
#            self.histograms['hDiJetPt'].Fill(diJetP4.Pt(), eventweight)
#            self.histograms['hDiJetEta'].Fill(diJetP4.Eta(), eventweight)
#            self.histograms['hDiJetPhi'].Fill(diJetP4.Phi(), eventweight)
#            self.histograms['hDiJetInvMass'].Fill(diJetP4.M(), eventweight)
#            self.histograms['hDiJetDeltaPt'].Fill(jetpair[0].Pt() - jetpair[1].Pt(), eventweight)
#            self.histograms['hDiJetDeltaEta'].Fill(jetpair[0].Eta() - jetpair[1].Eta(), eventweight)
#            self.histograms['hDiJetDeltaPhi'].Fill(jetpair[0].Phi() - jetpair[1].Phi(), eventweight)
#
#
#        #############################
#        # MET #######################
#        #############################
#        self.histograms['hMET'].Fill(self.met.Et(), eventweight)
#        self.histograms['hMETPhi'].Fill(self.met.Phi(), eventweight)
#
#
#
#
#
#
        pairindex1, pairindex2 = self.dimuon_pairs[0]
        muon1 = self.good_muons[pairindex1]
        muon2 = self.good_muons[pairindex2]
        dimuonobj = muon1.P4() + muon2.P4()

        mytInvMass = dimuonobj.M()

        passes_vh = check_vh_preselection(self)
        if not passes_vh: return
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

        ## debug
        #if (self.event.Number() % 10):
        #    self.ftreeCat0.Fill()
        #    self.fnumCat0 += 1
        #else:
        #    self.ftreeCat2.Fill()
        #    self.fnumCat2 += 1

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
        logging.info('Bucket events    = {0}'.format(self.fnumBucket))



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
