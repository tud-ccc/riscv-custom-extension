#!/usr/bin/env python2

import unittest
import sys

sys.path.append('..')
from modelparsing.parser import Operation
sys.path.remove('..')


class TestModel(unittest.TestCase):
    def testModel(self):
        pass


class TestOperation(unittest.TestCase):
    '''
    Tests for all functions in class Operation
    '''

    def setUp(self):
        self.form = 'R'
        self.funct3 = 0x01
        self.funct7 = 0x02
        self.name = 'test'
        self.opc = 0x03

        self.op = Operation(self.form,
                            self.funct3,
                            self.funct7,
                            self.name,
                            self.opc)

    def testOperation(self):
        self.assertEqual(self.op.form, self.form)
        self.assertEqual(self.op.funct3, self.funct3)
        self.assertEqual(self.op.funct7, self.funct7)
        self.assertEqual(self.op.name, self.name)
        self.assertEqual(self.op.opc, self.opc)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(verbosity=3).run(suite)
