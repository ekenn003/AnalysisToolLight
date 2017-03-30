from CutFlow import *
from Dataform import *
import math
import itertools
from tools.tools import delta_r, Z_MASS, event_is_on_list

## _____________________________________________________________________________
def initialize_cutflow(analysis):
    cutflow = CutFlow()
    cuts = analysis.cuts

    cutflow.add_static('nEv_Orig', 'Original number of events', analysis.nevents)
    cutflow.add('nEv_Skim', 'Skim number of events (>=2 muon candidates)')
    #############################
    # check_event_selection #####
    #############################
    # event selection
    cutflow.add('nEv_Trigger',
        'Trigger')
    # muon selection
    cutflow.add('nEv_GAndTr',
        'Global+Tracker muon')
    cutflow.add('nEv_Pt',
        'Muon pT > {0}'.format(cuts['cMuPt']))
    cutflow.add('nEv_Eta',
        'Muon |eta| < {0}'.format(cuts['cMuEta']))
    cutflow.add('nEv_PtEtaMax',
        'At least 1 trigger-matched mu with '
        'pT > {0} and |eta| < {1}'.format(cuts['cMuPtMax'], cuts['cMuEtaMax']))
    #cutflow.add('nEv_Iso',
    #    'Muon has {0} isolation'.format(cuts['cMuIso']))
    #cutflow.add('nEv_ID',
    #    'Muon has {0} muon ID'.format(cuts['cMuID']))
    cutflow.add('nEv_IDAndIso',
        'Muon has {0} muon ID and {1} {2} isolation'.format(cuts['cMuID'],
        cuts['cMuIsoLevel'], cuts['cMuIsoType']))
    cutflow.add('nEv_2Mu',
        'Require 2 "good" muons')
    #############################
    # check_preselection ########
    #############################
    # muon pair selection
    cutflow.add('nEv_ChargeDiMu',
        'Dimu pair has opposite-sign mus')
    cutflow.add('nEv_SamePVDiMu',
        'Dimu pair has same pv mus')
    cutflow.add('nEv_InvMassDiMu',
        'Dimu pair has invariant mass > {0}'.format(cuts['cDiMuInvMass']))
    cutflow.add('nEv_PtDiMu',
        'Dimu pair has pT > {0}'.format(cuts['cDiMuPt']))
    cutflow.add('nEv_1DiMu',
        'Require at least 1 "good" dimuon pair')
    # preselection
    #cutflow.add('nEv_4Lep', 
    #    'Preselection: Require 4 or fewer total isolated leptons')

    return cutflow


