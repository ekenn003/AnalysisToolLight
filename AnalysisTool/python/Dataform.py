# AnalysisToolLight/AnalysisTool/python/Dataform.py
'''
See RootMaker/RootMaker/python/objectBase.py
'''

from ROOT import TVector3, TLorentzVector
import math
from collections import OrderedDict, namedtuple


## ___________________________________________________________
class Event(object):
    '''
    Event object
    '''
    # constructors/helpers
    def __init__(self, tree, sumweights):
        self.tree = tree
        self.sumweights = sumweights
    def _get(self, var): return getattr(self.tree, var)

    # methods
    def number(self):        return self.tree.event_nr
    def run(self):           return self.tree.event_run
    def time_unix(self):     return self.tree.event_timeunix
    def time_microsec(self): return self.tree.event_timemicrosec
    def lumi_block(self):    return self.tree.event_luminosityblock
    def rho(self):           return self.tree.event_rho
    # pileup
    def num_pileup_interactions(self):
        return self.tree.numpileupinteractions
    def num_pileup_interactions_minus(self):
        return self.tree.numpileupinteractionsminus
    def num_pileup_interactions_plus(self):
        return self.tree.numpileupinteractionsplus
    def num_true_pileup_interactions(self):
        return self.tree.numtruepileupinteractions
    # generator info
    def gen_weight(self): return (self.tree.genweight)
    def gen_id1(self):    return self.tree.genid1
    def genx1(self):      return self.tree.genx1
    def gen_id2(self):    return self.tree.genid2
    def genx2(self):      return self.tree.genx2
    def gen_scale(self):  return self.tree.genScale

    ## _______________________________________________________
    def print_available_tau_discriminators(self):
        print 'Available discriminators are:'
        for x in self.tree.GetListOfBranches():
            if 'tau_tdisc_' in x.GetName(): print '    ' + x.GetName()[10:]
        print '\n'

    ## _______________________________________________________
    def print_available_btags(self):
        print 'Available btags are:'
        for x in self.tree.GetListOfBranches():
            if 'ak4pfchsjet_btag_' in x.GetName(): print '    ' + x.GetName()[17:]
        print '\n'

    ## _______________________________________________________
    def passes_HLTs(self, paths):
        ''' Returnsbool whether any of the triggers fired
        '''
        result = False
        for pathname in paths:
            try:
                result = result or self._get('passes_'+pathname)
            except AttributeError:
                print 'PassesHLTs: Event HLT path "' + pathname + '" not available.'
                #print 'Available paths are:'
                #for x in self.tree.GetListOfBranches():
                #    if 'event_hlt_passes_' in x.GetName():
                #        print '    ' + x.GetName()[17:]
                #print '\n'
        return result

    ## _______________________________________________________
    def any_is_prescaled(self, paths):
        # initialise empty map of results
        results = {}
        for pathname in paths:
            try:
                prescale = self._get('prescale_hlt_'+pathname)
            except AttributeError:
                pass
                #print 'AnyIsPrescaled: '
                #      'Event HLT path "{0}" not available.'.format(pathname)
                #print 'Available paths are:'
                #for x in self.tree.GetListOfBranches():
                #    if 'event_hlt_passes_' in x.GetName():
                #        print '    ' + x.GetName()[17:]
                #print '\n'
                #raise
            # only store results that are prescaled
            if prescale != 1: results[pathname] = prescale

        # check if we had any paths that were prescaled
        for x in results:
            print 'HLT path {0} has a prescale of {1}.'.format(x, results[x])
        return True if results else False

    ## _______________________________________________________
    def get_prescale(self, pathname):
        try:
            return self._get('prescale_hlt_'+pathname)
        except AttributeError:
            pass
        return -1


## ___________________________________________________________
class Vertex(object):
    '''
    Vertices from reco::Vertex objects
    '''
    # constructors/helpers
    def __init__(self, tree, entry):
        self.tree = tree
        self.candName = 'primvertex'
        self.entry = entry
    def _get(self, var): 
        return getattr(self.tree, '{0}_{1}'.format('primvertex', var))[self.entry]

    # methods
    def x(self): return self._get('x')
    def y(self): return self._get('y')
    def z(self): return self._get('z')
    def x_error(self): return self._get('xError')
    def y_error(self): return self._get('yError')
    def z_error(self): return self._get('zError')
    def chi2(self):      return self._get('chi2')
    def n_dof(self):     return self._get('ndof')
    def n_tracks(self):  return self._get('ntracks')
    def norm_chi2(self): return self._get('normalizedChi2')
    def is_valid(self):  return self._get('isvalid')
    def is_fake(self):   return self._get('isfake')
    def rho(self):       return self._get('rho')


