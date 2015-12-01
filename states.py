#python2
#marcustheisen@web.de

import io_routines as io

NormType = dict(phi=0, ci=1)
SymType = dict(m=0, mixed=0,
               u=1, ungerade=1,
               g=2, gerade=2,
               unknown=None)

#MaxError for LR normalization
ERR_NORM = 1e-10
#Minimal responce amplitude
MIN_RESPONSE = 1e-8
#Percentaged difference to distinguish between u and g states
MIN_DIFF = 0.5

class Node(object):
    """MCTDHB parameter class. Providing two links for sweeps."""
    # maybe better to pass and (store?) neighbors as tuples
    # i.e. neighbors=(None, state)
    def __init__(self, value, left=None, right=None):
        self.set_value(value)
        self.set_left(left)
        self.set_right(right)
    
    def set_value(self, value):
        if isinstance(value, (int, float)):
            self._value = value
        else:
            raise TypeError
    
    def set_left(self, state):
        if isinstance(state, State) or (state is None):
            self._left = state
        else:
            raise TypeError
    
    def set_right(self, state):
        if isinstance(state, State) or (state is None):
            self._right = state
        else:
            raise TypeError
    
    def get_value(self):
        return self._value
    
    def get_left(self):
        return self._left
    
    def get_right(self):
        return self._right
    
class State(object):
    """Mask for states in general."""
    # Attributing energy and symmetry to a physical state.
    def __init__(self, energy, symmetry):
        self.set_E(energy)
        self.set_sym(symmetry)
    
    def set_sym(self, sym):
        if (sym in SymType):
            self._sym = SymType[sym]
        elif (sym in SymType.values()):
            self._sym = sym
        else:
            raise ValueError
    
    def set_E(self, erg):
        if isinstance(erg, float):
            self._E = erg
        else:
            raise TypeError
    
    def get_sym(self):
        return self._sym
    
    def get_energy(self):
        return self._E
    
