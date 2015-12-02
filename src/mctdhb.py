#python2
#marcustheisen@web.de

"""mctdhb.py"""
import utilities as util
import io_routines as io
import states

f90_infiles = ['input.in', 'properties.in']
str_infiles = ['V_W_Psi_string.in']

outfiles = ['NO_PR.out', 'OP_PR.out']

class MCTDHB(object):
    """MCTDHB class"""
    def __init__(self):
        """Initalize MCTDHB object from current input files"""
        # extract parameters
        self.read()
        # set executives
        self.bins = util.get_binaries()
        
        # initialise output data container and current state link
        self.data = dict()
        self.state = None
    
    @classmethod
    def restore(cls):
        """Restore MCTDHB input files and binaries."""
        util.restore_infiles()
        util.restore_binaries()
    
    def relax(self, tolerance=1E-8,
                    t_final=11.,
                    t_tau=.1,
                    t_begin = 0.,
                    backward=False,
                    print_data=False):
        """Find system's GroundState (GS)."""
        if (backward):
            self.set_par('JOB_PREFAC', complex(+1, 0))
        else:
            self.set_par('JOB_PREFAC', complex(-1, 0))
        self.set_par('PRINT_DATA', print_data)
        self.set_par('GUESS', 'HAND')
        self.set_par('STATE', 1)        #relax to GS
        self.set_par('TIME_BGN', t_begin)
        self.set_par('TIME_FNL', t_final)
        self.set_par('TIME_TOLERROR_TOTAL', tolerance)
        self.set_par('TIME_TAU', t_tau)    #working relaxation step
        self.set_par('TIME_PRINT_STEP', t_tau)
        
        m = self.get_par('MORB')
        delta_t = 5
        relaxed = False
        while not relaxed:
            self.write()
            util.execute(self.bins[0])
            # Extract data from MCTDHB outfiles.
            for name in ['NO_PR.out', 'OP_PR.out']:
                self.data[name] = io.extract_data(name)
            # Check if converged.
            #          dE(last interation)      < 'TIME_TOLERROR_TOTAL' 
            if (self.data['NO_PR.out'][-1][m+3] < tolerance):
                relaxed = True
            else:
                t_final += delta_t
                self.set_par('TIME_FNL', t_fnl)
        
        self.state = states.GS(self) 
    
    def prop(self, backward=False,
                   t_fnl=200.,
                   tolerance=1E-6,
                   guess='BINR',
                   print_step=.01):
        """Propagate the last relaxed state."""
        if (backward):
            self.set_par('JOB_PREFAC', complex(0, +1))
        else:
            self.set_par('JOB_PREFAC', complex(0, -1))
        if (guess in ['BINR', 'HAND', 'DATA']):
            self.set_par('GUESS', guess)
            self.set_par('BINARY_START_POINT_T', self.get_par('TIME_BGN'))
            # TODO: Adjust *.dat files.
            self.set_par('TIME_RES_ORB_FILE_NAME', '10.0000000time.dat')
            self.set_par('TIME_RES_CIC_FILE_NAME', '10.0000000coef.dat')
        else:
            raise Exception('Invalid guess type')
        
        self.set_par('PRINT_DATA', True)
        self.set_par('TIME_BGN', 0.)
        self.set_par('TIME_FNL', t_fnl)
        self.set_par('TIME_TAU', print_step)   #initial propagation step
        self.set_par('TIME_PRINT_STEP', print_step)
        self.set_par('TIME_TOLERROR_TOTAL', tolerance)
        #run
        self.write()
        util.execute(self.bins[0])
        for name in ['NO_PR.out', 'OP_PR.out']:
            self.data[name] = io.extract_data(name)

    def linear_response(self):
        """Compute MCTDHB-LR."""
        if (self.state is None):
            raise Exception('No relaxed state to start from.')
        self.set_par('T_FROM', self.get_par('TIME_FNL'))
        self.set_par('T_TILL', self.get_par('TIME_FNL'))
        infile = 'properties.in'
        for record in self.pars[infile]:
            for pname in self.pars[infile][record]:
                if (type(self.get_par(pname)) is bool):
                    self.set_par(pname, False)
        self.set_par('GET_LR', True)
        self.set_par('DATA_PSI', True)
        self.set_par('DATA_CIC', True)
        self.set_par('LR_MAXSIL', 1000)     #this seems to affect nothing
        
        #run
        self.write()
        util.execute(self.bins[1])
        dpath = 'DATA/getLR/'
        for name in ['MC_anlsplotAll.out']:
            self.data[name] = io.extract_data(dpath + name)
        states.spec(self)
    
    def run(self, quiet=False):
        """Run the MCTDHB package."""
        self.write()
        util.execute(self.bins[1], quiet)
    
    def run_properties(self, quiet=False):
        """Compute MCTDHB properties."""
        self.write()
        util.execute(self.bins[0], quiet)
    
    def write(self):
        """Write MCTDHB parameters to input files."""
        for infile in f90_infiles:
            io.write_f90_input(self.pars[infile], infile)
        for infile in str_infiles:
            io.write_str_input(self.pars[infile], infile)
    
    def read(self):
        """Read MCTDHB parameters from input files."""
        self.pars = dict()
        for infile in f90_infiles:
            self.pars[infile] = io.read_f90_input(infile)
        for infile in str_infiles:
            self.pars[infile] = io.read_str_input(infile)
    
    def set_N(self, Npar):
        # set particle number
        if (Npar <= 0):
            raise ValueError
        self.set_par('Df_cnf_Fock', '')
        self.set_par('NPAR', Npar)
    
    def set_M(self, Morb):
        # set number of orbitals
        if not (0 < Morb <= 12):
            raise ValueError
        self.set_par('Df_cnf_Fock', '')
        self.set_par('MORB', Morb)
    
    def set_L(self, xlambda, normalize=False):
        # set particle interaction strength
        if (normalize):
            xlambda /= self.get_par('Npar') - 1
        self.set_par('xlambda_0', float(xlambda))

    def set_Wxx(self, Wxx):
        # set interaction type
        if (Wxx not in range(5)):
            raise ValueError
        if (Wxx == 0):
            self.set_par('W(R=|r1-r2|&t)', '')
        self.set_par('WXX_TYPE', Wxx)
    
    def get_par(self, name):
        """Get MCTDHB parameter."""
        for infile in self.pars:
            for record in self.pars[infile]:
                if (record is None):
                    assert (len(self.pars[infile]) == 1)
                    pname = name            #for string input, case matters
                else:
                    pname = name.upper()    #convert f90 variable to upper
                
                if (pname in self.pars[infile][record]):
                    return self.pars[infile][record][pname]
        raise ValueError(name, 'is no MCTDHB parameter or not set')
    
    def set_par(self, name, value):
        """Set MCTHDB parameter."""
        old_value = self.get_par(name)
        if (type(value) is not type(old_value)):
            raise TypeError
        for infile in self.pars:
            for record in self.pars[infile]:
                if (record is None):
                    pname = name            #for string input, case matters
                else:
                    pname = name.upper()    #convert f90 variable to upper
                
                if (pname in self.pars[infile][record]):
                    self.pars[infile][record][pname] = value
                    break
    
    def set_pot(self, pot):
        pass
    
    def set_inter(self, wpot):
        pass
    
    def set_mom(self, mom):
        pass
    
    def set_psi(self, orb, psi):
        pass
    
    def set_dnsFock(self, dnsFock):
        pass
