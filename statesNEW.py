#!/usr/bin/eval python2
#
#from __future__ import with_statement    # This isn't required in Python 2.6
#from __future__ import print_function    # This is only possible for >= 2.6
import numpy as np

sym_type = dict(u=1, g=2, unkonwn=0)

class Parameter(object):
    """MCTDHB parameter class."""
    # maybe better to pass and (store?) neighbors as tuples, ie neighbors=(None, state)
    def __init__(self, value, left=None, right=None):
        if isinstance(value, int) or isinstance(value, float):
            self.value = value
        else:
            raise TypeError
        self.add_left(left)
        self.add_right(right)
    
    def add_left(self, state):
        if isinstance(state, State) or (state is None):
            self.left = state
        else:
            raise TypeError
    
    def add_right(self, state):
        if isinstance(state, State) or (state is None):
            self.right = state
        else:
            raise TypeError

class State(object):
    """MCTDHB general state class."""
    def __init__(self, npar, xlambda, morb, occ, energy, sym=None):
        self.pars = dict()
        self.set_par('N', npar)
        self.set_par('L', xlambda)
        self.set_par('M', morb)
        self.set_occ(occ)
        self.set_par('E', energy)
        self.set_sym(sym)
    
    def set_par(self, name, value, left=None, right=None):
        if isinstance(name, str):
            self.pars[name] = Parameter(value, left, right)
        else:
            raise TypeError
    
    def set_occ(self, occ_numbers):
        if (len(occ_numbers) == self.pars['M'].value):
            self.occ = occ_numbers
        else:
            raise IndexError

    def set_sym(self, sym):
        pass
    

class GS(State):
    """MCTDHB groundstate (GS) class."""
    def __init__(self):
        State.__init__(self, )
    
    def __str__(self):
        pass

class ES(State):
    """MCTDHB excited state (ES) class."""
    def __init__(self, Morb, line):
        self.M = int(Morb)
        self.par = line[0]
        self.i = int(line[1]) - 10 - 2*self.M
        self.E_i = line[2]      #energy difference
        self.E = line[3]
        self.normPHI = line[4]      #real part
        self.normCI = line[5]
        self.uAmp = np.absolute(np.complex(line[6], line[7]))   #response amplitudes Orb and CI part
        self.gAmp = np.absolute(np.complex(line[8], line[9]))   #abs = Re^2 + Im^2
        self.set_sym()
    
    def set_sym(self):
        if (self.uAmp < self.gAmp):
            self.sym = 2            # gerade symmetry
        else:
            self.sym = 1            # ungerade symmetry 

class Spectrum(object):
        pass

def read_GS(filename, Morb):
    states = []
    pos = 0
    with open(filename, 'r') as f:
        for line in f:
            pos += 1
            if line[0] in '\n#':        # skip comments and empty lines
                pos = 0
                continue
            line = np.array(line.split())
            line = line.astype(np.float)
            if (pos == 2):
                states.append(GS(Morb, line))
    return np.array(states)

def read_ES(filename, Morb):
    states = []
    with open(filename, 'r') as f:
        states2 = []        #states with equal particle interaction
        for line in f:
            if line[0] == '#':        #skip first line
                continue
            if line[0] == '\n':
                states.append(states2)
                states2 = []
                continue
            line = np.array(line.split())
            line = line.astype(np.float)
            states2.append(ES(Morb, line))
    return np.array(states)

def sort_states(data):          #depreciated
    copy = np.copy(data)
    mask = np.zeros(data.shape)
    for i in range(data.shape[0] - 1):        #last xlambda has no neighbour
        for j in range(data.shape[1]):
            for k in range(data.shape[1]):
                if (mask[i+1][k] == 0) and (data[i][j].sym == data[i+1][k].sym):
                    copy[i+1][j] = data[i+1][k]
                    mask[i+1][k] = 1
                    break
    return copy

def link_states(data):
    for i in range(data.shape[0]):      #link xlambda states
        for j in range(data.shape[1]-1):
            data[i][j].above = data[i][j+1]
            data[i][j+1].below = data[i][j]
    for i in range(data.shape[0]-1):    #link avoid crossing states
        for j in range(data.shape[1]):
            for k in range(data.shape[1]):
                if (data[i+1][k].left == None) and (data[i][j].sym == data[i+1][k].sym):
                    data[i][j].right = data[i+1][k]
                    data[i+1][k].left = data[i][j]
                    break

def qprint(data):       #print sym to console
    for xlambda in data:
        for state in xlambda:
            print state.sym,
        print
    
def qprint2(data):      #print linked sym to console
    for state in data[0]:
        while (state != None):
            print state.sym,
            state = state.right
        print

def to_file(filename, data):
    with open(filename, 'w') as out:
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                state = data[0][j]
                for k in range(i):
                    if (state.right != None):
                        state = state.right
                if (state == None):
                    continue
                if (j == 0):
                    out.write("{0:e} ".format(state.par))
                out.write("{0:e} {1:d} ".format(state.E_i, state.sym))
                if (j == data.shape[1]-1):
                    out.write("\n")

def plot_range(data, sweep_parameter):
    from subprocess import call
    call('gnuplot -e "Nstat={0:d}; Par=\'{3:s}\'; Min={1:f}; Max={2:f}; Log=0; Phi=5" \
        plot_range2.plt'.format(data.shape[1], data[0][0].par, data[-1][0].par, sweep_parameter), shell=True)
    
    
if __name__ == "__main__":
    datafile1 = "GS_raw.dat"
    datafile2 = "ES_raw.dat"
    outfile = "ES.dat"
    sweep = 'b'
    
    out1 = read_GS(datafile1, 2)
    out2 = read_ES(datafile2, 2)
    print len(out1), len(out2)
    qprint(out2)
    print
    link_states(out2)
    qprint2(out2)
    to_file(outfile, out2)
    plot_range(out2, sweep)
