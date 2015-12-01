#python2
#marcustheisen@web.de
#
# The MCTDHB-package is written in Fortran90, which does not distingish
# between uppercase and lowercase.  Due to wild card punches, when running in
# fixed mode, there have to be 6 whitespaces in each line before actual code.
# Fixed line length is 72 characters, line continuation can be achieved by
# any character in the 6th column.  Comments begin with any of 'cC!' in
# the very first column or by '!' in the code section.  The identifiers for
# beginning and end of records are '&' and '/', respectively.  Variable names
# consist of letters [a-z], digits [0-9] and underscores '_' but have to
# start with a letter and can be no longer than 31 characters. 
# MCTDHB input files have a '.in', output files a '.out' extension.

"""Routines for handling MCTDHB input and output."""
from collections import OrderedDict
import subprocess as subp
import numpy as np
#import logging
#import re

class InterpretationError(Exception):
    """Error class for failed f90-string interpretation."""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'Could not interpreted' + repr(self.value)

def read_f90_input(infile):
    """read_f90_input(infile) -> dict
    
    Read f90-style input file.
    Return nested dictionary -- records, names and values.
    """
    # NOTE: Parameters could be set in one line seperated by commata...
    #+      Fortunately, with MCTDHB they are not -- single defintion per line.
    #+      f90-string variables may not contain any of '!='.
    
    #store input parameters in ordered dictionary
    pars = OrderedDict()
    with open(infile, 'r') as f:
        for line in f:
            #remove all kinds of comments
            line = line.split('!')[0].strip(' \n,')
            if (not line):          #skip empty lines
                continue
            if (line[0] == '&'):    #begin record
                record = line.lstrip('&').upper()
                names = pars[record] = OrderedDict()
                continue
            if (line[0] == '/'):    #end record
                record = None
            
            if (record):
                name, value = line.split('=')
                name = name.rstrip().upper()
                value = value.lstrip()
                names[name] = from_f90(value)
    return pars

def read_str_input(infile):
    """read_str_input(infile) -> dict
    
    Read string input file.
    Return dictionary of input parameters -- names and expressions.
    """
    # NOTE: Parameter names have to be exact, upper/lowercase matters!!!
    #+      Whitespaces are superfluous. One defintion per line.
    #+      Comments only at the beginning of line.
    #+      Expressions may not contain any of '#='.
    
    #store input expressions in OrderedDict with None-type record
    pars = OrderedDict({ None : OrderedDict() })
    with open(infile, 'r') as f:
        for line in f:
            #remove all kinds of comments
            line = line.split('#')[0].strip(' \n,')
            if (not line):      #skip empty lines
                continue
            
            name, value = line.replace(' ', '').rsplit('=', 1)
            pars[None][name] = value
    return pars

def write_f90_input(pars, outfile):
    """write_f90_input(pars, outfile)
    
    Write f90-style input parameters to outfile.
    """
    with open(outfile, 'w') as f:
        for record in pars:
            f.write('&' + record + '\n')
            for name, value in pars[record].items():
                f.write(name + '=' + to_f90(value) + '\n')
            f.write('/\n')

def write_str_input(pars, outfile):
    """write_str_input(pars, outfile)
    
    Write string input parameters to outfile.
    """
    with open(outfile, 'w') as f:
        for name, expr in pars[None].items():
            if (expr):
                f.write(name + '=' + expr + '\n')
    
def extract_data(filename):
    """extract_data(filename) -> np.ndarray of type np.float64"""
    # NOTE: Comments are omitted.
    #+      File contains columns with numbers.
    
    data = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.lstrip()
            if (line[0] in '#\n'):
                continue
            if (line.startswith('time')):       #OP_PR.out
                continue
            
            values = line.split()
            if (data):
                assert (len(data[-1]) == len(values))
            for i in range(len(values)):      #ignore too small numbers
                if (len(values[i]) > 10) and (values[i][-4] == '-'):
                    values[i] = 0
            
            data.append(values)
    return np.array(data).astype('float64')

def from_f90(fstring):
    """from_f90(fstring) -> type
    
    Convert string from f90-readable type to python equivalent.
    type in (None, str, bool, int, float, complex)
    """
    fstring = fstring.strip()
    #EMPTY/UNSET -- None
    if (fstring == ''):
        return None
    
    #COMPLEX -- complex
    elif (fstring.startswith('(') and fstring.endswith(')')):
        try:
            re, im = fstring.strip('()').split(',')     #ValueError
            return complex(from_f90(re), from_f90(im))  #TypeError
        except (ValueError, TypeError):
            raise InterpretationError(fstring)
    
    #CHARACTER --  str
    # TODO: Include escape characters and multiple occurrences
    #+      of quotation marks.
    elif (fstring.startswith(('"', "'")) and (fstring[0] == fstring[-1])):
        if (len(fstring) < 2):
            raise InterpretationError(fstring)
        return fstring.strip(fstring[0])
    
    #LOGICAL -- bool
    elif (fstring.startswith('.') and fstring.endswith('.')):
        if (fstring.upper() in ['.T.', '.TRUE.']):
            return True
        elif (fstring.upper() in ['.F.', '.FALSE.']):
            return False
        else:
            raise InterpretationError(fstring)
    
    #INTEGER -- int
    elif (fstring.isdigit() or fstring.lstrip('+-').isdigit()):
        try:
            return int(fstring)
        except ValueError:
            raise InterpretationError(fstring)
    
    #REAL -- float
    else:
        try:
            for char in 'dD':
                fstring = fstring.replace(char, 'e')
            return float(fstring)
        except ValueError:
            raise InterpretationError(fstring)

def to_f90(variable):
    """to_f90(variable) -> str
    
    Convert python type variable to f90-readable string.
    """
    if (type(variable) is int) or (type(variable) is float):
        ret = str(variable)
    elif (type(variable) is bool):
        if (variable):
            ret = '.T.'
        else:
            ret = '.F.'
    elif (type(variable) is str):
        ret = "'" + variable + "'"
    elif (type(variable) is complex):
        ret = '(' + str(variable.real) + ', ' + str(variable.imag) + ')'
    else:
        raise TypeError
    return ret
