#!/usr/bin/env python2

import os
import sys
import unittest

from mako.template import Template

sys.path.append('..')
from modelparsing.exceptions import ConsistencyError
from modelparsing.parser import Instruction
from modelparsing.parser import Model
from modelparsing.parser import Operation
sys.path.remove('..')


class CCModel:
    '''
    Gather all information that is used to generate a model.
    '''

    def __init__(self, name, ftype, inttype, opc, funct3, funct7, faults):
        self.name = name
        self.ftype = ftype
        self.inttype = inttype
        self.opc = opc
        self.funct3 = funct3
        self.funct7 = funct7
        self.faults = faults

        self.rd = '' if 'nord' in faults else 'Rd_uw'
        self.op1 = '' if 'nors1' in faults else 'Rs1_uw'

        self.rettype = inttype if 'nonvoid' in faults else 'void'

        if 'nodef' in faults:
            self.dfn = ';'
        elif 'noclose' in faults:
            self.dfn = '{\n    // function definition\n'
        elif 'return' in faults:
            self.dfn = '{\n    // function definition\n' \
                + '    return 0;\n}'
        else:
            self.dfn = '{\n    // function definition\n}'

        # inttypes
        if inttype == 'uint32_t':
            opsuf = '_uw'
        elif inttype == 'int32_t':
            opsuf = '_sw'
        elif inttype == 'uint64_t':
            opsuf = '_ud'
        elif inttype == 'int64_t':
            opsuf = '_sd'
        else:
            opsuf = ''

        if 'noop2' not in faults:
            if ftype == 'R':
                self.op2 = 'Rs2' + opsuf
            elif ftype == 'I':
                self.op2 = 'imm'
        else:
            self.op2 = ''


class TestInstruction(unittest.TestCase):
    '''
    Tests for all functions in class Instruction
    '''

    def setUp(self):
        # set up three different instructions to test all variants of operants
        # R-Type
        self.formr = 'R'
        self.mask = 'MASK'
        self.maskname = 'MASKNAME'
        self.match = 'MATCH'
        self.matchname = 'MATCHNAME'
        self.name0 = 'test0'
        # I-Type
        self.formi = 'I'
        self.name1 = 'test1'
        # unknown
        self.formx = 'X'
        self.name2 = 'test2'

        # create Instructions
        self.inst0 = Instruction(self.formr,
                                 self.mask,
                                 self.maskname,
                                 self.match,
                                 self.matchname,
                                 self.name0)
        self.inst1 = Instruction(self.formi,
                                 self.mask,
                                 self.maskname,
                                 self.match,
                                 self.matchname,
                                 self.name1)
        self.inst2 = Instruction(self.formx,
                                 self.mask,
                                 self.maskname,
                                 self.match,
                                 self.matchname,
                                 self.name2)

        # create expected operand strings
        self.opsr = 'd,s,t'
        self.opsi = 'd,s,j'
        self.opsx = ''

    def testInstructionRType(self):
        self.assertEqual(self.inst0.form, self.formr)
        self.assertEqual(self.inst0.mask, self.mask)
        self.assertEqual(self.inst0.maskname, self.maskname)
        self.assertEqual(self.inst0.match, self.match)
        self.assertEqual(self.inst0.matchname, self.matchname)
        self.assertEqual(self.inst0.name, self.name0)
        self.assertEqual(self.inst0.operands, self.opsr)

        self.assertNotEqual(self.inst0.form, self.formi)
        self.assertNotEqual(self.inst0.form, self.formx)
        self.assertNotEqual(self.inst0.name, self.name1)
        self.assertNotEqual(self.inst0.name, self.name2)
        self.assertNotEqual(self.inst0.operands, self.opsi)
        self.assertNotEqual(self.inst0.operands, self.opsx)

    def testInstructionIType(self):
        self.assertEqual(self.inst1.form, self.formi)
        self.assertEqual(self.inst1.name, self.name1)
        self.assertEqual(self.inst1.operands, self.opsi)

    def testInstructionXType(self):
        self.assertEqual(self.inst2.form, self.formx)
        self.assertEqual(self.inst2.name, self.name2)
        self.assertEqual(self.inst2.operands, self.opsx)


