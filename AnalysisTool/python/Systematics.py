# AnalysisToolLight/AnalysisTool/python/Systematics.py
'''
Systematic class base
'''
import argparse
import logging
import os.path

import ROOT
from collections import OrderedDict, namedtuple

## ____________________________________________________________________________
class Systematic(object):
    '''
    Scale factor object
    '''
    # constructors/helpers
    def __init__(self, cmsswversion, datadir):
        self.cmsswversion = cmsswversion
        self.datadir = datadir


## ____________________________________________________________________________
class JetShifts(Systematic):
    # constructors/helpers
    def __init__(self, cmsswversion, datadir):
        super(JetShifts, self).__init__(cmsswversion, datadir)
        self.error = False

        filename = '{0}/systematics/jetshifts_{1}.root'.format(self.datadir,
            self.cmsswversion)

        logging.info('  Looking for jet shifts file '
            'at {0}'.format(filename))
        if not os.path.exists(filename):
            self.error = True
            logging.info('       *   ')
            logging.info('    *******')
            logging.info('    WARNING: Can\'t find jet shifts file.')
            logging.info('    *******')
            logging.info('       *   ')
            return
        else:
            # this is the file created by
            #     AnalysisTool/scripts/parse_jec_unc.py
            self.jsfile = ROOT.TFile(filename)


        # the histograms in the file are named hJetShiftDown and hJetShiftUp,
        #     with x axis: Pt, y axis: Eta
        self.js_down = self.hltfile.Get('hJetShiftDown')
        self.js_up   = self.hltfile.Get('hJetShiftUp')

        self.minpt  = self.js_down.GetXaxis().GetXmin() + 0.01
        self.maxpt  = self.js_down.GetXaxis().GetXmax() - 1.
        self.mineta = self.js_down.GetYaxis().GetXmin() + 0.01
        self.maxeta = self.js_down.GetYaxis().GetXmax() - 0.01


    # methods
    ## ________________________________________________________________________
    def get_shifted_pt(self, jet, direction):
        if self.error: return 1.

        if direction in ['down', 'up']:
            if direction == 'down':
                sign = -1.
                h = self.js_down
            elif direction == 'up':
                sign = 1.
                h = self.js_up
        else:
            raise ValueError('JetShifts get_shifted_pt: shifts can only be '
                '"up" or "down"; "{0}" not recognised.'.format(direction))

        # make sure vals in range
        pt_  = max(self.minpt, min(self.maxpt, jet.pt()))
        eta_ = max(self.mineta, min(self.maxeta, jet.eta()))

        shift = h.GetBinContent(
            h.GetXaxis().FindBin(pt_),
            h.GetYaxis().FindBin(eta_) )


        return pt_ * (1 + sign*shift)



    ## ________________________________________________________________________
    def __del__(self):
        try:
            self.jsfile.Close()
        except AttributeError:
            pass
