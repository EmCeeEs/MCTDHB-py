#python3.5
#marcustheisen@web.de

"""HowTo"""
#from __future__ import with_statement    # This isn't required in Python 2.6
#from __future__ import print_function    # This is only possible for >= 2.6
import src.project as mctdhb
import numpy as np

if __name__ == '__main__':
    my = mctdhb.Project('lambda_sweep')
    temp1 = mctdhb.Project.from_template(temp1)
    
    LOG = True
    MIN = -2
    MAX = +2
    STEP = 1
    for xlambda in range(MIN, MAX, STEP):
        if (LOG):
            xlambda = np.exp(xlambda*np.log(10))
        my.set('XLAMBDA_0', xlambda)
        GS = my.relax()
        my.properties(GS)

