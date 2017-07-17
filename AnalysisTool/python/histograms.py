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



##############################
## Electrons #################
##############################
#histograms['hNumE'] = TH1F('hNumE', 'hNumE', 20, 0., 20.)
#histograms['hNumE'].GetXaxis().SetTitle('N_{e}')
#histograms['hNumE'].GetYaxis().SetTitle('Candidates')
#
#histograms['hEPt'] = TH1F('hEPt', 'hEPt', 500, 0., 1000.)
#histograms['hEPt'].GetXaxis().SetTitle('p_{T e}[GeV/c]')
#histograms['hEPt'].GetYaxis().SetTitle('Candidates/2.0[GeV/c]')
#
#histograms['hEEta'] = TH1F('hEEta', 'hEEta',  52, -2.6, 2.6)
#histograms['hEEta'].GetXaxis().SetTitle('#eta_{e}')
#histograms['hEEta'].GetYaxis().SetTitle('Candidates/0.1')
#
#histograms['hEPhi'] = TH1F('hEPhi', 'hEPhi', 34, -3.4, 3.4)
#histograms['hEPhi'].GetXaxis().SetTitle('#varphi_{e} [rad]')
#histograms['hEPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')
#
## leading/subleading good electrons
#histograms['hLeadEPt'] = TH1F('hLeadEPt', 'hLeadEPt', 500, 0., 1000.)
#histograms['hLeadEPt'].GetXaxis().SetTitle('p_{T e}[GeV/c]')
#histograms['hLeadEPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')
#
#histograms['hSubLeadEPt'] = TH1F('hSubLeadEPt', 'hSubLeadEPt', 500, 0., 1000.)
#histograms['hSubLeadEPt'].GetXaxis().SetTitle('p_{T e}[GeV/c]')
#histograms['hSubLeadEPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')

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

##############################
## Dielectron ################
##############################
#histograms['hDiEPt'] = TH1F('hDiEPt', 'hDiEPt', 500, 0., 1000.)
#histograms['hDiEPt'].GetXaxis().SetTitle('p_{T e^{+}e^{-}}[GeV/c]')
#histograms['hDiEPt'].GetYaxis().SetTitle('Candidates/2.0[GeV]')
#histograms['hDiEEta'] = TH1F('hDiEEta', 'hDiEEta',  132, -6.6, 6.6)
#histograms['hDiEEta'].GetXaxis().SetTitle('#eta_{e^{+}e^{-}}')
#histograms['hDiEEta'].GetYaxis().SetTitle('Candidates/0.1')
#histograms['hDiEPhi'] = TH1F('hDiEPhi', 'hDiEPhi', 34, -3.4, 3.4)
#histograms['hDiEPhi'].GetXaxis().SetTitle('#varphi_{e^{+}e^{-}} [rad]')
#histograms['hDiEPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')
#
#histograms['hDiEDeltaPt'] = TH1F('hDiEDeltaPt', 'hDiEDeltaPt', 400, 0., 800.)
#histograms['hDiEDeltaPt'].GetXaxis().SetTitle('#Delta p_{T e^{+} - e^{-}}[GeV/c]')
#histograms['hDiEDeltaPt'].GetYaxis().SetTitle('Candidates/5.0[GeV]')
#histograms['hDiEDeltaEta'] = TH1F('hDiEDeltaEta', 'hDiEDeltaEta',  132, -6.6, 6.6)
#histograms['hDiEDeltaEta'].GetXaxis().SetTitle('#Delta #eta_{e^{+} - e^{-}}')
#histograms['hDiEDeltaEta'].GetYaxis().SetTitle('Candidates/0.1')
#histograms['hDiEDeltaPhi'] = TH1F('hDiEDeltaPhi', 'hDiEDeltaPhi', 34, -3.4, 3.4)
#histograms['hDiEDeltaPhi'].GetXaxis().SetTitle('#Delta #varphi_{e^{+} - e^{-}} [rad]')
#histograms['hDiEDeltaPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')
#
#histograms['hDiEInvMass'] = TH1F('hDiEInvMass', 'hDiEInvMass'	, 2000, 0, 1000)
#histograms['hDiEInvMass'].GetXaxis().SetTitle('M_{e^{+}e^{-}} [GeV/c^{2}]')
#histograms['hDiEInvMass'].GetYaxis().SetTitle('Candidates/0.5[GeV/c^{2}]')

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
histograms['hDiJetDeltaEta'] = TH1F('hDiJetDeltaEta', 'hDiJetDeltaEta',  132, 0., 6.6)
histograms['hDiJetDeltaEta'].GetXaxis().SetTitle('|#Delta #eta_{j^{+} - j^{-}}|')
histograms['hDiJetDeltaEta'].GetYaxis().SetTitle('Candidates/0.1')
histograms['hDiJetDeltaPhi'] = TH1F('hDiJetDeltaPhi', 'hDiJetDeltaPhi', 34, 0., 3.4)
histograms['hDiJetDeltaPhi'].GetXaxis().SetTitle('|#Delta #varphi_{j^{+} - j^{-}}| [rad]')
histograms['hDiJetDeltaPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')

