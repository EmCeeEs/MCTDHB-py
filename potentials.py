#python2
#marcustheisen@web.de

"""potentials.py"""

from math import pow, sqrt, exp, log, cos
import unittest
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fmin
#import scipy.optimize
#import sympy

def Vpoly(x, par=(0.5, 2), as_str=False):
    """polynominal DW-potential"""
    if (len(par) != 2):
        raise TypeError()
    a, x0 = par
    if (a <= 0) or (x0 == 0):
        raise ValueError()
    if (as_str):
        return str(a) + '*(x^2-' + str(x0) + '^2)^2'
    return a*pow(pow(x, 2) - pow(x0, 2), 2)

def Vexp(x, par=(0.5, 5, 1), xs=0, as_str=False):
    """harmonic potential with Gaussian barrier"""
    if (len(par) != 3):
        raise TypeError() 
    a, b, c = par 
    if (a <= 0) or (b < 0) or (c < 0):
        raise ValueError()
    if (b != 0):        # if not harmonic potential
        k = b*c/a
        if (k <= 1):
            raise ValueError()
    if (as_str):
        return str(a) + '*(x-' + str(xs) + ')^2+' + \ 
            str(b) + '*exp(-' + str(c) + '*x^2)'
    #offset = a/c * (log(k) + 1)     # s.t. potential vanishes in minimum
    return a*pow(x - xs, 2) + b*exp( - c*pow(x, 2))

def Vcos(x, par=(0.5, 5, 1), xs=0, as_str=False):
    """harmonic potential with cos^2 barrier/deformation"""
    if (len(par) != 3):
        raise TypeError() 
    a, b, c = par
    if (a <= 0) or (b <= 0) or (c == 0):
        raise ValueError()
    if (as_str):
        return str(a) + '*(x-' + str(xs) + ')^2+' + \ 
            str(b) + '*cos(' + str(c) + '*x)^2'
    return a*pow(x - xs, 2) + b*pow(cos(c*x), 2)

class Potential(object):
    """mask for potentials"""
    def __init__(self, name, par=None):
        self.setV(name, par)
    
    def setV(self, name, par=None):
        if (name == 'poly'):
            self.V = Vpoly
            self.num_par = 2
            if (par is list) and (len(par) != self.num_par):
                raise TypeError()
            if (par is None):
                par = (0.5, 2)
        elif (name == 'harm'):
            self.V = Vexp 
            self.num_par = 3
            if (par is list) and (len(par) != self.num_par):
                raise TypeError()
            if (par is None):
                par = (0.5, 0, 0)
        elif (name == 'exp'):
            self.V = Vexp 
            self.num_par = 3
            if (par is list) and (len(par) != self.num_par):
                raise TypeError()
            if (par is None):
                par = (0.5, 5, 1)
        elif (name == 'cos'):
            self.V = Vcos 
            self.num_par = 3
            if (par is list) and (len(par) != self.num_par):
                raise TypeError()
            if (par is None):
                par = (0.5, 5, 1)
        else:
            raise TypeError()
        
        self.update_par(par)
    
    def update_par(self, par):
        if (len(par) != self.num_par):
            raise TypeError()
        try:
            self.V(0, par)
        except ValueError:
            raise
        self.par = par
        self.min_at = self.find_min()
        self.height = self.V_eval(0) - self.V_eval(self.min_at)
    
    def V_eval(self, x):
        return self.V(x, self.par)
    
    def find_min(self):
        if (self.V == Vpoly):
            a, x0 = self.par
            return abs(x0) 
        if (self.V == Vexp):
            a, b, c = self.par 
            if (b == 0):        # harmonic
                return 0
            k = b*c/a
            return sqrt(log(k)/c)
        # find minimum numerically. start at the origin and go right untill
        # pos of min value is reached. Go back to pos-1 and continue going
        # right with smaller steps.
        lower_guess = 0
        precision = 12
        for i in range(precision):
            guess = lower_guess
            new_guess = guess + pow(10, -i)
            count = 0
            while (self.V_eval(new_guess) < self.V_eval(guess)):
                guess = new_guess
                if (count > 20):
                    raise RuntimeError()
                if (count):
                    lower_guess += pow(10, -i) 
                new_guess += pow(10, -i)
                count += 1
        return guess
    
    def plot(self, Min=-4, Max=4, Step=0.01):
        # introduce plotrange
        xvalues = np.arange(Min, Max, Step)
        values = []
        for x in xvalues:
            values.append(self.V_eval(x)) 
        return xvalues, values


class TestPotentialMethods(unittest.TestCase):
    def setUp(self):
        poly = Potential('poly')
        harm = Potential('harm')
        expo = Potential('exp')
        cos2 = Potential('cos')
        self.pots = [poly, harm, expo, cos2]
    
    def testParameter(self):
        self.assertRaises(ValueError. Potential, 'Polynominal')
        
    @unittest.skip('skip plotting')
    def testPlot(self):
        for pot in self.pots:
            x, y = pot.plot()
            plt.plot(x, y)
            plt.show()
    
    def testFindMin(self):
        self.assertEqual(self.pots[0].find_min(), 2)
        self.assertEqual(self.pots[1].find_min(), 0)
        self.assertAlmostEqual(self.pots[2].find_min(), sqrt(log(10)))

if __name__ == '__main__':
    unittest.main()