class MCTDHBState(State):
    """Base class for states computed by MCTDHB."""
    def __init__(self, npar, morb, occupation, xlambda, energy, sym=None):
        State.__init__(self, energy, sym)
        # Set up nodes for MCTDHB (sweep) parameter.
        self.pars = dict()
        self.add_par('N', npar)
        self.add_par('M', morb)
        self.add_par('L', xlambda)
        # Set up occupation numbers.
        self.set_occ(occupation)
        
        # TODO: include potentials and time-dependency
    
    def set_occ(self, occ_numbers):
        if (len(occ_numbers) == self.get_pvalue('M')):
            if all([isinstance(i, float) for i in occ_numbers]):
                self._occ = occ_numbers
            else:
                raise TypeError
        else:
            raise Exception(
                'Number of occupation numbers {} '.format(len(ooc_numbers))
                + 'does not match '
                + 'number of orbitals {}.'.format(self.get_pvalue('M')))
    
    def add_par(self, pname, value, left=None, right=None):
        if (pname in self.pars):
            raise KeyError(pname + ' already exists as a ParNode!')
        if isinstance(pname, str):
            self.pars[pname] = ParNode(value, left, right)
        else:
            raise TypeError
    
    def set_pvalue(self, pname, value):
        if (pname in self.pars):
            self.pars[pname].set_value(value)
        else:
            raise ValueError
    
    def set_pleft(self, pname, state):
        if (pname in self.pars):
            self.pars[pname].set_left(state)
        else:
            raise ValueError
    
    def set_pright(self, pname, state):
        if (pname in self.pars):
            self.pars[pname].set_right(state)
        else:
            raise ValueError
    
    def get_pvalue(self, pname):
        return self.pars[pname].get_value()
    
    def get_pleft(self, pname):
        return self.pars[pname].get_left()
    
    def get_pright(self, pname):
        return self.pars[pname].get_right()
    
    @classmethod
    def from_files(cls, time_slice):
        """Read MCTDHB state from OutFiles."""
        pass
        for fname in ['NO_PR.out', 'OP_PR.out']:
    
    @classmethod
    def from_mctdhb(cls, mctdhb_obj, sym=None):
        if isinstance(mctdhb_obj, MCTDHB):
            return cls(mctdhb_obj.get_par('NPAR'),
                       mctdhb_obj.get_par('XLAMBDA_0'),
                       mctdhb_obj.get_par('MORB'),
                       mctdhb_obj.get_par(
                       sym)
        else:
            raise TypeError
 
class GS(MCTDHBState):
    """GroundState as computed by MCTDHB."""
    def __init__(self, mctdhb_obj):
        MCTDHBState.__init__(self, mctdhb_obj, SymType['g'])

        #operator values per particle
        self.op = mctdhb_obj.data['OP_PR.out'][-1]
        #energies constituents
        self.T = self.op[2]
        self.V = self.op[3]
        self.W = self.op[4]
        print self.E/self.N, self.op[1]
        assert abs(self.E/self.N - self.op[1]) < 1e-6
        assert abs(self.E/self.N - (self.T + self.V + self.W)) < 1e-6
        #x-space -- 3D
        self.x = self.op[5:8]
        self.xx = self.op[8:11]
        self.var_x = self.op[11:14]
        #k-space -- 3D
        self.k = self.op[14:17]
        self.kk = self.op[17:20]
        self.var_k = self.op[20:23]

class ES(MCTDHBState):
    """ExcitedState as computed by LR-MCTDHB."""
    def __init__(self, pars, GS_obj):
        self.GS = GS_obj            #link to corresponding GS object
        self.i = int(pars[0]) - 10 - 2*GS_obj.M
        self.E_i = pars[1]
        self.E = pars[2]
        #print abs(self.E - (self.GS.E*self.GS.N + self.E_i))
        assert abs(self.E - (self.GS.E + self.E_i)) < 1e-6
        self.norm_phi = pars[3]         #negative roots have negative norm
        self.norm_ci = pars[4]
        self.amp_u = pars[5]          #sum orbital(PHI) and coeff(CI) parts
        self.amp_g = pars[6]
        self.set_sym()
    
    def set_sym(self):
        """Try to derive symmetry of ES."""
        #check normalization
        if (self.GS.M == 1):
            assert abs(abs(self.norm_phi) - 1) < ERR_NORM
            assert abs(self.norm_ci) < ERR_NORM
        else:
            assert abs(abs(self.norm_phi+self.norm_ci) - 1) < ERR_NORM
        
        if (self.norm_ci < self.norm_phi):
            self.norm = NormType['phi']
            self.norm = 'phi'
        else:
            self.norm = NormType['ci']
            self.norm = 'ci'
        
        #check response amplitudes
        if (self.amp_g < MIN_RESPONSE) and (self.amp_u < MIN_RESPONSE):
            self.sym = SymType['unknown']
        elif (abs(self.amp_u-self.amp_g) < MIN_RESPONSE):
            self.sym = SymType['unknown']
        elif (self.amp_u/self.amp_g < MIN_DIFF):
            self.sym = SymType['gerade']
        elif (self.amp_g/self.amp_u < MIN_DIFF):
            self.sym = SymType['ungerade']
        else:
            self.sym = SymType['mixed']
    
    def __repr__(self):
        return State.__repr__(self) + ', norm: ' + repr(self.norm)

def mk_spec(mctdhb_obj):
    """Make excitation spectrum for given GS."""
    data = mctdhb_obj.data['MC_anlsplot.out']
    state = mctdhb_obj.state
    for dstate in data:
        new_state = ES(dstate, mctdhb_obj.state)
        if (new_state.i > 0):
            state.set_neighbor('E', right=new_state)
            new_state.set_neighbor('E', left=state)
            assert (state is not new_state)
            state = new_state
            assert (state is new_state)

def print_spec(GS_obj, Nstates=20):
    state = GS_obj
    count = 0
    while (state.neighbors['E'].right != None):
        print repr(state)
        state = state.neighbors['E'].right
        if (count < Nstates):
            count += 1
        else:
            break

#unused
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