## ___________________________________________________________
class METBase(object):
    '''
    Basic objects from reco::PFMET objects
    '''
    # constructors/helpers
    def __init__(self, tree, metName, entry):
        self.tree = tree
        self.metName = metName
        self.entry = entry
    def _get(self, var):
        return getattr(self.tree, '{0}_{1}'.format(self.metName, var))[self.entry]

    # methods
    def e(self):  return TVector3(self._get('ex'), self._get('ey'), 0.)
    def et(self): return self._get('et')
    def p4(self): 
        thisp4 = TLorentzVector()
        thisp4.SetPtEtaPhiM(self._get('et'), 0., self._get('phi'), 0.)
        return thisp4

    def phi(self):     return self._get('phi')
    def raw_et(self):  return self._get('rawet')
    def raw_phi(self): return self._get('rawphi')
    def mt_with(self, *cands):
        myP4 = self.p4()
        lepP4 = TLorentzVector()
        for lep in cands: lepP4 += lep.p4()
        # squared transverse mass of system = 
        #     (met.Et + lep.Et)^2 - (met + lep).Pt)^2
        mt = math.sqrt(abs((lepP4.et() + myP4.et())**2 - ((lepP4 + myP4).pt())**2))
        return mt


## ___________________________________________________________
class PFMETTYPE1(METBase):
    # constructors/helpers
    def __init__(self, tree, entry):
       super(PFMETTYPE1, self).__init__(tree, 'pfmettype1', entry)

    # methods



## ___________________________________________________________
class CandBase(object):
    '''
    Basic objects from reco::Candidate objects
    p4 = TLorentzVector(pt, eta, phi, mass)
    '''
    # constructors/helpers
    def __init__(self, tree, candName, entry):
        self.tree = tree
        self.candName = candName
        self.entry = entry
    def _get(self, var):
        return getattr(self.tree, '{0}_{1}'.format(self.candName, var))[self.entry]

    # misc methods
    def rho(self): return self.tree.event_rho
    def delta_r(self, cand): return deltaR(self, cand)

    # methods
    def p(self):
        return TVector3(self._get('px'), self._get('py'), self._get('pz'))
    def pt(self):      return self._get('pt')
    def eta(self):     return self._get('eta')
    def abs_eta(self): return abs(self._get('eta'))
    def phi(self):     return self._get('phi')
    def energy(self):  return self._get('energy')
    def p4(self):
        thisp4 = TLorentzVector()
        thisp4.SetPtEtaPhiM(self.pt(), self.eta(), self.phi(), self.mass())
        return thisp4
    def charge(self): return self._get('charge')
    def mass(self):   return self._get('mass')
    def pdg_id(self): return self._get('pdgid')



## ___________________________________________________________
class CommonCand(CandBase):
    # constructors/helpers
    def __init__(self, tree, obtype, entry):
       super(CommonCand, self).__init__(tree, obtype, entry)

    # methods
    #gen*

## ___________________________________________________________
class JettyCand(CandBase):
    # constructors/helpers
    def __init__(self, tree, jttype, entry):
       super(JettyCand, self).__init__(tree, jttype, entry)

    # methods
    #genJet*

