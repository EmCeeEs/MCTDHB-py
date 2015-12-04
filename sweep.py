#python2
#marcustheisen@web.de

"""Sweeeep it like it's Christmas Eve."""
#from __future__ import with_statement    # This isn't required in Python 2.6
#from __future__ import print_function    # This is only possible for >= 2.6
from src.mctdhb import MCTDHB
import src.routines as subr

if __name__ == '__main__':
    my = MCTDHB(True)
    my.set_M(2)
    my.set_N(2)
    my.set_L(.1, False)
    my.set_xtype(0)
    state = subr.relax(my, LR=True)
    subr.print_spec(state)
