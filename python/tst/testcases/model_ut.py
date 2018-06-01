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

from scripts import model_gen
from scripts.ccmodel import CCModel
from mako.template import Template

sys.path.append('..')
from modelparsing.exceptions import ConsistencyError
from modelparsing.parser import Model
from tst import folderpath
sys.path.remove('..')


class TestModel(unittest.TestCase):
    '''
    Test that checks if model parser works correctly.
    '''

    def __init__(self, *args, **kwargs):
        super(TestModel, self).__init__(*args, **kwargs)
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
        self.ftype = 'I'
        self.inttype = 'uint32_t'
        self.opc = 0x0a
        self.funct3 = 0x07

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

    def genModel(self, name, filename, funct7=0xff, faults=[]):
        '''
        Create local cc Model and from that cc file.
        '''
        self.ccmodel = CCModel(name,
                               self.ftype,
                               self.inttype,
                               self.opc,
                               self.funct3,
                               funct7,
                               faults)

        # generate .cc models
        modelgen = Template(filename=model_gen)

        with open(filename, 'w') as fh:
            fh.write(modelgen.render(model=self.ccmodel))

    def testRTypeModel(self):
        # map rtype.cc -- should be correct
        name = 'rtype'
        self.ftype = 'R'
        self.opc = 0x02
        funct7 = 0x01
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, funct7)

        # parse model
        model = Model(filename)

        # check parsed models for expected values
        self.assertEqual(model.form, self.ccmodel.ftype)
        self.assertEqual(model.funct3, self.ccmodel.funct3)
        self.assertEqual(model.funct7, self.ccmodel.funct7)
        self.assertEqual(model.name, self.ccmodel.name)
        self.assertEqual(model.opc, self.ccmodel.opc)
        self.assertEqual(model.cycles, self.ccmodel.cycles)

    def testITypeModel(self):
        # map itype.cc
        name = 'itype'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename)

        # parse model
        model = Model(filename)

        # check parsed models for expected values
        self.assertEqual(model.form, self.ccmodel.ftype)
        self.assertEqual(model.funct3, self.ccmodel.funct3)
        self.assertEqual(model.name, self.ccmodel.name)
        self.assertEqual(model.opc, self.ccmodel.opc)
        self.assertEqual(model.cycles, self.ccmodel.cycles)

    def testNoRdModel(self):
        # no opcode specified
        name = 'nord'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, faults=['nord'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoRs1Model(self):
        # no rs1 specified
        name = 'nors1'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, faults=['nors1'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoOp2Model(self):
        name = 'noop2'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, faults=['noop2'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoRdNoRs1Model(self):
        name = 'nordnors1'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, faults=['nord', 'nors1'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoRdNoOp2Model(self):
        name = 'nordnoop2'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, faults=['nord', 'noop2'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoRs1NoOp2Model(self):
        name = 'nors1noop2'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, faults=['nors1', 'noop2'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoRdNoRs1NoOp2Model(self):
        name = 'nordnors1noop2'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, faults=['nord', 'nors1', 'noop2'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testWrongOpcModel(self):
        # wrong opcode given
        name = 'wrongopc'
        self.opc = 0x10
        self.funct3 = 0x00
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, faults=['wrongopc'])

        # check whether the exceptions where thrown correctly
        with self.assertRaises(ValueError):
            Model(filename)

    def testWrongFunct3Model(self):
        # max funct3
        name = 'rightfunct3'
        self.funct3 = 0x07
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename)

        # parse model
        model = Model(filename)

        # check parsed models for expected values
        self.assertEqual(model.form, self.ccmodel.ftype)
        self.assertEqual(model.funct3, self.ccmodel.funct3)
        self.assertEqual(model.name, self.ccmodel.name)
        self.assertEqual(model.opc, self.ccmodel.opc)
        self.assertEqual(model.cycles, self.ccmodel.cycles)

        # now a wrong model
        name = 'wrongfunct3'
        self.funct3 = 0xaa
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, faults=['wrongfunct3'])

        with self.assertRaises(ValueError):
            Model(filename)

    def testWrongFunct7Model(self):
        # max funct7
        name = 'rightfunct7'
        self.ftype = 'R'
        funct7 = 0x7f
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, funct7=funct7)

        # parse model
        model = Model(filename)

        # check parsed models for expected values
        self.assertEqual(model.form, self.ccmodel.ftype)
        self.assertEqual(model.funct3, self.ccmodel.funct3)
        self.assertEqual(model.funct7, self.ccmodel.funct7)
        self.assertEqual(model.name, self.ccmodel.name)
        self.assertEqual(model.opc, self.ccmodel.opc)
        self.assertEqual(model.cycles, self.ccmodel.cycles)

        # wrong funct7
        name = 'wrongfunct7'
        self.ftype = 'R'
        funct7 = 0xaa
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, funct7=funct7)

        with self.assertRaises(ValueError):
            Model(filename)

    def testExtractDefinitionModel(self):
        name = 'extract'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename)

        # parse model
        model = Model(filename)

        self.assertEqual(model.definition,
                         '{\n    // function definition\n}')

    def testNoDefinitionModel(self):
        name = 'nodef'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, faults=['nodef'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoClosingBracket(self):
        name = 'noclose'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, faults=['noclose'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testReturnInFctBody(self):
        name = 'retfct'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, faults=['return'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNonVoidFct(self):
        name = 'nonvoid'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, faults=['nonvoid', 'return'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoCycleCount(self):
        name = 'nocycles'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename, faults=['nocycles'])

        with self.assertRaises(ValueError):
            Model(filename)
