# FinalState_2mu.py
import itertools
import argparse
import sys, logging
from ROOT import TTree, TH1F
from array import array
from AnalysisToolLight.AnalysisTool.tools.tools import *
from AnalysisToolLight.AnalysisTool.CutFlow import CutFlow
from AnalysisToolLight.AnalysisTool.AnalysisBase import AnalysisBase
from AnalysisToolLight.AnalysisTool.AnalysisBase import main as analysisBaseMain
from AnalysisToolLight.AnalysisTool.Preselection import get_event_category
from AnalysisToolLight.AnalysisTool.histograms import fill_category_hists
from cuts import vh_cuts as cuts

## ___________________________________________________________
class Ana2Mu(AnalysisBase):
    def __init__(self, args):

        self.cuts = cuts

        super(Ana2Mu, self).__init__(args)
        self.debug = False

        self.sigLow = 120. # GeV
        self.sigHigh = 130. # GeV
        self.do_pileup_reweighting = True
        self.include_trigger_scale_factors = True
        self.include_lepton_scale_factors = True
        self.use_rochester_corrections = True

        self.hltriggers = cuts['HLT']
        self.path_for_trigger_scale_factors = cuts['HLTstring']



        #basehist2D = ROOT.TH2D('hDiMuInvMass', 'hDiMuInvMass', 3, 110., 140., 3, 110., 140.)

        self.histograms_scan = {}

        # book step 1 histograms
        # met
        # dijet mass
        # dijet deta
        # dimu pt


        met_hist = TH1F('hMET', 'hMET', 500, 0., 500.)
        met_hist.GetXaxis().SetTitle('E_{T miss}[GeV/c]')
        met_hist.GetYaxis().SetTitle('Candidates/2.0[GeV/c]')

        dijetmass_hist = TH1F('hDiJetInvMass', 'hDiJetInvMass', 2000, 0, 1000)
        dijetmass_hist.GetXaxis().SetTitle('M_{j^{+}j^{-}} [GeV/c^{2}]')
        dijetmass_hist.GetYaxis().SetTitle('Candidates/0.5[GeV/c^{2}]')

        dijetdeta_hist = TH1F('hDiJetDeltaEta', 'hDiJetDeltaEta',  132, 0., 6.6)
        dijetdeta_hist.GetXaxis().SetTitle('|#Delta #eta_{j^{+} - j^{-}}|')
        dijetdeta_hist.GetYaxis().SetTitle('Candidates/0.1')

        dimupt_hist = TH1F('hDiMuPt', 'hDiMuPt', 500, 0., 1000.)
        dimupt_hist.GetXaxis().SetTitle('p_{T #mu^{+}#mu^{-}}[GeV/c]')
        dimupt_hist.GetYaxis().SetTitle('Candidates/2.0[GeV]')

        # MET
        for dijetmassvbf in range(2):
            for dijetmass in range(2):
                for dijetdeta in range(2):
                    for dimuptggf in range(2):
                        for dimupt in range(2):
                            # dijetmassvbf is always higher than dijetmass
                            if dijetmassvbf and not dijetmass: continue
                            # dimuptggf is always higher than dimupt
                            if dimuptggf and not dimupt: continue
                            hname = ('hMET_dijetmassvbf{0}_dijetmass{1}_dijetdeta{2}_'
                                     'dimuptggf{3}_dimupt{4}').format(dijetmassvbf,
                                         dijetmass, dijetdeta, dimuptggf, dimupt)
                            print hname
                            self.histograms_scan[hname] = met_hist.Clone(hname)

        # dijetmass vbf
        for met in range(2):
            for dijetmass in range(2):
                for dijetdeta in range(2):
                    for dimuptggf in range(2):
                        for dimupt in range(2):
                            # dimuptggf is always higher than dimupt
                            if dimuptggf and not dimupt: continue
                            hname = ('hDiJetInvMassVBF_met{0}_dijetmass{1}_dijetdeta{2}_'
                                     'dimuptggf{3}_dimupt{4}').format(met,
                                         dijetmass, dijetdeta, dimuptggf, dimupt)
                            print hname
                            self.histograms_scan[hname] = dijetmass_hist.Clone(hname)

        # dijetmass ggf
        for met in range(2):
            for dijetmassvbf in range(2):
                for dijetdeta in range(2):
                    for dimuptggf in range(2):
                        for dimupt in range(2):
                            # dimuptggf is always higher than dimupt
                            if dimuptggf and not dimupt: continue
                            hname = ('hDiJetInvMass_met{0}_dijetmassvbf{1}_dijetdeta{2}_'
                                     'dimuptggf{3}_dimupt{4}').format(met,
                                         dijetmassvbf, dijetdeta, dimuptggf, dimupt)
                            print hname
                            self.histograms_scan[hname] = dijetmass_hist.Clone(hname)

        # dijet d eta
        for met in range(2):
            for dijetmassvbf in range(2):
                for dijetmass in range(2):
                    for dimuptggf in range(2):
                        for dimupt in range(2):
                            # dijetmassvbf is always higher than dijetmass
                            if dijetmassvbf and not dijetmass: continue
                            # dimuptggf is always higher than dimupt
                            if dimuptggf and not dimupt: continue
                            hname = ('hDiJetDeltaEta_met{0}_dijetmassvbf{1}_dijetmass{2}_'
                                     'dimuptggf{3}_dimupt{4}').format(met,
                                         dijetmassvbf, dijetmass, dimuptggf, dimupt)
                            print hname
                            self.histograms_scan[hname] = dijetdeta_hist.Clone(hname)


        # dimupt ggf
        for met in range(2):
            for dijetmassvbf in range(2):
                for dijetmass in range(2):
                    for dijetdeta in range(2):
                        for dimupt in range(2):
                            # dijetmassvbf is always higher than dijetmass
                            if dijetmassvbf and not dijetmass: continue
                            hname = ('hDiMuPtGGF_met{0}_dijetmassvbf{1}_dijetmass{2}_'
                                     'dijetdeta{3}_dimupt{4}').format(met,
                                         dijetmassvbf, dijetmass, dijetdeta, dimupt)
                            print hname
                            self.histograms_scan[hname] = dimupt_hist.Clone(hname)


        # dimupt
        for met in range(2):
            for dijetmassvbf in range(2):
                for dijetmass in range(2):
                    for dijetdeta in range(2):
                        for dimuptggf in range(2):
                            # dijetmassvbf is always higher than dijetmass
                            if dijetmassvbf and not dijetmass: continue
                            hname = ('hDiMuPt_met{0}_dijetmassvbf{1}_dijetmass{2}_'
                                     'dijetdeta{3}_dimuptggf{4}').format(met,
                                         dijetmassvbf, dijetmass, dijetdeta, dimuptggf)
                            print hname
                            self.histograms_scan[hname] = dimupt_hist.Clone(hname)










        # add it to the extra histogram map
        self.extra_histogram_map['scan'] = self.histograms_scan




    ## _______________________________________________________
    def per_event_action(self):
        '''
        This is the core of the analysis loop. Selection is done here (not
        including event selection and preselection).
        This method only executes if the event passes event selection and
        preselection found in python/Preselection.
        '''


        if len(self.good_muons) != 2: return

        printevtinfo = False


        pairindex1, pairindex2 = self.dimuon_pairs[0]
        muon1 = self.good_muons[pairindex1]
        muon2 = self.good_muons[pairindex2]
        dimuonobj = muon1.p4() + muon2.p4()
        mytInvMass = dimuonobj.M()
        # only keep signal window 
        if mytInvMass > self.sigHigh or mytInvMass < self.sigLow: return
        eventweight_ = self.calculate_event_weight()
        eventweight = eventweight_.full

        ##########################################################
        #                                                        #
        #                                                        #
        ##########################################################
        thisdimupt = dimuonobj.Pt()
        thismet = self.met.et()

        # VBF tagged
        twojetcondition = (len(self.good_jets) > 1 
            and self.good_jets[0].pt() > cuts['VBF_lead_jet_pt']
            and self.good_jets[1].pt() > cuts['VBF_sublead_jet_pt'])


        thisdijetmass = (self.good_jets[0].p4() + self.good_jets[1].p4()).M() if twojetcondition else 0.
        thisdijetdeta = abs(self.good_jets[0].eta() - self.good_jets[1].eta()) if twojetcondition else 0.

        b_met = int(thismet > 40.)
        b_dijetmassvbf = int(thisdijetmass > 650.)
        b_dijetmass = int(thisdijetmass > 250.)
        b_dijetdeta = int(thisdijetdeta > 3.5)
        b_dimuptggf = int(thisdimupt > 50.)
        b_dimupt = int(thisdimupt > 10.)

        thishMET = ('hMET_dijetmassvbf{0}_dijetmass{1}_dijetdeta{2}_'
                    'dimuptggf{3}_dimupt{4}').format(b_dijetmassvbf, b_dijetmass, 
                        b_dijetdeta, b_dimuptggf, b_dimupt)


        thishDiJetInvMassVBF = ('hDiJetInvMassVBF_met{0}_dijetmass{1}_dijetdeta{2}_'
                 'dimuptggf{3}_dimupt{4}').format(b_met, b_dijetmass,
                     b_dijetdeta, b_dimuptggf, b_dimupt)


        thishDiJetInvMass = ('hDiJetInvMass_met{0}_dijetmassvbf{1}_dijetdeta{2}_'
                 'dimuptggf{3}_dimupt{4}').format(b_met, b_dijetmassvbf,
                     b_dijetdeta, b_dimuptggf, b_dimupt)

        thishDiJetDeltaEta = ('hDiJetDeltaEta_met{0}_dijetmassvbf{1}_dijetmass{2}_'
                 'dimuptggf{3}_dimupt{4}').format(b_met, b_dijetmassvbf,
                     b_dijetmass, b_dimuptggf, b_dimupt)

        thishDiMuPtGGF = ('hDiMuPtGGF_met{0}_dijetmassvbf{1}_dijetmass{2}_'
                 'dijetdeta{3}_dimupt{4}').format(b_met, b_dijetmassvbf, b_dijetmass,
                     b_dijetdeta, b_dimupt)

        thishDiMuPt = ('hDiMuPt_met{0}_dijetmassvbf{1}_dijetmass{2}_'
                 'dijetdeta{3}_dimuptggf{4}').format(b_met, b_dijetmassvbf, b_dijetmass,
                     b_dijetdeta, b_dimuptggf)





        self.histograms_scan[thishMET].Fill(thismet, eventweight)
        self.histograms_scan[thishDiJetInvMassVBF].Fill(thisdijetmass, eventweight)
        self.histograms_scan[thishDiJetInvMass].Fill(thisdijetmass, eventweight)
        self.histograms_scan[thishDiJetDeltaEta].Fill(thisdijetdeta, eventweight)
        self.histograms_scan[thishDiMuPtGGF].Fill(thisdimupt, eventweight)
        self.histograms_scan[thishDiMuPt].Fill(thisdimupt, eventweight)

