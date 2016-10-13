# FinalState_2mu.py
# This gives examples of how to access things with class AnalysisBase.

import itertools
import argparse
import sys, logging
import ROOT
from collections import OrderedDict
from AnalysisToolLight.AnalysisTool.AnalysisBase import AnalysisBase
from AnalysisToolLight.AnalysisTool.AnalysisBase import main as analysisBaseMain
from AnalysisToolLight.AnalysisTool.ScaleFactors import VariablePileupWeights

## ___________________________________________________________
class PU2Mu(AnalysisBase):
    def __init__(self, args):
        super(PU2Mu, self).__init__(args)

        ##########################################################
        #                                                        #
        # Sync and debugging                                     #
        #                                                        #
        ##########################################################
        self.debug = False

        ##########################################################
        #                                                        #
        # Some run options                                       #
        #                                                        #
        ##########################################################
        pufilerange = '68-75'
        self.puWeights = VariablePileupWeights(self.cmsswversion, self.data_dir, pufilerange)
        self.minBiasChoices = self.puWeights.getMinBiasRange()

        ##########################################################
        #                                                        #
        # Define cuts                                            #
        #                                                        #
        ##########################################################
        self.hltriggers = (
            'IsoMu20',
            'IsoTkMu20',
        )
        self.pathForTriggerScaleFactors = 'IsoMu20_OR_IsoTkMu20'

        # PV cuts
        self.cVtxNdf = 4
        self.cVtxZ   = 24. # cm



        ##########################################################
        #                                                        #
        # Book histograms                                        #
        #                                                        #
        ##########################################################

        self.histograms['hVtxN'] = ROOT.TH1F('hVtxN', 'hVtxN', 100, 0., 100.)
        self.histograms['hVtxN'].GetXaxis().SetTitle('N_{PV}')
        self.histograms['hVtxN'].GetYaxis().SetTitle('Candidates')

        for name in self.histograms.keys():
            for x in self.minBiasChoices:
                self.histograms['{0}_{1}'.format(name, x)] = self.histograms[name].Clone('{0}_{1}'.format(self.histograms[name].GetName(), x))


    ## _______________________________________________________
    def perEventAction(self):
        '''
        This is the core of the analysis loop. Selection is done here.
        '''

        ##########################################################
        #                                                        #
        # Event selection                                        #
        #                                                        #
        ##########################################################

        #############################
        # Trigger ###################
        #############################
        passesHLT = False
        if (self.cmsswversion=='80X' and self.ismc):
            passesHLT = True # 80X MC has no HLT 
        else:
            passesHLT = self.event.PassesHLTs(self.hltriggers)
        if not passesHLT: return

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







        #############################
        # MUONS #####################
        #############################
        # loop over muons and save the good ones
        goodMuons = []
        isGAndTr = False
        isPtCutOK = False
        isEtaCutOK = False
        isIsoOK = False
        isIDOK = False
        for muon in self.muons:
            # muon cuts
            if not (muon.IsGlobal() and muon.IsTracker()): continue
            isGAndTr = True
            if not muon.Pt() > 25.: continue
            isPtCutOK = True
            if not muon.AbsEta() < 2.4: continue
            isEtaCutOK = True

            # check isolation
            if not (muon.CheckIso('PF_dB', 'tight')): continue
            isIsoOK = True

            # check muon ID
            isIDOK = muon.IsTightMuon()
            if not (isIDOK): continue

            # if we get to this point, push muon into goodMuons
            goodMuons += [muon]


        # require at least 2 good muons in this event
        if len(goodMuons) < 2: return


        ##########################################################
        #                                                        #
        # Include pileup reweighting                             #
        #                                                        #
        ##########################################################
        baseEventWeight = 1.
        if self.ismc:
            baseEventWeight = self.event.GenWeight()
            #if self.doPileupReweighting:
            #    eventweight *= self.puweights.getWeight(self.event.NumTruePileUpInteractions())

        self.histograms['hVtxN'].Fill(len(goodVertices), baseEventWeight)
        for x in self.minBiasChoices:
            if self.ismc:
                eventWeight = baseEventWeight
                eventWeight *= self.puWeights.getWeightForXSec(x, self.event.NumTruePileUpInteractions())
            else: eventWeight = 1.

            self.histograms['hVtxN_{0}'.format(x)].Fill(len(goodVertices), eventWeight)








## ___________________________________________________________
# actually execute the analysis
def main(argv=None):
    PU2Mu(analysisBaseMain(argv)).analyze()

## ___________________________________________________________
# checks if this was run from the command line
if __name__ == "__main__":
    status = main()
    sys.exit(status)
