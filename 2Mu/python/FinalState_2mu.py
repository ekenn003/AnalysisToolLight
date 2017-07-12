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
from cuts import vh_cuts

## ___________________________________________________________
class Ana2Mu(AnalysisBase):
    def __init__(self, args):

        self.cuts = vh_cuts

        super(Ana2Mu, self).__init__(args)

        ##########################################################
        #                                                        #
        # Sync and debugging                                     #
        #                                                        #
        ##########################################################
        self.debug = False

        self.nMultipleDimuEvents = 0
        self.nSyncEvents = 0
        self.sync_low = 100. # GeV
        self.sync_high = 110. # GeV

        # signal region for control plots
        self.sigLow = 120. # GeV
        self.sigHigh = 130. # GeV



        ##########################################################
        #                                                        #
        # Some run options (defaults are False)                  #
        #                                                        #
        ##########################################################
        #self.do_pileup_reweighting = True
        self.include_trigger_scale_factors = True
        self.include_lepton_scale_factors = True

        self.use_rochester_corrections = True

        ##########################################################
        #                                                        #
        # Define event HLT requirement                           #
        #                                                        #
        ##########################################################
        self.hltriggers = self.cuts['HLT']
        self.path_for_trigger_scale_factors = self.cuts['HLTstring']



        ##########################################################
        #                                                        #
        # Initialize additional event counters                   #
        #                                                        #
        ##########################################################
        #self.cutflow.add('nEv_NoBJets', 'V(lep)h selection: Require 0 bjets')
        #self.cutflow.add('nEv_3or4Lep', 'V(lep)h selection: Require 1 or 2 extra isolated leptons')


        #self.cutflow.add('nEv_NoElectrons', 'Require 0 electrons')
        #self.cutflow.add('nEv_NoBJets', 'Require 0 bjets')
        #self.cutflow.add('nEv_2Jets', 'Require 2 jets')
        #self.cutflow.add('nEv_MET', 'Require <40 MET')