histograms['hDiJetInvMass'] = TH1F('hDiJetInvMass', 'hDiJetInvMass', 2000, 0, 1000)
histograms['hDiJetInvMass'].GetXaxis().SetTitle('M_{j^{+}j^{-}} [GeV/c^{2}]')
histograms['hDiJetInvMass'].GetYaxis().SetTitle('Candidates/0.5[GeV/c^{2}]')


#############################
# MET #######################
#############################
histograms['hMET'] = TH1F('hMET', 'hMET', 500, 0., 500.)
histograms['hMET'].GetXaxis().SetTitle('E_{T miss}[GeV/c]')
histograms['hMET'].GetYaxis().SetTitle('Candidates/2.0[GeV/c]')

histograms['hMETPhi'] = TH1F('hMETPhi', 'hMETPhi', 34, -3.4, 3.4)
histograms['hMETPhi'].GetXaxis().SetTitle('#varphi_{MET} [rad]')
histograms['hMETPhi'].GetYaxis().SetTitle('Candidates/0.2[rad]')



###### ___________________________________________________________
####def fill_base_histograms(analysis, eventweight, fillcontrol):
####    '''
####    Fills histograms which are included in every derived analysis.
####    '''
####    ##########################################################
####    #                                                        #
####    # Fill histograms                                        #
####    #                                                        #
####    ##########################################################
####
####    #############################
####    # PV after selection ########
####    #############################
####    # fill histograms with good pvs
####    analysis.histograms['hVtxN'].Fill(len(analysis.vertices), eventweight)
####
####    #############################
####    # Muons #####################
####    #############################
####    analysis.histograms['hNumMu'].Fill(len(analysis.good_muons), eventweight)
####    analysis.histograms['hLeadMuPt'].Fill(analysis.good_muons[0].pt(), eventweight)
####
####    if analysis.good_muons[0].pt() < 26.:
####    #if analysis.good_muons[0].pt('uncor') != analysis.good_muons[0].pt('cor'):
####        print '****************************\npt anomaly found :', analysis.event.number()
####        print 'pt muon[0] =', analysis.good_muons[0].pt(), ' pt muon[1] =', analysis.good_muons[1].pt()
####        print '****************************'
####
####
####    analysis.histograms['hSubLeadMuPt'].Fill(analysis.good_muons[1].pt(), eventweight)
####    if fillcontrol:
####        analysis.histograms_ctrl['hLeadMuPt_ctrl'].Fill(analysis.good_muons[0].pt(), eventweight)
####        analysis.histograms_ctrl['hSubLeadMuPt_ctrl'].Fill(analysis.good_muons[1].pt(), eventweight)
####
####    for mu in analysis.good_muons:
####        analysis.histograms['hMuPt'].Fill(mu.pt(), eventweight)
####        analysis.histograms['hMuEta'].Fill(mu.eta(), eventweight)
####        analysis.histograms['hMuPhi'].Fill(mu.phi(), eventweight)
####        # fill comtrol plots
####        if fillcontrol:
####            analysis.histograms_ctrl['hMuPt_ctrl'].Fill(mu.pt(), eventweight)
####            analysis.histograms_ctrl['hMuEta_ctrl'].Fill(mu.eta(), eventweight)
####            analysis.histograms_ctrl['hMuPhi_ctrl'].Fill(mu.phi(), eventweight)
####
####    #############################
####    # Dimuon ####################
####    #############################
####    for i, j in analysis.dimuon_pairs:
####        muon1 = analysis.good_muons[i]
####        muon2 = analysis.good_muons[j]
####        dimuobj = muon1.p4() + muon2.p4()
####
####        analysis.histograms['hDiMuPt'].Fill(dimuobj.Pt(), eventweight)
####        analysis.histograms['hDiMuEta'].Fill(dimuobj.Eta(), eventweight)
####        analysis.histograms['hDiMuPhi'].Fill(dimuobj.Phi(), eventweight)
####        analysis.histograms['hDiMuInvMass'].Fill(dimuobj.M(), eventweight)
####
####        analysis.histograms['hDiMuDeltaPt'].Fill(muon1.pt() - muon2.pt(), eventweight)
####        analysis.histograms['hDiMuDeltaEta'].Fill(muon1.eta() - muon2.eta(), eventweight)
####        analysis.histograms['hDiMuDeltaPhi'].Fill(muon1.phi() - muon2.phi(), eventweight)
####
####        # fill control plots
####        if fillcontrol:
####            analysis.histograms_ctrl['hDiMuPt_ctrl'].Fill(dimuobj.Pt(), eventweight)
####            analysis.histograms_ctrl['hDiMuEta_ctrl'].Fill(dimuobj.Eta(), eventweight)
####            analysis.histograms_ctrl['hDiMuPhi_ctrl'].Fill(dimuobj.Phi(), eventweight)
####            analysis.histograms_ctrl['hDiMuInvMass_ctrl'].Fill(dimuobj.M(), eventweight)
####
####            analysis.histograms_ctrl['hDiMuDeltaPt_ctrl'].Fill(muon1.pt() - muon2.pt(), eventweight)
####            analysis.histograms_ctrl['hDiMuDeltaEta_ctrl'].Fill(muon1.eta() - muon2.eta(), eventweight)
####            analysis.histograms_ctrl['hDiMuDeltaPhi_ctrl'].Fill(muon1.phi() - muon2.phi(), eventweight)
####
#####    #############################
#####    # Electrons #################
#####    #############################
#####    analysis.histograms['hNumE'].Fill(len(analysis.good_electrons), eventweight)
#####    for e in analysis.good_electrons:
#####        analysis.histograms['hEPt'].Fill(e.pt(), eventweight)
#####        analysis.histograms['hEEta'].Fill(e.eta(), eventweight)
#####        analysis.histograms['hEPhi'].Fill(e.phi(), eventweight)
#####    # leading electron
#####    if len(analysis.good_electrons) > 0:
#####        analysis.histograms['hLeadEPt'].Fill(analysis.good_electrons[0].pt(), eventweight)
#####    # subleading electron
#####    if len(analysis.good_electrons) > 1:
#####        analysis.histograms['hSubLeadEPt'].Fill(analysis.good_electrons[1].pt(), eventweight)
#####
#####    #############################
#####    # Dielectron ################
#####    #############################
#####    for i, j in analysis.dielectron_pairs:
#####        elec1 = analysis.good_electrons[i]
#####        elec2 = analysis.good_electrons[j]
#####        dielobj = elec1.p4() + elec2.p4()
#####
#####        analysis.histograms['hDiEPt'].Fill(dielobj.Pt(), eventweight)
#####        analysis.histograms['hDiEEta'].Fill(dielobj.Eta(), eventweight)
#####        analysis.histograms['hDiEPhi'].Fill(dielobj.Phi(), eventweight)
#####        analysis.histograms['hDiEInvMass'].Fill(dielobj.M(), eventweight)
#####
#####        analysis.histograms['hDiEDeltaPt'].Fill(elec1.pt() - elec2.pt(), eventweight)
#####        analysis.histograms['hDiEDeltaEta'].Fill(elec1.eta() - elec2.eta(), eventweight)
#####        analysis.histograms['hDiEDeltaPhi'].Fill(elec1.phi() - elec2.phi(), eventweight)
#####
#####        # fill control plots
#####        if fillcontrol:
#####            analysis.histograms_ctrl['hDiEPt_ctrl'].Fill(dielobj.Pt(), eventweight)
#####            analysis.histograms_ctrl['hDiEEta_ctrl'].Fill(dielobj.Eta(), eventweight)
#####            analysis.histograms_ctrl['hDiEPhi_ctrl'].Fill(dielobj.Phi(), eventweight)
#####            analysis.histograms_ctrl['hDiEInvMass_ctrl'].Fill(dielobj.M(), eventweight)
#####
#####            analysis.histograms_ctrl['hDiEDeltaPt_ctrl'].Fill(elec1.pt() - elec2.pt(), eventweight)
#####            analysis.histograms_ctrl['hDiEDeltaEta_ctrl'].Fill(elec1.eta() - elec2.eta(), eventweight)
#####            analysis.histograms_ctrl['hDiEDeltaPhi_ctrl'].Fill(elec1.phi() - elec2.phi(), eventweight)
####
####
####    #############################
####    # Jets ######################
####    #############################
####    analysis.histograms['hNumJets'].Fill(len(analysis.good_jets), eventweight)
####    analysis.histograms['hNumBJets'].Fill(len(analysis.good_bjets), eventweight)
####
####    for jet in analysis.good_jets:
####        analysis.histograms['hJetPt'].Fill(jet.pt(), eventweight)
####        analysis.histograms['hJetEta'].Fill(jet.eta(), eventweight)
####        analysis.histograms['hJetPhi'].Fill(jet.phi(), eventweight)
####    # leading jet
####    if len(analysis.good_jets) > 0:
####        analysis.histograms['hLeadJetPt'].Fill(analysis.good_jets[0].pt(), eventweight)
####    # subleading jet
####    if len(analysis.good_jets) > 1:
####        analysis.histograms['hSubLeadJetPt'].Fill(analysis.good_jets[1].pt(), eventweight)
####
####    #############################
####    # Dijet #####################
####    #############################
####    #for i, j in analysis.dijet_pairs:
####    if analysis.dijet_pairs:
####        jet0, jet1 = analysis.good_jets[0], analysis.good_jets[1]
####        diJetP4 = jet0.p4() + jet1.p4()
####        analysis.histograms['hDiJetPt'].Fill(diJetP4.Pt(), eventweight)
####        analysis.histograms['hDiJetEta'].Fill(diJetP4.Eta(), eventweight)
####        analysis.histograms['hDiJetPhi'].Fill(diJetP4.Phi(), eventweight)
####        analysis.histograms['hDiJetInvMass'].Fill(diJetP4.M(), eventweight)
####        analysis.histograms['hDiJetDeltaPt'].Fill(jet0.pt() -  jet1.pt(), eventweight)
####        analysis.histograms['hDiJetDeltaEta'].Fill(abs(jet0.eta() - jet1.eta()), eventweight)
####        analysis.histograms['hDiJetDeltaPhi'].Fill(abs(jet0.phi() - jet1.phi()), eventweight)
####
####
####    #############################
####    # MET #######################
####    #############################
####    analysis.histograms['hMET'].Fill(analysis.met.et(), eventweight)
####    analysis.histograms['hMETPhi'].Fill(analysis.met.phi(), eventweight)
####    # fill control plots
####    if fillcontrol:
####        analysis.histograms_ctrl['hMET_ctrl'].Fill(analysis.met.et(), eventweight)
####        analysis.histograms_ctrl['hMETPhi_ctrl'].Fill(analysis.met.phi(), eventweight)
####
####




