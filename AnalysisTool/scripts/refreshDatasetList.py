import os, sys
import time
from shutil import move
from tempfile import TemporaryFile

#t2 = 'T2_CH_CERN'
t2 = 'T2_US_UCSD'

era = 'oct16'

version = '76X'
#version = '80X'

ds = [
    'SingleMuon_Run2015C',
    'SingleMuon_Run2015D'
]

ms = [
    'DYJetsToLL',
    'GluGlu_HToMuMu_M125',
    'TTJets',
    'TTZToLLNuNu',
    'VBF_HToMuMu_M125',
    'WWTo2L2Nu',
    'WZTo2L2Q',
    'WZTo3LNu',
    'ZZTo2L2Nu',
    'ZZTo2L2Q',
    'ZZTo4L',
]



# common
datadir = '{0}/src/AnalysisToolLight/AnalysisTool/data/{1}'.format(os.environ['CMSSW_BASE'], version)
partialpath = 'store/user/ekennedy/{0}/smh2mu/{1}/{2}'.format(t2, version, era)



# __________________________________________________________
def main():
    commandlist = []

    # delete them if they exist
    for dset in ds+ms:
        outfile = '{0}/inputfiles_{1}.txt'.format(datadir, dset)
        try:
            os.remove(outfile)
        except OSError:
            print 'could not remove ' + outfile
            pass
    
    
    # set up commands to get new lists
    if (t2 == 'T2_CH_CERN'): 
    
        for dset in ds+ms:
            fullpath = 'cms/{0}/{2}/{1}/*.*'.format(partialpath, dset, 'data' if (dset in ds) else 'mc')
            command = 'eos ls /eos/{0} >> {1}/inputfiles_{2}.txt'.format(fullpath, datadir, dset)
            commandlist += [command]
    
    elif (t2 == 'T2_US_UCSD'):
        #basecommand = 'gfal-ls srm://bsrm-3.t2.ucsd.edu:8443/srm/v2/server?SFN=/hadoop/{0}/'.format(path)
        print 'Make sure you have done the commands:'
        print '    exec ssh-agent bash'
        print '    ssh-add'
        print '    cmsenv'
        print
    
        for dset in ds+ms:
            fullpath = 'cms/{0}/{1}/{2}/'.format(partialpath, 'data' if (dset in ds) else 'mc', dset)
            command = 'ssh ekennedy@uaf-4.t2.ucsd.edu "cd /hadoop/{0}; ls" >> {1}/inputfiles_{2}.txt'.format(fullpath, datadir, dset)
            commandlist += [command]
        
    else:
        raise ValueError('"{0}" is not a choice of T2 storage site'.format(t2))
    
    # execute commands
    for c in commandlist:
        print
        print c
        os.system(c)

    # prepend with correct path
    print '\nCreated the following files:'
    for dset in ds+ms:
        f = '{0}/inputfiles_{1}.txt'.format(datadir, dset)
        f_ = TemporaryFile()
        with open(f) as fin:
            with open(f_.name, 'w') as fout:
                for line in fin:
                    #fout.write(''.join([t2, '/', partialpath, '/', dset, '/', line]))
                    fout.write('{0}/{1}/{2}/{3}/{4}'.format(t2, partialpath, 'data' if (dset in ds) else 'mc', dset, line))
        move(f_.name, f)
        print '    ' + f





# __________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print