## _____________________________________________________________________________
def check_event_selection(analysis):
    cuts = analysis.cuts

    #############################
    # Trigger ###################
    #############################
    exemptHLT = False
    passesHLT = analysis.event.passes_HLTs(analysis.hltriggers)

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
        if not isVtxNdfOK: isVtxNdfOK = pv.n_dof() > cuts['cVtxNdf']
        if not isVtxZOK:   isVtxZOK = pv.z() < cuts['cVtxZ']
        # check if it's passed
        if not (isVtxNdfOK and isVtxZOK): continue
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
    isIDAndIsoOK = False
    for muon in analysis.muons:
        # muon cuts
        if not (muon.is_global() and muon.is_tracker()): continue
        isGAndTr = True
        if muon.pt() < cuts['cMuPt']: continue
        isPtCutOK = True
        if muon.abs_eta() > cuts['cMuEta']: continue
        isEtaCutOK = True

        # make sure at least one HLT-matched muon passes extra cuts
        if (muon.pt() > cuts['cMuPtMax']
            and muon.abs_eta() < cuts['cMuEtaMax']): nMuPtEtaMax += 1

        # check muon ID and isolation
        if not all(muon.check_id_and_iso(cuts['cMuID'],
            cuts['cMuIsoType'], cuts['cMuIsoLevel'])): continue
        isIDAndIsoOK = True

        # if we get to this point, push muon into goodMuons
        analysis.good_muons += [muon]


    if isGAndTr: analysis.cutflow.increment('nEv_GAndTr')
    if isPtCutOK: analysis.cutflow.increment('nEv_Pt')
    if isEtaCutOK: analysis.cutflow.increment('nEv_Eta')

    # make sure at least one muon passed extra cuts
    if nMuPtEtaMax < 1: return False
    analysis.cutflow.increment('nEv_PtEtaMax')

    if isIDAndIsoOK: analysis.cutflow.increment('nEv_IDAndIso')

    # require at least 2 good muons in this event
    if len(analysis.good_muons) < 2: return False
    analysis.cutflow.increment('nEv_2Mu')




    #############################
    # ELECTRONS #################
    #############################
    # loop over electrons and save the good ones
    for electron in analysis.electrons:
        # electron cuts
        if electron.pt() < cuts['cEPt']: continue
        if electron.abs_eta() > cuts['cEEta']: continue

        # check electron id
        # options: cutbased: IsVetoElectron, IsLooseElectron, IsMediumElectron, IsTightElectron
        #          mva: WP90_v1, WP80_v1
        electronIDOK = False
        cEID = cuts['cEID']
        if cEID=='cbloose':    electronIDOK = electron.is_loose()
        elif cEID=='cbmedium': electronIDOK = electron.is_medium()
        elif cEID=='cbtight':  electronIDOK = electron.is_tight()

        if not electronIDOK: continue

        # sync
        if not (electron.abs_eta() < 1.4442
            or (electron.abs_eta() < 2.5 and electron.abs_eta() > 1.566)):
            continue


        # if we get to this point, push electron into goodElectrons
        analysis.good_electrons += [electron]




    #############################
    # JETS ######################
    #############################
    # loop over jets
    for jet in analysis.jets:
        # jet cuts
        if jet.pt() < cuts['cJetPt']: continue
        if jet.abs_eta() > cuts['cJetEta']: continue
        if not jet.is_loose(): continue

        # jet cleaning
        # clean jets against our selected muons, electrons:
        jetIsClean = True
        for mu in analysis.good_muons:
            if delta_r(mu, jet) < cuts['cDeltaR']: jetIsClean = False
        for e in analysis.good_electrons:
            if delta_r(e, jet) < cuts['cDeltaR']: jetIsClean = False
        if not jetIsClean: continue

        # save it            
        analysis.good_jets += [jet]

        # btag
        if (jet.btag(cuts['cBJetAlg'])
            and jet.abs_eta() < cuts['cBJetEta']
            and jet.pt() > cuts['cBJetPt']):
            analysis.good_bjets += [jet]


    #############################
    # MET #######################
    #############################
    evtmet = analysis.met.et()
    evtmetphi = analysis.met.phi()




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
        if muon_i.charge() * muon_j.charge() > 0: continue
        isChargeMuCutOK = True
        # require from same PV
        if abs(muon_i.dz() - muon_j.dz()) > 0.14: continue
        isSamePVMuCutOK = True
        # create composite four-vector
        diMuonP4 = muon_i.p4() + muon_j.p4()
        # require min pT and min InvMass
        if diMuonP4.M() < cuts['cDiMuInvMass']: continue
        isInvMassMuCutOK = True
        if diMuonP4.Pt() < cuts['cDiMuPt']: continue
        isPtDiMuCutOK = True

        goodpair = (i, j) if muon_i.pt() > muon_j.pt() else (j, i)
        analysis.dimuon_pairs += [goodpair]

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
        if elec_i.charge() * elec_j.charge() > 0: continue
        if abs(elec_i.dz() - elec_j.dz()) > 0.14: continue

        #thispair = pair if pair[0].Pt() > pair[1].Pt() else (pair[1], pair[0])
        goodpair = (i, j) if elec_i.pt() > elec_j.pt() else (j, i)
        analysis.dielectron_pairs += [goodpair]



    #############################
    # DIJET PAIRS ###############
    #############################
    #if len(analysis.good_jets) > 1: analysis.dijet_pairs += [(0, 1)]

    for p in itertools.combinations(enumerate(analysis.good_jets), 2):
        (i, jet_i), (j, jet_j) = p

        goodpair = (i, j) if jet_i.pt() > jet_j.pt() else (j, i)
        analysis.dijet_pairs += [goodpair]

    return True


