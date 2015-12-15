#python3.5
#marcustheisen@web.de

"""mctdhb.py"""
import src.utilities as util
import src.io_routines as io

f90_infiles = ['input.in', 'properties.in']
str_infiles = ['V_W_Psi_string.in']

class MCTDHB_infile(object):
    """MCTDHB infile class."""
    def __init__(self, path, from_str=False):
        self.read(path, from_str)
    
    def read(self, path, from_str=False):
        self.is_str = from_str
        self.path = path
        if (self.is_str):
            self._data = read_str_input(self.path)
        else:
            self._data = read_f90_input(self.path)
    
    def write(self, path=self._path):
        if (self.is_str):
            write_str_input(self.path)
        else:
            write_f90_input(self._data, path)
    
    def get(self, name):
        """Get parameter value."""
        if (self.is_str):
            for key, value in self._data.items(): 
                if (key == name):
                    retval = value
                    found = True
        else:
            name = name.upper()
            for namespace, pars in self._data.items():
                for key, value in pars.items(): 
                    if (key == name):
                        retval = value
                        found = True
        
        if (not found):
            raise ValueError(pname, 'is no MCTDHB parameter!')
        else:
            return retvalue
        
    def set(self, name, value):
        """Set parameter value."""
        oldval = self.get(name)
        if (type(value) is not type(oldval)):
            raise TypeError(name, 'is of type', type(oldval), '!')
        
        if (self.is_str):
            for key in self._data: 
                if (key == name):
                    self._data[key] = value
                    return
        else:
            name = name.upper()
            for namespace, pars in self._data.items():
                for key in pars: 
                    if (key == name):
                        pars[key] = value
                        return

class MCTDHB(object):
    """MCTDHB class"""
    def __init__(self):
        """Initalize MCTDHB object from current input files."""
        self.read_input()
        self.update_binaries()
    
    @classmethod
    def restore(cls):
        """Restore MCTDHB input files and binaries."""
        util.restore_infiles()
        util.restore_binaries()
    
    def run(self, quiet=False):
        """Run the MCTDHB package."""
        self.write_input()
        util.execute(self._bins[0], quiet)
    
    def run_properties(self, quiet=False):
        """Compute MCTDHB properties."""
        self.write_input()
        util.execute(self._bins[1], quiet)
    
    def read_input(self):
        """Read MCTDHB parameters from input files."""
        self._pars = dict()
        for infile in f90_infiles:
            self._pars[infile] = io.read_f90_input(infile)
        for infile in str_infiles:
            self._pars[infile] = io.read_str_input(infile)
    
    def write_input(self):
        """Write MCTDHB parameters to input files."""
        for infile in f90_infiles:
            io.write_f90_input(self._pars[infile], infile)
        for infile in str_infiles:
            io.write_str_input(self._pars[infile], infile)
    
    def update_binaries(self):
        """Update binary files."""
        self._bins = util.get_binaries()
    
    def get_N(self):
        """Get particle number."""
        return self.get_par('NPAR')
    
    def get_M(self):
        """Get number of orbitals."""
        return self.get_par('MORB')
    
    def get_L(self):
        """Get particle interaction strength."""
        return self.get_par('XLAMBDA_0')
    
    def set_N(self, npar):
        """Set particle number."""
        if (npar <= 0):
            raise ValueError
        self.set_par('Df_cnf_Fock', '')
        self.set_par('NPAR', npar)
    
    def set_M(self, morb):
        """Set number of orbitals."""
        if not (0 < morb <= 12):
            raise ValueError
        self.set_par('Df_cnf_Fock', '')
        self.set_par('MORB', morb)
    
    def set_L(self, xlambda, Lcap=False):
        """Set particle interaction strength.
        If normalize, set GP equivalent Lcap=xlambda*(N-1) instead.
        """
        if (Lcap):
            xlambda /= self.get_N() - 1.
        self.set_par('XLAMBDA_0', float(xlambda))
    
    def set_xtype(self, xtype):
        """Set interaction type."""
        if (xtype not in range(5)):
            raise ValueError
        if (xtype == 0):
            self.set_par('W(R=|r1-r2|&t)', '')
        self.set_par('WXX_TYPE', xtype)
    
    def get_par(self, name):
        """Get MCTDHB parameter."""
        for infile in self._pars:
            for record in self._pars[infile]:
                if (record is None):
                    assert (len(self._pars[infile]) == 1)
                    pname = name            #for string input, case matters
                else:
                    pname = name.upper()    #convert f90 variable to upper
                
                if (pname in self._pars[infile][record]):
                    return self._pars[infile][record][pname]
        raise ValueError(name, 'is no MCTDHB parameter or not set')
    
    def set_par(self, name, value):
        """Set MCTHDB parameter."""
        old_value = self.get_par(name)
        if type(value) is not type(old_value):
            if type(old_value) is float:
                value = float(value)
            else:
                raise TypeError
        for infile in self._pars:
            for record in self._pars[infile]:
                if (record is None):
                    pname = name            #for string input, case matters
                else:
                    pname = name.upper()    #convert f90 variable to upper
                
                if (pname in self._pars[infile][record]):
                    self._pars[infile][record][pname] = value
                    break
    
    def unset_properties(self):
        infile = 'properties.in'
        for record in self._pars[infile]:
            for pname in self._pars[infile][record]:
                if (type(self.get_par(pname)) is bool):
                    self.set_par(pname, False)
    
    def set_pot(self, pot):
        """V(x_y_z&t)"""
        pass
    
    def set_inter(self, wpot):
        """W(R=|r1-r2|&t)"""
        pass
    
    def set_mom(self, mom):
        """Imprint_MOM"""
        pass
    
    def set_psi(self, orb, psi):
        """Psi_m(x_y_z), m in M"""
        pass
    
    def set_dnsFock(self, dnsFock):
        """Df_cnf_Fock"""
        pass
