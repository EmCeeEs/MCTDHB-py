#python3.5
#marcustheisen@web.de

import src.io_routines as io
from src.mctdhb import MCTDHB

NormType = dict(phi=0, ci=1)
SymType = dict(m=0, mixed=0,
               u=1, ungerade=1,
               g=2, gerade=2,
               unknown=None)

# MaxError for LR normalization.
ERR_NORM = 1e-10
# Minimal response amplitude.
MIN_RESPONSE = 1e-8
# Percentaged difference to distinguish between u and g states.
MIN_DIFF = 0.5

class Node(object):
    """Parameter node providing a value and two links."""
    # May be better to pass and (store?) neighbors as tuples...
    # i.e. neighbors=(None, right_state)
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
            self.sym = SymType[sym]
        elif (sym in SymType.values()):
            self.sym = sym
        else:
            raise ValueError
    
    def set_E(self, erg):
        if isinstance(erg, float):
            self.E = erg
        else:
            raise TypeError
    
    def __repr__(self):
        return 'energy: ' + repr(self.E) + ' sym: ' + repr(self.sym)
 
class MCTDHBState(State):
    """Base class for states computed by MCTDHB."""
    def __init__(self, npar, morb, xlambda, energy, sym=None):
        State.__init__(self, energy, sym)
        # Set up nodes for MCTDHB (sweep) parameter.
        self.pars = dict()
        self.add_par('N', npar)
        self.add_par('M', morb)
        self.add_par('L', xlambda)
        
        # TODO: include potentials and time-dependency
    
    def add_par(self, pname, value, left=None, right=None):
        if (pname in self.pars):
            raise Exception(pname + ' already exists!')
        self.pars[pname] = Node(value, left, right)
    
    def set_pvalue(self, pname, value):
        self.pars[pname].set_value(value)
    
    def set_pleft(self, pname, state):
        self.pars[pname].set_left(state)
    
    def set_pright(self, pname, state):
        self.pars[pname].set_right(state)
    
    def get_pvalue(self, pname):
        return self.pars[pname].get_value()
    
    def get_pleft(self, pname):
        return self.pars[pname].get_left()
    
    def get_pright(self, pname):
        return self.pars[pname].get_right()

class GS(MCTDHBState):
    """GroundState as computed by MCTDHB."""
    def __init__(self, obj, data):
        if not isinstance(obj, MCTDHB):
            raise TypeError
        
        self.op, self.no = data
        MCTDHBState.__init__(self, obj.get_N(), obj.get_M(), obj.get_L(),
                             self.no[obj.get_M()+1], sym='g')
        self.add_par('i', 0) 
        assert abs(self.E/self.get_pvalue('N') - self.op[1]) < 1e-6
        assert abs(self.E/self.get_pvalue('N') - sum(self.op[2:5])) < 1e-6
 
class ES(MCTDHBState):
    """ExcitedState as computed by LR-MCTDHB."""
    def __init__(self, obj, data):
        if not isinstance(obj, GS):
            raise TypeError
        assert abs(data[2] - (obj.E + data[1])) < 1e-6
        self.GS = obj
        self.data = data
        MCTDHBState.__init__(self, obj.get_pvalue('N'),
                obj.get_pvalue('M'), obj.get_pvalue('L'),
                data[2], sym=self.guess_sym())
        
        self.set_norm()
        # Enumerate excited states.
        self.add_par('i', int(data[0]) - 10 - 2*obj.get_pvalue('M'))
    
    def guess_sym(self):
        """Try to derive symmetry of ES."""
        #check response amplitudes
        odd = self.data[5:7]
        even = self.data[7:9]
        if sum(odd) < MIN_RESPONSE and sum(even) < MIN_RESPONSE:
            retval = SymType['unknown']
        elif abs(sum(odd) - sum(even)) < MIN_RESPONSE:
            retval = SymType['unknown']
        elif (sum(odd)/sum(even) < MIN_DIFF):
            retval = SymType['gerade']
        elif (sum(even)/sum(odd) < MIN_DIFF):
            retval = SymType['ungerade']
        else:
            retval = SymType['mixed']
        return retval
    
    def set_norm(self):
        """Set normalization type."""
        phi, ci = self.data[3:5]
        if abs(1 - (phi+ci)) < ERR_NORM:
            if abs(ci) < abs(phi):
                self.norm = 'phi'
            else:
                self.norm = 'ci'
        elif abs(1 + (phi+ci)) < ERR_NORM:
            if abs(ci) < abs(phi):
                self.norm = '-phi'
            else:
                self.norm = '-ci'
        else:
            self.norm = 'not normalized'
     
    def __repr__(self):
        return State.__repr__(self) + ', norm: ' + repr(self.norm)

#not in use
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