#        ##########################################################
#        #                                                        #
#        # Book additional histograms                             #
#        #                                                        #
#        ##########################################################
#        self.histograms['hNumDiMu'] = TH1F('hNumDiMu', 'hNumDiMu', 20, 0., 20.)
#        self.histograms['hNumDiMu'].GetXaxis().SetTitle('N_{#mu^{+}#mu^{-}}')
#        self.histograms['hNumDiMu'].GetYaxis().SetTitle('Candidates')
#
#        self.histograms['hMetMtWithMu'] = TH1F('hMetMtWithMu', 'hMetMtWithMu', 500, 0., 1000.)
#        self.histograms['hMetMtWithMu'].GetXaxis().SetTitle('M_{T}(#mu, MET)[GeV/c^{2}]')
#        self.histograms['hMetMtWithMu'].GetYaxis().SetTitle('Candidates/2.0[GeV/c^{2}]')


        ##########################################################
        #                                                        #
        # Book control plot histograms                           #
        #                                                        #
        ##########################################################
        # make control versions of new the plots - they won't all be filled though
        self.histograms_ctrl = {}
        for name in self.histograms.keys():
            self.histograms_ctrl[name+'_ctrl'] = self.histograms[name].Clone(
                self.histograms[name].GetName()+'_ctrl')
        # add it to the extra histogram map
        self.extra_histogram_map['control'] = self.histograms_ctrl




        ##########################################################
        #                                                        #
        # Book optimi. plot histograms                           #
        #                                                        #
        ##########################################################

        self.opt_met   = [ 30.,  40.,  50.]
        self.opt_djm   = [550., 650., 750.]
        self.opt_dje   = [  3.,  3.5,   4.]
        self.opt_djm_g = [200., 250., 300.]
        self.opt_dm_pt = [ 40.,  50.,  60.]

        # make control versions of new the plots - they won't all be filled though
        self.histograms_opt = {}
        #for name in self.histograms.keys():
        #    self.histograms_ctrl[name+'_ctrl'] = self.histograms[name].Clone(
        #        self.histograms[name].GetName()+'_ctrl')

        #self.itergrid = [(c,v,w,x,y,z) \
        #            for c in range(1,4) \
        #            for v in range(len(self.opt_met)) \
        #            for w in range(len(self.opt_djm)) \
        #            for x in range(len(self.opt_dje)) \
        #            for y in range(len(self.opt_djm_g)) \
        #            for z in range(len(self.opt_dm_pt))]


        #for c in xrange(1,4):
        #    for v in xrange(1,1+len(self.opt_met)):
        #        for w in xrange(1,1+len(self.opt_djm)):
        #            for x in xrange(1,1+len(self.opt_dje)):
        #                for y in xrange(1,1+len(self.opt_djm_g)):
        #                    for z in xrange(1,1+len(self.opt_dm_pt)):
        #for c, v, w, x, y, z in self.itergrid:
        #    hn = ('hDiMuInvMass_{1}{2}{3}{4}{5}_cat0{0}').format(c,v,w,x,y,z)
        #    self.histograms_opt[hn] = self.histograms['hDiMuInvMass'].Clone(hn)



        # add it to the extra histogram map
        #self.extra_histogram_map['opt'] = self.histograms_opt




        ##########################################################
        #                                                        #
        # Book category histograms                               #
        #                                                        #
        ##########################################################

        #self.categories = [
        #    'Category0_All',
        #    'Category1_VBFTight',
        #    'Category2_GGFTight',
        #    'Category3_VBFLoose',
        #    'Category4_01JetTight',
        #    'Category5_01JetLoose',
        #]
        self.fnumCat0 = 0
        self.fnumCat1 = 0
        self.fnumCat2 = 0
        self.fnumCat3 = 0
        self.fnumCat4 = 0
        self.fnumCat5 = 0
        self.fnumBucket = 0

        #category_hists = ['hVtxN', 'hMET', 'hDiMuPt', 'hDiMuInvMass', 'hNumMu', 'hMuPt']


        self.categories = ['cat'+str(i).zfill(2) for i in xrange(0,16)]


        self.histograms_categories = {}
        for name in self.histograms.keys():
            #if name not in category_hists: continue
            for cat in self.categories:
                self.histograms_categories[name+'_'+cat] = self.histograms[name].Clone(
                    (self.histograms[name].GetName()+'_'+cat))
            if name in ['hDiMuInvMass', 'hDiMuPt', 'hDiJetInvMass', 'hDiJetDeltaEta', 'hNumJets']:
                for kitten in ['k1', 'k2']:
                    self.histograms_categories[name+'_'+kitten] = self.histograms[name].Clone(
                        (self.histograms[name].GetName()+'_'+kitten))
        # add it to the extra histogram map
        self.extra_histogram_map['categories'] = self.histograms_categories






        ##########################################################
        #                                                        #
        # Book category control plot histograms                  #
        #                                                        #
        ##########################################################
        # make control versions of new the plots - they won't all be filled though
        self.histograms_categories_ctrl = {}
        for name in self.histograms_categories.keys():
            self.histograms_categories_ctrl[name+'_ctrl'] = self.histograms_categories[name
                ].Clone(self.histograms_categories[name].GetName()+'_ctrl')
        # add it to the extra histogram map
        self.extra_histogram_map['control'] = self.histograms_categories_ctrl

        ##########################################################
        #                                                        #
        # Set up trees for limit calculations                    #
        #                                                        #
        ##########################################################
        self.tEventNr = array('L', [0])
        self.tLumiNr  = array('L', [0])
        self.tRunNr   = array('L', [0])
        self.tInvMass = array('f', [0.])
        self.tEventWt = array('f', [0.])

        self.category_trees = []

        for i, cat in enumerate(self.categories):
            self.category_trees += [TTree(cat, cat)]
            self.category_trees[i].Branch('tEventNr', self.tEventNr, 'tEventNr/l')
            self.category_trees[i].Branch('tLumiNr', self.tLumiNr, 'tLumiNr/l')
            self.category_trees[i].Branch('tRunNr', self.tRunNr, 'tRunNr/l')
            self.category_trees[i].Branch('tInvMass', self.tInvMass, 'tInvMass/F')
            self.category_trees[i].Branch('tEventWt', self.tEventWt, 'tEventWt/F')


    ## _______________________________________________________
    def per_event_action(self):
        '''
        This is the core of the analysis loop. Selection is done here (not
        including event selection and preselection).
        This method only executes if the event passes event selection and
        preselection found in python/Preselection.
        '''

        thisrun = self.event.run()
        thislumi = self.event.lumi_block()
        thisevent = self.event.number()

        if len(self.good_muons) != 2: return

        vbfevtlist = [

            #153657,
            391898480,

        ]


        # sync
        #if thisevent not in vbfevtlist: return
        #printevtinfo = True
        printevtinfo = False

        #if thisevent in vbfevtlist: printevtinfo = True



        ##########################################################
        #                                                        #
        # Determine dimuon pairs                                 #
        #                                                        #
        ##########################################################


        if len(self.dimuon_pairs) > 1: self.nMultipleDimuEvents += 1
        pairindex1, pairindex2 = self.dimuon_pairs[0]
        muon1 = self.good_muons[pairindex1]
        muon2 = self.good_muons[pairindex2]
        dimuonobj = muon1.p4() + muon2.p4()
