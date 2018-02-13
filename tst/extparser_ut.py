#!/usr/bin/env python3

import unittest
import sys


class TestModel(unittest.TestCase):
    def testOne(self):
        pass


class TestOperation(unittest.TestCase):
    def testOne(self):
        pass


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(verbosity=3).run(suite)
