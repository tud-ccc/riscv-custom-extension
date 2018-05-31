#!/usr/bin/env python2

# Copyright (c) 2018 TU Dresden
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Robert Scheffel

from testcases import compiler_ut
from testcases import gem5_ut
from testcases import extensions_ut
from testcases import instruction_ut
from testcases import model_ut
from testcases import parser_ut
from testcases import registers_ut

import unittest


if __name__ == '__main__':
    # load test cases
    suiteList = []
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(
        compiler_ut.TestCompiler))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(
        gem5_ut.TestGem5))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(
        extensions_ut.TestExtensions))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(
        instruction_ut.TestInstruction))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(
        model_ut.TestModel))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(
        parser_ut.TestParser))
    suiteList.append(unittest.TestLoader().loadTestsFromTestCase(
        registers_ut.TestRegisters))

    # join them and run
    suite = unittest.TestSuite(suiteList)
    unittest.TextTestRunner(verbosity=3).run(suite)