class TestModel(unittest.TestCase):
    '''
    Test that checks if model parser works correctly.
    '''

    def setUp(self):
        # save all models and remove them after the test
        self.tstmodels = []

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
            for model in self.tstmodels:
                os.remove(model)

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
        modelgen = Template(filename='test_models/model-gen.mako')

        with open(filename, 'w') as fh:
            fh.write(modelgen.render(model=self.ccmodel))

        self.tstmodels.append(filename)

    def testRTypeModel(self):
        # map rtype.cc -- should be correct
        name = 'rtype'
        self.ftype = 'R'
        self.opc = 0x02
        funct7 = 0x01
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, funct7)

        # parse model
        model = Model(filename)

        # check parsed models for expected values
        self.assertEqual(model.form, self.ccmodel.ftype)
        self.assertEqual(model.funct3, self.ccmodel.funct3)
        self.assertEqual(model.funct7, self.ccmodel.funct7)
        self.assertEqual(model.name, self.ccmodel.name)
        self.assertEqual(model.opc, self.ccmodel.opc)

    def testITypeModel(self):
        # map itype.cc
        name = 'itype'
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename)

        # parse model
        model = Model(filename)

        # check parsed models for expected values
        self.assertEqual(model.form, self.ccmodel.ftype)
        self.assertEqual(model.funct3, self.ccmodel.funct3)
        self.assertEqual(model.name, self.ccmodel.name)
        self.assertEqual(model.opc, self.ccmodel.opc)

    def testNoRdModel(self):
        # no opcode specified
        name = 'nord'
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, faults=['nord'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoRs1Model(self):
        # no rs1 specified
        name = 'nors1'
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, faults=['nors1'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoOp2Model(self):
        name = 'noop2'
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, faults=['noop2'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoRdNoRs1Model(self):
        name = 'nordnors1'
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, faults=['nord', 'nors1'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoRdNoOp2Model(self):
        name = 'nordnoop2'
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, faults=['nord', 'noop2'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoRs1NoOp2Model(self):
        name = 'nors1noop2'
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, faults=['nors1', 'noop2'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoRdNoRs1NoOp2Model(self):
        name = 'nordnors1noop2'
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, faults=['nord', 'nors1', 'noop2'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testWrongOpcModel(self):
        # wrong opcode given
        name = 'wrongopc'
        self.opc = 0x10
        self.funct3 = 0x00
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, faults=['wrongopc'])

        # check whether the exceptions where thrown correctly
        with self.assertRaises(ValueError):
            Model(filename)

    def testWrongFunct3Model(self):
        # max funct3
        name = 'rightfunct3'
        self.funct3 = 0x07
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename)

        # parse model
        model = Model(filename)

        # check parsed models for expected values
        self.assertEqual(model.form, self.ccmodel.ftype)
        self.assertEqual(model.funct3, self.ccmodel.funct3)
        self.assertEqual(model.name, self.ccmodel.name)
        self.assertEqual(model.opc, self.ccmodel.opc)

        # now a wrong model
        name = 'wrongfunct3'
        self.funct3 = 0xaa
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, faults=['wrongfunct3'])

        with self.assertRaises(ValueError):
            Model(filename)

    def testWrongFunct7Model(self):
        # max funct7
        name = 'rightfunct7'
        self.ftype = 'R'
        funct7 = 0x7f
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, funct7=funct7)

        # parse model
        model = Model(filename)

        # check parsed models for expected values
        self.assertEqual(model.form, self.ccmodel.ftype)
        self.assertEqual(model.funct3, self.ccmodel.funct3)
        self.assertEqual(model.funct7, self.ccmodel.funct7)
        self.assertEqual(model.name, self.ccmodel.name)
        self.assertEqual(model.opc, self.ccmodel.opc)

        # wrong funct7
        name = 'wrongfunct7'
        self.ftype = 'R'
        funct7 = 0xaa
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, funct7=funct7)

        with self.assertRaises(ValueError):
            Model(filename)

    def testExtractDefinitionModel(self):
        name = 'extract'
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename)

        # parse model
        model = Model(filename)

        self.assertEqual(model.definition,
                         '{\n    // function definition\n}')

    def testNoDefinitionModel(self):
        name = 'nodef'
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, faults=['nodef'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoClosingBracket(self):
        name = 'noclose'
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, faults=['noclose'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testReturnInFctBody(self):
        name = 'ret'
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, faults=['return'])

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNonVoidFct(self):
        name = 'ret'
        filename = 'test_models/' + name + '.cc'

        self.genModel(name, filename, faults=['nonvoid', 'return'])

        with self.assertRaises(ConsistencyError):
            Model(filename)


class TestOperation(unittest.TestCase):
    '''
    Tests for all functions in class Operation
    '''

    def setUp(self):
        # define test variables
        self.form = 'R'
        self.funct3 = 0x01
        self.funct7 = 0x02
        self.name = 'test'
        self.opc = 0x03

        # create operation with the help of previously defined variables
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


class TestParser(unittest.TestCase):
    '''
    Tests for the Parser class.
    More or less a complete functional test.
    '''

    def setUp(self):
        # save all models and remove them after the test
        self.tstmodels = []

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
            for model in self.tstmodels:
                os.remove(model)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(verbosity=3).run(suite)