## ___________________________________________________________
class EgammaCand(CommonCand):
    # constructors/helpers
    def __init__(self, tree, egtype, entry):
       super(EgammaCand, self).__init__(tree, egtype, entry)

    # methods
    def effective_area(self): return self._get('effectiveArea')
    # isolation
    def iso_PFr3_charged(self): return self._get('isolationpfr3charged')
    def iso_PFr3_photon(self):  return self._get('isolationpfr3photon')
    def iso_PFr3_neutral(self): return self._get('isolationpfr3neutral')
    def iso_r3_track(self):     return self._get('isolationr3track')
    def iso_r3_ecal(self):      return self._get('isolationr3ecal')
    def iso_r3_hcal(self):      return self._get('isolationr3hcal')
    def iso_r4_track(self):     return self._get('isolationr4track')
    def iso_r4_ecal(self):      return self._get('isolationr4ecal')
    def iso_r4_hcal(self):      return self._get('isolationr4hcal')
    # corrected relative isolation
    def iso_PFr3dB_comb_rel(self):
        isoval = (
            (self._get('isolationpfr3charged')
            + max(0.0, (self._get('isolationpfr3neutral')
                        + self._get('isolationpfr3photon')
                        - 0.5 * self._get('isolationpfr3chargedpu'))
                 )
            ) / self._get('pt')
        )
        return isoval
    # corrected relative isolation
    def iso_PFr3rho_comb_rel(self):
        isoval = (
            (self._get('isolationpfr3charged')
            + max(0.0, (self._get('isolationpfr3neutral')
                     + self._get('isolationpfr3photon')
                     - self.rho() * self._get('effectiveArea'))
                 )
            ) / self._get('pt')
        )
        return isoval