#            # VBFTight
#            if (thisdijetmass > cuts['VBF_dijet_mass'] 
#                and thisdijetdeta > cuts['VBF_dijet_deta']):
#                this_cat = 1
#                self.fnumCat1 += 1
#            # GGFTight
#            elif (thisdijetmass > cuts['GGF_dijet_mass']
#                and thisdimupt > cuts['GGF_dimu_pt']):
#                this_cat = 2
#                self.fnumCat2 += 1
#            # VBFLoose
#            else: 
#                this_cat = 3
#                self.fnumCat3 += 1
#
#        # non-VBF tagged
#        else:
#            geo_cat = self.get_geo_cat(muon1, muon2)
#            # 01JetTight
#            if thisdimupt > cuts['nonVBF_dimu_pt']:
#                self.fnumCat4 += 1
#                if   geo_cat == 'BB': this_cat = 4
#                elif geo_cat == 'BO': this_cat = 5
#                elif geo_cat == 'BE': this_cat = 6
#                elif geo_cat == 'OO': this_cat = 7
#                elif geo_cat == 'OE': this_cat = 8
#                elif geo_cat == 'EE': this_cat = 9
#            # 01JetLoose
#            else:
#                self.fnumCat5 += 1
#                if   geo_cat == 'BB': this_cat = 10
#                elif geo_cat == 'BO': this_cat = 11
#                elif geo_cat == 'BE': this_cat = 12
#                elif geo_cat == 'OO': this_cat = 13
#                elif geo_cat == 'OE': this_cat = 14
#                elif geo_cat == 'EE': this_cat = 15
#
#
#








    ## _______________________________________________________
    def end_of_job_action(self):
        pass
