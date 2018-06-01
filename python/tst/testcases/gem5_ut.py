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

import os
import shutil
import sys
import unittest

sys.path.append('..')
from modelparsing.gem5 import Gem5
from tst import folderpath
sys.path.remove('..')


class TestGem5(unittest.TestCase):
    '''
    Test that checks the decoder class output.
    '''

    class Model:
        def __init__(self, name, form, opc, funct3, definition, funct7=0xff):
            self._name = name
            self._form = form
            self._opc = opc
            self._funct3 = funct3
            self._funct7 = funct7
            self._definition = definition

        @property
        def name(self):
            return self._name

        @property
        def form(self):
            return self._form

        @property
        def opc(self):
            return self._opc

        @property
        def funct3(self):
            return self._funct3

        @property
        def funct7(self):
            return self._funct7

        @property
        def definition(self):
            return self._definition

    class Registers:
        def __init__(self, regmap):
            self._regmap = regmap

        @property
        def regmap(self):
            return self._regmap

    def __init__(self, *args, **kwargs):
        super(TestGem5, self).__init__(*args, **kwargs)
        # create temp folder
        if not os.path.isdir(folderpath):
            os.mkdir(folderpath)
            # test specific folder in temp folder
        test = self._testMethodName + '/'
        self.folderpath = os.path.join(folderpath, test)
        if not os.path.isdir(self.folderpath):
            os.mkdir(self.folderpath)

    def __del__(self):
        if os.path.isdir(folderpath) and not os.listdir(folderpath):
            try:
                os.rmdir(folderpath)
            except OSError:
                pass

    def setUp(self):
        # frequently used variables
        self.form = 'I'
        self.opc = 0x02
        self.funct3 = 0x00
        self.definition = "{\n    test;\n}"

        regmap = {'q0': 0x7000000}
        self.regs = self.Registers(regmap)

    def tearDown(self):
        # remove generated file
        if hasattr(self, '_outcome'):  # Python 3.4+
            # these 2 methods have no side effects
            result = self.defaultTestResult()
            self._feedErrorsToResult(result, self._outcome.errors)
        else:
            # Python 3.2 - 3.3 or 3.0 - 3.1 and 2.7
            result = getattr(self, '_outcomeForDoCleanups',
                             self._resultForDoCleanups)

        error = ''
        if result.errors and result.errors[-1][0] is self:
            error = result.errors[-1][1]

        failure = ''
        if result.failures and result.failures[-1][0] is self:
            failure = result.failures[-1][1]

        if not error and not failure:
            shutil.rmtree(self.folderpath)

    def testITypeDecoder(self):
        # test a simple decoder generation for an i type operation
        name = 'itype'
        models = [self.Model(name, self.form, self.opc,
                             self.funct3, self.definition)]
        decoder = Gem5(models, self.regs)
        decoder._buildpath = self.folderpath
        decoder.gen_decoder()

        expect = '''\
decode OPCODE default Unknown::unknown() {
0x2: decode FUNCT3 {
0x0: I32Op::itype({{
    test;
}}, uint32_t, IntCustOp);
}
}
'''
        self.assertEqual(decoder.decoder, expect)

    def testRTypeDecoder(self):
        # test a simple decoder generation for a r type operation
        name = 'rtype'
        self.form = 'R'
        funct7 = 0x00
        models = [self.Model(name, self.form, self.opc,
                             self.funct3, self.definition, funct7)]

        decoder = Gem5(models, self.regs)
        decoder._buildpath = self.folderpath
        decoder.gen_decoder()

        expect = '''\
decode OPCODE default Unknown::unknown() {
0x2: decode FUNCT3 {
0x0: decode FUNCT7 {
0x0: R32Op::rtype({{
    test;
}}, IntCustOp);
}
}
}
'''
        self.assertEqual(decoder.decoder, expect)

    def testInsertMultipleDecoder(self):
        name0 = 'itype0'
        name1 = 'itype1'
        name2 = 'rtype2'
        name3 = 'rtype3'
        name4 = 'rtype4'
        name5 = 'rtype5'

        models = [self.Model(name0, 'I', 0x02, 0x0, self.definition),
                  self.Model(name1, 'I', 0x02, 0x1, self.definition),
                  self.Model(name2, 'R', 0x02, 0x2, self.definition, 0x0),
                  self.Model(name3, 'R', 0x02, 0x2, self.definition, 0x1),
                  self.Model(name4, 'R', 0x16, 0x0, self.definition, 0x0),
                  self.Model(name5, 'R', 0x16, 0x0, self.definition, 0x1)]

        decoder = Gem5(models, self.regs)
        decoder._buildpath = self.folderpath
        decoder.gen_decoder()

        expect = '''\
decode OPCODE default Unknown::unknown() {
0x2: decode FUNCT3 {
0x0: I32Op::itype0({{
    test;
}}, uint32_t, IntCustOp);
0x1: I32Op::itype1({{
    test;
}}, uint32_t, IntCustOp);
0x2: decode FUNCT7 {
0x0: R32Op::rtype2({{
    test;
}}, IntCustOp);
0x1: R32Op::rtype3({{
    test;
}}, IntCustOp);
}
}
0x16: decode FUNCT3 {
0x0: decode FUNCT7 {
0x0: R32Op::rtype4({{
    test;
}}, IntCustOp);
0x1: R32Op::rtype5({{
    test;
}}, IntCustOp);
}
}
}
'''
        self.assertEqual(decoder.decoder, expect)
