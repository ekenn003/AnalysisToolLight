# FinalState_2mu.py
# This gives examples of how to access things with class AnalysisBase.

import itertools
import argparse
import sys, logging
import ROOT
from collections import OrderedDict
from AnalysisToolLight.AnalysisTool.AnalysisBase import AnalysisBase
from AnalysisToolLight.AnalysisTool.AnalysisBase import main as analysisBaseMain

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
        self.doPileupReweighting = True
        #self.includeTriggerScaleFactors = True
        #self.includeLeptonScaleFactors = True

        ## use rochester corrections (default is false)
        #self.useRochesterCorrections = True

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
        self.histograms['hVtxN_u'] = ROOT.TH1F('hVtxN_u', 'hVtxN_u', 100, 0., 100.)
        self.histograms['hVtxN_u'].GetXaxis().SetTitle('N_{PV} before event weighting')
        self.histograms['hVtxN_u'].GetYaxis().SetTitle('Candidates')
        self.histograms['hVtxN_nopu'] = ROOT.TH1F('hVtxN_nopu', 'hVtxN_nopu', 100, 0., 100.)
        self.histograms['hVtxN_nopu'].GetXaxis().SetTitle('N_{PV} before event or PU weighting')
        self.histograms['hVtxN_nopu'].GetYaxis().SetTitle('Candidates')

        self.histograms['hWeight'] = ROOT.TH1F('hWeight', 'hWeight', 100, -1000., 100.)
        self.histograms['hWeight'].GetXaxis().SetTitle('Event weight')
        self.histograms['hWeight'].GetYaxis().SetTitle('Events')




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
        self.cutflow.increment('nEv_Trigger')

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

        ##########################################################
        #                                                        #
        # Include pileup reweighting                             #
        #                                                        #
        ##########################################################
        self.histograms['hVtxN_nopu'].Fill(len(goodVertices))

        eventweight = 1.

        if not self.isdata:
            eventweight = self.event.GenWeight()
            if self.doPileupReweighting:
                eventweight *= self.puweights.getWeight(self.event.NumTruePileUpInteractions())

        # Fill selected plots without scale factors
        self.histograms['hVtxN_u'].Fill(len(goodVertices), eventweight)

        ##########################################################
        #                                                        #
        # Update event weight (MC only)                          #
        #                                                        #
        ##########################################################
        if not self.isdata:
            if self.includeTriggerScaleFactors:
                eventweight *= self.hltweights.getScale(goodMuons)
            if self.includeLeptonScaleFactors:
                eventweight *= self.muonweights.getIdScale(goodMuons, self.cMuID)
                # NB: the below only works for PF w/dB isolation
                eventweight *= self.muonweights.getIsoScale(goodMuons, self.cMuID, self.cIsoMuLevel)
        self.histograms['hWeight'].Fill(eventweight)

        #############################
        # PV after selection ########
        #############################
        # fill histograms with good pvs
        self.histograms['hVtxN'].Fill(len(goodVertices), eventweight)



## ___________________________________________________________
# actually execute the analysis
def main(argv=None):
    PU2Mu(analysisBaseMain(argv)).analyze()

## ___________________________________________________________
# checks if this was run from the command line
if __name__ == "__main__":
    status = main()
    sys.exit(status)
