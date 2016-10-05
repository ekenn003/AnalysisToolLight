import os, sys
import time

#t2 = 'T2_CH_CERN'
t2 = 'T2_US_UCSD'

era = 'oct16'

version = '80X'


ds = ['SingleMuon2016D', 'SingleMuon2016E']
ms = ['DYJetsToLL', 'TTJets']







commandlist = []
partialpath = 'cms/store/user/ekennedy/smh2mu/{0}/{1}'.format(version, era)


if (t2 == 'T2_CH_CERN'): 

    for dset in ds:
        fullpath = '{0}/data/{1}/*.*'.format(partialpath, dset)
        command = 'eos ls /eos/{0}'.format(fullpath)
        commandlist += [command]
    
    for dset in ms:
        fullpath = '{0}/mc/{1}/*.*'.format(partialpath, dset)
        command = 'eos ls /eos/{0}'.format(fullpath)
        commandlist += [command]

elif (t2 == 'T2_US_UCSD'):
    #basecommand = 'gfal-ls srm://bsrm-3.t2.ucsd.edu:8443/srm/v2/server?SFN=/hadoop/{0}/'.format(path)
    print 'Make sure you have done the commands:'
    print '    exec ssh-agent bash'
    print '    ssh-add'
    print '    cmsenv'
    print

    for dset in ds:
        fullpath = '{0}/data/{1}/'.format(partialpath, dset)
        command = 'ssh ekennedy@uaf-4.t2.ucsd.edu "cd /hadoop/{0}; ls"'.format(fullpath)
        commandlist += [command]
    
    for dset in ms:
        fullpath = '{0}/mc/{1}/'.format(partialpath, dset)
        command = 'ssh ekennedy@uaf-4.t2.ucsd.edu "cd /hadoop/{0}; ls *.*"'.format(fullpath)
        commandlist += [command]
    
else:
    raise ValueError('"{0}" is not a choice of T2 storage site'.format(t2))


for c in commandlist:
    print c

