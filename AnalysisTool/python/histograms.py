from ROOT import TH1F, TH2D

##########################################################
#                                                        #
# Book histograms                                        #
#                                                        #
##########################################################

histograms = {}

histograms['hVtxN'] = TH1F('hVtxN', 'hVtxN', 100, 0., 100.)
histograms['hVtxN'].GetXaxis().SetTitle('N_{PV}')
histograms['hVtxN'].GetYaxis().SetTitle('Candidates')
histograms['hVtxN_u'] = TH1F('hVtxN_u', 'hVtxN_u', 100, 0., 100.)
histograms['hVtxN_u'].GetXaxis().SetTitle('N_{PV} before event weighting')
histograms['hVtxN_u'].GetYaxis().SetTitle('Candidates')
histograms['hVtxN_nopu'] = TH1F('hVtxN_nopu', 'hVtxN_nopu', 100, 0., 100.)
histograms['hVtxN_nopu'].GetXaxis().SetTitle('N_{PV} before event or PU weighting')
histograms['hVtxN_nopu'].GetYaxis().SetTitle('Candidates')

histograms['hWeight'] = TH1F('hWeight', 'hWeight', 100, -1000., 100.)
histograms['hWeight'].GetXaxis().SetTitle('Event weight')
histograms['hWeight'].GetYaxis().SetTitle('Events')


#############################
# Muons #####################
#############################
histograms['hNumMu'] = TH1F('hNumMu', 'hNumMu', 20, 0., 20.)
histograms['hNumMu'].GetXaxis().SetTitle('N_{#mu}')
histograms['hNumMu'].GetYaxis().SetTitle('Candidates')

histograms['hMuPt'] = TH1F('hMuPt', 'hMuPt', 500, 0., 1000.)
histograms['hMuPt'].GetXaxis().SetTitle('p_{T #mu}[GeV/c]')
histograms['hMuPt'].GetYaxis().SetTitle('Candidates/2.0[GeV/c]')

histograms['hMuEta'] = TH1F('hMuEta', 'hMuEta',  52, -2.6, 2.6)
histograms['hMuEta'].GetXaxis().SetTitle('#eta_{#mu}')
histograms['hMuEta'].GetYaxis().SetTitle('Candidates/0.1')

