import os
import sys
import glob

import ROOT

# constants
## ___________________________________________________________
Z_MASS = 91.1876 # GeV
INF = float('Inf') # infinity




# misc functions

## ___________________________________________________________
def delta_phi(c0, c1):
    result = c0.phi() - c1.phi()
    while result>ROOT.TMath.Pi():
        result -= 2*ROOT.TMath.Pi()
    while result <= -ROOT.TMath.Pi():
        result += 2*ROOT.TMath.Pi()
    return result

## ___________________________________________________________
def delta_r(c0, c1):
    deta = c0.eta() - c1.eta()
    dphi = delta_phi(c0, c1)
    return ROOT.TMath.Sqrt(deta**2+dphi**2)



# eventlist must be a textfile with events listed as follows:
# run:lumi:event number
# eg. 1:239472:60085100
## ___________________________________________________________
def event_is_on_list(run, lumi, event, evtlist):
    with open(evtlist,'r') as f:
        for line in f.readlines():
            info = line.strip().split(':')
            if (run == long(float(info[0])) and lumi == long(float(info[1])) and event == long(float(info[2]))):
                return True

    return False



