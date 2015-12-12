#python3.5
#marcustheisen@web.de

"""testsuit.py"""
import unittest

import io_routines as io
import subprocess as subp
class TestFortranWrapping(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from collections import OrderedDict
        cls.pars = OrderedDict()
        cls.pars['foo.in'] = OrderedDict(
            REC1 = OrderedDict(
                FLOAT1 = 23e-24,
                FLOAT2 = -.2,
                ),
            REC2 = OrderedDict(
                INT1 = 5000,
                INT2 = -2,
                ),
            REC3 = OrderedDict(
                COMPLEX1 = complex(0, 0e-2),
                COMPLEX2 = complex(-0.002, +0.002),
                ),
            REC4 = OrderedDict(
                STR1 = '##??//<<>>CCcc**',
                STR2 = '([ ]}}]    )',
                STR3 = '.damn you, brave new world.',
                ),
            )
        cls.pars['foo2.in'] = OrderedDict(
            REC5 = OrderedDict(
                BOOL1 = True,
                BOOL2 = False,
                ),
            )
        #string InFile
        cls.pars['bar.in'] = OrderedDict()
        cls.pars['bar.in'][None] = OrderedDict(
            STR4 = '24*exp(2^x)',
            STR5 = '-500+x^(-0.5)',
            STR6 = 'abs',
            ) 
    
    @classmethod
    def tearDownClass(cls):
        for infile in cls.pars:
            try:
                subp.check_call(['rm', infile])
            except:
                pass
    
    def testReadWrite(self):
        for infile in self.pars:
            if (infile == 'bar.in'):
                io.write_str_input(self.pars[infile], infile)
                pars = io.read_str_input(infile)
            else:
                io.write_f90_input(self.pars[infile], infile)
                pars = io.read_f90_input(infile)
            self.assertEqual(self.pars[infile], pars)
    
    def testFromFortran(self):
        #bool
        self.assertTrue(io.from_f90(' .tRUe.'))
        self.assertFalse(io.from_f90('.f.'))
        self.assertRaises(io.InterpretationError, io.from_f90, 'true')
        self.assertRaises(io.InterpretationError, io.from_f90, '.f')
        
        #str
        self.assertEqual(io.from_f90("  ''"), '')
        self.assertEqual(io.from_f90("'\t\r\n'"), '\t\r\n')
        self.assertNotEqual(io.from_f90("'hallO welT'"), 'Hallo Welt')
        self.assertRaises(io.InterpretationError, io.from_f90, 'abc')
        self.assertRaises(io.InterpretationError, io.from_f90, "', ) ")
        
        #complex
        self.assertEqual(io.from_f90("(0, 0)"), 0j)
        self.assertEqual(io.from_f90("(32, -.2)"), (32 - 0.2j))
        self.assertIs(type(io.from_f90("(3, .2D-2)")), complex)
        self.assertRaises(io.InterpretationError, io.from_f90, "( 'du' , 'ich' )")
        self.assertRaises(io.InterpretationError, io.from_f90, '(3.76)')
        self.assertRaises(io.InterpretationError, io.from_f90, "(('')")
        
        #int & float
        self.assertEqual(io.from_f90(' -01'), -1)
        self.assertAlmostEqual(io.from_f90('9e-2'), 0.09)
        self.assertAlmostEqual(io.from_f90('-.201D03'), -201.)
        self.assertRaises(io.InterpretationError, io.from_f90, '4E 2')
        self.assertRaises(io.InterpretationError, io.from_f90, '-.2f')
        self.assertRaises(io.InterpretationError, io.from_f90, '34,2')
        self.assertRaises(io.InterpretationError, io.from_f90, '47e')
        self.assertRaises(io.InterpretationError, io.from_f90, 'd+2')
    
    def testToFortran(self):
        #self.assertEqual(io.to_f90(- 07), '-7')
        self.assertEqual(io.to_f90(3.), '3.0')
        self.assertEqual(io.to_f90(+ .1e-31), '1e-32')
        self.assertEqual(io.to_f90(complex(-2, 0.4)), '(-2.0, 0.4)')
        self.assertEqual(io.to_f90('\n\t\r '), "'\n\t\r '")
        self.assertNotEqual(io.to_f90('hallO welT'), "'Hallo Welt'")
        
        for container in [tuple(), list(), dict(), set()]:
            self.assertRaises(TypeError, io.to_f90, container)

if __name__ == '__main__':
    unittest.main()
