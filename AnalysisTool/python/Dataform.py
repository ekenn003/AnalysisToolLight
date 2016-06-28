# AnalysisToolLight/AnalysisTool/python/Dataform.py
'''
See RootMaker/RootMaker/python/objectBase.py
'''

import ROOT
#import math
from collections import OrderedDict, namedtuple


## ___________________________________________________________
BeamSpot = namedtuple('BeamSpot', ['x', 'y', 'z', 'xwidth','ywidth','zsigma'])

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
    def Number(self):       return self.tree.event_nr
    def Run(self):          return self.tree.event_run
    def TimeUnix(self):     return self.tree.event_timeunix
    def TimeMicroSec(self): return self.tree.event_timemicrosec
    def LumiBlock(self):    return self.tree.event_luminosityblock
    def Rho(self):          return self.tree.event_rho
    # beamspot
    def BeamSpot(self):
        return Beamspot(self.tree.beamspot_x, self.tree.beamspot_y, self.tree.beamspot_z, self.tree.beamspot_xwidth, self.tree.beamspot_ywidth, self.tree.beamspot_zsigma)
    # pileup
    def NumPileUpInteractionsMinus(self): return self.tree.numpileupinteractionsminus
    def NumPileUpInteractions(self):      return self.tree.numpileupinteractions
    def NumPileUpInteractionsPlus(self):  return self.tree.numpileupinteractionsplus
    def NumTruePileUpInteractions(self):  return self.tree.numtruepileupinteractions
    # generator info
    def GenWeight(self):    return (self.tree.genweight)
    def GenWeightRel(self): return (self.tree.genweight/self.sumweights)
    def GenId1(self):    return self.tree.genid1
    def Genx1(self):     return self.tree.genx1
    def GenId2(self):    return self.tree.genid2
    def Genx2(self):     return self.tree.genx2
    def GenScale(self):  return self.tree.genScale

    ## _______________________________________________________
    def PrintAvailableTauDiscriminators(self):
        print 'Available discriminators are:'
        for x in self.tree.GetListOfBranches():
            if 'tau_tdisc_' in x.GetName(): print '    ' + x.GetName()[10:]
        print '\n'

    ## _______________________________________________________
    def PrintAvailableBtags(self):
        print 'Available btags are:'
        for x in self.tree.GetListOfBranches():
            if 'ak4pfchsjet_btag_' in x.GetName(): print '    ' + x.GetName()[17:]
        print '\n'

    ## _______________________________________________________
    # event.PassesHLTs returns True if any of the triggers fired
    def PassesHLTs(self, paths):
        result = False
        for pathname in paths:
            try:
                result = self._get('event_hlt_passes_'+pathname)
            except AttributeError:
                pass
                #print 'PassesHLTs: Event HLT path "' + pathname + '" not available.'
                #print 'Available paths are:'
                #for x in self.tree.GetListOfBranches():
                #    if 'event_hlt_passes_' in x.GetName(): print '    ' + x.GetName()[17:]
                #print '\n'
        return result

    ## _______________________________________________________
    def AnyIsPrescaled(self, paths):
        # initialise empty map of results
        results = {}
        for pathname in paths:
            try:
                prescale = self._get('prescale_hlt_'+pathname)
            except AttributeError:
                pass
                #print 'AnyIsPrescaled: Event HLT path "{0}" not available.'.format(pathname)
                #print 'Available paths are:'
                #for x in self.tree.GetListOfBranches():
                #    if 'event_hlt_passes_' in x.GetName(): print '    ' + x.GetName()[17:]
                #print '\n'
                #raise
            # only store results that are prescaled
            if prescale != 1: results[pathname] = prescale

        # check if we had any paths that were prescaled
        for x in results:
            print 'HLT path {0} has a prescale of {1}.'.format(x, results[x])
        return True if results else False

    ## _______________________________________________________
    def GetPrescale(self, pathname):
        prescale = -1
        try:
            prescale = self._get('prescale_hlt_'+pathname)
        except AttributeError:
            pass
        return prescale


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
    def _get(self, var): return getattr(self.tree, '{0}_{1}'.format('primvertex', var))[self.entry]

    # methods
    def X(self): return self._get('x')
    def Y(self): return self._get('y')
    def Z(self): return self._get('z')
    def XError(self): return self._get('xError')
    def YError(self): return self._get('yError')
    def ZError(self): return self._get('zError')
    def Chi2(self):     return self._get('chi2')
    def Ndof(self):     return self._get('ndof')
    def NTracks(self):  return self._get('ntracks')
    def NormChi2(self): return self._get('normalizedChi2')
    def IsValid(self):  return self._get('isvalid')
    def IsFake(self):   return self._get('isfake')
    def Rho(self):      return self._get('rho')


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
    def _get(self, var): return getattr(self.tree, '{0}_{1}'.format(self.metName, var))[self.entry]

    # methods
    def E(self):   return ROOT.TVector3(self._get('ex'), self._get('ey'), 0.)
    def Et(self):  return self._get('et')
    def Phi(self): return self._get('phi')
    def RawEt(self):  return self._get('rawet')
    def RawPhi(self): return self._get('rawphi')


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
    P4 = TLorentzVector(Pt, Eta, Phi, Energy)
    '''
    # constructors/helpers
    def __init__(self, tree, candName, entry):
        self.tree = tree
        self.candName = candName
        self.entry = entry
    def _get(self, var): return getattr(self.tree, '{0}_{1}'.format(self.candName, var))[self.entry]

    # misc methods
    def Rho(self):          return self.tree.event_rho
    def deltaR(self, cand): return deltaR(self, cand)

    # methods
    def P(self):      return ROOT.TVector3(self._get('px'), self._get('py'), self._get('pz'))
    def Pt(self):     return self._get('pt')
    def Eta(self):    return self._get('eta')
    def AbsEta(self): return abs(self._get('eta'))
    def Phi(self):    return self._get('phi')
    def Energy(self): return self._get('energy')
    def P4(self):
        thisp4 = ROOT.TLorentzVector()
        thisp4.SetPtEtaPhiE(self.Pt(), self.Eta(), self.Phi(), self.Energy())
        return thisp4
    def Charge(self): return self._get('charge')
    def PDGID(self):  return self._get('pdgid')



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
    def EffectiveArea(self): return self._get('effectiveArea')
    # supercluster
    def SCEnergy(self):          return self._get('supercluster_e')
    def SCEta(self):             return self._get('supercluster_eta')
    def SCPhi(self):             return self._get('supercluster_phi')
    def SCRawEnergy(self):       return self._get('supercluster_rawe')
    def SCPreshowerEnergy(self): return self._get('supercluster_preshowere')
    def SCPhiWidth(self):        return self._get('supercluster_phiwidth')
    def SCEtaWidth(self):        return self._get('supercluster_etawidth')
    def SCNClusters(self):       return self._get('supercluster_nbasiccluster')
    # shower
    def E1x5(self): return self._get('e1x5')
    def E2x5(self): return self._get('e2x5')
    def E5x5(self): return self._get('e5x5')
    # isolation
    def IsoPFR3Charged(self): return self._get('isolationpfr3charged')
    def IsoPFR3Photon(self):  return self._get('isolationpfr3photon')
    def IsoPFR3Neutral(self): return self._get('isolationpfr3neutral')
    def IsoR3Track(self):     return self._get('isolationr3track')
    def IsoR3Ecal(self):      return self._get('isolationr3ecal')
    def IsoR3Hcal(self):      return self._get('isolationr3hcal')
    def IsoR4Track(self):     return self._get('isolationr4track')
    def IsoR4Ecal(self):      return self._get('isolationr4ecal')
    def IsoR4Hcal(self):      return self._get('isolationr4hcal')
    # corrected relative isolation
    def IsoPFR3dBCombRel(self):
        isoval = (
            (self._get('isolationpfr3charged')
            + max(0.0, self._get('isolationpfr3neutral') + self._get('isolationpfr3photon')
                  - 0.5 * self._get('isolationpfr3chargedpu')
                 )
            ) / self._get('pt')
        )
        return isoval
    # corrected relative isolation
    def IsoPFR3RhoCombRel(self):
        isoval = (
            (self._get('isolationpfr3charged')
            + max(0.0, self._get('isolationpfr3neutral') + self._get('isolationpfr3photon')
                  - self.Rho() * self._get('effectiveArea')
                 )
            ) / self._get('pt')
        )
        return isoval

    # shower shapes
    def SigmaEtaEta(self):   return self._get('sigmaetaeta')
    def SigmaIEtaIEta(self): return self._get('sigmaietaieta')
    def SigmaIPhiIPhi(self): return self._get('sigmaiphiiphi')
    def SigmaIEtaIPhi(self): return self._get('sigmaietaiphi')
    # calorimeter
    def HcalOverEcal(self):        return self._get('hcalOverEcal')
    def EHcalOverEcal(self):       return (self._get('ehcaloverecaldepth1') + self._get('ehcaloverecaldepth2'))
    def EHcalOverEcalDepth1(self): return self._get('ehcaloverecaldepth1')
    def EHcalOverEcalDepth2(self): return self._get('ehcaloverecaldepth2')
    def EHcalTowerOverEcal(self):  return (self._get('ehcaltoweroverecaldepth1') + self._get('ehcaltoweroverecaldepth2'))
    def EHcalTowerOverEcalDepth1(self): return self._get('ehcaltoweroverecaldepth1')
    def EHcalTowerOverEcalDepth2(self): return self._get('ehcaltoweroverecaldepth2')




## ___________________________________________________________
class Muon(CommonCand):
    '''
    Muon: 
    P(), P4(), Pt(), Eta(), Phi(), and Energy() all return rochester-corrected values.
    To use the uncorrected values, use UncorrP(), etc.
    '''
    # constructors/helpers
    def __init__(self, tree, entry):
       super(Muon, self).__init__(tree, 'muon', entry)

    # methods
    def Dz(self):       return self._get('dz')
    def DzError(self):  return self._get('dzerr')
    def Dxy(self):      return self._get('dxy')
    def DxyError(self): return self._get('dxyerr')
    # rochester-corrected values
    def P(self):      return ROOT.TVector3(self._get('rochesterPx'), self._get('rochesterPy'), self._get('rochesterPz'))
    def Pt(self):     return self._get('rochesterPt')
    def Eta(self):    return self._get('rochesterEta')
    def Phi(self):    return self._get('rochesterPhi')
    def Energy(self): return self._get('rochesterEnergy')
    def P4(self): # pt, eta, phi, e
        thisp4 = ROOT.TLorentzVector()
        thisp4.SetPtEtaPhiE(self.Pt(), self.Eta(), self.Phi(), self.Energy())
        return thisp4
    def CorrectionError(self): return self._get('rochesterError')
    # uncorrected values
    def UncorrP(self):      return ROOT.TVector3(self._get('px'), self._get('py'), self._get('pz'))
    def UncorrPt(self):     return self._get('pt')
    def UncorrEta(self):    return self._get('eta')
    def UncorrPhi(self):    return self._get('phi')
    def UncorrEnergy(self): return self._get('energy')
    def UncorrP4(self): # pt, eta, phi, e
        thisp4 = ROOT.TLorentzVector()
        thisp4.SetPtEtaPhiE(self.UncorrPt(), self.UncorrEta(), self.UncorrPhi(), self.UncorrEnergy())
        return thisp4

    # energy
    def EcalEnergy(self): return self._get('ecalenergy')
    def HcalEnergy(self): return self._get('hcalenergy')
    # muon ID
    def IsTightMuon(self):  return self._get('is_tight_muon')
    def IsMediumMuon(self): return self._get('is_medium_muon')
    def IsLooseMuon(self):  return self._get('is_loose_muon')
    # track info
    def IsPFMuon(self):       return self._get('is_pf_muon')
    def IsGlobal(self):       return self._get('is_global')
    def HasGlobalTrack(self): return self._get('hasglobaltrack') # this might be exactly the above - check
    def IsTracker(self):      return self._get('is_tracker')
    def IsStandalone(self):   return self._get('is_standalone')
    def IsCaloMuon(self):     return self._get('is_calo')
    def PtError(self):          return self._get('pterror')
    def Chi2(self):             return self._get('chi2')
    def Ndof(self):             return self._get('ndof')
    def NumValidMuonHits(self):        return self._get('numvalidmuonhits')
    def NumChambers(self):             return self._get('numchambers')
    def NumMatchedStations(self):      return self._get('nummatchedstations')
    def NumChambersWithSegments(self): return self._get('numchamberswithsegments')
    # inner track
    def HasInnerTrack(self): return self._get('hasinnertrack')
    def InnerTrackDz(self):       return self._get('innertrack_dz')
    def InnerTrackDzError(self):  return self._get('innertrack_dzerr')
    def InnerTrackDxy(self):      return self._get('innertrack_dxy')
    def InnerTrackDxyError(self): return self._get('innertrack_dxyerr')
    def InnerTrackChi2(self):     return self._get('innertrack_chi2')
    def InnerTrackNdof(self):     return self._get('innertrack_ndof')
    def InnerTrackCharge(self):   return self._get('innertrack_charge')
    def InnerTrackNHits(self):        return self._get('innertrack_nhits')
    def InnerTrackNMissingHits(self): return self._get('innertrack_nmissinghits')
    def InnerTrackNPixelHits(self):   return self._get('innertrack_npixelhits')
    def InnerTrackNPixelLayers(self): return self._get('innertrack_npixellayers')
    def InnerTrackNStripLayers(self): return self._get('innertrack_nstriplayers')
    # outer track
    def HasOutTrack(self): return self._get('hasoutertrack')
    def OuterTrackChi2(self): return self._get('outertrack_chi2')
    def OuterTrackNdof(self): return self._get('outertrack_ndof')
    def OuterTrackNHits(self):        return self._get('outertrack_hits')
    def OuterTrackNMissingHits(self): return self._get('outertrack_missinghits')
    # isolation r3
    def IsoPFR3ChargedHadrons(self):   return self._get('pfisolationr3_sumchargedhadronpt')
    def IsoPFR3ChargedParticles(self): return self._get('pfisolationr3_sumchargedparticlept')
    def IsoPFR3NeutralHadrons(self):   return self._get('pfisolationr3_sumneutralhadronet')
    def IsoPFR3SumPhotonEt(self):      return self._get('pfisolationr3_sumphotonet')
    def IsoPFR3SumPUPt(self):          return self._get('pfisolationr3_sumpupt')
    # isolation r4
    def IsoPFR4ChargedHadrons(self):   return self._get('pfisolationr4_sumchargedhadronpt')
    def IsoPFR4ChargedParticles(self): return self._get('pfisolationr4_sumchargedparticlept')
    def IsoPFR4NeutralHadrons(self):   return self._get('pfisolationr4_sumneutralhadronet')
    def IsoPFR4Photons(self):          return self._get('pfisolationr4_sumphotonet')
    def IsoPFR4SumPUPt(self):          return self._get('pfisolationr4_sumpupt')
    # more isolation
    def IsoR3Track(self):       return self._get('isolationr3track')
    def IsoR3Ecal(self):        return self._get('isolationr3ecal')
    def IsoR3Hcal(self):        return self._get('isolationr3hcal')
    def IsoR3TrackRel(self):    return (self._get('isolationr3track') / self._get('pt'))
    def IsoR3NTrack(self):      return self._get('isolationr3ntrack')
    def IsoR3Combined(self):    return (self._get('isolationr3track') + self._get('isolationr3ecal') + self._get('isolationr3hcal'))
    def IsoR3CombinedRel(self): return ((self._get('isolationr3track') + self._get('isolationr3ecal') + self._get('isolationr3hcal')) / self._get('pt'))
    # corrected relative isolation
    def IsoPFR3dBCombRel(self): 
        isoval = (
            (self._get('pfisolationr3_sumchargedhadronpt')
            + max(0., self._get('pfisolationr3_sumneutralhadronet') + self._get('pfisolationr3_sumphotonet')
                  - 0.5 * self._get('pfisolationr3_sumpupt')
                  )
            ) / self._get('pt')
        )
        return isoval
    # check isolation function
    def CheckIso(self, isotype, isolevel):
        ''' Returns whether the muon passes selected hard-coded isolation values taken
        from https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2#Muon_Isolation
        '''
        # kind of validate input
        if not (isotype=='PF_dB' or isotype=='tracker'):
            raise ValueError('Muon.CheckIso: "{0}" not an available choice for isotype. Available choices are "PF_dB" and "tracker".'.format(isotype))
        if not (isolevel=='tight' or isolevel=='loose'):
            raise ValueError('Muon.CheckIso: "{0}" not an available choice for isolevel. Available choices are "tight" and "loose".'.format(isolevel))
        # return result of isolation check
        if isotype=='PF_dB':
            return (self.IsoPFR3dBCombRel() < 0.15) if isolevel=='tight' else (self.IsoPFR3dBCombRel() < 0.25)
        if isotype=='tracker':
            return (self.IsoR3Track() < 0.05) if isolevel=='tight' else (self.IsoR3Track() < 0.10)

    # muon.MatchesHLTs returns True if any of the triggers fired
    def MatchesHLTs(self, paths):
        result = False
        for pathname in paths:
            try:
                result = self._get('hlt_matches_'+pathname)
            except AttributeError:
                pass
                #print 'Muon HLT path "' + pathname + '" not available.'
                #print 'Available paths are:'
                #for x in self.tree.GetListOfBranches():
                #    if 'muon_hlt_matches_' in x.GetName(): print '    ' + x.GetName()[17:]
                #print '\n'
        return result



## ___________________________________________________________
class Electron(EgammaCand):
    # constructors/helpers
    def __init__(self, tree, entry):
       super(Electron, self).__init__(tree, 'electron', entry)

    # methods
    def Dz(self):       return self._get('dz')
    def DzError(self):  return self._get('dzerr')
    def Dxy(self):      return self._get('dxy')
    def DxyError(self): return self._get('dxyerr')
    def CorrectedEcalEnergy(self):  return self._get('correctedecalenergy')
    def PassesConversionVeto(self): return self._get('passconversionveto')
    def EcalDrivenSeed(self):       return self._get('ecaldrivenseed')
    def TrackerDrivenSeed(self):    return self._get('trackerdrivenseed')
    # track
    def TrackChi2(self): return self._get('trackchi2')
    def TrackNdof(self): return self._get('trackndof')
    def NHits(self):         return self._get('nhits')
    def NPixelHits(self):    return self._get('npixelhits')
    def NPixelLayers(self):  return self._get('npixellayers')
    def NStripLayers(self):  return self._get('nstriplayers')
    def NMissingHits(self):  return self._get('nmissinghits')
    def NHitsExpected(self): return self._get('nhitsexpected')
    # shower 
    def R9(self):   return self._get('r9')
    def FractionBrems(self): return self._get('fbrems')
    def NumBrems(self):      return self._get('numbrems')
    # supercluster
    def SCE1x5(self):        return self._get('scE1x5')
    def SCE2x5Max(self):     return self._get('scE2x5Max')
    def SCE5x5(self):        return self._get('scE5x5')
    def ESuperClusterOverTrack(self):    return self._get('esuperclusterovertrack')
    def ESeedClusterOverTrack(self):     return self._get('eseedclusterovertrack')
    def DeltaEtaSuperClusterTrack(self): return self._get('deltaetasuperclustertrack')
    def DeltaPhiSuperClusterTrack(self): return self._get('deltaphisuperclustertrack')
    # electron id
    def IsVetoElectron(self):   return self._get('cutBasedVeto')
    def IsLooseElectron(self):  return self._get('cutBasedLoose')
    def IsMediumElectron(self): return self._get('cutBasedMedium')
    def IsTightElectron(self):  return self._get('cutBasedTight')
    def WP90_v1(self): return self._get('mvaNonTrigWP90')
    def WP80_v1(self): return self._get('mvaNonTrigWP80')

    # electron.MatchesHLTs returns True if any of the triggers fired
    def MatchesHLTs(self, paths):
        result = False
        for pathname in paths:
            try:
                result = self._get('hlt_matches_'+pathname)
            except AttributeError:
                pass
                #print 'Electron HLT path "{0}" not available.'.format(pathname)
                #print 'Available paths are:'
                #for x in self.tree.GetListOfBranches():
                #    if 'electron_hlt_matches_' in x.GetName(): print '    ' + x.GetName()[21:]
                #print '\n'
        return result

## ___________________________________________________________
class Photon(EgammaCand):
    # constructors/helpers
    def __init__(self, tree, entry):
       super(Photon, self).__init__(tree, 'photon', entry)

    # methods
    def HasConversionTracks(self): return self._get('hasconversiontracks')
    def HasPixelSeed(self):        return self._get('haspixelseed')
    def PassesElectronVeto(self):  return self._get('passelectronveto')
    def IsPFPhoton(self):          return self._get('ispfphoton')
    def MaxEnergyXtal(self):       return self._get('maxenergyxtal')
    # shower
    def E3x3(self): return self._get('e3x3')
    # more isolation
    def IsoR3TrackHollow(self):  return self._get('isolationr3trackhollow')
    def IsoR3NTrack(self):       return self._get('isolationr3ntrack')
    def IsoR3NTrackHollow(self): return self._get('isolationr3ntrackhollow')
    def IsoR4TrackHollow(self):  return self._get('isolationr4trackhollow')
    def IsoR4NTrack(self):       return self._get('isolationr4ntrack')
    def IsoR4NTrackHollow(self): return self._get('isolationr4ntrackhollow')

## ___________________________________________________________
class Tau(JettyCand):
    # constructors/helpers
    def __init__(self, tree, entry):
       super(Tau, self).__init__(tree, 'tau', entry)

    # methods
    def Dz(self):       return self._get('dz')
    def DzError(self):  return self._get('dzerr')
    def Dxy(self):      return self._get('dxy')
    def DxyError(self): return self._get('dxyerr')

    #ak4pfjet_*

    # isolation
    def IsoNeutralsPt(self):  return self._get('isolationneutralspt')
    def IsoNeutralsNum(self): return self._get('isolationneutralsnum')
    def IsoChargedPt(self):   return self._get('isolationchargedpt')
    def IsoChargedNum(self):  return self._get('isolationchargednum')
    def IsoGammaPt(self):     return self._get('isolationgammapt')
    def IsoGammaNum(self):    return self._get('isolationgammanum')
    # raw values of the isolation
    def NeutralIsoPtSumWeight(self): return self._get('neutralIsoPtSumWeight')
    def FootprintCorrection(self):   return self._get('footprintCorrection')
    def PUCorrPtSum(self):           return self._get('puCorrPtSum')

    # tau ids
    def TauDiscriminator(self, discname): 
        result = False
        try:
            result = self._get('tdisc_'+discname)
        except AttributeError:
            print 'Tau discriminator "' + discname + '" not available.'
            print 'Print a list of available discriminators with:\n    self.event.PrintAvailableTauDiscriminators()'
            #raise
        return result


## ___________________________________________________________
JetShape = namedtuple('JetShape', ['chargeda', 'chargedb', 'neutrala', 'neutralb', 'alla', 'allb', 'chargedfractionmv'])

## ___________________________________________________________
class Jet(JettyCand):
    # constructors/helpers
    def __init__(self, tree, entry):
       super(Jet, self).__init__(tree, 'ak4pfchsjet', entry)

    # methods
    def Area(self): return self._get('area')
    # energy
    def HadEnergy(self):        return self._get('hadronicenergy')
    def ChargedHadEnergy(self): return self._get('chargedhadronicenergy')
    def EMEnergy(self):         return self._get('emenergy')
    def ChargedEMEnergy(self):  return self._get('chargedemenergy')
    def HFHadEnergy(self):      return self._get('hfhadronicenergy')
    def HFEMEnergy(self):       return self._get('hfemenergy')
    def ElectronEnergy(self):   return self._get('electronenergy')
    def MuonEnergy(self):       return self._get('muonenergy')
    # multiplicities
    def ChargedMulti(self):  return self._get('chargedmulti')
    def NeutralMulti(self):  return self._get('neutralmulti')
    def HFHadMulti(self):    return self._get('hfhadronicmulti')
    def HFEMMulti(self):     return self._get('hfemmulti')
    def ElectronMulti(self): return self._get('electronmulti')
    def MuonMulti(self):     return self._get('muonmulti')
    # energy fractions
    def NeutralHadEnergyFraction(self): return self._get('neutralhadronenergyfraction')
    def NeutralEMEnergyFraction(self):  return self._get('neutralemenergyfraction')
    def ChargedHadEnergyFraction(self): return self._get('chargedhadronenergyfraction')
    def MuonEnergyFraction(self):       return self._get('muonenergyfraction')
    def ChargedEMEnergyFraction(self):  return self._get('chargedemenergyfraction')
    # jet id
    def IsLooseJet(self):        return self._get('is_loose')
    def IsTightJet(self):        return self._get('is_tight')
    def IsTightLepVetoJet(self): return self._get('is_tightLepVeto')
    # shape
    def Shape(self):
        return JetShape(self._get('chargeda'), self._get('chargedb'), self._get('neutrala'), self._get('neutralb'), self._get('alla'), self._get('allb'), self._get('chargedfractionmv'))
    # btagging
    def Btag(self, tagname): 
        result = False
        try:
            result = self._get('btag_'+tagname)
        except AttributeError:
            print 'Btag "' + tagname + '" not available.'
            print 'Print a list of available btags with:\n    self.event.PrintAvailableBtags()'
            #raise
        return result





## ___________________________________________________________
class CutFlow(object):
    '''
    The CutFlow object keeps track of the cutflow and helps fill
    the efficiencies histogram at the end of the job.
    '''
    def __init__(self):
        self.counters = OrderedDict()
        self.pretty = {}
    def getPretty(self, name):
        return self.pretty.get(name, name)
    def add(self, var, label):
        self.counters[var] = 0
        self.pretty[var] = label
    def increment(self, arg): # increases counter "arg" by 1
        self.counters[arg] += 1.
    def numBins(self): # returns number of counters
        return len(self.counters)
    def count(self, name): # returns the current value of the counter "name"
        return self.counters[name]
    def getNames(self): # returns ordered dict of counters
        return self.counters.keys()
    def getSkimEff(self, index):
        if index == 0: return '---'
        num = self.count(self.getNames()[index])
        den = self.count(self.getNames()[0])
        if den!=0: return format((100.*num)/den, '0.2f')
        return '-'
    def getRelEff(self, index):
        if index == 0: return '---'
        num = self.count(self.getNames()[index])
        den = self.count(self.getNames()[index-1])
        if den!=0: return format((100.*num)/den, '0.2f')
        return '-'









