from CutFlow import *
from Dataform import *
import math
import itertools
from tools.tools import DeltaR, Z_MASS, EventIsOnList

## ___________________________________________________________
def initialize_cutflow(analysis):
    cutflow = CutFlow()
    cuts = analysis.cuts

    cutflow.add_static('nEv_Orig', 'Original number of events', analysis.nevents)
    cutflow.add('nEv_Skim', 'Skim number of events (>=2 muon candidates)')
    #############################
    # check_event_selection #####
    #############################
    # event selection
    cutflow.add('nEv_Trigger', 'Trigger')
    # muon selection
    cutflow.add('nEv_GAndTr',   'Global+Tracker muon')
    cutflow.add('nEv_Pt',       'Muon pT > {0}'.format(cuts['cMuPt']))
    cutflow.add('nEv_Eta',      'Muon |eta| < {0}'.format(cuts['cMuEta']))
    cutflow.add('nEv_PtEtaMax', 'At least 1 trigger-matched mu with pT > {0} and |eta| < {1}'.format(cuts['cMuPtMax'], cuts['cMuEtaMax']))
    cutflow.add('nEv_Iso',      'Muon has {0} isolation'.format(cuts['cMuIso']))
    cutflow.add('nEv_ID',       'Muon has {0} muon ID'.format(cuts['cMuID']))
    cutflow.add('nEv_2Mu',      'Require 2 "good" muons')
    #############################
    # check_preselection ########
    #############################
    # muon pair selection
    cutflow.add('nEv_ChargeDiMu',  'Dimu pair has opposite-sign mus')
    cutflow.add('nEv_SamePVDiMu',  'Dimu pair has same pv mus')
    cutflow.add('nEv_InvMassDiMu', 'Dimu pair has invariant mass > {0}'.format(cuts['cDiMuInvMass']))
    cutflow.add('nEv_PtDiMu',      'Dimu pair has pT > {0}'.format(cuts['cDiMuPt']))
    cutflow.add('nEv_1DiMu',       'Require at least 1 "good" dimuon pair')
    # preselection
    cutflow.add('nEv_4Lep', 'Preselection: Require 4 or fewer total isolated leptons')

    return cutflow


