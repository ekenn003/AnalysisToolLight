# VH/FinalState_4mu.py
import glob
import itertools
import argparse
import sys, logging
import ROOT
from collections import OrderedDict
from AnalysisToolLight.AnalysisTool.tools.tools import DeltaR, Z_MASS, INF, EventIsOnList
from AnalysisToolLight.AnalysisTool.AnalysisBase import AnalysisBase, CutFlow
from AnalysisToolLight.AnalysisTool.AnalysisBase import main as analysisBaseMain

## ___________________________________________________________
class ZH4Mu(AnalysisBase):
    def __init__(self, args):
        super(ZH4Mu, self).__init__(args)

        ##########################################################
        #                                                        #
        # Some run options                                       #
        #                                                        #
        ##########################################################
        self.debug = False

        # careful! this will print out event info for every single event
        self.printEventInfo = False

        # the default for all of these is False
        self.doPileupReweighting = True
        #self.includeTriggerScaleFactors = True
        #self.includeLeptonScaleFactors = True


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
        self.cPtDiMu = 30. # GeV

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
        self.cutflow.add('nEv_4Mu',         'Require 4 "good" muons')
        self.cutflow.add('nEv_ChargeDiMu',  'Dimu pair has opposite-sign mus')
        self.cutflow.add('nEv_SamePVDiMu',  'Dimu pair has same pv mus')
        self.cutflow.add('nEv_InvMassDiMu', 'Dimu pair has invariant mass > {0}'.format(self.cDiMuInvMass))
        self.cutflow.add('nEv_PtDiMu',      'Dimu pair has pT > {0}'.format(self.cPtDiMu))
        self.cutflow.add('nEv_2DiMu',       'Require at least 2 dimuon pairs')
        self.cutflow.add('nEv_2RealDiMu',   'Require at least 2 "good" dimuon pairs')



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

        self.histograms['hWeight'] = ROOT.TH1F('hWeight', 'hWeight', 100, -1000., 100.)
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
        # MET #######################
        #############################
        self.histograms['hMET'] = ROOT.TH1F('hMET', 'hMET', 500, 0., 1000.)
        self.histograms['hMET'].GetXaxis().SetTitle('E_{T miss}[GeV/c]')
        self.histograms['hMET'].GetYaxis().SetTitle('Candidates/2.0[GeV]')


    ## _______________________________________________________
    def perEventAction(self):
        '''
        This is the core of the analysis loop. Selection is done here.
        '''

        self.cutflow.increment('nEv_Skim')

        ##########################################################
        #                                                        #
        # Preselection                                           #
        #                                                        #
        ##########################################################



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

        # require at least 4 good muons in this event
        if len(goodMuons) < 4: return
        self.cutflow.increment('nEv_4Mu')



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
            if not jetIsClean: continue
            
            # save good jet
            goodJets += [jet]


        #############################
        # MET #######################
        #############################

        # you can also do self.met.E().Pt(), self.met.E().Phi()
        # also available: self.met.E() (TVector3), self.met.RawE(), self.met.RawEt(), self.met.RawPhi()
        evtmet = self.met.Et()
        evtmetphi = self.met.Phi()



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

            # if we reach this part, we have a pair!
            # set thispair to the pair, ordered by pT
            # and then push back into diMuonPairs
            thispair = pair if pair[0].Pt() > pair[1].Pt() else (pair[1], pair[0])
            diMuonPairs += [thispair]

        if isChargeMuCutOK: self.cutflow.increment('nEv_ChargeDiMu')
        if isSamePVMuCutOK: self.cutflow.increment('nEv_SamePVDiMu')
        if isInvMassMuCutOK: self.cutflow.increment('nEv_InvMassDiMu')
        if isPtDiMuCutOK: self.cutflow.increment('nEv_PtDiMu')

        # require two dimuon pairs
        if len(diMuonPairs) < 2: return
        self.cutflow.increment('nEv_2DiMu')


        # decide which one is the Z
        dMassMax = INF
        pairZ = None
        pairH = None
        for pair in diMuonPairs:
            # is this pair closer to the Z mass than the last one?
            dMass = abs(Z_MASS - diMuonP4.M())
            if dMass < dMassMax:
                dMassMax = dMass
                pairZ = pair
        # set the other one to the H
        for pair in diMuonPairs:
            # does this pair have one of the same muons as pairZ?
            if pair[0] in pairZ: continue
            if pair[1] in pairZ: continue
            pairH = pair
            break

        # make sure we got two distinct pairs
        if not (pairZ and pairH): return
        self.cutflow.increment('nEv_2RealDiMu')



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
        # Update event weight (MC only)                          #
        #                                                        #
        ##########################################################
        eventweight = 1.
        if not self.isdata:
            eventweight = self.event.GenWeight()
            if self.doPileupReweighting:
                eventweight *= self.puweights.getWeight(self.event.NumTruePileUpInteractions())
        #    if self.includeTriggerScaleFactors:
        #        eventweight *= self.hltweights.getScale(goodMuons)
        #    if self.includeLeptonScaleFactors:
        #        eventweight *= self.muonweights.getIdScale(goodMuons, self.cMuID)
        #        # NB: the below only works for PF w/dB isolation
        #        eventweight *= self.muonweights.getIsoScale(goodMuons, self.cMuID, self.cIsoMuLevel)
        self.histograms['hWeight'].Fill(eventweight)



        ##########################################################
        #                                                        #
        # Fill histograms                                        #
        #                                                        #
        ##########################################################
        #############################
        # PV after selection ########
        #############################
        # fill histograms with good pvs
        self.histograms['hVtxN'].Fill(len(goodVertices), eventweight)
        self.histograms['hVtxN_u'].Fill(len(goodVertices))

        #############################
        # Muons #####################
        #############################
        self.histograms['hNumMu'].Fill(len(goodMuons), eventweight)
        for mu in goodMuons:
            self.histograms['hMuPt'].Fill(mu.Pt(), eventweight)
            self.histograms['hMuEta'].Fill(mu.Eta(), eventweight)
            self.histograms['hMuPhi'].Fill(mu.Phi(), eventweight)


        #############################
        # Dimuon ####################
        #############################
        for mupair in diMuonPairs:
            self.histograms['hLeadMuPt'].Fill(mupair[0].Pt(), eventweight)
            self.histograms['hSubLeadMuPt'].Fill(mupair[1].Pt(), eventweight)
            diMuP4 = mupair[0].P4() + mupair[1].P4()
            self.histograms['hDiMuPt'].Fill(diMuP4.Pt(), eventweight)
            self.histograms['hDiMuEta'].Fill(diMuP4.Eta(), eventweight)
            self.histograms['hDiMuPhi'].Fill(diMuP4.Phi(), eventweight)
            self.histograms['hDiMuInvMass'].Fill(diMuP4.M(), eventweight)
            self.histograms['hDiMuDeltaPt'].Fill(mupair[0].Pt() - mupair[1].Pt(), eventweight)
            self.histograms['hDiMuDeltaEta'].Fill(mupair[0].Eta() - mupair[1].Eta(), eventweight)
            self.histograms['hDiMuDeltaPhi'].Fill(mupair[0].Phi() - mupair[1].Phi(), eventweight)
        



        #############################
        # Jets ######################
        #############################
        self.histograms['hNumJets'].Fill(len(goodJets), eventweight)
        for jet in goodJets:
            self.histograms['hJetPt'].Fill(jet.Pt(), eventweight)
            self.histograms['hJetEta'].Fill(jet.Eta(), eventweight)
            self.histograms['hJetPhi'].Fill(jet.Phi(), eventweight)
        # leading jet
        if len(goodJets) > 0:
            self.histograms['hLeadJetPt'].Fill(goodJets[0].Pt(), eventweight)
        # subleading jet
        if len(goodJets) > 1:
            self.histograms['hSubLeadJetPt'].Fill(goodJets[1].Pt(), eventweight)



        #############################
        # MET #######################
        #############################
        self.histograms['hMET'].Fill(self.met.Et(), eventweight)



        if not self.event.Number()%100: logging.info('histos filled with event weight {0}'.format(eventweight))




## ___________________________________________________________
# actually execute the analysis
def main(argv=None):
    ZH4Mu(analysisBaseMain(argv)).analyze()

## ___________________________________________________________
# checks if this was run from the command line
if __name__ == "__main__":
    status = main()
    sys.exit(status)