## ___________________________________________________________
class Muon(CommonCand):
    '''
    Muon: 
    p4(), pt(), eta(), phi(), and energy() all return uncorrected values by
    default. To use the rochester corrections (assuming they are available
    in the ntuple), turn on the option self.use_rochester_corrections, or
    you can also explicitly call:
        mu.pt('corr') and mu.pt('uncorr')
    '''
    # constructors/helpers
    def __init__(self, tree, entry, corrected):
       super(Muon, self).__init__(tree, 'muon', entry)
       self.corrected = corrected

    # methods
    def dz(self):        return self._get('dz')
    def dz_error(self):  return self._get('dzerr')
    def dxy(self):       return self._get('dxy')
    def dxy_error(self): return self._get('dxyerr')

    def pt(self, correction=''):
        uncor = self._get('pt')
        cor   = self._get('rochesterPt')
        # decide which value to return
        if correction == 'corr':   return cor
        if correction == 'uncorr': return uncor
        if self.corrected: return cor
        return uncor

    def pt_roch(self):
        return self._get('rochesterPt')

    def p4(self, correction=''): # pt, eta, phi, m
        corrp4 = TLorentzVector()
        corrp4.SetPtEtaPhiM(self.pt('corr'), self.eta(),
                            self.phi(), self.mass())
        uncorrp4 = TLorentzVector()
        uncorrp4.SetPtEtaPhiM(self.pt('uncorr'), self.eta(),
                              self.phi(), self.mass())
        # decide which value to return
        if correction == 'corr':     return corrp4
        elif correction == 'uncorr': return uncorrp4
        elif self.corrected:         return corrp4
        else: return uncorrp4

    # energy
    def ecal_energy(self): return self._get('ecalenergy')
    def hcal_energy(self): return self._get('hcalenergy')
    # muon ID
    def is_tight(self):      return self._get('is_tight_muon')
    def is_medium(self):     return self._get('is_medium_muon')
    def is_medium2016(self): return self._get('is_medium2016_muon')
    def is_loose(self):      return self._get('is_loose_muon')
    # track info
    def is_PF_muon(self):    return self._get('is_pf_muon')
    def is_global(self):     return self._get('is_global')
    def is_tracker(self):    return self._get('is_tracker')
    def is_standalone(self): return self._get('is_standalone')
    def is_calo(self):       return self._get('is_calo')
    def pt_error(self): return self._get('pterror')
    def chi2(self):     return self._get('chi2')
    def n_dof(self):    return self._get('ndof')
    def num_valid_muon_hits(self):  return self._get('numvalidmuonhits')
    def num_chambers(self):         return self._get('numchambers')
    def num_matched_stations(self): return self._get('nummatchedstations')
    def num_chambers_with_segments(self):
        return self._get('numchamberswithsegments')
    # inner track
    def has_inner_track(self): return self._get('hasinnertrack')
    def inner_track_dz(self):        return self._get('innertrack_dz')
    def inner_rack_dz_error(self):   return self._get('innertrack_dzerr')
    def inner_track_dxy(self):       return self._get('innertrack_dxy')
    def inner_track_dxy_error(self): return self._get('innertrack_dxyerr')
    def inner_track_chi2(self):   return self._get('innertrack_chi2')
    def inner_track_n_dof(self):  return self._get('innertrack_ndof')
    def inner_track_charge(self): return self._get('innertrack_charge')
    def inner_track_n_hits(self): return self._get('innertrack_nhits')
    def inner_track_n_missing_hits(self):
       return self._get('innertrack_nmissinghits')
    def inner_track_n_pixel_hits(self):
        return self._get('innertrack_npixelhits')
    def inner_track_n_pixel_layers(self):
        return self._get('innertrack_npixellayers')
    def inner_track_n_strip_layers(self):
        return self._get('innertrack_nstriplayers')
    # outer track
    def has_outer_track(self): return self._get('hasoutertrack')
    def outer_track_chi2(self):   return self._get('outertrack_chi2')
    def outer_track_n_dof(self):  return self._get('outertrack_ndof')
    def outer_track_n_hits(self): return self._get('outertrack_hits')
    def outer_track_n_missing_hits(self):
        return self._get('outertrack_missinghits')
    # isolation r3
    def iso_PFr3_charged_hadrons(self):
        return self._get('pfisolationr3_sumchargedhadronpt')
    def iso_PFr3_charged_particles(self):
        return self._get('pfisolationr3_sumchargedparticlept')
    def iso_PFr3_neutral_hadrons(self):
        return self._get('pfisolationr3_sumneutralhadronet')
    def iso_PFr3_sum_photon_et(self):
        return self._get('pfisolationr3_sumphotonet')
    def iso_PFr3_sum_PU_pt(self):
        return self._get('pfisolationr3_sumpupt')
    # isolation r4
    def iso_PFr4_charged_hadrons(self):
        return self._get('pfisolationr4_sumchargedhadronpt')
    def iso_PFr4_charged_particles(self):
        return self._get('pfisolationr4_sumchargedparticlept')
    def iso_PFr4_neutral_hadrons(self):
        return self._get('pfisolationr4_sumneutralhadronet')
    def iso_PFr4_sum_photon_et(self):
        return self._get('pfisolationr4_sumphotonet')
    def iso_PFr4_sum_PU_pt(self):
        return self._get('pfisolationr4_sumpupt')
    # more isolation
    def iso_r3_track(self):   return self._get('isolationr3track')
    def iso_r3_ecal(self):    return self._get('isolationr3ecal')
    def iso_r3_hcal(self):    return self._get('isolationr3hcal')
    def iso_r3_n_track(self): return self._get('isolationr3ntrack')
    def iso_r3_track_rel(self):
        return (self._get('isolationr3track') / self.pt())
    def iso_r3_combined(self):
        return (self._get('isolationr3track') + self._get('isolationr3ecal')
                + self._get('isolationr3hcal'))
    def iso_r3_combined_rel(self):
        return ((self._get('isolationr3track') + self._get('isolationr3ecal')
                + self._get('isolationr3hcal')) / self.pt())
    # corrected relative isolation
    def iso_PFr3dB_comb_rel(self): 
        isoval = (
            (self._get('pfisolationr3_sumchargedhadronpt')
            + max(0., (self._get('pfisolationr3_sumneutralhadronet')
                       + self._get('pfisolationr3_sumphotonet')
                       - 0.5 * self._get('pfisolationr3_sumpupt'))
                  )
            ) / self.pt()
        )
        return isoval
    def iso_PFr4dB_comb_rel(self): 
        isoval = (
            (self._get('pfisolationr4_sumchargedhadronpt')
            + max(0., (self._get('pfisolationr4_sumneutralhadronet')
                       + self._get('pfisolationr4_sumphotonet')
                       - 0.5 * self._get('pfisolationr4_sumpupt'))
                  )
            ) / self.pt()
        )
        return isoval

    def check_id_and_iso(self, idtype, isotype, isolevel):
        return (self.check_id(idtype), self.check_iso(isotype, isolevel))

    def check_id(self, idtype):
        ''' Returns bool whether the muon passes Muon POG ID definitions
        '''
        if idtype == 'tight':        return self.is_tight()
        elif idtype == 'medium':     return self.is_medium()
        elif idtype == 'medium2016': return self.is_medium2016()
        elif idtype == 'loose':      return self.is_loose()
        else:
            raise ValueError('Muon.check_id: "{0}" not an available choice for '
                             'idtype. Available choices are "tight", "medium", '
                             '"medium2016", and "loose".'.format(idtype))

    def check_iso(self, isotype, isolevel):
        ''' Returns bool whether the muon passes selected hard-coded isolation
            values taken from:
            https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2#Muon_Isolation
        '''
         # r = 0.4
        PF_dB_tight = 0.15
        PF_dB_loose = 0.25
         # r = 0.3
        tracker_tight = 0.05
        tracker_loose = 0.10

        # check result
        if isotype == 'PF_dB':
            if isolevel == 'tight':
                return (self.iso_PFr4dB_comb_rel() < PF_dB_tight)
            elif isolevel == 'loose':
                return (self.iso_PFr4dB_comb_rel() < PF_dB_loose)
            else:
                raise ValueError('Muon.check_iso: "{0}" not an available choice '
                                 'for isolevel. Available choices are "tight" '
                                 'and "loose".'.format(isolevel))
