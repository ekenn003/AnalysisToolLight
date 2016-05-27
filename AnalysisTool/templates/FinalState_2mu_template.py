# VH/FinalState_4mu.py
import glob
import itertools
import argparse
import sys
import ROOT
from collections import OrderedDict
from AnalysisToolLight.AnalysisTool.AnalysisBase import AnalysisBase, CutFlow
from AnalysisToolLight.AnalysisTool.AnalysisBase import main as analysisBaseMain

## ___________________________________________________________
class Ana2Mu(AnalysisBase):
    def __init__(self, args):
        super(Ana2Mu, self).__init__(args)

        self.debug = False

        #############################
        # Define cuts ###############
        #############################
        # PV cuts
        self.cVtxNdf = 4
        self.cVtxZ   = 24. # cm

        # muon cuts
        self.cMuPt = 10. # GeV
        self.cMuEta = 2.4
        self.cMuPtMax = 20. # choice here should depend on HLT
        self.cMuEtaMax = 2.4 # choice here should depend on HLT
        # muon pv cuts
        self.cMuDxy = 0.02 # cm
        self.cMuDz  = 0.14 # cm

        # isolation (https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2#Muon_Isolation)
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
        self.cDiMuPt = 38. # GeV

        # electron cuts
        self.cPtE = 10.
        self.cEtaE = 2.4

        # jet cuts
        self.cPtJet = 30. # GeV
        self.cEtaJet = 4.7

        # MET cuts
        self.cMET = 40. # GeV





        #############################
        # Initialise event counters #
        #############################
        self.cutflow = CutFlow()
        self.cutflow.add('nEv_Skim', 'Skim number of events')
        # event selection
        self.cutflow.add('nEv_Trigger', 'Trigger')
        self.cutflow.add('nEv_PV', 'PV cuts')
        # muon selection
        self.cutflow.add('nEv_GAndTr',   'Global+Tracker muon')
        self.cutflow.add('nEv_Pt',       'Muon pT > {0}'.format(self.cMuPt))
        self.cutflow.add('nEv_Eta',      'Muon |eta| < {0}'.format(self.cMuEta))
        self.cutflow.add('nEv_PtEtaMax', 'At least 1 trigger-matched mu with pT > {0} and |eta| < {1}'.format(self.cMuPtMax, self.cMuEtaMax))
        self.cutflow.add('nEv_Iso',      'Muon has {0} {1} isolation'.format(self.cIsoMuType, self.cIsoMuLevel))
        self.cutflow.add('nEv_ID',       'Muon has {0} muon ID'.format(self.cMuID))
        self.cutflow.add('nEv_PVMu',     'Muon Dxy < {0} and Dx < {1}'.format(self.cMuDxy, self.cMuDz))
        # muon pair slection
        self.cutflow.add('nEv_2Mu',         'Require 2 "good" muons')
        self.cutflow.add('nEv_ChargeDiMu',  'Dimu pair has opposite-sign mus')
        self.cutflow.add('nEv_SamePVDiMu',  'Dimu pair has same pv mus')
        self.cutflow.add('nEv_InvMassDiMu', 'Dimu pair has invariant mass > {0}'.format(self.cDiMuInvMass))
        self.cutflow.add('nEv_PtDiMu',      'Dimu pair has pT > {0}'.format(self.cDiMuPt))
        self.cutflow.add('nEv_1DiMu',       'Require at least 1 "good" dimuon pair')






        #############################
        # Book histograms ###########
        #############################
        self.histograms['hVtxN'] = ROOT.TH1F('hVtxN', 'hVtxN', 100, 0., 100.)
        self.histograms['hVtxN'].GetXaxis().SetTitle('N_{PV}')
        self.histograms['hVtxN'].GetYaxis().SetTitle('Candidates')
        self.histograms['hVtxN_u'] = ROOT.TH1F('hVtxN_u', 'hVtxN_u', 100, 0., 100.)
        self.histograms['hVtxN_u'].GetXaxis().SetTitle('N_{PV} before weighting')
        self.histograms['hVtxN_u'].GetYaxis().SetTitle('Candidates')

        self.histograms['hWeight'] = ROOT.TH1F('hWeight', 'hWeight', 100000, -10000., 10000.)
        self.histograms['hWeight'].GetXaxis().SetTitle('Event weight')
        self.histograms['hWeight'].GetYaxis().SetTitle('Events')

        # muons
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

        # dimuon
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





    ## _______________________________________________________
    def perEventAction(self):
        '''
        This is the core of the analysis loop. Selection is done here.
        '''
        #############################
        # Event weight ##############
        #############################
        pileupweight = 1.
        if not self.isdata: pileupweight = self.event.GenWeight()
        self.histograms['hWeight'].Fill(pileupweight)

        self.cutflow.increment('nEv_Skim')


        #############################
        # Trigger ###################
        #############################
        #evtnr = self.event.Number()

        # list of triggers we want to check for this event
        hltriggers = (
            'IsoMu20',
            'IsoTkMu20',
        )
        # event.PassesHLTs returns True if any of the triggers fired
        if not self.event.PassesHLTs(hltriggers): return
        self.cutflow.increment('nEv_Trigger')



        # optional: make funtion here that alerts you to any prescales


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
            if not muon.Pt() > self.cMuPt: continue
            isPtCutOK = True
            if not muon.AbsEta() < self.cMuEta: continue
            isEtaCutOK = True

            # make sure at least one HLT-matched muon passes extra cuts
            if muon.MatchesHLTs(hltriggers) and muon.Pt > self.cMuPtMax and muon.AbsEta() < self.cMuEtaMax: nMuPtEtaMax += 1

            # check isolation
            # here you can also do muon.IsoR3CombinedRelIso() < stuff, muon.PFR4ChargedHadrons() etc.
            # see Muon object in Dataform.py for all avaiable methods
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
            if not (muon.Dxy() < self.cMuDxy and muon.Dz() < self.cMuDz): continue
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




        #if self.taus: print 'Tau(0) has pT = ' + str(self.taus[0].Pt())
        #if self.taus: print ' = ' + str(self.taus[0].TauDiscriminator('cantfindme'))


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
            if not (diMuonP4.Pt() > self.cDiMuPt): continue
            isPtDiMuCutOK = True

            # if we reach this part, we have a pair! set thisdimuon to the pair, ordered by pT
            thisdimuon = pair if pair[0].Pt() > pair[1].Pt() else (pair[1], pair[0])
            diMuonPairs += [thisdimuon]

        if isChargeMuCutOK: self.cutflow.increment('nEv_ChargeDiMu')
        if isSamePVMuCutOK: self.cutflow.increment('nEv_SamePVDiMu')
        if isInvMassMuCutOK: self.cutflow.increment('nEv_InvMassDiMu')
        if isPtDiMuCutOK: self.cutflow.increment('nEv_PtDiMu')

        # require at least one dimuon pair
        if len(diMuonPairs) < 1: return
        self.cutflow.increment('nEv_1DiMu')






        if self.debug:
            # print muon info
            print 'Event number {0} has {1} good muons and {2} good dimuon pairs.'.format(self.event.Number(), len(goodMuons), len(diMuonPairs))
            print '\n=================================================='
            for i, m in enumerate(goodMuons):
                print '  Muon({2}):\n    pT = {0}\n    eta = {1}'.format(m.Pt(), m.Eta(), i)
            print
            for i, p in enumerate(diMuonPairs):
                print '  Pair({0}):\n'.format(i)
                print '      Muon(0):\n    pT = {0}\n    eta = {1}\n'.format(p[0].Pt(), p[0].Eta())
                print '      Muon(1):\n    pT = {0}\n    eta = {1}\n'.format(p[1].Pt(), p[1].Eta())
            print '==================================================\n'

            # print electron info
            print 'Event number {0} has {1} good muons and {2} good dimuon pairs.'.format(self.event.Number(), len(goodMuons), len(diMuonPairs))
            print '\n=================================================='
            for i, m in enumerate(goodMuons):
                print '  Muon({2}):\n    pT = {0}\n    eta = {1}'.format(m.Pt(), m.Eta(), i)
            print
            for i, p in enumerate(diMuonPairs):
                print '  Pair({0}):\n'.format(i)
                print '      Muon(0):\n    pT = {0}\n    eta = {1}\n'.format(p[0].Pt(), p[0].Eta())
                print '      Muon(1):\n    pT = {0}\n    eta = {1}\n'.format(p[1].Pt(), p[1].Eta())
            print '==================================================\n'



      #      if diMuP4.Pt() > min(maxDiMuPt, self.cDiMuPt):
      #          maxDiMuPt = diMuP4.Pt()





        # fill histograms
        #self.fill()
        # leading muon
        if len(goodMuons) > 0:
            mu0 = goodMuons[0]
            self.histograms['hLeadMuPt'].Fill(mu0.Pt(), pileupweight)

        # subleading muon
        if len(goodMuons) > 1:
            mu1 = goodMuons[1]
            self.histograms['hSubLeadMuPt'].Fill(mu1.Pt(), pileupweight)

        # diumuon
        if diMuonPairs:
            diMuP4 = mu0.P4() + mu1.P4()
            self.histograms['hDiMuPt'].Fill(diMuP4.Pt(), pileupweight)
            self.histograms['hDiMuInvMass'].Fill(diMuP4.M(), pileupweight)
        



## ___________________________________________________________
# actually execute the analysis
def main(argv=None):
    Ana2Mu(analysisBaseMain(argv)).analyze()

## ___________________________________________________________
# checks if this was run from the command line
if __name__ == "__main__":
    status = main()
    sys.exit(status)
