'''
See RootMaker/RootMaker/python/objectBase.py
'''

import ROOT

## ___________________________________________________________
def deltaPhi(c0, c1):
    result = c0.phi() - c1.phi()
    while result>ROOT.TMath.Pi():
        result -= 2*ROOT.TMath.Pi()
    while result<=-ROOT.TMath.Pi():
        result += 2*ROOT.TMath.Pi()
    return result

## ___________________________________________________________
def deltaR(c0, c1):
    deta = c0.eta() - c1.eta()
    dphi = deltaPhi(c0, c1)
    return ROOT.TMath.Sqrt(deta**2+dphi**2)

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
    def XError(self):   return self._get('xError')
    def YError(self):   return self._get('yError')
    def ZError(self):   return self._get('zError')
    def Chi2(self):     return self._get('chi2')
    def Ndof(self):     return self._get('ndof')
    def NTracks(self):  return self._get('ntracks')
    def NormChi2(self): return self._get('normalizedChi2')
    def IsValid(self):  return self._get('isvalid')
    def IsFake(self):   return self._get('isfake')
    def VRho(self):     return self._get('rho')


## ___________________________________________________________
class ObjectBase(object):
    '''
    Basic objects
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
    def P4(self):     return ROOT.TLorentzVector(self._get('pt'), self._get('eta'), self._get('phi'), self._get('energy'))
    def Pt(self):     return self._get('pt')
    def Eta(self):    return self._get('eta')
    def Phi(self):    return self._get('phi')
    def Energy(self): return self._get('energy')
    def Charge(self): return self._get('charge')
    def PDGID(self):  return self._get('pdgid')



## ___________________________________________________________
class CommonObject(ObjectBase):
    # constructors/helpers
    def __init__(self, tree, obtype, entry):
       super(CommonObject, self).__init__(tree, obtype, entry)

    # methods
    #gen*

## ___________________________________________________________
class JettyObject(ObjectBase):
    # constructors/helpers
    def __init__(self, tree, jttype, entry):
       super(JettyObject, self).__init__(tree, jttype, entry)

    # methods
    #genJet*

## ___________________________________________________________
class EgammaObject(CommonObject):
    # constructors/helpers
    def __init__(self, tree, egtype, entry):
       super(EgammaObject, self).__init__(tree, egtype, entry)

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
    #def (self): return self._get('isolationpfr3chargedpu')
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
class Muon(CommonObject):
    # constructors/helpers
    def __init__(self, tree, entry):
       super(Muon, self).__init__(tree, 'muon', entry)

    # methods
    def Dz(self):       return self._get('dz')
    def DzError(self):  return self._get('dzerr')
    def Dxy(self):      return self._get('dxy')
    def DxyError(self): return self._get('dxyerr')
    # rochester corrected values
    def CorrectedP(self):      return ROOT.TVector3(self._get('rochesterPx'), self._get('rochesterPy'), self._get('rochesterPx'))
    def CorrectedP4(self):     return ROOT.TLorentzVector(self._get('rochesterPt'), self._get('rochesterEta'), self._get('rochesterPhi'), self._get('rochesterEnergy'))
    def CorrectedPt(self):     return self._get('rochesterPt')
    def CorrectedEta(self):    return self._get('rochesterEta')
    def CorrectedPhi(self):    return self._get('rochesterPhi')
    def CorrectedEnergy(self): return self._get('rochesterEnergy')
    def CorrectionError(self): return self._get('rochesterError')
    # energy
    def EcalEnergy(self): return self._get('ecalenergy')
    def HcalEnergy(self): return self._get('hcalenergy')
    # muon ID
    def IsTightMuon(self):  return self._get('is_tight_muon')
    def IsMediumMuon(self): return self._get('is_medium_muon')
    def IsLooseMuon(self):  return self._get('is_loose_muon')
    # track info
    def IsPFMuon(self):         return self._get('is_pf_muon')
    def IsGlobalMuon(self):     return self._get('is_global')
    def HasGlobalTrack(self):   return self._get('hasglobaltrack') # this might be exactly the above - check
    def IsTrackerMuon(self):    return self._get('is_tracker')
    def IsStandaloneMuon(self): return self._get('is_standalone')
    def IsCaloMuon(self):       return self._get('is_calo')
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







## ___________________________________________________________
class Electron(EgammaObject):
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


## ___________________________________________________________
class Photon(EgammaObject):
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
class Tau(JettyObject):
    # constructors/helpers
    def __init__(self, tree, entry):
       super(Tau, self).__init__(tree, 'tau', entry)
    def ListAvailableTauDiscriminators(self):          return self.infotree

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
    #disc
    def TauDiscriminator(self, discname):
        if 


    'againstElectronVLooseMVA6',
    'againstElectronLooseMVA6',
    'againstElectronMediumMVA6',
    'againstElectronTightMVA6',
    'againstElectronVTightMVA6',
    'againstElectronMVA6category',
    'againstElectronMVA6raw',
    'againstMuonLoose3',
    'againstMuonTight3',
    'byLoosePileupWeightedIsolation3Hits',
    'byMediumPileupWeightedIsolation3Hits',
    'byTightPileupWeightedIsolation3Hits',
    'byPileupWeightedIsolationRaw3Hits',
    'byLooseCombinedIsolationDeltaBetaCorr3Hits',
    'byMediumCombinedIsolationDeltaBetaCorr3Hits',
    'byTightCombinedIsolationDeltaBetaCorr3Hits',
    'byCombinedIsolationDeltaBetaCorrRaw3Hits',
    'byLooseCombinedIsolationDeltaBetaCorr3HitsdR03',
    'byMediumCombinedIsolationDeltaBetaCorr3HitsdR03',
    'byTightCombinedIsolationDeltaBetaCorr3HitsdR03',
    'byVLooseIsolationMVA3newDMwLT',
    'byLooseIsolationMVA3newDMwLT',
    'byMediumIsolationMVA3newDMwLT',
    'byTightIsolationMVA3newDMwLT',
    'byVTightIsolationMVA3newDMwLT',
    'byVVTightIsolationMVA3newDMwLT',
    'byIsolationMVA3newDMwLTraw',
    # BDT based tau ID discriminator based on isolation Pt sums plus tau lifetime information, trained on 1-prong and 3-prong tau candidates
    'byVLooseIsolationMVA3oldDMwLT',
    'byLooseIsolationMVA3oldDMwLT',
    'byMediumIsolationMVA3oldDMwLT',
    'byTightIsolationMVA3oldDMwLT',
    'byVTightIsolationMVA3oldDMwLT',
    'byVVTightIsolationMVA3oldDMwLT',
    'byIsolationMVA3oldDMwLTraw',
    'byLooseIsolationMVArun2v1DBoldDMwLT',
    'byMediumIsolationMVArun2v1DBoldDMwLT',
    'byTightIsolationMVArun2v1DBoldDMwLT',
    'byVTightIsolationMVArun2v1DBoldDMwLT',
    'byLooseIsolationMVArun2v1DBdR03oldDMwLT',
    'byMediumIsolationMVArun2v1DBdR03oldDMwLT',
    'byTightIsolationMVArun2v1DBdR03oldDMwLT',
    'byVTightIsolationMVArun2v1DBdR03oldDMwLT',
    'byLooseIsolationMVArun2v1DBnewDMwLT',
    'byMediumIsolationMVArun2v1DBnewDMwLT',
    'byTightIsolationMVArun2v1DBnewDMwLT',
    'byVTightIsolationMVArun2v1DBnewDMwLT',
    'byLooseIsolationMVArun2v1PWoldDMwLT',
    'byMediumIsolationMVArun2v1PWoldDMwLT',
    'byTightIsolationMVArun2v1PWoldDMwLT',
    'byVTightIsolationMVArun2v1PWoldDMwLT',
    'byLooseIsolationMVArun2v1PWdR03oldDMwLT',
    'byMediumIsolationMVArun2v1PWdR03oldDMwLT',
    'byTightIsolationMVArun2v1PWdR03oldDMwLT',
    'byVTightIsolationMVArun2v1PWdR03oldDMwLT',
    'byLooseIsolationMVArun2v1PWnewDMwLT',
    'byMediumIsolationMVArun2v1PWnewDMwLT',
    'byTightIsolationMVArun2v1PWnewDMwLT',
    'byVTightIsolationMVArun2v1PWnewDMwLT',
    'decayModeFinding',
    'decayModeFindingNewDMs',






## ___________________________________________________________
class Jet(JettyObject):
    # constructors/helpers
    def __init__(self, tree, entry):
       super(Jet, self).__init__(tree, 'ak4pfchsjet', entry)



