#        elif isotype == 'tracker':
#            if isolevel == 'tight':
#                return (self.iso_r3_track_rel() < tracker_tight)
#            elif isolevel == 'loose':
#                return (self.iso_r3_track_rel() < tracker_loose)
#            else:
#                raise ValueError('Muon.check_iso: "{0}" not an available choice '
#                                 'for isolevel. Available choices are "tight" '
#                                 'and "loose".'.format(isolevel))
        else:
            raise ValueError('Muon.check_iso: "{0}" not an available choice for '
                             'isotype. Available choices are "PF_dB" and '
#                             '"tracker".'.format(isotype))
                             'that\'s it lol'.format(isotype))

    # muon.MatchesHLTs returns True if any of the triggers fired
    def matches_HLTs(self, paths):
        ''' Returns bool whether any of the triggers fired
        '''
        result = False
        for pathname in paths:
            try:
                result = result or self._get('matches_'+pathname)
            except AttributeError:
                pass
                #print 'Muon HLT path "' + pathname + '" not available.'
                #print 'Available paths are:'
                #for x in self.tree.GetListOfBranches():
                #    if 'muon_hlt_matches_' in x.GetName():
                #        print '    ' + x.GetName()[17:]
                #print '\n'
        return result



## ___________________________________________________________
class Electron(EgammaCand):
    # constructors/helpers
    def __init__(self, tree, entry):
       super(Electron, self).__init__(tree, 'electron', entry)

    # methods
    def dz(self):        return self._get('dz')
    def dz_error(self):  return self._get('dzerr')
    def dxy(self):       return self._get('dxy')
    def dxy_error(self): return self._get('dxyerr')

    def corrected_ecal_energy(self):  return self._get('correctedecalenergy')
    def passes_conversion_veto(self): return self._get('passconversionveto')
    def ecal_driven_seed(self):       return self._get('ecaldrivenseed')
    def tracker_driven_seed(self):    return self._get('trackerdrivenseed')
    # track
    def track_chi2(self):  return self._get('trackchi2')
    def track_n_dof(self): return self._get('trackndof')
    def n_hits(self):          return self._get('nhits')
    def n_pixel_hits(self):    return self._get('npixelhits')
    def n_pixel_layers(self):  return self._get('npixellayers')
    def n_strip_layers(self):  return self._get('nstriplayers')
    def n_missing_hits(self):  return self._get('nmissinghits')
    def n_hits_expected(self): return self._get('nhitsexpected')
    # shower 
    def r9(self): return self._get('r9')
    def fraction_brems(self): return self._get('fbrems')
    def num_brems(self):      return self._get('numbrems')
    # electron id
    def is_veto(self):   return self._get('cutBasedVeto')
    def is_loose(self):  return self._get('cutBasedLoose')
    def is_medium(self): return self._get('cutBasedMedium')
    def is_tight(self):  return self._get('cutBasedTight')

    # electron.MatchesHLTs returns True if any of the triggers fired
    def matches_HLTs(self, paths):
        result = False
        for pathname in paths:
            try:
                result = result or self._get('matches_'+pathname)
            except AttributeError:
                pass
                #print 'Electron HLT path "{0}" not available.'.format(pathname)
                #print 'Available paths are:'
                #for x in self.tree.GetListOfBranches():
                #    if 'electron_hlt_matches_' in x.GetName():
                #        print '    ' + x.GetName()[21:]
                #print '\n'
        return result

