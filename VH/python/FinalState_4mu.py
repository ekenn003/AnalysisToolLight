# VH/FinalState_4mu.py
import glob
import itertools
import argparse
import sys
import ROOT
from collections import OrderedDict
from AnalysisToolLight.AnalysisToolLight.AnalysisBase import AnalysisBase, CutFlow
from AnalysisToolLight.AnalysisToolLight.AnalysisBase import main as analysisBaseMain

## ___________________________________________________________
class VH4Mu(AnalysisBase):
    def __init__(self, args):
        super(VH4Mu, self).__init__(args)
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
        self.cDxyMu = 0.02 # cm
        self.cDzMu  = 0.14 # cm

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
        self.cutflow.add('nEv_Eta',      'Muon eta < {0}'.format(self.cMuEta))
        self.cutflow.add('nEv_PtEtaMax', 'At least 1 trigger-matched mu with pT > {0} and |eta| < {1}'.format(self.cMuPtMax, self.cMuEtaMax))
        self.cutflow.add('nEv_Iso',      'Muon has {0} {1} isolation'.format(self.cIsoMuType, self.cIsoMuLevel))
        self.cutflow.add('nEv_ID',       'Muon has {0} muon ID'.format(self.cMuID))
        self.cutflow.add('nEv_PVMu',     'Muon Dxy < {0} and Dx < {1}'.format(self.cMuDxy, self.cMuDz))
        # muon pair slection
        self.cutflow.add('nEv_SamePVDiMu',  'Dimu pair has same pv mus')
        self.cutflow.add('nEv_ChargeDiMu',  'Dimu pair has opposite-sign mus')
        self.cutflow.add('nEv_InvMassDiMu', 'Dimu pair has invariant mass > {0}'.format(self.cDiMuInvMass))
        self.cutflow.add('nEv_PtDiMu',      'Dimu pair has pT > {0}'.format(self.cDiMuPt))






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
        # debugging:
        evtnr = self.event.Number()
        if not evtnr%2: self.cutflow.increment('nEv_Trigger')
        else: return





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
            if not muon.Eta() < self.cMuEta: continue
            isEtaCutOK = True


            # check isolation
            # here you can also do muon.IsoR3CombinedRelIso() < stuff, muon.PFR4ChargedHadrons() etc.
            # see Muon object in Dataform.py for all avaiable methods
            if not (muon.CheckIso(cIsoMuType, cIsoMuLevel)): continue
            isIsoOK = True
            if not (): continue
            isIDOK = True





            if not (muon.Dxy() < self.cMuDxy and muon.Dz() < self.cMuDz): continue
            isTrackCutOK = True


            # if we get to this point, push muon into goodMuons
            goodMuons += [muon]



        if isGAndTr: self.cutflow.increment('nEv_GAndTr')
        if isPtCutOK: self.cutflow.increment('nEv_Pt')
        if isEtaCutOK: self.cutflow.increment('nEv_Eta')
        # make sure at least one HLT-matched muon passed extra cuts
        if nMuPtEtaMax > 0: self.cutflow.increment('nEv_PtEtaMax')
        else: return
        if isIsoOK: self.cutflow.increment('nEv_Iso')
        if isIDOK: self.cutflow.increment('nEv_ID')
        if isTrackCutOK: self.cutflow.increment('nEv_PVMu')






        #if self.taus: print 'Tau(0) has pT = ' + str(self.taus[0].Pt())
        #if self.taus: print ' = ' + str(self.taus[0].TauDiscriminator('cantfindme'))


        #############################
        # DIMUON PAIRS ##############
        #############################
        # loop over all possible pairs of muons
        self.dimuon = () 
        maxDiMuPt = 0
        if len(goodMuons) >= 2:
            for pair in itertools.combinations(goodMuons, 2):
                diMuP4 = pair[0].P4() + pair[1].P4()
                if diMuP4.Pt() > min(maxDiMuPt, self.cDiMuPt):
                    maxDiMuPt = diMuP4.Pt()
                    # order the pair by pt
                    self.dimuon = pair if pair[0].Pt() > pair[1].Pt() else (pair[1], pair[0])






        self.cutflow.add('nEv_SamePVDiMu',  'Dimu pair has same pv mus')
        self.cutflow.add('nEv_ChargeDiMu',  'Dimu pair has opposite-sign mus')
        self.cutflow.add('nEv_InvMassDiMu', 'Dimu pair has invariant mass > {0}'.format(self.cDiMuInvMass))
        self.cutflow.add('nEv_PtDiMu',      'Dimu pair has pT > {0}'.format(self.cDiMuPt))










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
        if self.dimuon:
            diMuP4 = mu0.P4() + mu1.P4()
            self.histograms['hDiMuPt'].Fill(diMuP4.Pt(), pileupweight)
            self.histograms['hDiMuInvMass'].Fill(diMuP4.M(), pileupweight)
        


    ### _______________________________________________________
    #def endJob(self):
    #    '''
    #    At the end of the job, fill efficiencies histogram.
    #    '''
    #    for i, name in enumerate(self.cutflow.getNames()):
    #        # 0 is the underflow bin in root: first bin to fill is bin 1
    #        self.histograms['hEfficiencies'].SetBinContent(i+1, self.cutflow.count(name))
    #        self.histograms['hEfficiencies'].GetXaxis().SetBinLabel(i+1, name)


## ___________________________________________________________
# actually execute the analysis
def main(argv=None):
    VH4Mu(analysisBaseMain(argv)).analyze()

## ___________________________________________________________
# checks if this was run from the command line
if __name__ == "__main__":
    status = main()
    sys.exit(status)
