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
class Candidate(object):
    '''
    Basic objects
    '''
    def __init__(self, tree, candName, entry):
        self.tree = tree
        self.candName = candName
        self.entry = entry
    def _get(self, var): return getattr(self.tree, '{0}_{1}'.format(self.candName, var))[self.entry]

    def Pt(self):     return self._get("pt")
    def Eta(self):    return self._get("eta")
    def Phi(self):    return self._get("phi")
    def Energy(self): return self._get("energy")
    def Charge(self): return self._get("charge")
    def PDGID(self):  return self._get("pdgid")

    def P4(self): return ROOT.TLorentzVector(self.Pt(), self.Eta(), self.Phi(), self.Energy())

    def deltaR(self,cand): return deltaR(self, cand)

class Muon(Candidate):
    def __init__(self,tree,entry):
       super(Muon, self).__init__(tree,'muon',entry)

class Electron(Candidate):
    def __init__(self,tree,entry):
       super(Electron, self).__init__(tree,'electron',entry)



