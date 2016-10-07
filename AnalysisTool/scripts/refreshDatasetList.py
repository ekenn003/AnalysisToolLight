import os, sys
import time

t2 = 'T2_CH_CERN'
#t2 = 'T2_US_UCSD'

era = 'oct16'

version = '80X'


ds = ['SingleMuon2016D', 'SingleMuon2016E']
ms = ['DYJetsToLL', 'TTJets']




# common
commandlist = []
datadir = '{0}/src/AnalysisToolLight/AnalysisTool/data/{1}'.format(os.environ['CMSSW_BASE'], version)
partialpath = 'cms/store/user/ekennedy/smh2mu/{0}/{1}'.format(version, era)


# delete them if they exist
for dset in ds:
    outfile = '{0}/inputfiles_{1}.txt'.format(datadir, dset)
    try:
        #os.remove(outfile)
        print 'os.remove({0})'.format(outfile)
    except OSError:
        pass
for dset in ms:
    outfile = '{0}/inputfiles_{1}.txt'.format(datadir, dset)
    try:
        #os.remove(outfile)
        print 'os.remove({0})'.format(outfile)
    except OSError:
        pass


# set up commands to get new lists
if (t2 == 'T2_CH_CERN'): 

    for dset in ds:
        fullpath = '{0}/data/{1}/*.*'.format(partialpath, dset)
        command = 'eos ls /eos/{0} >> {1}/inputfiles_{2}.txt'.format(fullpath, datadir, dset)
        commandlist += [command]
    for dset in ms:
        fullpath = '{0}/mc/{1}/*.*'.format(partialpath, dset)
        command = 'eos ls /eos/{0} >> {1}/inputfiles_{2}.txt'.format(fullpath, datadir, dset)
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
        command = 'ssh ekennedy@uaf-4.t2.ucsd.edu "cd /hadoop/{0}; ls" >> {1}/inputfiles_{2}.txt'.format(fullpath, datadir, dset)
        commandlist += [command]
    for dset in ms:
        fullpath = '{0}/mc/{1}/'.format(partialpath, dset)
        command = 'ssh ekennedy@uaf-4.t2.ucsd.edu "cd /hadoop/{0}; ls *.*" >> {1}/inputfiles_{2}.txt'.format(fullpath, datadir, dset)
        commandlist += [command]
    
else:
    raise ValueError('"{0}" is not a choice of T2 storage site'.format(t2))

# execute commands
for c in commandlist:
    print c
    time.sleep(3)