## _____________________________________________________________________________
def check_preselection(analysis):
    cuts = analysis.cuts

    num_leptons = len(analysis.good_muons) + len(analysis.good_electrons)

    if (num_leptons > 4): return False
    #analysis.cutflow.increment('nEv_4Lep')
    return True


## _____________________________________________________________________________
def check_vh_preselection(analysis):
    cuts = analysis.cuts

    num_leptons = len(analysis.good_muons) + len(analysis.good_electrons)

    if len(analysis.good_bjets) > 0: return False
    analysis.cutflow.increment('nEv_NoBJets')

    if num_leptons < 3: return False
    #analysis.cutflow.increment('nEv_3or4Lep')
    return True



## _____________________________________________________________________________
def get_event_category(analysis, dimuonobj):
    #cuts = analysis.cuts

    # 80X sync evt selection: exactly 2 muons, 0 electrons
    passes_sync_selection = (len(analysis.good_electrons) == 0
        and len(analysis.good_muons) == 2
        and len(analysis.good_bjets) == 0)

    # 80X sync preselection: 0 bjets, at least 2 regular jets,
    #     leading/subleading jet 40/30 GeV
    jet_count_is_ok = len(analysis.good_bjets) == 0 and len(analysis.good_jets) >= 2

    jet_pts_are_ok = False
    for i, p in enumerate(analysis.dijet_pairs):
        # should already be ordered by pT
        if (analysis.good_jets[p[0]].pt() > 40.
            and analysis.good_jets[p[1]].pt() > 30.):
            jet_pts_are_ok = True

    passes_sync_preselection = jet_count_is_ok and jet_pts_are_ok


    if not passes_sync_selection: return -1



    # check if we have a VBF tight jet pair
    have_vbftight_pair = False

    for i, p in enumerate(analysis.dijet_pairs):
        vbftight_dijet_mass_ok = False
        vbftight_dijet_deta_ok = False

        if not (analysis.good_jets[p[0]].pt() > 40.
            and analysis.good_jets[p[1]].pt() > 30.): continue

        thisdijet = analysis.good_jets[p[0]].p4() + analysis.good_jets[p[1]].p4()

        # VBFTight: two conditions
        if thisdijet.M() > 650.:
            vbftight_dijet_mass_ok = True
        if abs(analysis.good_jets[p[0]].eta()
            - analysis.good_jets[p[1]].eta()) > 3.5:
            vbftight_dijet_deta_ok = True

        if vbftight_dijet_mass_ok and vbftight_dijet_deta_ok:
            have_vbftight_pair = True
            break

    # check if we have a GGF tight jet pair
    have_ggftight_pair = False

    for i, p in enumerate(analysis.dijet_pairs):    
        ggftight_dijet_mass_ok = False
        ggftight_dimuon_pt_ok = False

        if not (analysis.good_jets[p[0]].pt() > 40.
            and analysis.good_jets[p[1]].pt() > 30.): continue

        thisdijet = analysis.good_jets[p[0]].p4() + analysis.good_jets[p[1]].p4()

        # GGFTight: two conditions
        if thisdijet.M() > 250.: ggftight_dijet_mass_ok = True
        if dimuonobj.Pt() > 50.: ggftight_dimuon_pt_ok = True

        if ggftight_dijet_mass_ok and ggftight_dimuon_pt_ok:
            have_ggftight_pair = True
            break



    analysis.fnumCat0 += 1
    if passes_sync_selection and passes_sync_preselection:
        if have_vbftight_pair:
            analysis.fnumCat1 += 1
            return 1
        elif have_ggftight_pair:
            analysis.fnumCat2 += 1
            return 2
        else:
            analysis.fnumCat3 += 1
            return 3
    elif passes_sync_selection:
        if dimuonobj.Pt() >= 25.:
            analysis.fnumCat4 += 1
            return 4
        else:
            analysis.fnumCat5 += 1
            return 5
    else: return -111111111111111111111


