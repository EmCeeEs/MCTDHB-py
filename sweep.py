#python2
#marcustheisen@web.de

"""Sweeeep it like it's Christmas Eve."""
#from __future__ import with_statement    # This isn't required in Python 2.6
#from __future__ import print_function    # This is only possible for >= 2.6
from src.mctdhb import MCTDHB
from src.states import print_spec

if __name__ == '__main__':
    MCTDHB.restore()
    my = MCTDHB()
    my.set_M(2)
    my.set_N(2)
    my.set_L(.1, False)
    my.set_Wxx(0)
    my.relax(t_fnl=6.)
