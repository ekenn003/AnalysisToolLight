# VH/FinalState_4mu.py
import glob
import itertools
import argparse
import sys
import ROOT
from collections import OrderedDict
from AnalysisToolLight.AnalysisTool.tools.tools import DeltaR, Z_MASS, EventIsOnList
from AnalysisToolLight.AnalysisTool.AnalysisBase import AnalysisBase, CutFlow
from AnalysisToolLight.AnalysisTool.AnalysisBase import main as analysisBaseMain

## ___________________________________________________________
class Ana2Mu(AnalysisBase):
    def __init__(self, args):
        super(Ana2Mu, self).__init__(args)

        ##########################################################
        #                                                        #
        # Some run options                                       #
        #                                                        #
        ##########################################################
        self.debug = False

        # careful! this will print out event info for every single event
        self.printEventInfo = False

        self.doPileupReweighting = True
        #self.doPileupReweighting = False

        # include trigger scale factors
        #self.includeTriggerScaleFactors = True


        ##########################################################
        #                                                        #
        # Define cuts                                            #
        #                                                        #
        ##########################################################

        # list of triggers we want to check for this event
        self.hltriggers = (
            'IsoMu20',
            'IsoTkMu20',
        )
        self.pathForTriggerScaleFactors = 'IsoMu20_OR_IsoTkMu20'

        # PV cuts
        self.cVtxNdf = 4
        self.cVtxZ   = 24. # cm

        # muon cuts
        self.cPtMu = 10. # GeV
        self.cEtaMu = 2.4
        self.cPtMuMax = 20. # choice here should depend on HLT
        self.cEtaMuMax = 2.4 # choice here should depend on HLT
        # muon pv cuts
        self.cDxyMu = 0.02 # cm
        self.cDzMu  = 0.14 # cm

        # isolation (https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2#Muon_Isolation)
        # special function for muons
        self.cIsoMuType = 'PF_dB' # PF combined w/dB correction Loose
        #self.cIsoMuType = 'tracker' # Tracker-based
        self.cIsoMuLevel = 'tight'
        #self.cIsoMuLevel = 'loose'

        # muon id 
        #self.cMuID = 'tight'
        self.cMuID = 'medium'
        #self.cMuID = 'loose'

        # dimuon pair cuts
        self.cDiMuInvMass = 50. # GeV
        self.cPtDiMu = 38. # GeV

        # electron cuts
        self.cPtE = 10.
        self.cEtaE = 2.4

        # electron iso: FIND NEW RUN2 WPs
        self.cIsoE = 0.12

        # jet cuts
        self.cPtJet = 30. # GeV
        self.cEtaJet = 4.7
        # delta R to clean jets
        self.cDeltaR = 0.4

        # MET cuts
        self.cMET = 40. # GeV



        ##########################################################
        #                                                        #
        # Initialize event counters                              #
        #                                                        #
        ##########################################################

        self.cutflow = CutFlow()
        self.cutflow.add('nEv_Skim', 'Skim number of events')
        # event selection
        self.cutflow.add('nEv_Trigger', 'Trigger')
        self.cutflow.add('nEv_PV', 'PV cuts')
        # muon selection
        self.cutflow.add('nEv_GAndTr',   'Global+Tracker muon')
        self.cutflow.add('nEv_Pt',       'Muon pT > {0}'.format(self.cPtMu))
        self.cutflow.add('nEv_Eta',      'Muon |eta| < {0}'.format(self.cEtaMu))
        self.cutflow.add('nEv_PtEtaMax', 'At least 1 trigger-matched mu with pT > {0} and |eta| < {1}'.format(self.cPtMuMax, self.cEtaMuMax))
        self.cutflow.add('nEv_Iso',      'Muon has {0} {1} isolation'.format(self.cIsoMuType, self.cIsoMuLevel))
        self.cutflow.add('nEv_ID',       'Muon has {0} muon ID'.format(self.cMuID))
        self.cutflow.add('nEv_PVMu',     'Muon Dxy < {0} and Dx < {1}'.format(self.cDxyMu, self.cDzMu))
        # muon pair slection
        self.cutflow.add('nEv_2Mu',         'Require 2 "good" muons')
        self.cutflow.add('nEv_ChargeDiMu',  'Dimu pair has opposite-sign mus')
        self.cutflow.add('nEv_SamePVDiMu',  'Dimu pair has same pv mus')
        self.cutflow.add('nEv_InvMassDiMu', 'Dimu pair has invariant mass > {0}'.format(self.cDiMuInvMass))
        self.cutflow.add('nEv_PtDiMu',      'Dimu pair has pT > {0}'.format(self.cPtDiMu))
        self.cutflow.add('nEv_1DiMu',       'Require at least 1 "good" dimuon pair')



        ##########################################################
        #                                                        #
        # Book histograms                                        #
        #                                                        #
        ##########################################################

        self.histograms['hVtxN'] = ROOT.TH1F('hVtxN', 'hVtxN', 100, 0., 100.)
        self.histograms['hVtxN'].GetXaxis().SetTitle('N_{PV}')
        self.histograms['hVtxN'].GetYaxis().SetTitle('Candidates')
        self.histograms['hVtxN_u'] = ROOT.TH1F('hVtxN_u', 'hVtxN_u', 100, 0., 100.)
        self.histograms['hVtxN_u'].GetXaxis().SetTitle('N_{PV} before weighting')
        self.histograms['hVtxN_u'].GetYaxis().SetTitle('Candidates')

        self.histograms['hVtxN_after'] = ROOT.TH1F('hVtxN_after', 'hVtxN_after', 100, 0., 100.)
        self.histograms['hVtxN_after'].GetXaxis().SetTitle('N_{PV} after selection')
        self.histograms['hVtxN_after'].GetYaxis().SetTitle('Candidates')

        self.histograms['hWeight'] = ROOT.TH1F('hWeight', 'hWeight', 100, -10., 10.)
        self.histograms['hWeight'].GetXaxis().SetTitle('Event weight')
        self.histograms['hWeight'].GetYaxis().SetTitle('Events')


        #############################
        # Muons #####################
        #############################
        self.histograms['hNumMu'] = ROOT.TH1F('hNumMu', 'hNumMu', 20, 0., 20.)
        self.histograms['hNumMu'].GetXaxis().SetTitle('N_{#mu}')
        self.histograms['hNumMu'].GetYaxis().SetTitle('Candidates')
        self.histograms['hMuPt'] = ROOT.TH1F('hMuPt', 'hMuPt', 500, 0., 1000.)
        self.histograms['hMuPt'].GetXaxis().SetTitle('p_{T #mu}[GeV/c]')
        self.histograms['hMuPt'].GetYaxis().SetTitle('Candidates/2.0[GeV/c]')
        self.histograms['hMuEta'] = ROOT.TH1F('hMuEta', 'hMuEta',  52, -2.6, 2.6)
        self.histograms['hMuEta'].GetXaxis().SetTitle('#eta_{#mu}')
        self.histograms['hMuEta'].GetYaxis().SetTitle('Candidates/0.1')
        self.histograms['hMuPhi'] = ROOT.TH1F('hMuPhi', 'hMuPhi', 34, -3.4, 3.4)
        self.histograms['hMuPhi'].GetXaxis().SetTitle('#varphi_{#mu} [rad]')
        self.histograms['hMuPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')
        # leading/subleading good muons
        self.histograms['hLeadMuPt'] = ROOT.TH1F('hLeadMuPt', 'hLeadMuPt', 500, 0., 1000.)
        self.histograms['hLeadMuPt'].GetXaxis().SetTitle('p_{T #mu}[GeV/c]')
        self.histograms['hLeadMuPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')
        self.histograms['hSubLeadMuPt'] = ROOT.TH1F('hSubLeadMuPt', 'hSubLeadMuPt', 500, 0., 1000.)
        self.histograms['hSubLeadMuPt'].GetXaxis().SetTitle('p_{T #mu}[GeV/c]')
        self.histograms['hSubLeadMuPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')

        #############################
        # Electrons #################
        #############################
        self.histograms['hNumE'] = ROOT.TH1F('hNumE', 'hNumE', 20, 0., 20.)
        self.histograms['hNumE'].GetXaxis().SetTitle('N_{e}')
        self.histograms['hNumE'].GetYaxis().SetTitle('Candidates')
        self.histograms['hEPt'] = ROOT.TH1F('hEPt', 'hEPt', 500, 0., 1000.)
        self.histograms['hEPt'].GetXaxis().SetTitle('p_{T e}[GeV/c]')
        self.histograms['hEPt'].GetYaxis().SetTitle('Candidates/2.0[GeV/c]')
        self.histograms['hEEta'] = ROOT.TH1F('hEEta', 'hEEta',  52, -2.6, 2.6)
        self.histograms['hEEta'].GetXaxis().SetTitle('#eta_{e}')
        self.histograms['hEEta'].GetYaxis().SetTitle('Candidates/0.1')
        self.histograms['hEPhi'] = ROOT.TH1F('hEPhi', 'hEPhi', 34, -3.4, 3.4)
        self.histograms['hEPhi'].GetXaxis().SetTitle('#varphi_{e} [rad]')
        self.histograms['hEPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')
        # leading/subleading good electrons
        self.histograms['hLeadEPt'] = ROOT.TH1F('hLeadEPt', 'hLeadEPt', 500, 0., 1000.)
        self.histograms['hLeadEPt'].GetXaxis().SetTitle('p_{T e}[GeV/c]')
        self.histograms['hLeadEPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')
        self.histograms['hSubLeadEPt'] = ROOT.TH1F('hSubLeadEPt', 'hSubLeadEPt', 500, 0., 1000.)
        self.histograms['hSubLeadEPt'].GetXaxis().SetTitle('p_{T e}[GeV/c]')
        self.histograms['hSubLeadEPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')

        #############################
        # Jets ######################
        #############################
        self.histograms['hNumJets'] = ROOT.TH1F('hNumJets', 'hNumJets', 20, 0., 20.)
        self.histograms['hNumJets'].GetXaxis().SetTitle('N_{j}')
        self.histograms['hNumJets'].GetYaxis().SetTitle('Candidates')

        self.histograms['hJetPt'] = ROOT.TH1F('hJetPt', 'hJetPt', 500, 0., 1000.)
        self.histograms['hJetPt'].GetXaxis().SetTitle('p_{T j}[GeV/c]')
        self.histograms['hJetPt'].GetYaxis().SetTitle('Candidates/2.0[GeV/c]')
        self.histograms['hJetEta'] = ROOT.TH1F('hJetEta', 'hJetEta',  52, -2.6, 2.6)
        self.histograms['hJetEta'].GetXaxis().SetTitle('#eta_{j}')
        self.histograms['hJetEta'].GetYaxis().SetTitle('Candidates/0.1')
        self.histograms['hJetPhi'] = ROOT.TH1F('hJetPhi', 'hJetPhi', 34, -3.4, 3.4)
        self.histograms['hJetPhi'].GetXaxis().SetTitle('#varphi_{j} [rad]')
        self.histograms['hJetPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')
        # leading/subleading good jets
        self.histograms['hLeadJetPt'] = ROOT.TH1F('hLeadJetPt', 'hLeadJetPt', 500, 0., 1000.)
        self.histograms['hLeadJetPt'].GetXaxis().SetTitle('p_{T j}[GeV/c]')
        self.histograms['hLeadJetPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')
        self.histograms['hSubLeadJetPt'] = ROOT.TH1F('hSubLeadJetPt', 'hSubLeadJetPt', 500, 0., 1000.)
        self.histograms['hSubLeadJetPt'].GetXaxis().SetTitle('p_{T j}[GeV/c]')
        self.histograms['hSubLeadJetPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')


        #############################
        # Dimuon ####################
        #############################
        self.histograms['hDiMuPt'] = ROOT.TH1F('hDiMuPt', 'hDiMuPt', 500, 0., 1000.)
        self.histograms['hDiMuPt'].GetXaxis().SetTitle('p_{T #mu^{+}#mu^{-}}[GeV/c]')
        self.histograms['hDiMuPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')
        self.histograms['hDiMuEta'] = ROOT.TH1F('hDiMuEta', 'hDiMuEta',  132, -6.6, 6.6)
        self.histograms['hDiMuEta'].GetXaxis().SetTitle('#eta_{#mu^{+}#mu^{-}}')
        self.histograms['hDiMuEta'].GetYaxis().SetTitle('Candidates/0.1')
        self.histograms['hDiMuPhi'] = ROOT.TH1F('hDiMuPhi', 'hDiMuPhi', 34, -3.4, 3.4)
        self.histograms['hDiMuPhi'].GetXaxis().SetTitle('#varphi_{#mu^{+}#mu^{-}} [rad]')
        self.histograms['hDiMuPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

        self.histograms['hDiMuDeltaPt'] = ROOT.TH1F('hDiMuDeltaPt', 'hDiMuDeltaPt', 320, -800., 800.)
        self.histograms['hDiMuDeltaPt'].GetXaxis().SetTitle('#Delta p_{T #mu^{+} - #mu^{-}}[GeV/c]')
        self.histograms['hDiMuDeltaPt'].GetYaxis().SetTitle('Candidates/5.0[GeV]')
        self.histograms['hDiMuDeltaEta'] = ROOT.TH1F('hDiMuDeltaEta', 'hDiMuDeltaEta',  132, -6.6, 6.6)
        self.histograms['hDiMuDeltaEta'].GetXaxis().SetTitle('#Delta #eta_{#mu^{+} - #mu^{-}}')
        self.histograms['hDiMuDeltaEta'].GetYaxis().SetTitle('Candidates/0.1')
        self.histograms['hDiMuDeltaPhi'] = ROOT.TH1F('hDiMuDeltaPhi', 'hDiMuDeltaPhi', 34, -3.4, 3.4)
        self.histograms['hDiMuDeltaPhi'].GetXaxis().SetTitle('#Delta #varphi_{#mu^{+} - #mu^{-}} [rad]')
        self.histograms['hDiMuDeltaPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

        self.histograms['hDiMuInvMass'] = ROOT.TH1F('hDiMuInvMass', 'hDiMuInvMass', 2000, 0, 1000)
        self.histograms['hDiMuInvMass'].GetXaxis().SetTitle('M_{#mu^{+}#mu^{-}} [GeV/c^{2}]')
        self.histograms['hDiMuInvMass'].GetYaxis().SetTitle('Candidates/0.5[GeV/c^{2}]')

        #############################
        # Dielectron ################
        #############################
        self.histograms['hDiEPt'] = ROOT.TH1F('hDiEPt', 'hDiEPt', 500, 0., 1000.)
        self.histograms['hDiEPt'].GetXaxis().SetTitle('p_{T e^{+}e^{-}}[GeV/c]')
        self.histograms['hDiEPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')
        self.histograms['hDiEEta'] = ROOT.TH1F('hDiEEta', 'hDiEEta',  132, -6.6, 6.6)
        self.histograms['hDiEEta'].GetXaxis().SetTitle('#eta_{e^{+}e^{-}}')
        self.histograms['hDiEEta'].GetYaxis().SetTitle('Candidates/0.1')
        self.histograms['hDiEPhi'] = ROOT.TH1F('hDiEPhi', 'hDiEPhi', 34, -3.4, 3.4)
        self.histograms['hDiEPhi'].GetXaxis().SetTitle('#varphi_{e^{+}e^{-}} [rad]')
        self.histograms['hDiEPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

        self.histograms['hDiEDeltaPt'] = ROOT.TH1F('hDiEDeltaPt', 'hDiEDeltaPt', 320, -800., 800.)
        self.histograms['hDiEDeltaPt'].GetXaxis().SetTitle('#Delta p_{T e^{+} - e^{-}}[GeV/c]')
        self.histograms['hDiEDeltaPt'].GetYaxis().SetTitle('Candidates/5.0[GeV]')
        self.histograms['hDiEDeltaEta'] = ROOT.TH1F('hDiEDeltaEta', 'hDiEDeltaEta',  132, -6.6, 6.6)
        self.histograms['hDiEDeltaEta'].GetXaxis().SetTitle('#Delta #eta_{e^{+} - e^{-}}')
        self.histograms['hDiEDeltaEta'].GetYaxis().SetTitle('Candidates/0.1')
        self.histograms['hDiEDeltaPhi'] = ROOT.TH1F('hDiEDeltaPhi', 'hDiEDeltaPhi', 34, -3.4, 3.4)
        self.histograms['hDiEDeltaPhi'].GetXaxis().SetTitle('#Delta #varphi_{e^{+} - e^{-}} [rad]')
        self.histograms['hDiEDeltaPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

        self.histograms['hDiEInvMass'] = ROOT.TH1F('hDiEInvMass', 'hDiEInvMass', 2000, 0, 1000)
        self.histograms['hDiEInvMass'].GetXaxis().SetTitle('M_{e^{+}e^{-}} [GeV/c^{2}]')
        self.histograms['hDiEInvMass'].GetYaxis().SetTitle('Candidates/0.5[GeV/c^{2}]')

        #############################
        # Dijet #####################
        #############################
        self.histograms['hDiJetPt'] = ROOT.TH1F('hDiJetPt', 'hDiJetPt', 500, 0., 1000.)
        self.histograms['hDiJetPt'].GetXaxis().SetTitle('p_{T j^{+}j^{-}}[GeV/c]')
        self.histograms['hDiJetPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')
        self.histograms['hDiJetEta'] = ROOT.TH1F('hDiJetEta', 'hDiJetEta',  132, -6.6, 6.6)
        self.histograms['hDiJetEta'].GetXaxis().SetTitle('#eta_{j^{+}j^{-}}')
        self.histograms['hDiJetEta'].GetYaxis().SetTitle('Candidates/0.1')
        self.histograms['hDiJetPhi'] = ROOT.TH1F('hDiJetPhi', 'hDiJetPhi', 34, -3.4, 3.4)
        self.histograms['hDiJetPhi'].GetXaxis().SetTitle('#varphi_{j^{+}j^{-}} [rad]')
        self.histograms['hDiJetPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

        self.histograms['hDiJetDeltaPt'] = ROOT.TH1F('hDiJetDeltaPt', 'hDiJetDeltaPt', 320, -800., 800.)
        self.histograms['hDiJetDeltaPt'].GetXaxis().SetTitle('#Delta p_{T j^{+} - j^{-}}[GeV/c]')
        self.histograms['hDiJetDeltaPt'].GetYaxis().SetTitle('Candidates/5.0[GeV]')
        self.histograms['hDiJetDeltaEta'] = ROOT.TH1F('hDiJetDeltaEta', 'hDiJetDeltaEta',  132, -6.6, 6.6)
        self.histograms['hDiJetDeltaEta'].GetXaxis().SetTitle('#Delta #eta_{j^{+} - j^{-}}')
        self.histograms['hDiJetDeltaEta'].GetYaxis().SetTitle('Candidates/0.1')
        self.histograms['hDiJetDeltaPhi'] = ROOT.TH1F('hDiJetDeltaPhi', 'hDiJetDeltaPhi', 34, -3.4, 3.4)
        self.histograms['hDiJetDeltaPhi'].GetXaxis().SetTitle('#Delta #varphi_{j^{+} - j^{-}} [rad]')
        self.histograms['hDiJetDeltaPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

        self.histograms['hDiJetInvMass'] = ROOT.TH1F('hDiJetInvMass', 'hDiJetInvMass', 2000, 0, 1000)
        self.histograms['hDiJetInvMass'].GetXaxis().SetTitle('M_{j^{+}j^{-}} [GeV/c^{2}]')
        self.histograms['hDiJetInvMass'].GetYaxis().SetTitle('Candidates/0.5[GeV/c^{2}]')


        #############################
        # MET #######################
        #############################
        self.histograms['hMET'] = ROOT.TH1F('hMET', 'hMET', 500, 0., 1000.)
        self.histograms['hMET'].GetXaxis().SetTitle('E_{T miss}[GeV/c]')
        self.histograms['hMET'].GetYaxis().SetTitle('Candidates/2.0[GeV]')
        self.histograms['hMETPhi'] = ROOT.TH1F('hMETPhi', 'hMETPhi', 34, -3.4, 3.4)
        self.histograms['hMETPhi'].GetXaxis().SetTitle('#varphi_{MET} [rad]')
        self.histograms['hMETPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

    ## _______________________________________________________
    def perEventAction(self):
        '''
        This is the core of the analysis loop. Selection is done here.
        '''

        #############################
        # Event weight ##############
        #############################
        pileupweight = 1.

        if not self.isdata:
            pileupweight = self.event.GenWeight()
            if self.doPileupReweighting:
                pileupweight *= self.puweights.getWeight(self.event.NumTruePileUpInteractions())


        self.histograms['hWeight'].Fill(pileupweight)

        self.cutflow.increment('nEv_Skim')



        ##########################################################
        #                                                        #
        # Event selection                                        #
        #                                                        #
        ##########################################################

        #############################
        # Trigger ###################
        #############################
        #evtnr = self.event.Number()

        # event.PassesHLTs returns True if any of the triggers fired
        if not self.event.PassesHLTs(self.hltriggers): return
        self.cutflow.increment('nEv_Trigger')



        # alerts you to any prescales
        if self.event.AnyIsPrescaled(self.hltriggers): logging.info('WARNING! One of the selected HLT paths is prescaled.')

        # How to check the prescale of a path
        #mypathname = 'IsoTkMu20'
        #myprescale = self.event.GetPrescale(mypathname)
        #print 'HLT path {0} has prescale of {1}!'.format(mypathname, myprescale)

        print 'self.pathForTriggerScaleFactors = ' + (self.pathForTriggerScaleFactors)

        #############################
        # Primary vertices ##########
        #############################
        # save good vertices
        goodVertices = []
        isVtxNdfOK = False
        isVtxZOK = False
        for pv in self.vertices:
            if not isVtxNdfOK: isVtxNdfOK = pv.Ndof() > self.cVtxNdf
            if not isVtxZOK:   isVtxZOK = pv.Z() < self.cVtxZ
            # check if it's passed
            if not (isVtxNdfOK and isVtxZOK): continue
            # save it if it did
            goodVertices += [pv]

        # require at least one good vertex
        if not goodVertices: return
        if (isVtxNdfOK and isVtxZOK): self.cutflow.increment('nEv_PV')

        # fill histograms with good pvs
        self.histograms['hVtxN'].Fill(len(goodVertices), pileupweight)
        self.histograms['hVtxN_u'].Fill(len(goodVertices))


        #weight1 = self.event.GenWeight()
        #weight2 = self.event.GenWeight() * self.GetPileupWeight(self.event.NumTruePileUpInteractions())
        #weight3 = self.event.GenWeight() * self.GetPileupWeight(self.event.NumTruePileUpInteractions()) * (6025.2/self.sumweights)
        ## check pileup reweighting
        #if self.isdata:
        #    self.histograms['hVtxN_evrw'].Fill(len(goodVertices), 1.)
        #    self.histograms['hVtxN_purw'].Fill(len(goodVertices), 1.)
        #    self.histograms['hVtxN_totrw'].Fill(len(goodVertices), 1.)
        #else:
        #    self.histograms['hVtxN_evrw'].Fill(len(goodVertices), weight1)
        #    self.histograms['hVtxN_purw'].Fill(len(goodVertices), weight2)
        #    self.histograms['hVtxN_totrw'].Fill(len(goodVertices), weight3)


        ##########################################################
        #                                                        #
        # Candidate selection                                    #
        #                                                        #
        ##########################################################

        #############################
        # MUONS #####################
        #############################
        # loop over muons and save the good ones
        goodMuons = []
        isGAndTr = False
        isPtCutOK = False
        isEtaCutOK = False
        nMuPtEtaMax = 0
        isIsoOK = False
        isIDOK = False
        isTrackCutOK = False
        for muon in self.muons:
            # muon cuts
            if not (muon.IsGlobal() and muon.IsTracker()): continue
            isGAndTr = True
            if not muon.Pt() > self.cPtMu: continue
            isPtCutOK = True
            if not muon.AbsEta() < self.cEtaMu: continue
            isEtaCutOK = True

            # make sure at least one HLT-matched muon passes extra cuts
            if muon.MatchesHLTs(self.hltriggers) and muon.Pt > self.cPtMuMax and muon.AbsEta() < self.cEtaMuMax: nMuPtEtaMax += 1

            # check isolation
            # here you can also do muon.IsoR3CombinedRelIso() < stuff, muon.PFR4ChargedHadrons() etc.
            # see Muon object in Dataform.py for all avaiable methods
            # muons have special function to check these four choices
            if not (muon.CheckIso(self.cIsoMuType, self.cIsoMuLevel)): continue
            isIsoOK = True

            # check muon ID
            if self.cMuID=='tight':
                isIDOK = muon.IsTightMuon()
            elif self.cMuID=='medium': 
                isIDOK = muon.IsMediumMuon()
            elif self.cMuID=='loose':
                isIDOK = muon.IsLooseMuon()
            elif self.cMuID=='none':
                isIDOK = True
            if not (isIDOK): continue

            # check muon PV
            if not (muon.Dxy() < self.cDxyMu and muon.Dz() < self.cDzMu): continue
            isTrackCutOK = True

            # if we get to this point, push muon into goodMuons
            goodMuons += [muon]


        if isGAndTr: self.cutflow.increment('nEv_GAndTr')
        if isPtCutOK: self.cutflow.increment('nEv_Pt')
        if isEtaCutOK: self.cutflow.increment('nEv_Eta')

        # make sure at least one HLT-matched muon passed extra cuts
        if nMuPtEtaMax < 1: return
        else: self.cutflow.increment('nEv_PtEtaMax')

        if isIsoOK: self.cutflow.increment('nEv_Iso')
        if isIDOK: self.cutflow.increment('nEv_ID')
        if isTrackCutOK: self.cutflow.increment('nEv_PVMu')

        # require at least 2 good muons in this event
        if len(goodMuons) < 2: return
        self.cutflow.increment('nEv_2Mu')




        #############################
        # ELECTRONS #################
        #############################
        # loop over electrons and save the good ones
        goodElectrons = []
        for electron in self.electrons:
            # electron cuts
            if not electron.Pt() > self.cPtE: continue
            if not electron.AbsEta() < self.cEtaE: continue

            # check electron id
            # options: cutbased: IsVetoElectron, IsLooseElectron, IsMediumElectron, IsTightElectron
            #          mva: WP90_v1, WP80_v1
            if not electron.IsMediumElectron(): continue

            # check isolation
            # options: rel PF r3 combined with dB correction (IsoPFR3dBCombRel), 
            #          rel PF r3 combined with rho correction (IsoPFR3RhoCombRel),
            #          and lots more in Dataform.py
            # WARNING: check with egamma POG for run 2 working points
            if not electron.IsoPFR3RhoCombRel() < self.cIsoE: continue

            # if we get to this point, push electron into goodElectrons
            goodElectrons += [electron]


        # uncomment the line below to require at least 2 good electrons
        #if len(goodElectrons) < 2: return


        #############################
        # TAUS ######################
        #############################
        # initialise empty list of good taus
        goodTaus = []
        for tau in self.taus:
            # tau cuts
            if not (tau.Pt() > 10. and tau.AbsEta() < 2.4): continue

            # tau discriminator
            # lots of choices! uncomment the following line to see the available discriminators:
            #self.event.PrintAvailableTauDiscriminators()
            if not tau.TauDiscriminator('againstMuonLoose3'): continue

            goodTaus += [tau]



        #############################
        # JETS ######################
        #############################
        # initialise empty list of good jets
        goodJets = []
        # loop over jets
        for jet in self.jets:
            # jet cuts
            if not jet.Pt() > self.cPtJet: continue
            if not jet.AbsEta() < self.cEtaJet: continue

            # btag
            # right now the choices are: passJPL, passJPM, passJPT, passCSVv2L, passCSVv2M, passCSVv2T, passCMVAv2L, passCMVAv2M, passCMVAv2T
            # uncomment the line below to print a list of all available btags in the ntuple
            # self.event.PrintAvailableBtags()

            # require jet to be b-tagged
            #if not jet.Btag('passJPL'): continue
            # require jet to be not b-tagged
            #if jet.Btag('passJPL'): continue

            # jet cleaning
            # clean jets against our selected muons, electrons, and taus:
            jetIsClean = True
            for mu in goodMuons:
                if DeltaR(mu, jet) < self.cDeltaR: jetIsClean = False
            for e in goodElectrons:
                if DeltaR(e, jet) < self.cDeltaR: jetIsClean = False
            for t in goodTaus:
                if DeltaR(t, jet) < self.cDeltaR: jetIsClean = False
            
            # save good jet
            goodJets += [jet]


        #############################
        # MET #######################
        #############################

        # you can also do self.met.E().Pt(), self.met.E().Phi()
        # also available: self.met.E() (TVector3), self.met.RawE(), self.met.RawEt(), self.met.RawPhi()
        evtmet = self.met.Et()
        evtmetphi = self.met.Phi()

        #############################
        # PHOTONS ###################
        #############################
        # you can also do photons, but why would you



        ##########################################################
        #                                                        #
        # Di-candidate reconstruction                            #
        #                                                        #
        ##########################################################

        #############################
        # DIMUON PAIRS ##############
        #############################
        # loop over all possible pairs of muons
        diMuonPairs = []
        isChargeMuCutOK = False
        isSamePVMuCutOK = False
        isInvMassMuCutOK = False
        isPtDiMuCutOK = False

        maxDiMuPt = 0
        # iterate over every (non-ordered) pair of 2 muons in goodMuons
        for pair in itertools.combinations(goodMuons, 2):
            # require opposite sign
            if not (pair[0].Charge() * pair[1].Charge() < 0): continue
            isChargeMuCutOK = True
            # require from same PV
            if not (abs(pair[0].Dz() - pair[1].Dz()) < 0.14): continue
            isSamePVMuCutOK = True
            # create composite four-vector
            diMuonP4 = pair[0].P4() + pair[1].P4()
            # require min pT and min InvMass
            if not (diMuonP4.M() > self.cDiMuInvMass): continue
            isInvMassMuCutOK = True
            if not (diMuonP4.Pt() > self.cPtDiMu): continue
            isPtDiMuCutOK = True

            # if we reach this part, we have a pair! set thispair to the pair, ordered by pT
            # and then push back into diMuonPairs
            thispair = pair if pair[0].Pt() > pair[1].Pt() else (pair[1], pair[0])
            diMuonPairs += [thispair]

        if isChargeMuCutOK: self.cutflow.increment('nEv_ChargeDiMu')
        if isSamePVMuCutOK: self.cutflow.increment('nEv_SamePVDiMu')
        if isInvMassMuCutOK: self.cutflow.increment('nEv_InvMassDiMu')
        if isPtDiMuCutOK: self.cutflow.increment('nEv_PtDiMu')

        # require at least one dimuon pair
        if len(diMuonPairs) < 1: return
        self.cutflow.increment('nEv_1DiMu')



        #############################
        # DIELECTRON PAIRS ##########
        #############################
        # loop over all possible pairs of electrons
        diElectronPairs = []
        # iterate over every pair of electrons
        for pair in itertools.combinations(goodElectrons, 2):

            # electron pair cuts
            if not (pair[0].Charge() * pair[1].Charge() < 0): continue
            if not (abs(pair[0].Dz() - pair[1].Dz()) < 0.14): continue

            # if we reach this part, we have a pair! set thispair to the pair, ordered by pT
            # and then push back into diElectronPairs
            thispair = pair if pair[0].Pt() > pair[1].Pt() else (pair[1], pair[0])
            diElectronPairs += [thispair]



        #############################
        # DIJET PAIRS ###############
        #############################
        # loop over all possible pairs of jets
        diJetPairs = []
        # iterate over every pair of jets
        for pair in itertools.combinations(goodJets, 2):

            # jet pair cuts
            if not (pair[0].Charge() * pair[1].Charge() < 0): continue

            thispair = pair if pair[0].Pt() > pair[1].Pt() else (pair[1], pair[0])
            diJetPairs += [thispair]




        ##########################################################
        #                                                        #
        # Optionally print out event info                        #
        #                                                        #
        ##########################################################
        # if you want to print the event info only if the event is or is not on an event list, use the following two lines
        # the event list has to be formatted as one event per line, RUN:LUMI:EVENTNR
        #eventlistpath = '/afs/cern.ch/work/e/ekennedy/work/fsanalysis/ana76/root6/CMSSW_7_6_5/src/AnalysisToolLight/AnalysisTool/data/eventlist2015C_ucr.txt'
        #if EventIsOnList(self.event.Run(), self.event.LumiBlock(), self.event.Number(), eventlistpath):

        if self.printEventInfo:
            print '\n=================================================='
            print 'Event info for {0}:{1}:{2}'.format(self.event.Run(), self.event.LumiBlock(), self.event.Number())
            print '=================================================='
            # print muon info
            print 'good muons: {0}\ngood dimuon pairs: {1}'.format(len(goodMuons) if goodMuons else 0, len(diMuonPairs) if diMuonPairs else 0)
            for i, m in enumerate(goodMuons):
                print '    Muon({2}):\n    pT = {0:0.4f}\n    eta = {1:0.4f}'.format(m.Pt(), m.Eta(), i)
            print
            for i, p in enumerate(diMuonPairs):
                print '    Pair({0}):'.format(i)
                print '        Muon(0):\n        pT = {0:0.4f}\n        eta = {1:0.4f}'.format(p[0].Pt(), p[0].Eta())
                print '        Muon(1):\n        pT = {0:0.4f}\n        eta = {1:0.4f}\n'.format(p[1].Pt(), p[1].Eta())

            # print electron info
            print 'good electrons: {0}\ngood dielectron pairs: {1}'.format(len(goodElectrons) if goodElectrons else 0, len(diElectronPairs) if diElectronPairs else 0)
            for i, e in enumerate(goodElectrons):
                print '    Electron({2}):\n        pT = {0:0.4f}\n        eta = {1:0.4f}'.format(e.Pt(), e.Eta(), i)
            print
            for i, p in enumerate(diElectronPairs):
                print '    Pair({0}):'.format(i)
                print '        Electron(0):\n        pT = {0:0.4f}\n        eta = {1:0.4f}'.format(p[0].Pt(), p[0].Eta())
                print '        Electron(1):\n        pT = {0:0.4f}\n        eta = {1:0.4f}\n'.format(p[1].Pt(), p[1].Eta())

            # print jet info
            print 'good jets: {0}\ngood dijet pairs: {1}'.format(len(goodJets) if goodJets else 0, len(diJetPairs) if diJetPairs else 0)
            for i, e in enumerate(goodJets):
                print '    Jet({2}):\n        pT = {0:0.4f}\n        eta = {1:0.4f}'.format(e.Pt(), e.Eta(), i)
            print
            for i, p in enumerate(diJetPairs):
                print '    Pair({0}):'.format(i)
                print '        Jet(0):\n        pT = {0:0.4f}\n        eta = {1:0.4f}'.format(p[0].Pt(), p[0].Eta())
                print '        Jet(1):\n        pT = {0:0.4f}\n        eta = {1:0.4f}\n'.format(p[1].Pt(), p[1].Eta())

            # print met info
            print 'MET: {0}'.format(evtmet)

            # if you want to print out taus etc. add that here

            print '==================================================\n'





        ##########################################################
        #                                                        #
        # Fill histograms                                        #
        #                                                        #
        ##########################################################
        #############################
        # PV after selection ########
        #############################
        self.histograms['hVtxN_after'].Fill(len(goodVertices), pileupweight)

        #############################
        # Muons #####################
        #############################
        self.histograms['hNumMu'].Fill(len(goodMuons), pileupweight)
        for mu in goodMuons:
            self.histograms['hMuPt'].Fill(mu.Pt(), pileupweight)
            self.histograms['hMuEta'].Fill(mu.Eta(), pileupweight)
            self.histograms['hMuPhi'].Fill(mu.Phi(), pileupweight)
        # leading muon
        if len(goodMuons) > 0:
            self.histograms['hLeadMuPt'].Fill(goodMuons[0].Pt(), pileupweight)
        # subleading muon
        if len(goodMuons) > 1:
            self.histograms['hSubLeadMuPt'].Fill(goodMuons[1].Pt(), pileupweight)

        #############################
        # Dimuon ####################
        #############################
        for mupair in diMuonPairs:
            diMuP4 = mupair[0].P4() + mupair[1].P4()
            self.histograms['hDiMuPt'].Fill(diMuP4.Pt(), pileupweight)
            self.histograms['hDiMuEta'].Fill(diMuP4.Eta(), pileupweight)
            self.histograms['hDiMuPhi'].Fill(diMuP4.Phi(), pileupweight)
            self.histograms['hDiMuInvMass'].Fill(diMuP4.M(), pileupweight)
            self.histograms['hDiMuDeltaPt'].Fill(mupair[0].Pt() - mupair[1].Pt(), pileupweight)
            self.histograms['hDiMuDeltaEta'].Fill(mupair[0].Eta() - mupair[1].Eta(), pileupweight)
            self.histograms['hDiMuDeltaPhi'].Fill(mupair[0].Phi() - mupair[1].Phi(), pileupweight)
        

        #############################
        # Electrons #################
        #############################
        self.histograms['hNumE'].Fill(len(goodElectrons), pileupweight)
        for e in goodElectrons:
            self.histograms['hEPt'].Fill(e.Pt(), pileupweight)
            self.histograms['hEEta'].Fill(e.Eta(), pileupweight)
            self.histograms['hEPhi'].Fill(e.Phi(), pileupweight)
        # leading electron
        if len(goodElectrons) > 0:
            self.histograms['hLeadEPt'].Fill(goodElectrons[0].Pt(), pileupweight)
        # subleading electron
        if len(goodElectrons) > 1:
            self.histograms['hSubLeadEPt'].Fill(goodElectrons[1].Pt(), pileupweight)

        #############################
        # Dielectron ################
        #############################
        for epair in diElectronPairs:
            diEP4 = epair[0].P4() + epair[1].P4()
            self.histograms['hDiEPt'].Fill(diEP4.Pt(), pileupweight)
            self.histograms['hDiEEta'].Fill(diEP4.Eta(), pileupweight)
            self.histograms['hDiEPhi'].Fill(diEP4.Phi(), pileupweight)
            self.histograms['hDiEInvMass'].Fill(diEP4.M(), pileupweight)
            self.histograms['hDiEDeltaPt'].Fill(epair[0].Pt() - epair[1].Pt(), pileupweight)
            self.histograms['hDiEDeltaEta'].Fill(epair[0].Eta() - epair[1].Eta(), pileupweight)
            self.histograms['hDiEDeltaPhi'].Fill(epair[0].Phi() - epair[1].Phi(), pileupweight)


        #############################
        # Jets ######################
        #############################
        self.histograms['hNumJets'].Fill(len(goodJets), pileupweight)
        for jet in goodJets:
            self.histograms['hJetPt'].Fill(jet.Pt(), pileupweight)
            self.histograms['hJetEta'].Fill(jet.Eta(), pileupweight)
            self.histograms['hJetPhi'].Fill(jet.Phi(), pileupweight)
        # leading jet
        if len(goodJets) > 0:
            self.histograms['hLeadJetPt'].Fill(goodJets[0].Pt(), pileupweight)
        # subleading jet
        if len(goodJets) > 1:
            self.histograms['hSubLeadJetPt'].Fill(goodJets[1].Pt(), pileupweight)

        #############################
        # Dijet #####################
        #############################
        for jetpair in diJetPairs:
            diJetP4 = jetpair[0].P4() + jetpair[1].P4()
            self.histograms['hDiJetPt'].Fill(diJetP4.Pt(), pileupweight)
            self.histograms['hDiJetEta'].Fill(diJetP4.Eta(), pileupweight)
            self.histograms['hDiJetPhi'].Fill(diJetP4.Phi(), pileupweight)
            self.histograms['hDiJetInvMass'].Fill(diJetP4.M(), pileupweight)
            self.histograms['hDiJetDeltaPt'].Fill(jetpair[0].Pt() - jetpair[1].Pt(), pileupweight)
            self.histograms['hDiJetDeltaEta'].Fill(jetpair[0].Eta() - jetpair[1].Eta(), pileupweight)
            self.histograms['hDiJetDeltaPhi'].Fill(jetpair[0].Phi() - jetpair[1].Phi(), pileupweight)


        #############################
        # MET #######################
        #############################
        self.histograms['hMET'].Fill(self.met.Et(), pileupweight)
        self.histograms['hMETPhi'].Fill(self.met.Phi(), pileupweight)

## ___________________________________________________________
# actually execute the analysis
def main(argv=None):
#    try:
    Ana2Mu(analysisBaseMain(argv)).analyze()
#    except KeyboardInterrupt:
#        Ana2Mu(analysisBaseMain(argv)).endJob()

## ___________________________________________________________
# checks if this was run from the command line
if __name__ == "__main__":
    status = main()
    sys.exit(status)