## ___________________________________________________________
def fill_category_hists(analysis, eventweight, fillcontrol, thiscat, pairindex1, pairindex2):
   # pass
    '''
    Fills category histograms which are included in every derived analysis.
    '''

    #############################
    # PV after selection ########
    #############################
    # fill histograms with good pvs
    analysis.histograms_categories['hVtxN_cat00'].Fill(len(analysis.vertices), eventweight)

    this_cat = 'cat'+str(thiscat).zfill(2)
    this_kitten = '1' if (thiscat > 0 and thiscat < 4) else '2'

    mu1, mu2 = analysis.good_muons[pairindex1], analysis.good_muons[pairindex2]
    dimu = mu1.p4() + mu2.p4()
    jet1, jet2, dijet = None, None, None
    if len(analysis.good_jets) > 0:
        jet1 = analysis.good_jets[0]
    if len(analysis.good_jets) > 1:
        jet2 = analysis.good_jets[1]
        dijet = jet1.p4() + jet2.p4()

    ##########################################################
    #                                                        #
    # Fill histograms                                        #
    #                                                        #
    ##########################################################
    #############################
    # Muons #####################
    #############################
    analysis.histograms_categories['hNumMu_'+this_cat].Fill(len(analysis.good_muons), eventweight)
    analysis.histograms_categories['hNumMu_cat00'].Fill(len(analysis.good_muons), eventweight)
    analysis.histograms_categories['hLeadMuPt_'+this_cat].Fill(mu1.pt(), eventweight)
    analysis.histograms_categories['hLeadMuPt_cat00'].Fill(mu1.pt(), eventweight)
    analysis.histograms_categories['hSubLeadMuPt_'+this_cat].Fill(mu2.pt(), eventweight)
    analysis.histograms_categories['hSubLeadMuPt_cat00'].Fill(mu2.pt(), eventweight)
    if fillcontrol:
        analysis.histograms_categories_ctrl['hLeadMuPt_'+this_cat+'_ctrl'].Fill(mu1.pt(), eventweight)
        analysis.histograms_categories_ctrl['hLeadMuPt_cat00_ctrl'].Fill(mu1.pt(), eventweight)
        analysis.histograms_categories_ctrl['hSubLeadMuPt_'+this_cat+'_ctrl'].Fill(mu2.pt(), eventweight)
        analysis.histograms_categories_ctrl['hSubLeadMuPt_cat00_ctrl'].Fill(mu2.pt(), eventweight)

    for mu in analysis.good_muons:
        analysis.histograms_categories['hMuPt_'+this_cat].Fill(mu.pt(), eventweight)
        analysis.histograms_categories['hMuPt_cat00'].Fill(mu.pt(), eventweight)
        analysis.histograms_categories['hMuEta_'+this_cat].Fill(mu.eta(), eventweight)
        analysis.histograms_categories['hMuEta_cat00'].Fill(mu.eta(), eventweight)
        analysis.histograms_categories['hMuPhi_'+this_cat].Fill(mu.phi(), eventweight)
        analysis.histograms_categories['hMuPhi_cat00'].Fill(mu.phi(), eventweight)
        # fill comtrol plots
        if fillcontrol:
            analysis.histograms_categories_ctrl['hMuPt_'+this_cat+'_ctrl'].Fill(mu.pt(), eventweight)
            analysis.histograms_categories_ctrl['hMuPt_cat00_ctrl'].Fill(mu.pt(), eventweight)
            analysis.histograms_categories_ctrl['hMuEta_'+this_cat+'_ctrl'].Fill(mu.eta(), eventweight)
            analysis.histograms_categories_ctrl['hMuEta_cat00_ctrl'].Fill(mu.eta(), eventweight)
            analysis.histograms_categories_ctrl['hMuPhi_'+this_cat+'_ctrl'].Fill(mu.phi(), eventweight)
            analysis.histograms_categories_ctrl['hMuPhi_cat00_ctrl'].Fill(mu.phi(), eventweight)

    #############################
    # Dimuon ####################
    #############################
    analysis.histograms_categories['hNumDiMu_'+this_cat].Fill(len(analysis.dimuon_pairs), eventweight)
    analysis.histograms_categories['hNumDiMu_cat00'].Fill(len(analysis.dimuon_pairs), eventweight)
    for i, j in analysis.dimuon_pairs:
        muon1 = analysis.good_muons[i]
        muon2 = analysis.good_muons[j]
        dimuobj = muon1.p4() + muon2.p4()

        analysis.histograms_categories['hDiMuPt_'+this_cat].Fill(dimuobj.Pt(), eventweight)
        analysis.histograms_categories['hDiMuPt_cat00'].Fill(dimuobj.Pt(), eventweight)
        analysis.histograms_categories['hDiMuEta_'+this_cat].Fill(dimuobj.Eta(), eventweight)
        analysis.histograms_categories['hDiMuEta_cat00'].Fill(dimuobj.Eta(), eventweight)
        analysis.histograms_categories['hDiMuPhi_'+this_cat].Fill(dimuobj.Phi(), eventweight)
        analysis.histograms_categories['hDiMuPhi_cat00'].Fill(dimuobj.Phi(), eventweight)

        analysis.histograms_categories['hDiMuInvMass_'+this_cat].Fill(dimuobj.M(), eventweight)
        analysis.histograms_categories['hDiMuInvMass_cat00'].Fill(dimuobj.M(), eventweight)

        analysis.histograms_categories['hDiMuDeltaPt_'+this_cat].Fill(muon1.pt() - muon2.pt(), eventweight)
        analysis.histograms_categories['hDiMuDeltaPt_cat00'].Fill(muon1.pt() - muon2.pt(), eventweight)
        analysis.histograms_categories['hDiMuDeltaEta_'+this_cat].Fill(muon1.eta() - muon2.eta(), eventweight)
        analysis.histograms_categories['hDiMuDeltaEta_cat00'].Fill(muon1.eta() - muon2.eta(), eventweight)
        analysis.histograms_categories['hDiMuDeltaPhi_'+this_cat].Fill(muon1.phi() - muon2.phi(), eventweight)
        analysis.histograms_categories['hDiMuDeltaPhi_cat00'].Fill(muon1.phi() - muon2.phi(), eventweight)

        analysis.histograms_categories['hDiMuPt_k'+this_kitten].Fill(dimuobj.Pt(), eventweight)
        analysis.histograms_categories['hDiMuInvMass_k'+this_kitten].Fill(dimuobj.M(), eventweight)


        # fill control plots
        if fillcontrol:
            analysis.histograms_categories_ctrl['hDiMuPt_'+this_cat+'_ctrl'].Fill(dimuobj.Pt(), eventweight)
            analysis.histograms_categories_ctrl['hDiMuPt_cat00_ctrl'].Fill(dimuobj.Pt(), eventweight)
            analysis.histograms_categories_ctrl['hDiMuEta_'+this_cat+'_ctrl'].Fill(dimuobj.Eta(), eventweight)
            analysis.histograms_categories_ctrl['hDiMuEta_cat00_ctrl'].Fill(dimuobj.Eta(), eventweight)
            analysis.histograms_categories_ctrl['hDiMuPhi_'+this_cat+'_ctrl'].Fill(dimuobj.Phi(), eventweight)
            analysis.histograms_categories_ctrl['hDiMuPhi_cat00_ctrl'].Fill(dimuobj.Phi(), eventweight)

            analysis.histograms_categories_ctrl['hDiMuInvMass_'+this_cat+'_ctrl'].Fill(dimuobj.M(), eventweight)
            analysis.histograms_categories_ctrl['hDiMuInvMass_cat00_ctrl'].Fill(dimuobj.M(), eventweight)

            analysis.histograms_categories_ctrl['hDiMuDeltaPt_'+this_cat+'_ctrl'].Fill(muon1.pt() - muon2.pt(), eventweight)
            analysis.histograms_categories_ctrl['hDiMuDeltaPt_cat00_ctrl'].Fill(muon1.pt() - muon2.pt(), eventweight)
            analysis.histograms_categories_ctrl['hDiMuDeltaEta_'+this_cat+'_ctrl'].Fill(muon1.eta() - muon2.eta(), eventweight)
            analysis.histograms_categories_ctrl['hDiMuDeltaEta_cat00_ctrl'].Fill(muon1.eta() - muon2.eta(), eventweight)
            analysis.histograms_categories_ctrl['hDiMuDeltaPhi_'+this_cat+'_ctrl'].Fill(muon1.phi() - muon2.phi(), eventweight)
            analysis.histograms_categories_ctrl['hDiMuDeltaPhi_cat00_ctrl'].Fill(muon1.phi() - muon2.phi(), eventweight)



    #############################
    # Jets ######################
    #############################
    analysis.histograms_categories['hNumJets_'+this_cat].Fill(len(analysis.good_jets), eventweight)
    analysis.histograms_categories['hNumJets_cat00'].Fill(len(analysis.good_jets), eventweight)
    analysis.histograms_categories['hNumBJets_'+this_cat].Fill(len(analysis.good_bjets), eventweight)
    analysis.histograms_categories['hNumBJets_cat00'].Fill(len(analysis.good_bjets), eventweight)

    for jet in analysis.good_jets:
        analysis.histograms_categories['hJetPt_'+this_cat].Fill(jet.pt(analysis.jet_shift), eventweight)
        analysis.histograms_categories['hJetPt_cat00'].Fill(jet.pt(analysis.jet_shift), eventweight)
        analysis.histograms_categories['hJetEta_'+this_cat].Fill(jet.eta(), eventweight)
        analysis.histograms_categories['hJetEta_cat00'].Fill(jet.eta(), eventweight)
        analysis.histograms_categories['hJetPhi_'+this_cat].Fill(jet.phi(), eventweight)
        analysis.histograms_categories['hJetPhi_cat00'].Fill(jet.phi(), eventweight)
    # leading jet
    if jet1:
        analysis.histograms_categories['hLeadJetPt_'+this_cat].Fill(jet1.pt(analysis.jet_shift), eventweight)
        analysis.histograms_categories['hLeadJetPt_cat00'].Fill(jet1.pt(analysis.jet_shift), eventweight)
    # subleading jet
    if jet2:
        analysis.histograms_categories['hSubLeadJetPt_'+this_cat].Fill(jet2.pt(analysis.jet_shift), eventweight)
        analysis.histograms_categories['hSubLeadJetPt_cat00'].Fill(jet2.pt(analysis.jet_shift), eventweight)

    #############################
    # Dijet #####################
    #############################
    #for i, j in analysis.dijet_pairs:
    if dijet:
        analysis.histograms_categories['hDiJetPt_'+this_cat].Fill(dijet.Pt(), eventweight)
        analysis.histograms_categories['hDiJetPt_cat00'].Fill(dijet.Pt(), eventweight)
        analysis.histograms_categories['hDiJetEta_'+this_cat].Fill(dijet.Eta(), eventweight)
        analysis.histograms_categories['hDiJetEta_cat00'].Fill(dijet.Eta(), eventweight)
        analysis.histograms_categories['hDiJetPhi_'+this_cat].Fill(dijet.Phi(), eventweight)
        analysis.histograms_categories['hDiJetPhi_cat00'].Fill(dijet.Phi(), eventweight)

        analysis.histograms_categories['hDiJetInvMass_'+this_cat].Fill(dijet.M(), eventweight)
        analysis.histograms_categories['hDiJetInvMass_cat00'].Fill(dijet.M(), eventweight)
        analysis.histograms_categories['hDiJetDeltaPt_'+this_cat].Fill(jet1.pt(analysis.jet_shift) -  jet2.pt(analysis.jet_shift), eventweight)
        analysis.histograms_categories['hDiJetDeltaPt_cat00'].Fill(jet1.pt(analysis.jet_shift) -  jet2.pt(analysis.jet_shift), eventweight)
        analysis.histograms_categories['hDiJetDeltaEta_'+this_cat].Fill(abs(jet1.eta() - jet2.eta()), eventweight)
        analysis.histograms_categories['hDiJetDeltaEta_cat00'].Fill(abs(jet1.eta() - jet2.eta()), eventweight)
        analysis.histograms_categories['hDiJetDeltaPhi_'+this_cat].Fill(abs(jet1.phi() - jet2.phi()), eventweight)
        analysis.histograms_categories['hDiJetDeltaPhi_cat00'].Fill(abs(jet1.phi() - jet2.phi()), eventweight)

        analysis.histograms_categories['hDiJetInvMass_k'+this_kitten].Fill(dijet.M(), eventweight)
        analysis.histograms_categories['hDiJetDeltaEta_k'+this_kitten].Fill(abs(jet1.eta() - jet2.eta()), eventweight)

    #############################
    # MET #######################
    #############################
    analysis.histograms_categories['hMET_'+this_cat].Fill(analysis.met.et(), eventweight)
    analysis.histograms_categories['hMET_cat00'].Fill(analysis.met.et(), eventweight)
    analysis.histograms_categories['hMETPhi_'+this_cat].Fill(analysis.met.phi(), eventweight)
    analysis.histograms_categories['hMETPhi_cat00'].Fill(analysis.met.phi(), eventweight)
    # fill control plots
    if fillcontrol:
        analysis.histograms_categories_ctrl['hMET_'+this_cat+'_ctrl'].Fill(analysis.met.et(), eventweight)
        analysis.histograms_categories_ctrl['hMET_cat00_ctrl'].Fill(analysis.met.et(), eventweight)
        analysis.histograms_categories_ctrl['hMETPhi_'+this_cat+'_ctrl'].Fill(analysis.met.phi(), eventweight)
        analysis.histograms_categories_ctrl['hMETPhi_cat00_ctrl'].Fill(analysis.met.phi(), eventweight)



