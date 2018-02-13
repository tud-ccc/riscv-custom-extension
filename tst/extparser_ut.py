#!/usr/bin/env python3

import unittest
import sys


class TestModel(unittest.TestCase):
    def testOne(self):
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

    def testOne(self):
        pass


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(verbosity=3).run(suite)
