#python3.5
#marcustheisen@web.de

"""Provides basic classes and functions"""
import subprocess as subp
import os
import os.path
#import os.stat
import glob
import shutil

# TODO: Include Scripts and Templates

def mctdhb_path():
    """Return shell environment variable 'mctdhb_dir'."""
    path = os.getenv('mctdhb_dir')
    if (path is None):
        raise EnvironmentError("'mctdhb_dir' not set!")
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
    print('Binary files are ' + mctdhb[0] + ' and ' + properties[0] + '.')
    return tuple(mctdhb + properties)

def execute(command, quiet=False):
    """execute(command, quiet=False)"""
    # If exit status of program is non-zero,
    # always raise subp.CalledProcessError.
    path = './'
    if (quiet):
        # Catch everything from stdout and sterr and return it.
        subp.check_output([path + command], stderr=subp.STDOUT)
    else:
        # Print everything and return exit status.
        subp.check_call([path + command])
    return
    process = subp.Popen(command, stdout=subp.PIPE)
    for line in iter(process.stdout.readline, b''):
        print(repr(line))
        #print(line) # yield line
    return
    

def rm_output():
    """Remove existing MCTDHB output data."""
    if os.path.isdir('DATA'):
        shutil.rmtree('DATA') 
    outfiles = glob.glob('*.out') + glob.glob('*.dat')
    for outfile in outfiles:
        os.remove(outfile)

def mk_dir(directory):
    """Create folder if not existing."""
    # Beware race-condition???
    if not os.path.exists(directory):
        os.makedirs(directory)