#
#        # pick which inv mass to put in limit tree
#
        mytInvMass = dimuonobj.M()
#
#        # decide whether to fill control plots
#        fill_control_plots = mytInvMass > self.sigHigh or mytInvMass < self.sigLow
        fill_control_plots = False


        ##########################################################
        #                                                        #
        # Determine category                                     #
        #                                                        #
        ##########################################################

        thisdimupt = dimuonobj.Pt()
        this_cat = -1
        self.fnumCat0 += 1

        # VBF tagged
        if (len(self.good_jets) > 1 
            and self.good_jets[0].pt() > self.cuts['VBF_lead_jet_pt']
            and self.good_jets[1].pt() > self.cuts['VBF_sublead_jet_pt']
            and self.met.et() < self.cuts['VBF_met']):


            thisdijetmass = (self.good_jets[0].p4() + self.good_jets[1].p4()).M()
            thisdijetdeta = abs(self.good_jets[0].eta() - self.good_jets[1].eta())

            # VBFTight
            if (thisdijetmass > self.cuts['VBF_dijet_mass'] 
                and thisdijetdeta > self.cuts['VBF_dijet_deta']):
                this_cat = 1
                self.fnumCat1 += 1
            # GGFTight
            elif (thisdijetmass > self.cuts['GGF_dijet_mass']
                and thisdimupt > self.cuts['GGF_dimu_pt']):
                this_cat = 2
                self.fnumCat2 += 1
            # VBFLoose
            else: 
                this_cat = 3
                self.fnumCat3 += 1

        # non-VBF tagged
        else:
            geo_cat = self.get_geo_cat(muon1, muon2)
            # 01JetTight
            if thisdimupt > self.cuts['nonVBF_dimu_pt']:
                self.fnumCat4 += 1
                if   geo_cat == 'BB': this_cat = 4
                elif geo_cat == 'BO': this_cat = 5
                elif geo_cat == 'BE': this_cat = 6
                elif geo_cat == 'OO': this_cat = 7
                elif geo_cat == 'OE': this_cat = 8
                elif geo_cat == 'EE': this_cat = 9
            # 01JetLoose
            else:
                self.fnumCat5 += 1
                if   geo_cat == 'BB': this_cat = 10
                elif geo_cat == 'BO': this_cat = 11
                elif geo_cat == 'BE': this_cat = 12
                elif geo_cat == 'OO': this_cat = 13
                elif geo_cat == 'OE': this_cat = 14
                elif geo_cat == 'EE': this_cat = 15






        ##########################################################
        #                                                        #
        # Calculate event weight                                 #
        #                                                        #
        ##########################################################
        eventweight_ = self.calculate_event_weight()
        #print 'eventweight_.base_event_weight =', eventweight_.base_event_weight
        #print 'eventweight_.pileup_factor =',     eventweight_.pileup_factor
        #print 'eventweight_.trigger_factor =',    eventweight_.trigger_factor
        #print 'eventweight_.lepton_factor =',     eventweight_.lepton_factor

        eventweight = eventweight_.full

        ##########################################################
        #                                                        #
        # Fill them histograms                                   #
        #                                                        #
        ##########################################################

        # fill base histograms
#        fill_base_histograms(self, eventweight, fill_control_plots)

#        # fill extra histograms
#        fill_category_hists(self, eventweight, fill_control_plots, this_cat, pairindex1, pairindex2)
#        #if len(self.good_muons)==3:
#        #    self.histograms['hMetMtWithMu'].Fill(self.met.MtWith(mu), eventweight)





        #twojetcondition = (len(self.good_jets) > 1 
        #        and self.good_jets[0].pt() > self.cuts['VBF_lead_jet_pt']
        #        and self.good_jets[1].pt() > self.cuts['VBF_sublead_jet_pt'])

        #if twojetcondition:
        #    thisdijetmass = (self.good_jets[0].p4() + self.good_jets[1].p4()).M()
        #    thisdijetdeta = abs(self.good_jets[0].eta() - self.good_jets[1].eta())

        #    for c, v, w, x, y, z in self.itergrid:
        #        # vwxyz defines a unique opt scheme
        #        this_opt_scheme = '{0}{1}{2}{3}{4}'.format(v,w,x,y,z)
        #        if self.met.et() < self.opt_met[v]:
        #            # VBFTight
        #            if (thisdijetmass > self.opt_djm[w]
        #                and thisdijetdeta > self.opt_dje[x]):
        #                this_opt_cat = 'cat01'
        #            # GGFTight
        #            elif (thisdijetmass > self.opt_djm_g[y]
        #                and thisdimupt > self.opt_dm_pt[z]):
        #                this_opt_cat = 'cat02'
        #            # VBFLoose
        #            else: 
        #                this_opt_cat = 'cat03'
        #            this_opt_hn = 'hDiMuInvMass_{0}_{1}'.format(
        #                this_opt_scheme, this_opt_cat)
        #            self.histograms_opt[this_opt_hn].Fill(mytInvMass, eventweight)


