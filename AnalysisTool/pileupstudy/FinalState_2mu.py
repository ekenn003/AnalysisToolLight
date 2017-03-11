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
from AnalysisToolLight.AnalysisTool.cuts import vh_cuts as cuts
from AnalysisToolLight.AnalysisTool.ScaleFactors import VariablePileupWeights


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

        ##########################################################
        #                                                        #
        # Some run options                                       #
        #                                                        #
        ##########################################################
        ## use rochester corrections (default is false)
        self.useRochesterCorrections = True

        fname_tail = 'new'
        self.xsec_range = [
            '63500',
            '63750',
            '64000',
            '64250',
            '64500',
            '64750',
            '65000',
        ]


        self.puWeights = VariablePileupWeights(self.cmsswversion, self.data_dir, fname_tail, self.xsec_range)
        #self.minBiasChoices = self.puWeights.get_minbias_range()

        self.hltriggers = cuts['HLT']
        self.pathForTriggerScaleFactors = cuts['HLTstring'] #'IsoMu20_OR_IsoTkMu20'

        ##########################################################
        #                                                        #
        # Book additional histograms                             #
        #                                                        #
        ##########################################################
        for x in self.xsec_range:
            self.histograms['hVtxN_{0}'.format(x)] = self.histograms['hVtxN'].Clone('hVtxN_{0}'.format(x))



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
        # Calculate event weight                                 #
        #                                                        #
        ##########################################################
        eventweight_ = self.calculate_event_weight()

        eventweight = eventweight_.full



        ##########################################################
        #                                                        #
        # Fill them histograms                                   #
        #                                                        #
        ##########################################################

        self.histograms['hVtxN'].Fill(len(self.good_vertices), eventweight)
        for x in self.xsec_range:
            if self.ismc:
                thiseventweight = eventweight
                thiseventweight *= self.puWeights.getWeightForXSec(x, self.event.NumTruePileUpInteractions())
            else: thiseventweight = 1.

            self.histograms['hVtxN_{0}'.format(x)].Fill(len(self.good_vertices), thiseventweight)



    ## _______________________________________________________
    def end_of_job_action(self):
        pass



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
