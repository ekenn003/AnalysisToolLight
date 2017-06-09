import os, sys
import time
from shutil import move
from tempfile import TemporaryFile



#printonly = True
printonly = False


version = '80X'
t2 = 'T2_CH_CERN'
#t2 = 'T2_US_UCSD'

era = 'final'


ds = [
    'SingleMuon_Run2016Bv2',
    'SingleMuon_Run2016C',
    'SingleMuon_Run2016D',
    'SingleMuon_Run2016E',
    'SingleMuon_Run2016F',
    'SingleMuon_Run2016G',
    'SingleMuon_Run2016Hv2',
    'SingleMuon_Run2016Hv3',
]

ms = [

    'GluGlu_HToMuMu',
    'VBF_HToMuMu',
    'WMinusH_HToMuMu',
    'WPlusH_HToMuMu',
    'ZH_HToMuMu',

    'DYJetsToLL',
    'TTJets',
    'WJetsToLNu',
    'WWTo2L2Nu',
    'WWW',
    'WWZ',
    'WZTo2L2Q',
    'WZTo3LNu',
    'WZZ',
    'ZZTo2L2Nu',
    'ZZTo2L2Q',
    'ZZTo4L',
    'ZZZ',

    'ST_tW_antitop_5f',
    'ST_tW_top_5f',
    'TTWJetsToLNu',
    'TTZToLLNuNu',
    'TZQ_ll_4f',

]


# common
datadir = '{0}/src/AnalysisToolLight/AnalysisTool/data/{1}'.format(os.environ['CMSSW_BASE'], version)
partialpath = 'store/user/ekennedy/{0}/smh2mu/{1}/{2}'.format(t2, version, era)




# __________________________________________________________
def main():
    commandlist = []

    if not printonly:
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
            fullpath = 'cms/{0}/{2}/{1}'.format(partialpath, dset, 'data' if (dset in ds) else 'mc')
            #command = 'eos ls /eos/{0}/*.root >> {1}/inputfiles_{2}.txt'.format(fullpath, datadir, dset)
            command = 'eos ls /eos/{0}/ >> {1}/inputfiles_{2}.txt'.format(fullpath, datadir, dset)
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
            command = 'ssh ekennedy@uaf-4.t2.ucsd.edu "cd /hadoop/{0}; ls ./*.root" >> {1}/inputfiles_{2}.txt'.format(fullpath, datadir, dset)
            commandlist += [command]
        
    else:
        raise ValueError('"{0}" is not a choice of T2 storage site'.format(t2))
    
    # execute commands
    for c in commandlist:
        print
        print c
        if not printonly:
            os.system(c)


    if not printonly:
        # prepend with correct path
        print '\nCreating the following files:'
        for dset in ds+ms:
            f = '{0}/inputfiles_{1}.txt'.format(datadir, dset)
            f_ = TemporaryFile()
            with open(f) as fin:
                with open(f_.name, 'w') as fout:
                    for line in fin:
                        fout.write('{0}/{1}/{2}/{3}/{4}'.format(t2, partialpath, 'data' if (dset in ds) else 'mc', dset, line))
            move(f_.name, f)
            print '    ' + f




        emptyfiles = []
        for dset in ds+ms:
            f = '{0}/inputfiles_{1}.txt'.format(datadir, dset)
            if os.path.getsize(f)==0:
                emptyfiles += [f]
        if emptyfiles:
            print '\nWARNING: The following files are empty:'
            for f in emptyfiles:
                print '    {0}'.format(f.split('/')[-1])
            print
        else:
            print '\nHooray! No empty lists.'


# __________________________________________________________
try:
    main()
except KeyboardInterrupt:
    print