##        logging.info('nSyncEvents = ' + str(self.nSyncEvents))
#        logging.info('Category1 (VBFTight) events   = {0}'.format(self.fnumCat1))
#        logging.info('Category2 (GGFTight) events   = {0}'.format(self.fnumCat2))
#        logging.info('Category3 (VBFLoose) events   = {0}'.format(self.fnumCat3))
#        logging.info('Category4 (01JetTight) events = {0}'.format(self.fnumCat4))
#        logging.info('Category5 (01JetLoose) events = {0}'.format(self.fnumCat5))
#        logging.info('')
#        logging.info('Category0 (Total) events      = {0}'.format(self.fnumCat0))

    ## _______________________________________________________
    def get_geo_cat(self, m0, m1):
        n, n0, n1 = 0, 0, 0
        nB, nO, nE = self.cuts['nB'], self.cuts['nO'], self.cuts['nE']
        if m0.abs_eta() <= cuts['nB']: n0 = 4
        elif nB < m0.abs_eta() and m0.abs_eta() <= nO: n0 = 2
        elif nO < m0.abs_eta() and m0.abs_eta() <= nE: n0 = 1
        if m1.abs_eta() <= cuts['nB']: n1 = 4
        elif nB < m1.abs_eta() and m1.abs_eta() <= nO: n1 = 2
        elif nO < m1.abs_eta() and m1.abs_eta() <= nE: n1 = 1
        n = n0+n1
        if   n==8: return 'BB'
        elif n==6: return 'BO'
        elif n==5: return 'BE'
        elif n==4: return 'OO'
        elif n==3: return 'OE'
        elif n==2: return 'EE'
        return 'XX'




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








