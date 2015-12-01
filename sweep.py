#python2
#marcustheisen@web.de

"""sweep.py"""
#from __future__ import with_statement    # This isn't required in Python 2.6
#from __future__ import print_function    # This is only possible for >= 2.6
from mctdhb import MCTDHB
from states import print_spec

if __name__ == '__main__':
    my = MCTDHB.restore()
    my.set_Morb(2)
    my.set_lambda(.1, False)
    my.set_Wxx(0)
    my.run('relax') 
    my.run_properties()
    print_spec(my.state)