## ___________________________________________________________
def check_event_selection(analysis):
    cuts = analysis.cuts

    #############################
    # Trigger ###################
    #############################
    # 80X MC has no HLT 
    #exemptHLT = True if (analysis.cmsswversion=='80X' and analysis.ismc) else False
    exemptHLT = False
    passesHLT = analysis.event.PassesHLTs(analysis.hltriggers)

    # if it fails the HLT and isn't exempt, return
    if not exemptHLT:
        if not passesHLT: return False
    analysis.cutflow.increment('nEv_Trigger')

    #############################
    # Primary vertices ##########
    #############################
    # save good vertices
    isVtxNdfOK = False
    isVtxZOK = False
    for pv in analysis.vertices:
        if not isVtxNdfOK: isVtxNdfOK = pv.Ndof() > cuts['cVtxNdf']
        if not isVtxZOK:   isVtxZOK = pv.Z() < cuts['cVtxZ']
        # check if it's passed
        #if not (isVtxNdfOK and isVtxZOK): continue
        # save it if it did
        analysis.good_vertices += [pv]

    # require at least one good vertex
    if not analysis.good_vertices: return False



    ##########################################################
    #                                                        #
    # Candidate selection                                    #
    #                                                        #
    ##########################################################

    #############################
    # MUONS #####################
    #############################
    # loop over muons and save the good ones
    isGAndTr = False
    isPtCutOK = False
    isEtaCutOK = False
    nMuPtEtaMax = 0
    isIsoOK = False
    isIDOK = False
    for muon in analysis.muons:
        # muon cuts
        if not (muon.IsGlobal() and muon.IsTracker()): continue
        isGAndTr = True
        if muon.Pt() < cuts['cMuPt']: continue
        isPtCutOK = True
        if muon.AbsEta() > cuts['cMuEta']: continue
        isEtaCutOK = True

        # make sure at least one HLT-matched muon passes extra cuts
        #if muon.MatchesHLTs(analysis.hltriggers) and muon.Pt() > cuts['cMuPtMax'] and muon.AbsEta() < cuts['cMuEtaMax']: nMuPtEtaMax += 1
        if muon.Pt() > cuts['cMuPtMax'] and muon.AbsEta() < cuts['cMuEtaMax']: nMuPtEtaMax += 1

        # check isolation
        if not (muon.CheckIso('PF_dB', cuts['cMuIso'])): continue
        isIsoOK = True

        # check muon ID
        cMuID = cuts['cMuID']
        isThisIDOK = False
        if cMuID=='tight':    isThisIDOK = muon.IsTightMuon()
        if cMuID=='tight':    isThisIDOK = muon.IsTightMuon()
        elif cMuID=='medium': isThisIDOK = muon.IsMediumMuon()
        elif cMuID=='loose':  isThisIDOK = muon.IsLooseMuon()
        if not (isThisIDOK): continue
        isIDOK = True

        # if we get to this point, push muon into goodMuons
        analysis.good_muons += [muon]


    if isGAndTr: analysis.cutflow.increment('nEv_GAndTr')
    if isPtCutOK: analysis.cutflow.increment('nEv_Pt')
    if isEtaCutOK: analysis.cutflow.increment('nEv_Eta')

    # make sure at least one muon passed extra cuts
    if nMuPtEtaMax < 1: return False
    else: analysis.cutflow.increment('nEv_PtEtaMax')

    if isIsoOK: analysis.cutflow.increment('nEv_Iso')
    if isIDOK: analysis.cutflow.increment('nEv_ID')

    # require at least 2 good muons in this event
    if len(analysis.good_muons) < 2: return False
    analysis.cutflow.increment('nEv_2Mu')




    #############################
    # ELECTRONS #################
    #############################
    # loop over electrons and save the good ones
    for electron in analysis.electrons:
        # electron cuts
        if not electron.Pt() > cuts['cEPt']: continue
        if not electron.AbsEta() < cuts['cEEta']: continue

        # check electron id
        # options: cutbased: IsVetoElectron, IsLooseElectron, IsMediumElectron, IsTightElectron
        #          mva: WP90_v1, WP80_v1
        electronIDOK = False
        cEID = cuts['cEID']
        if cEID=='cbloose':    electronIDOK = electron.IsLooseElectron()
        elif cEID=='cbmedium': electronIDOK = electron.IsMediumElectron()
        elif cEID=='cbtight':  electronIDOK = electron.IsTightElectron()
        elif cEID=='mva80': electronIDOK = electron.WP80_v1()
        elif cEID=='mva90': electronIDOK = electron.WP90_v1()

        if not electronIDOK: continue

        # if we get to this point, push electron into goodElectrons
        analysis.good_electrons += [electron]




    #############################
    # JETS ######################
    #############################
    # initialise empty list of good jets
    # loop over jets
    for jet in analysis.jets:
        # jet cuts
        if not jet.Pt() > cuts['cJetPt']: continue
        if not jet.AbsEta() < cuts['cJetEta']: continue
        if not jet.IsLooseJet(): continue

        # jet cleaning
        # clean jets against our selected muons, electrons, and taus:
        jetIsClean = True
        for mu in analysis.good_muons:
            if DeltaR(mu, jet) < cuts['cDeltaR']: jetIsClean = False
        for e in analysis.good_electrons:
            if DeltaR(e, jet) < cuts['cDeltaR']: jetIsClean = False
        if not jetIsClean: continue

        # save it            
        analysis.good_jets += [jet]

        # btag
        bjetAlg = cuts['cBJetAlg']
        if ((jet.Btag('pass'+bjetAlg)) and (jet.Pt() > cuts['cBJetEta']) and (jet.Pt() > cuts['cBJetPt'])):
            analysis.good_bjets += [jet]


    #############################
    # MET #######################
    #############################
    evtmet = analysis.met.Et()
    evtmetphi = analysis.met.Phi()










    ##########################################################
    #                                                        #
    # Di-candidate reconstruction                            #
    #                                                        #
    ##########################################################

    #############################
    # DIMUON PAIRS ##############
    #############################
    # loop over all possible pairs of muons
    isChargeMuCutOK = False
    isSamePVMuCutOK = False
    isInvMassMuCutOK = False
    isPtDiMuCutOK = False

    # iterate over every (non-ordered) pair of 2 muons in goodMuons
    for p in itertools.combinations(enumerate(analysis.good_muons), 2):
        (i, muon_i), (j, muon_j) = p
        # require opposite sign
        if muon_i.Charge() * muon_j.Charge() > 0: continue
        isChargeMuCutOK = True
        # require from same PV
        if abs(muon_i.Dz() - muon_j.Dz()) > 0.14: continue
        isSamePVMuCutOK = True
        # create composite four-vector
        diMuonP4 = muon_i.P4() + muon_j.P4()
        # require min pT and min InvMass
        if diMuonP4.M() < cuts['cDiMuInvMass']: continue
        isInvMassMuCutOK = True
        if diMuonP4.Pt() < cuts['cDiMuPt']: continue
        isPtDiMuCutOK = True

        #thispair = pair if pair[0].Pt() > pair[1].Pt() else (pair[1], pair[0])
        goodpair = (i, j) if muon_i.Pt() > muon_j.Pt() else (j, i)
        analysis.dimuon_pairs += [goodpair]
        #if (diMuonP4.M() >= analysis.syncLow and diMuonP4.M() <= analysis.syncHigh): analysis.nSyncEvents += 1

    # leftover efficiency counters
    if isChargeMuCutOK: analysis.cutflow.increment('nEv_ChargeDiMu')
    if isSamePVMuCutOK: analysis.cutflow.increment('nEv_SamePVDiMu')
    if isInvMassMuCutOK: analysis.cutflow.increment('nEv_InvMassDiMu')
    if isPtDiMuCutOK: analysis.cutflow.increment('nEv_PtDiMu')

    # require at least one dimuon pair
    if len(analysis.dimuon_pairs) < 1: return False
    analysis.cutflow.increment('nEv_1DiMu')



    #############################
    # DIELECTRON PAIRS ##########
    #############################
    # loop over all possible pairs of electrons
    # iterate over every pair of electrons
    for p in itertools.combinations(enumerate(analysis.good_electrons), 2):
        (i, elec_i), (j, elec_j) = p

        # electron pair cuts
        if elec_i.Charge() * elec_j.Charge() > 0: continue
        if abs(elec_i.Dz() - elec_j.Dz()) > 0.14: continue

        #thispair = pair if pair[0].Pt() > pair[1].Pt() else (pair[1], pair[0])
        goodpair = (i, j) if elec_i.Pt() > elec_j.Pt() else (j, i)
        analysis.dielectron_pairs += [goodpair]



    #############################
    # DIJET PAIRS ###############
    #############################
    if len(analysis.good_jets) > 1: analysis.dijet_pairs += [(0, 1)]



    return True


