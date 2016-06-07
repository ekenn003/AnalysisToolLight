# AnalysisToolLight/AnalysisTool/python/ScaleFactors.py
'''
ScaleFactor class base
'''
import argparse
import logging

import ROOT
from collections import OrderedDict, namedtuple

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
        self.error = False

        self.pileupScale = []
        self.pileupScale_up = []
        self.pileupScale_down = []

        logging.info('  Looking for pileup file at {0}/pileup/pileup_{1}.root'.format(self.datadir, self.cmsswversion))
        # now we look for a file called pileup_76X.root or pileup_80X.root in datadir/pileup/
        try:
            pufile = ROOT.TFile('{0}/pileup/pileup_{1}.root'.format(self.datadir, self.cmsswversion))
            scalehist_ = pufile.Get('pileup_scale')

            # save scale factors in vectors where each index corresponds to the NumTruePileupInteractions
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

        # AttributeError: 'TObject' object has no attribute 'GetNbinsX' - happens if we couldn't find the file
        except AttributeError:
            logging.info('    *******')
            logging.info('    WARNING: Pileup file probably doesn\'t exist or was made improperly.')
            logging.info('    Will not include pileup reweighting.')
            logging.info('    *******')
            self.error = True

    # methods
    ## _______________________________________________________
    def getWeight(self, numtrueinteractions):
        if self.error: return 1.
        return self.pileupScale[int(round(numtrueinteractions))] if len(self.pileupScale) > numtrueinteractions else 0.
    ## _______________________________________________________
    def getWeightUp(self, numtrueinteractions):
        if self.error: return 1.
        return self.pileupScale_up[int(round(numtrueinteractions))] if len(self.pileupScale_up) > numtrueinteractions else 0.
    ## _______________________________________________________
    def getWeightDown(self, numtrueinteractions):
        if self.error: return 1.
        return self.pileupScale_down[int(round(numtrueinteractions))] if len(self.pileupScale_down) > numtrueinteractions else 0.








## ___________________________________________________________
class HLTScaleFactors(ScaleFactor):
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffsRun2
    # constructors/helpers
    def __init__(self, cmsswversion, datadir, hltrigger):
        super(HLTScaleFactors, self).__init__(cmsswversion, datadir)
        self.error = False

        # right now the only choice is single muon hlt
        if hltrigger=='IsoMu20_OR_IsoTkMu20':
            filename = 'singlemuontrigger'
        else:
            raise ValueError('Right now the only available HLT for scale factors is "IsoMu20_OR_IsoTkMu20".')

        logging.info('  Looking for scale factor file at {0}/scalefactors/{1}_{2}.root'.format(self.datadir, filename, self.cmsswversion))
        try:
            # this is the file created by AnalysisTool/scripts/collectTriggerScaleFactors.py
            self.hltfile = ROOT.TFile('{0}/scalefactors/{1}_{2}.root'.format(self.datadir, filename, self.cmsswversion))
            # the histograms in the file are named effMC and effDA, with x axis: Pt, y axis: AbsEta
            self.effhistDA_ = self.hltfile.Get('effDA')
            self.effhistMC_ = self.hltfile.Get('effMC')
            self.maxpt = self.effhistDA_.GetXaxis().GetXmax() - 1.
            self.maxeta = self.effhistDA_.GetYaxis().GetXmax()

        except AttributeError:
            logging.info('    *******')
            logging.info('    WARNING: HLT scale factors file probably doesn\'t exist or was made improperly.')
            logging.info('    Will not include trigger scale factors.')
            logging.info('    *******')
            self.error = True

    # methods
    def getScale(self, muons):
        if self.error: return 1.

        xda = 1.
        xmc = 1.
        for mu in muons:
            # make sure the muon is in range
            pt_ = min(self.maxpt, mu.Pt())
            eta_ = min(self.maxeta, mu.AbsEta())
            # find efficiencies for this muon
            effda = self.effhistDA_.GetBinContent( self.effhistDA_.GetXaxis().FindBin(pt_) , self.effhistDA_.GetYaxis().FindBin(eta_))
            effmc = self.effhistMC_.GetBinContent( self.effhistMC_.GetXaxis().FindBin(pt_) , self.effhistMC_.GetYaxis().FindBin(eta_))
            # update total efficiency
            xda *= (1. - effda)
            xmc *= (1. - effmc)
        # calculate scale factor and return it
        return (1.-xda)/(1.-xmc) if (xmc!= 1.) else 1.


    ## _______________________________________________________
    def __del__(self):
        self.hltfile.Close()


