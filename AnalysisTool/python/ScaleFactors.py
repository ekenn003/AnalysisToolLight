# AnalysisToolLight/AnalysisTool/python/ScaleFactors.py
'''
ScaleFactor class base
'''
import argparse

import ROOT
#import math
from collections import OrderedDict, namedtuple
from Dataform import Muon

## ___________________________________________________________
class ScaleFactor(object):
    '''
    Scale factor object
    '''
    # constructors/helpers
    def __init__(self, cmsswversion, datadir):
        self.cmsswversion = cmsswversion
        self.datadir = datadir


## ___________________________________________________________
class PileupWeights(ScaleFactor):
    # constructors/helpers
    def __init__(self, cmsswversion, datadir):
        super(PileupWeights, self).__init__(cmsswversion, datadir)

        self.pileupScale = []
        self.pileupScale_up = []
        self.pileupScale_down = []

        logging.info('  Looking for pileup file at {0}/pileup/pileup_{1}.root'.format(self.dataDir, self.cmsswversion))
        # now we look for a file called pileup_76X.root or pileup_80X.root in datadir/pileup/
        pufile = ROOT.TFile('{0}/pileup/pileup_{1}.root'.format(self.datadir, self.cmsswversion))

        # save scale factors in vectors where each index corresponds to the NumTruePileupInteractions
        scalehist_ = pufile.Get('pileup_scale')
        # for each histogram, set (b)th entry in self.pileupScale to bin content of (b+1)th bin (0th bin is underflow)
        for b in range(scalehist_.GetNbinsX()):
            self.pileupScale.append(scalehist_.GetBinContent(b+1))
        scalehist_ = pufile.Get('pileup_scale_up')
        for b in range(scalehist_.GetNbinsX()):
            self.pileupScale_up.append(scalehist_.GetBinContent(b+1))
        scalehist_ = pufile.Get('pileup_scale_down')
        for b in range(scalehist_.GetNbinsX()):
            self.pileupScale_down.append(scalehist_.GetBinContent(b+1))

        pufile.Close()


    # methods
    def getWeight(self, numtrueinteractions):
        return self.pileupScale[int(round(numtrueinteractions))] if len(self.pileupScale) > numtrueinteractions else 0.
    def getWeightUp(self, numtrueinteractions):
        return self.pileupScale_up[int(round(numtrueinteractions))] if len(self.pileupScale_up) > numtrueinteractions else 0.
    def getWeightDown(self, numtrueinteractions):
        return self.pileupScale_down[int(round(numtrueinteractions))] if len(self.pileupScale_down) > numtrueinteractions else 0.








## ___________________________________________________________
class HLTScaleFactors(ScaleFactor):
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffsRun2
    # constructors/helpers
    def __init__(self, cmsswversion, datadir, hltrigger):
        super(HLTScaleFactors, self).__init__(cmsswversion, datadir)

        # right now the only choice is single muon hlt
        if hltrigger=='IsoMu20_OR_IsoTkMu20':
            filename = 'singlemuontrigger'
        else:
            print 'Right now the only available HLT for scale factors is "IsoMu20_OR_IsoTkMu20".'
            raise

        logging.info('  Looking for scale factor file at {0}/scalefactors/{1}_{2}.root'.format(self.dataDir, filename, self.cmsswversion))
        # this is the file created by AnalysisTool/scripts/collectTriggerScaleFactors.py
        hltfile = ROOT.TFile('{0}/scalefactors/{1}_{2}.root'.format(self.datadir, filename, self.cmsswversion))

        # the histograms in the file are named effMC and effDA, with x axis: Pt, y axis: AbsEta
        effhistDA_ = hltfile.Get('effDA')
        effhistMC_ = hltfile.Get('effMC')
        maxpt = effhistDA_.GetXaxis().GetXmax()
        maxeta = effhistDA_.GetYaxis().GetXmax()

        print 'maxpt = {0} and maxeta = {1}'.format(maxpt, maxeta)

    # methods
    def getScale(self, *args):
        xda = 1.
        xmc = 1.
        for mu in args:
            # make sure the muon is in range

            pt = min(maxpt, mu.Pt())
            eta = min(maxeta, mu.AbsEta())

            effda = effhistDA_.GetBinContent( effhistDA_.FindBin(pt, eta) )
            effmc = effhistMC_.GetBinContent( effhistMC_.FindBin(pt, eta) )

            xda *= (1.-effda)
            xmc *= (1.-effmc)

        sf = (1. - xda) / (1. - xmc)
        return sf


