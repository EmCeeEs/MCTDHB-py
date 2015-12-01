#python2
#marcustheisen@web.de

"""mctdhb.py"""
import utilities as util
import io_routines as io
from states import GS, mk_spec

f90_infiles = ['input.in', 'properties.in']
str_infiles = ['V_W_Psi_string.in']

class MCTDHB(object):
    """MCTDHB class"""
    def __init__(self):
        """Initalise MCTDHB object from current input files"""
        # extract parameters
        self.pars = dict()
        for infile in f90_infiles:
            self.pars[infile] = io.read_f90_input(infile)
        for infile in str_infiles:
            self.pars[infile] = io.read_str_input(infile)
        
        # set executives
        self.bins = util.get_binaries()
        
        # initialise output data container and current state link
        self.data = dict()
        self.state = None
    
    @classmethod
    def restore(cls):
        """Inialize object from restored MCTDHB input files and binaries."""
        util.restore_infiles()
        util.restore_binaries()
        return cls()
    
    def run(self, job=None, quiet=False):
        """run MCTDHB"""
        if (job):
            self.set_job(job)
        self.write()
        util.execute(self.bins[0], quiet)
        for name in ['NO_PR.out', 'OP_PR.out']:
            self.data[name] = io.extract_data(name)
        #converg/relax errors: dE(last interation) < 'TIME_TOLERROR_TOTAL' 
        assert (self.data['NO_PR.out'][-1][self.get_par('MORB')+3]
                < self.data['NO_PR.out'][-1][self.get_par('MORB')+2])
        self.state = GS(self)
    
    def run_properties(self, quiet=False):
        """compute properties -- includes MCTDHB-LR"""
        if (self.state is None):
            raise IOError
        self.activate_LR()
        self.write()
        util.execute(self.bins[1], quiet)
        dpath = 'DATA/getLR/'
        for name in ['MC_anlsplot.out']:
            self.data[name] = io.extract_data(dpath + name)
        mk_spec(self)
    
    def write(self):
        """Write MCTDHB parameters to input files."""
        for infile in f90_infiles:
            io.write_f90_input(self.pars[infile], infile)
        for infile in str_infiles:
            io.write_str_input(self.pars[infile], infile)
    
    def basic_setup(self, dim=1):
        """Basic parameter adjustment."""
        # TODO: generalise to 3D
        self.set_par('MB_JOB_TYPE', 'ALL')
        self.set_par('DIM_MCTDHB', dim)
#       for char in 'XYZ':
#           self.set_par('TIME_DVRMETHOD' + char, 4)  #FFT
#           self.set_par('ND' + char, 128)
        self.set_par('PRINT_DATA', False)
        self.set_par('ORB_DIAG', True)
    
    def set_Npar(self, Npar):
        # set particle number
        if (Npar <= 0):
            raise ValueError
        self.set_par('Df_cnf_Fock', '')
        self.set_par('NPAR', Npar)
    
    def set_Morb(self, Morb):
        # set number of orbitals
        if not (0 < Morb <= 12):
            raise ValueError
        self.set_par('Df_cnf_Fock', '')
        self.set_par('MORB', Morb)
    
    def set_lambda(self, xlambda, normalize=False):
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
    
    def activate_LR(self):
        """Activate LR and deactivate other properties."""
        assert self.get_par('T_FROM') <= self.get_par('TIME_FNL')
        self.set_par('T_FROM', self.get_par('TIME_FNL')-1)
        self.set_par('T_TILL', self.get_par('TIME_FNL')-1)
        infile = 'properties.in'
        for record in self.pars[infile]:
            for pname in self.pars[infile][record]:
                if (type(self.get_par(pname)) is bool):
                    self.set_par(pname, False)
        self.set_par('GET_LR', True)
        self.set_par('DATA_PSI', True)
        self.set_par('DATA_CIC', True)
        self.set_par('LR_MAXSIL', 1000)
        
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
    
    def set_job(self, job):
        """Basic job setup."""
        if (job == 'relax'):
            self.set_par('JOB_PREFAC', complex(-1, 0))
            self.set_par('GUESS', 'HAND')
            self.set_par('STATE', 1)        #relax to GS
            self.set_par('TIME_BGN', 0.)
            self.set_par('TIME_FNL', 15.)
            self.set_par('TIME_TAU', .1)    #working relaxation step
            self.set_par('TIME_PRINT_STEP', .1)
            self.set_par('TIME_TOLERROR_TOTAL', 1E-8)
        elif (job == 'relax_backward'):
            self.set_job('relax')
            self.set_par('JOB_PREFAC', complex(+1, 0))
        elif (job == 'prop'):
            self.set_par('JOB_PREFAC', complex(0, -1))
            self.set_par('GUESS', 'BINR')
            self.set_par('BINARY_START_POINT_T', 10.)
            self.set_par('TIME_BGN', 0.)
            self.set_par('TIME_FNL', 200.)
            self.set_par('TIME_TAU', .01)   #initial propagation step
            self.set_par('TIME_PRINT_STEP', .01)
            self.set_par('TIME_TOLERROR_TOTAL', 1E-6)
        elif (job == 'prop_backward'):
            self.set_job('prop')
            self.set_par('JOB_PREFAC', complex(0, +1))
        else:
            raise ValueError('unknown job name')
    
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