## ___________________________________________________________
class MuonScaleFactors(ScaleFactor):
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffsRun2
    # constructors/helpers
    def __init__(self, cmsswversion, datadir):
        super(MuonScaleFactors, self).__init__(cmsswversion, datadir)
        self.error = False

        self.muonideffs = {
            'looseID' : {},
            'softID' : {},
            'mediumID' : {},
            'tightID' : {},
        }
        self.muonisoeffs = {
            'looseIso_looseID' : {},
            'looseIso_mediumID' : {},
            'looseIso_tightID' : {},
            'tightIso_mediumID' : {},
            'tightIso_tightID' : {},
        }

        logging.info('  Looking for muon scale factor file at {0}/scalefactors/muonidiso_{1}.root'.format(self.datadir, self.cmsswversion))
        try:
            # this is the file created by AnalysisTool/scripts/collectMuonScaleFactors.py
            self.mufile = ROOT.TFile('{0}/scalefactors/muonidiso_{1}.root'.format(self.datadir, self.cmsswversion))
            # the histograms in the file have x axis: Pt, y axis: AbsEta
            for cut in self.muonideffs:
                self.muonideffs[cut]['RATIO'] = ROOT.TH2F(self.mufile.Get(cut))
            for cut in self.muonisoeffs:
                self.muonisoeffs[cut]['RATIO'] = ROOT.TH2F(self.mufile.Get(cut))

            self.maxpt  = self.muonideffs['softID']['RATIO'].GetXaxis().GetXmax() - 1.
            self.maxeta = self.muonideffs['softID']['RATIO'].GetYaxis().GetXmax()

        except AttributeError:
            logging.info('    *******')
            logging.info('    WARNING: Muon scale factors file probably doesn\'t exist or was made improperly.')
            logging.info('    Will not include trigger scale factors.')
            logging.info('    *******')
            self.error = True


    # methods
    ## _______________________________________________________
    def getIdScale(self, muons, idcut):
        '''
        Returns the total scale factor for a list of muons
        for ID cuts.
        '''
        if self.error: return 1.

        if idcut in ['soft', 'loose', 'medium', 'tight']:
            cut = '{0}ID'.format(idcut)
        else:
            raise ValueError('Muon getIdScale: id "{0}" not recognised.'.format(idcut))

        sf = 1.
        for mu in muons:
            # make sure the muon is in range
            pt_ = min(self.maxpt, mu.Pt())
            eta_ = min(self.maxeta, mu.AbsEta())
            # find efficiencies for this muon
            musf = self.muonideffs[cut]['RATIO'].GetBinContent( self.muonideffs[cut]['RATIO'].GetXaxis().FindBin(pt_) , self.muonideffs[cut]['RATIO'].GetYaxis().FindBin(eta_) )
            if not musf: 
                print 'found ID eff {0} for mu pt = {1}, eta = {2}'.format(musf, pt_, eta_)
            # update total efficiency
            sf *= musf

        return sf


    ## _______________________________________________________
    def getIsoScale(self, muons, idcut, isocut):
        '''
        Returns the total scale factor for a list of muons
        for ID and isolation cuts. The efficiencies for these two cuts
        are already merged and located in a single TH2F.
        '''
        if self.error: return 1.

        # input validation
        if isocut=='loose':
            if idcut in ['loose', 'medium', 'tight']:
                cut = '{0}Iso_{1}ID'.format(isocut, idcut)
            else:
                raise ValueError('Muon getIsoScale: ID "{0}" not recognised, or you are trying to use an invalid ID+Iso pairing ({0}+{1}.'.format(idcut, isocut))
        elif isocut=='tight':
            if idcut in ['medium', 'tight']:
                cut = '{0}Iso_{1}ID'.format(isocut, idcut)
            else:
                raise ValueError('Muon getIsoScale: ID "{0}" not recognised, or you are trying to use an invalid ID+Iso pairing ({0}+{1}.'.format(idcut, isocut))
        else:
            raise ValueError('Muon getIsoScale: Iso "{0}" not recognised.'.format(isocut))

        # find scale factor
        sf = 1.
        for mu in muons:
            # make sure the muon is in range
            pt_ = min(self.maxpt, mu.Pt())
            eta_ = min(self.maxeta, mu.AbsEta())
            # find efficiencies for this muon
            musf = self.muonisoeffs[cut]['RATIO'].GetBinContent( self.muonisoeffs[cut]['RATIO'].GetXaxis().FindBin(pt_) , self.muonisoeffs[cut]['RATIO'].GetYaxis().FindBin(eta_) )
            if not musf: 
                print 'found Iso eff {0} for mu pt = {1}, eta = {2}'.format(musf, pt_, eta_)
            # update total efficiency
            sf *= musf

        return sf


    ## _______________________________________________________
    def __del__(self):
        self.mufile.Close()