## ___________________________________________________________
def check_preselection(analysis):
    cuts = analysis.cuts

    num_leptons = len(analysis.good_muons) + len(analysis.good_electrons)

    if (num_leptons > 4): return
    analysis.cutflow.increment('nEv_4Lep')
    return True


## ___________________________________________________________
def check_vh_preselection(analysis):
    cuts = analysis.cuts

    num_leptons = len(analysis.good_muons) + len(analysis.good_electrons)

    if len(analysis.good_bjets) > 0: return False
    analysis.cutflow.increment('nEv_NoBJets')

    if num_leptons < 3: return False
    analysis.cutflow.increment('nEv_3or4Lep')
    return True


####
###### ___________________________________________________________
####def calculate_event_weight(analysis):
####
####break
####
####    ##########################################################
####    # Include pileup reweighting                             #
####    ##########################################################
####    eventweight = 1.
####
####    if not analysis.isdata:
####        eventweight = analysis.event.GenWeight()
####        if analysis.doPileupReweighting:
####            eventweight *= analysis.puweights.getWeight(analysis.event.NumTruePileUpInteractions())
####
####
####    ##########################################################
####    #                                                        #
####    # Update event weight (MC only)                          #
####    #                                                        #
####    ##########################################################
####    if not analysis.isdata:
####        if analysis.includeTriggerScaleFactors:
####            eventweight *= analysis.hltweights.getScale(goodMuons)
####        #else: eventweight *= 0.93
####        if analysis.includeLeptonScaleFactors:
####            eventweight *= analysis.muonweights.getIdScale(goodMuons, cuts['cMuID'])
####            # NB: the below only works for PF w/dB isolation
####            eventweight *= analysis.muonweights.getIsoScale(goodMuons, cuts['cMuID'], cuts['cMuIso'])
####
####
####