histograms['hMuPhi'] = TH1F('hMuPhi', 'hMuPhi', 34, -3.4, 3.4)
histograms['hMuPhi'].GetXaxis().SetTitle('#varphi_{#mu} [rad]')
histograms['hMuPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

# leading/subleading good muons
histograms['hLeadMuPt'] = TH1F('hLeadMuPt', 'hLeadMuPt', 500, 0., 1000.)
histograms['hLeadMuPt'].GetXaxis().SetTitle('p_{T #mu}[GeV/c]')
histograms['hLeadMuPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')

histograms['hSubLeadMuPt'] = TH1F('hSubLeadMuPt', 'hSubLeadMuPt', 500, 0., 1000.)
histograms['hSubLeadMuPt'].GetXaxis().SetTitle('p_{T #mu}[GeV/c]')
histograms['hSubLeadMuPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')



#############################
# Electrons #################
#############################
histograms['hNumE'] = TH1F('hNumE', 'hNumE', 20, 0., 20.)
histograms['hNumE'].GetXaxis().SetTitle('N_{e}')
histograms['hNumE'].GetYaxis().SetTitle('Candidates')

histograms['hEPt'] = TH1F('hEPt', 'hEPt', 500, 0., 1000.)
histograms['hEPt'].GetXaxis().SetTitle('p_{T e}[GeV/c]')
histograms['hEPt'].GetYaxis().SetTitle('Candidates/2.0[GeV/c]')

histograms['hEEta'] = TH1F('hEEta', 'hEEta',  52, -2.6, 2.6)
histograms['hEEta'].GetXaxis().SetTitle('#eta_{e}')
histograms['hEEta'].GetYaxis().SetTitle('Candidates/0.1')

histograms['hEPhi'] = TH1F('hEPhi', 'hEPhi', 34, -3.4, 3.4)
histograms['hEPhi'].GetXaxis().SetTitle('#varphi_{e} [rad]')
histograms['hEPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

# leading/subleading good electrons
histograms['hLeadEPt'] = TH1F('hLeadEPt', 'hLeadEPt', 500, 0., 1000.)
histograms['hLeadEPt'].GetXaxis().SetTitle('p_{T e}[GeV/c]')
histograms['hLeadEPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')

histograms['hSubLeadEPt'] = TH1F('hSubLeadEPt', 'hSubLeadEPt', 500, 0., 1000.)
histograms['hSubLeadEPt'].GetXaxis().SetTitle('p_{T e}[GeV/c]')
histograms['hSubLeadEPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')

#############################
# Jets ######################
#############################
histograms['hNumBJets'] = TH1F('hNumBJets', 'hNumBJets', 20, 0., 20.)
histograms['hNumBJets'].GetXaxis().SetTitle('N_{j_{b}}')
histograms['hNumBJets'].GetYaxis().SetTitle('Candidates')

histograms['hNumJets'] = TH1F('hNumJets', 'hNumJets', 20, 0., 20.)
histograms['hNumJets'].GetXaxis().SetTitle('N_{j}')
histograms['hNumJets'].GetYaxis().SetTitle('Candidates')

histograms['hJetPt'] = TH1F('hJetPt', 'hJetPt', 500, 0., 1000.)
histograms['hJetPt'].GetXaxis().SetTitle('p_{T j}[GeV/c]')
histograms['hJetPt'].GetYaxis().SetTitle('Candidates/2.0[GeV/c]')

histograms['hJetEta'] = TH1F('hJetEta', 'hJetEta',  52, -2.6, 2.6)
histograms['hJetEta'].GetXaxis().SetTitle('#eta_{j}')
histograms['hJetEta'].GetYaxis().SetTitle('Candidates/0.1')

histograms['hJetPhi'] = TH1F('hJetPhi', 'hJetPhi', 34, -3.4, 3.4)
histograms['hJetPhi'].GetXaxis().SetTitle('#varphi_{j} [rad]')
histograms['hJetPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')
# leading/subleading good jets
histograms['hLeadJetPt'] = TH1F('hLeadJetPt', 'hLeadJetPt', 500, 0., 1000.)
histograms['hLeadJetPt'].GetXaxis().SetTitle('p_{T j}[GeV/c]')
histograms['hLeadJetPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')

histograms['hSubLeadJetPt'] = TH1F('hSubLeadJetPt', 'hSubLeadJetPt', 500, 0., 1000.)
histograms['hSubLeadJetPt'].GetXaxis().SetTitle('p_{T j}[GeV/c]')
histograms['hSubLeadJetPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')


#############################
# Dimuon ####################
#############################
histograms['hNumDiMu'] = TH1F('hNumDiMu', 'hNumDiMu', 6, 0, 6)
histograms['hNumDiMu'].GetXaxis().SetTitle('N_{#mu^{+}#mu^{-}}')
histograms['hNumDiMu'].GetYaxis().SetTitle('Candidates')

histograms['hDiMuPt'] = TH1F('hDiMuPt', 'hDiMuPt', 500, 0., 1000.)
histograms['hDiMuPt'].GetXaxis().SetTitle('p_{T #mu^{+}#mu^{-}}[GeV/c]')
histograms['hDiMuPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')
histograms['hDiMuEta'] = TH1F('hDiMuEta', 'hDiMuEta',  132, -6.6, 6.6)
histograms['hDiMuEta'].GetXaxis().SetTitle('#eta_{#mu^{+}#mu^{-}}')
histograms['hDiMuEta'].GetYaxis().SetTitle('Candidates/0.1')
histograms['hDiMuPhi'] = TH1F('hDiMuPhi', 'hDiMuPhi', 34, -3.4, 3.4)
histograms['hDiMuPhi'].GetXaxis().SetTitle('#varphi_{#mu^{+}#mu^{-}} [rad]')
histograms['hDiMuPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

histograms['hDiMuDeltaPt'] = TH1F('hDiMuDeltaPt', 'hDiMuDeltaPt', 400, 0., 800.)
histograms['hDiMuDeltaPt'].GetXaxis().SetTitle('#Delta p_{T #mu^{+} - #mu^{-}}[GeV/c]')
histograms['hDiMuDeltaPt'].GetYaxis().SetTitle('Candidates/5.0[GeV]')
histograms['hDiMuDeltaEta'] = TH1F('hDiMuDeltaEta', 'hDiMuDeltaEta',  132, -6.6, 6.6)
histograms['hDiMuDeltaEta'].GetXaxis().SetTitle('#Delta #eta_{#mu^{+} - #mu^{-}}')
histograms['hDiMuDeltaEta'].GetYaxis().SetTitle('Candidates/0.1')
histograms['hDiMuDeltaPhi'] = TH1F('hDiMuDeltaPhi', 'hDiMuDeltaPhi', 34, -3.4, 3.4)
histograms['hDiMuDeltaPhi'].GetXaxis().SetTitle('#Delta #varphi_{#mu^{+} - #mu^{-}} [rad]')
histograms['hDiMuDeltaPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

histograms['hDiMuInvMass'] = TH1F('hDiMuInvMass', 'hDiMuInvMass', 2000, 0, 1000)
histograms['hDiMuInvMass'].GetXaxis().SetTitle('M_{#mu^{+}#mu^{-}} [GeV/c^{2}]')
histograms['hDiMuInvMass'].GetYaxis().SetTitle('Candidates/0.5[GeV/c^{2}]')

#############################
# Dielectron ################
#############################
histograms['hDiEPt'] = TH1F('hDiEPt', 'hDiEPt', 500, 0., 1000.)
histograms['hDiEPt'].GetXaxis().SetTitle('p_{T e^{+}e^{-}}[GeV/c]')
histograms['hDiEPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')
histograms['hDiEEta'] = TH1F('hDiEEta', 'hDiEEta',  132, -6.6, 6.6)
histograms['hDiEEta'].GetXaxis().SetTitle('#eta_{e^{+}e^{-}}')
histograms['hDiEEta'].GetYaxis().SetTitle('Candidates/0.1')
histograms['hDiEPhi'] = TH1F('hDiEPhi', 'hDiEPhi', 34, -3.4, 3.4)
histograms['hDiEPhi'].GetXaxis().SetTitle('#varphi_{e^{+}e^{-}} [rad]')
histograms['hDiEPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

histograms['hDiEDeltaPt'] = TH1F('hDiEDeltaPt', 'hDiEDeltaPt', 400, 0., 800.)
histograms['hDiEDeltaPt'].GetXaxis().SetTitle('#Delta p_{T e^{+} - e^{-}}[GeV/c]')
histograms['hDiEDeltaPt'].GetYaxis().SetTitle('Candidates/5.0[GeV]')
histograms['hDiEDeltaEta'] = TH1F('hDiEDeltaEta', 'hDiEDeltaEta',  132, -6.6, 6.6)
histograms['hDiEDeltaEta'].GetXaxis().SetTitle('#Delta #eta_{e^{+} - e^{-}}')
histograms['hDiEDeltaEta'].GetYaxis().SetTitle('Candidates/0.1')
histograms['hDiEDeltaPhi'] = TH1F('hDiEDeltaPhi', 'hDiEDeltaPhi', 34, -3.4, 3.4)
histograms['hDiEDeltaPhi'].GetXaxis().SetTitle('#Delta #varphi_{e^{+} - e^{-}} [rad]')
histograms['hDiEDeltaPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

histograms['hDiEInvMass'] = TH1F('hDiEInvMass', 'hDiEInvMass', 2000, 0, 1000)
histograms['hDiEInvMass'].GetXaxis().SetTitle('M_{e^{+}e^{-}} [GeV/c^{2}]')
histograms['hDiEInvMass'].GetYaxis().SetTitle('Candidates/0.5[GeV/c^{2}]')

#############################
# Dijet #####################
#############################
histograms['hDiJetPt'] = TH1F('hDiJetPt', 'hDiJetPt', 500, 0., 1000.)
histograms['hDiJetPt'].GetXaxis().SetTitle('p_{T j^{+}j^{-}}[GeV/c]')
histograms['hDiJetPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')
histograms['hDiJetEta'] = TH1F('hDiJetEta', 'hDiJetEta',  132, -6.6, 6.6)
histograms['hDiJetEta'].GetXaxis().SetTitle('#eta_{j^{+}j^{-}}')
histograms['hDiJetEta'].GetYaxis().SetTitle('Candidates/0.1')
histograms['hDiJetPhi'] = TH1F('hDiJetPhi', 'hDiJetPhi', 34, -3.4, 3.4)
histograms['hDiJetPhi'].GetXaxis().SetTitle('#varphi_{j^{+}j^{-}} [rad]')
histograms['hDiJetPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

histograms['hDiJetDeltaPt'] = TH1F('hDiJetDeltaPt', 'hDiJetDeltaPt', 400, 0., 800.)
histograms['hDiJetDeltaPt'].GetXaxis().SetTitle('#Delta p_{T j^{+} - j^{-}}[GeV/c]')
histograms['hDiJetDeltaPt'].GetYaxis().SetTitle('Candidates/5.0[GeV]')
histograms['hDiJetDeltaEta'] = TH1F('hDiJetDeltaEta', 'hDiJetDeltaEta',  132, -6.6, 6.6)
histograms['hDiJetDeltaEta'].GetXaxis().SetTitle('#Delta #eta_{j^{+} - j^{-}}')
histograms['hDiJetDeltaEta'].GetYaxis().SetTitle('Candidates/0.1')
histograms['hDiJetDeltaPhi'] = TH1F('hDiJetDeltaPhi', 'hDiJetDeltaPhi', 34, -3.4, 3.4)
histograms['hDiJetDeltaPhi'].GetXaxis().SetTitle('#Delta #varphi_{j^{+} - j^{-}} [rad]')
histograms['hDiJetDeltaPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

histograms['hDiJetInvMass'] = TH1F('hDiJetInvMass', 'hDiJetInvMass', 2000, 0, 1000)
histograms['hDiJetInvMass'].GetXaxis().SetTitle('M_{j^{+}j^{-}} [GeV/c^{2}]')
histograms['hDiJetInvMass'].GetYaxis().SetTitle('Candidates/0.5[GeV/c^{2}]')


#############################
# MET #######################
#############################
histograms['hMET'] = TH1F('hMET', 'hMET', 500, 0., 1000.)
histograms['hMET'].GetXaxis().SetTitle('E_{T miss}[GeV/c]')
histograms['hMET'].GetYaxis().SetTitle('Candidates/2.0[GeV/c]')

histograms['hMETPhi'] = TH1F('hMETPhi', 'hMETPhi', 34, -3.4, 3.4)
histograms['hMETPhi'].GetXaxis().SetTitle('#varphi_{MET} [rad]')
histograms['hMETPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')



## ___________________________________________________________
def fill_base_histograms(analysis, eventweight, fillcontrol):
    '''
    Fills histograms which are included in every derived analysis.
    '''
    ##########################################################
    #                                                        #
    # Fill histograms                                        #
    #                                                        #
    ##########################################################

    #############################
    # PV after selection ########
    #############################
    # fill histograms with good pvs
    analysis.histograms['hVtxN'].Fill(len(analysis.vertices), eventweight)

    #############################
    # Muons #####################
    #############################
    analysis.histograms['hNumMu'].Fill(len(analysis.good_muons), eventweight)
    analysis.histograms['hLeadMuPt'].Fill(analysis.good_muons[0].pt(), eventweight)

    if analysis.good_muons[0].pt() < 26.:
    #if analysis.good_muons[0].pt('uncor') != analysis.good_muons[0].pt('cor'):
        print '****************************\npt anomaly found :', analysis.event.number()
        print 'pt muon[0] =', analysis.good_muons[0].pt(), ' pt muon[1] =', analysis.good_muons[1].pt()
        print '****************************'


    analysis.histograms['hSubLeadMuPt'].Fill(analysis.good_muons[1].pt(), eventweight)
    if fillcontrol:
        analysis.histograms_ctrl['hLeadMuPt_ctrl'].Fill(analysis.good_muons[0].pt(), eventweight)
        analysis.histograms_ctrl['hSubLeadMuPt_ctrl'].Fill(analysis.good_muons[1].pt(), eventweight)

    for mu in analysis.good_muons:
        analysis.histograms['hMuPt'].Fill(mu.pt(), eventweight)
        analysis.histograms['hMuEta'].Fill(mu.eta(), eventweight)
        analysis.histograms['hMuPhi'].Fill(mu.phi(), eventweight)
        # fill comtrol plots
        if fillcontrol:
            analysis.histograms_ctrl['hMuPt_ctrl'].Fill(mu.pt(), eventweight)
            analysis.histograms_ctrl['hMuEta_ctrl'].Fill(mu.eta(), eventweight)
            analysis.histograms_ctrl['hMuPhi_ctrl'].Fill(mu.phi(), eventweight)

    #############################
    # Dimuon ####################
    #############################
    for i, j in analysis.dimuon_pairs:
        muon1 = analysis.good_muons[i]
        muon2 = analysis.good_muons[j]
        dimuobj = muon1.p4() + muon2.p4()

        analysis.histograms['hDiMuPt'].Fill(dimuobj.Pt(), eventweight)
        analysis.histograms['hDiMuEta'].Fill(dimuobj.Eta(), eventweight)
        analysis.histograms['hDiMuPhi'].Fill(dimuobj.Phi(), eventweight)
        analysis.histograms['hDiMuInvMass'].Fill(dimuobj.M(), eventweight)

        analysis.histograms['hDiMuDeltaPt'].Fill(muon1.pt() - muon2.pt(), eventweight)
        analysis.histograms['hDiMuDeltaEta'].Fill(muon1.eta() - muon2.eta(), eventweight)
        analysis.histograms['hDiMuDeltaPhi'].Fill(muon1.phi() - muon2.phi(), eventweight)

        # fill control plots
        if fillcontrol:
            analysis.histograms_ctrl['hDiMuPt_ctrl'].Fill(dimuobj.Pt(), eventweight)
            analysis.histograms_ctrl['hDiMuEta_ctrl'].Fill(dimuobj.Eta(), eventweight)
            analysis.histograms_ctrl['hDiMuPhi_ctrl'].Fill(dimuobj.Phi(), eventweight)
            analysis.histograms_ctrl['hDiMuInvMass_ctrl'].Fill(dimuobj.M(), eventweight)

            analysis.histograms_ctrl['hDiMuDeltaPt_ctrl'].Fill(muon1.pt() - muon2.pt(), eventweight)
            analysis.histograms_ctrl['hDiMuDeltaEta_ctrl'].Fill(muon1.eta() - muon2.eta(), eventweight)
            analysis.histograms_ctrl['hDiMuDeltaPhi_ctrl'].Fill(muon1.phi() - muon2.phi(), eventweight)

    #############################
    # Electrons #################
    #############################
    analysis.histograms['hNumE'].Fill(len(analysis.good_electrons), eventweight)
    for e in analysis.good_electrons:
        analysis.histograms['hEPt'].Fill(e.pt(), eventweight)
        analysis.histograms['hEEta'].Fill(e.eta(), eventweight)
        analysis.histograms['hEPhi'].Fill(e.phi(), eventweight)
    # leading electron
    if len(analysis.good_electrons) > 0:
        analysis.histograms['hLeadEPt'].Fill(analysis.good_electrons[0].pt(), eventweight)
    # subleading electron
    if len(analysis.good_electrons) > 1:
        analysis.histograms['hSubLeadEPt'].Fill(analysis.good_electrons[1].pt(), eventweight)

    #############################
    # Dielectron ################
    #############################
    for i, j in analysis.dielectron_pairs:
        elec1 = analysis.good_electrons[i]
        elec2 = analysis.good_electrons[j]
        dielobj = elec1.p4() + elec2.p4()

        analysis.histograms['hDiEPt'].Fill(dielobj.Pt(), eventweight)
        analysis.histograms['hDiEEta'].Fill(dielobj.Eta(), eventweight)
        analysis.histograms['hDiEPhi'].Fill(dielobj.Phi(), eventweight)
        analysis.histograms['hDiEInvMass'].Fill(dielobj.M(), eventweight)

        analysis.histograms['hDiEDeltaPt'].Fill(elec1.pt() - elec2.pt(), eventweight)
        analysis.histograms['hDiEDeltaEta'].Fill(elec1.eta() - elec2.eta(), eventweight)
        analysis.histograms['hDiEDeltaPhi'].Fill(elec1.phi() - elec2.phi(), eventweight)

        # fill control plots
        if fillcontrol:
            analysis.histograms_ctrl['hDiEPt_ctrl'].Fill(dielobj.Pt(), eventweight)
            analysis.histograms_ctrl['hDiEEta_ctrl'].Fill(dielobj.Eta(), eventweight)
            analysis.histograms_ctrl['hDiEPhi_ctrl'].Fill(dielobj.Phi(), eventweight)
            analysis.histograms_ctrl['hDiEInvMass_ctrl'].Fill(dielobj.M(), eventweight)

            analysis.histograms_ctrl['hDiEDeltaPt_ctrl'].Fill(elec1.pt() - elec2.pt(), eventweight)
            analysis.histograms_ctrl['hDiEDeltaEta_ctrl'].Fill(elec1.eta() - elec2.eta(), eventweight)
            analysis.histograms_ctrl['hDiEDeltaPhi_ctrl'].Fill(elec1.phi() - elec2.phi(), eventweight)


    #############################
    # Jets ######################
    #############################
    analysis.histograms['hNumJets'].Fill(len(analysis.good_jets), eventweight)
    analysis.histograms['hNumBJets'].Fill(len(analysis.good_bjets), eventweight)

    for jet in analysis.good_jets:
        analysis.histograms['hJetPt'].Fill(jet.pt(), eventweight)
        analysis.histograms['hJetEta'].Fill(jet.eta(), eventweight)
        analysis.histograms['hJetPhi'].Fill(jet.phi(), eventweight)
    # leading jet
    if len(analysis.good_jets) > 0:
        analysis.histograms['hLeadJetPt'].Fill(analysis.good_jets[0].pt(), eventweight)
    # subleading jet
    if len(analysis.good_jets) > 1:
        analysis.histograms['hSubLeadJetPt'].Fill(analysis.good_jets[1].pt(), eventweight)

#    #############################
#    # Dijet #####################
#    #############################
#    for i, j in analysis.dijet_pairs:
#        
#        diJetP4 = jetpair[0].P4() + jetpair[1].P4()
#        analysis.histograms['hDiJetPt'].Fill(diJetP4.Pt(), eventweight)
#        analysis.histograms['hDiJetEta'].Fill(diJetP4.Eta(), eventweight)
#        analysis.histograms['hDiJetPhi'].Fill(diJetP4.Phi(), eventweight)
#        analysis.histograms['hDiJetInvMass'].Fill(diJetP4.M(), eventweight)
#        analysis.histograms['hDiJetDeltaPt'].Fill(jetpair[0].Pt() - jetpair[1].Pt(), eventweight)
#        analysis.histograms['hDiJetDeltaEta'].Fill(jetpair[0].Eta() - jetpair[1].Eta(), eventweight)
#        analysis.histograms['hDiJetDeltaPhi'].Fill(jetpair[0].Phi() - jetpair[1].Phi(), eventweight)
#

    #############################
    # MET #######################
    #############################
    analysis.histograms['hMET'].Fill(analysis.met.et(), eventweight)
    analysis.histograms['hMETPhi'].Fill(analysis.met.phi(), eventweight)
    # fill control plots
    if fillcontrol:
        analysis.histograms_ctrl['hMET_ctrl'].Fill(analysis.met.et(), eventweight)
        analysis.histograms_ctrl['hMETPhi_ctrl'].Fill(analysis.met.phi(), eventweight)