## ___________________________________________________________
class Photon(EgammaCand):
    # constructors/helpers
    def __init__(self, tree, entry):
       super(Photon, self).__init__(tree, 'photon', entry)

    # methods
    def has_conversion_tracks(self): return self._get('hasconversiontracks')
    def has_pixel_seed(self):        return self._get('haspixelseed')
    def passes_electron_veto(self):  return self._get('passelectronveto')
    def is_PF_photon(self):          return self._get('ispfphoton')
    def max_energy_xtal(self):       return self._get('maxenergyxtal')
    # more isolation
    def iso_r3_track_hollow(self):   return self._get('isolationr3trackhollow')
    def iso_r3_n_track(self):        return self._get('isolationr3ntrack')
    def iso_r3_n_track_hollow(self): return self._get('isolationr3ntrackhollow')
    def iso_r4_track_hollow(self):   return self._get('isolationr4trackhollow')
    def iso_r4_n_track(self):        return self._get('isolationr4ntrack')
    def iso_r4_n_track_hollow(self): return self._get('isolationr4ntrackhollow')

## ___________________________________________________________
class Tau(JettyCand):
    # constructors/helpers
    def __init__(self, tree, entry):
       super(Tau, self).__init__(tree, 'tau', entry)

    # methods
    def dz(self):        return self._get('dz')
    def dz_error(self):  return self._get('dzerr')
    def dxy(self):       return self._get('dxy')
    def dxy_error(self): return self._get('dxyerr')

    #ak4pfjet_*

    # isolation
    def iso_neutrals_pt(self):  return self._get('isolationneutralspt')
    def iso_neutrals_num(self): return self._get('isolationneutralsnum')
    def iso_charged_pt(self):   return self._get('isolationchargedpt')
    def iso_charged_num(self):  return self._get('isolationchargednum')
    def iso_gamma_pt(self):     return self._get('isolationgammapt')
    def iso_gamma_num(self):    return self._get('isolationgammanum')
    # raw values of the isolation
    def neutral_iso_pt_sum_weight(self): return self._get('neutralIsoPtSumWeight')
    def footprint_correction(self):      return self._get('footprintCorrection')
    def PU_corr_pt_sum(self):            return self._get('puCorrPtSum')

    # tau ids
    def tau_discriminator(self, discname): 
        try:
            return self._get('tdisc_'+discname)
        except AttributeError:
            print 'Tau discriminator "' + discname + '" not available.'
            print ('Print a list of available discriminators with:'
                   '\n    self.event.print_available_tau_discriminators()')
            #raise


## ___________________________________________________________
class Jet(JettyCand):
    # constructors/helpers
    def __init__(self, tree, entry):
       super(Jet, self).__init__(tree, 'ak4pfchsjet', entry)

    # methods
    def area(self): return self._get('area')
    # energy
    def had_energy(self):         return self._get('hadronicenergy')
    def charged_had_energy(self): return self._get('chargedhadronicenergy')
    def em_energy(self):          return self._get('emenergy')
    def charged_em_energy(self):  return self._get('chargedemenergy')
    def hf_had_energy(self):      return self._get('hfhadronicenergy')
    def hf_em_energy(self):       return self._get('hfemenergy')
    def electron_energy(self):    return self._get('electronenergy')
    def muon_energy(self):        return self._get('muonenergy')
    # jet id
    def is_loose(self):          return self._get('is_loose')
    def is_tight(self):          return self._get('is_tight')
    def is_tight_lep_veto(self): return self._get('is_tightLepVeto')
    # btagging
    def btag(self, tagname): 
        result = False
        try:
            return self._get('btag_pass'+tagname)
        except AttributeError:
            print 'Btag "' + tagname + '" not available.'
            print ('Print a list of available btags with:'
                   '\n    self.event.print_available_btags()')
            #raise

