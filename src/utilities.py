#python2
#marcustheisen@web.de

"""Provides basic classes and functions"""
from collections import OrderedDict
import subprocess as subp
import os
import glob

# TODO: Include Scripts and Templates

class ViviDict(OrderedDict):
    """Implementation of perl's autovivification feature."""
    def __missing__(self, key):
        value = self[key] = type(self)()
        return value

def mctdhb_path():
    """Return shell environment variable 'mctdhb_dir'."""
    path = os.getenv('mctdhb_dir')
    if (path is None):
        raise EnvironmentError("Shell environment 'mctdhb_dir' not set!")
    return path

def restore_infiles():
    """Restore MCTDHB input files."""
    path = mctdhb_path() + '/IN.FILES/'
    for infile in os.listdir(path):
        subp.check_call(['cp', path + infile, '.'])

def restore_binaries():
    """Restore MCTDHB binary files."""
    #remove obsolete binaries
    old_bins = glob.glob('boson_MCTDHB*') + glob.glob('properties_LR*')
    for binary in old_bins:
        subp.check_call(['rm', binary])
    
    #restore actual binaries
    path = mctdhb_path() + '/bin/'
    for binary in os.listdir(path):
        subp.check_call(['cp', path + binary, '.'])

def get_binaries():
    """Return tuple with names of existing binary files."""
    mctdhb = glob.glob('boson_MCTDHB*')
    properties = glob.glob('properties_LR*')
    if (len(mctdhb) != 1) or (len(properties) != 1):
        raise EnvironmentError('Could not find unambiguous MCTDHB binaries!')
    return tuple(mctdhb + properties)

def execute(binary, quiet=False):
    """execute(binary, quiet=True) -> int
    
    Execute binary.
    """
    if (quiet):
        #catch everything from stdout and sterr and return it
        subp.check_output([binary], stderr=subp.STDOUT)
    else:
        #print everything
        subp.check_call([binary])
