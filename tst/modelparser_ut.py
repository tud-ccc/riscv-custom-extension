#!/usr/bin/env python2

from testcases import extensions_ut
from testcases import instruction_ut
from testcases import model_ut
from testcases import operation_ut
from testcases import parser_ut

import unittest


if __name__ == '__main__':
    # load test cases
    suiteList = []
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(
        extensions_ut.TestExtensions))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(
        instruction_ut.TestInstruction))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(
        model_ut.TestModel))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(
        operation_ut.TestOperation))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(
        parser_ut.TestParser))

    # join them and run
    suite = unittest.TestSuite(suiteList)
    unittest.TextTestRunner(verbosity=3).run(suite)
