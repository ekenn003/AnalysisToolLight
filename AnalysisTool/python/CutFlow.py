
## ___________________________________________________________
class CutFlow(object):
    '''
    The CutFlow object keeps track of the cutflow and helps fill
    the efficiencies histogram at the end of the job.
    '''
    def __init__(self):
        self.counters = OrderedDict()
        self.pretty = {}
    def getPretty(self, name):
        return self.pretty.get(name, name)
    def add(self, var, label):
        self.counters[var] = 0
        self.pretty[var] = label
    def increment(self, arg): # increases counter "arg" by 1
        self.counters[arg] += 1.
    def numBins(self): # returns number of counters
        return len(self.counters)
    def count(self, name): # returns the current value of the counter "name"
        return self.counters[name]
    def getNames(self): # returns ordered dict of counters
        return self.counters.keys()
    def getSkimEff(self, index):
        if index == 0: return '---'
        num = self.count(self.getNames()[index])
        den = self.count(self.getNames()[0])
        if den!=0: return format((100.*num)/den, '0.2f')
        return '-'
    def getRelEff(self, index):
        if index == 0: return '---'
        num = self.count(self.getNames()[index])
        den = self.count(self.getNames()[index-1])
        if den!=0: return format((100.*num)/den, '0.2f')
        return '-'

