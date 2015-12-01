class ViviDict(dict):
    """Implementation of perl's autovivification feature."""
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

def get_par_value(pars, name):
    """Get par value."""
    #search parameter dictionary recursively
    for par in pars:
        if isinstance(pars[par], dict):
            if (par is not None):       #string inFile
                name = name.upper()
            try:
                value = get_par_value(pars[par], name)
            except ValueError:
                value = None
                continue
        
        #deepest level reached
        elif (par == name):
            value = pars[par][name]
        else:
            value = None
        #break if par found
        if (value):
            return value
    
    raise ValueError(name, 'is no MCTDHB parameter or not set')

def set_par_value(pars, name, value):
    """Set par value."""
    old_value = get_par_value(pars, name)
    if (type(value) is not type(old_value)):
        raise TypeError
    for infile in pars:
        for record in pars[infile]:
            if (record is None):
                pname = name            #str has to be identical
            else:
                pname = name.upper()    #convert f90 variable to upper
            
            if (pname in self.pars[infile][record]):
                self.pars[infile][record][pname] = value
                break

#depreciated & stupidity: tuples do not exist in f90
def from_f90_old(fstring):
    """Recursively convert from Fortran
    readable string to Python equivalent type.
    """
    fstring = fstring.strip()
    if (fstring == ''):     #empty
        return None
    
    #tuples
    if (fstring.startswith('(')):
        if (not fstring.endswith(')')):
            raise InterpretationError(fstring)
        if (fstring == '()'):
            return tuple()
        array = fstring[1:-1].split(',')
        array.reverse()
        substr, ret = None, []
        while (array):
            if (substr is None):
                substr = array.pop()
            else:
                substr = ','.join([substr, array.pop()])
            try:
                ret.append(from_f90_old(substr))
                substr = None
            except InterpretationError:
                if (not array):     #while array not empty ignore errors
                    raise
        
        if (len(ret) == 1):
            raise InterpretationError(fstring)
        return tuple(ret)
    
    # str
    if (fstring.startswith("'")):
        if (not fstring.endswith("'")) or (not fstring.count("'") == 2):
            raise InterpretationError(fstring)
        return fstring.strip("'")
    
    # bool
    if (fstring.upper() in ['.T.', '.TRUE.']):
        return True
    if (fstring.upper() in ['.F.', '.FALSE.']):
        return False
    
    # int & float
    try:
        return int(fstring)
    except ValueError:
        pass
    try:
        for char in 'dD':
            fstring = fstring.replace(char, 'e')
        return float(fstring)
    except ValueError:
        raise InterpretationError(fstring)