#
#        twojetcondition = (len(self.good_jets) > 1 
#            and self.good_jets[0].pt() > self.cuts['VBF_lead_jet_pt']
#            and self.good_jets[1].pt() > self.cuts['VBF_sublead_jet_pt'])
#
#
#        thisdijetmass = (self.good_jets[0].p4()
#            + self.good_jets[1].p4()).M() if twojetcondition else 0.
#        thisdijetdeta = abs(self.good_jets[0].eta()
#            - self.good_jets[1].eta()) if twojetcondition else 0.
#        thismet = self.met.et()
#
#        if twojetcondition and thismet < self.cuts['VBF_met']:
#            for eta_p, eta_cut in self.etacutmap.iteritems():
#                if thisdijetdeta > eta_cut:
#                    self.histograms_opt['hDiJetInvMass_'
#                        +eta_p].Fill(thisdijetmass, eventweight)
#
#        for met_p, met_cut in self.metcutmap.iteritems():
#            if thismet < met_cut:
#                self.histograms_opt['hNumJets_'
#                    +met_p].Fill(len(self.good_jets), eventweight)
#
#
#
#        if twojetcondition:
#            for eta_p, eta_cut in self.etacutmap.iteritems():
#                for met_p, met_cut in self.metcutmap.iteritems():
#                    if (thisdijetdeta > eta_cut and thismet < met_cut):
#                        hname = 'hDiMuInvMass_eta'+eta_p+'_met'+met_p
#                        self.histograms_opt[hname].Fill(mytInvMass, eventweight)
#





        if printevtinfo:
            #self.print_event_info(this_cat)
            self.print_event_info(2)
        

        #############################################################
        ####                                                        #
        #### Fill limit trees                                       #
        ####                                                        #
        #############################################################
        ###self.tEventNr[0] = self.event.Number()
        ###self.tLumiNr[0]  = self.event.LumiBlock()
        ###self.tRunNr[0]   = self.event.Run()
        ###self.tInvMass[0] = mytInvMass
        ###self.tEventWt[0] = eventweight


        ###if this_cat: self.category_trees[this_cat-1].Fill()

        ###for cat in self.categories:
        ###    if 'Category{0}'.format(this_cat) not in cat: continue
        ###    self.histograms_categories['hDiMuInvMass_'+self.categories[this_cat-1]].Fill(mytInvMass, eventweight)


    ## _______________________________________________________
    def end_of_job_action(self):
#        logging.info('nSyncEvents = ' + str(self.nSyncEvents))
        logging.info('Category1 (VBFTight) events   = {0}'.format(self.fnumCat1))
        logging.info('Category2 (GGFTight) events   = {0}'.format(self.fnumCat2))
        logging.info('Category3 (VBFLoose) events   = {0}'.format(self.fnumCat3))
        logging.info('Category4 (01JetTight) events = {0}'.format(self.fnumCat4))
        logging.info('Category5 (01JetLoose) events = {0}'.format(self.fnumCat5))
        logging.info('')
        logging.info('Category0 (Total) events      = {0}'.format(self.fnumCat0))
        logging.info('Multiple dimuon events        = {0}'.format(self.nMultipleDimuEvents))

    ## _______________________________________________________
    def get_geo_cat(self, m0, m1):
        n, n0, n1 = 0, 0, 0
        nB, nO, nE = self.cuts['nB'], self.cuts['nO'], self.cuts['nE']
        if m0.abs_eta() <= self.cuts['nB']: n0 = 4
        elif nB < m0.abs_eta() and m0.abs_eta() <= nO: n0 = 2
        elif nO < m0.abs_eta() and m0.abs_eta() <= nE: n0 = 1
        if m1.abs_eta() <= self.cuts['nB']: n1 = 4
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








