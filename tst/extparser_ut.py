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


class TestModel(unittest.TestCase):
    '''
    Test, that check if model parser works correctly.
    '''

    class Model:
        '''
        Gather all information that is used to generate a model.
        '''

        def __init__(self, name, ftype, inttype, opc, funct3, funct7=0xff, faults=[]):
            self.name = name
            self.ftype = ftype
            self.inttype = inttype
            self.opc = opc
            self.funct3 = funct3
            self.funct7 = funct7
            self.faults = faults

            if 'nord' in faults:
                self.rd = ''
            else:
                self.rd = 'Rd_uw'
            if 'noop1' in faults:
                self.op1 = ''
            else:
                self.op1 = 'Rs1_uw'

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

            if ftype == 'R':
                self.op2 = 'Rs2' + opsuf
            elif ftype == 'I':
                self.op2 = 'imm'
            else:
                self.op2 = ''

    def setUp(self):
        # save all models and remove them after the test
        self.tstmodels = ''

        self.ftype = 'I'
        self.inttype = 'uint32_t'
        self.opc = 0x0a
        self.funct3 = 0x07

    def tearDown(self):
        # remove generated file
        os.remove(self.tstmodels)

    def testRTypeModel(self):
        # map rtype.cc -- should be correct
        name = 'rtype'
        self.ftype = 'R'
        self.opc = 0x02
        funct7 = 0x01
        filename = 'test_models/' + name + '.cc'

        ccmodel = self.Model(
            name, self.ftype, self.inttype, self.opc, self.funct3, funct7)

        # generate .cc models
        modelgen = Template(filename='test_models/model-gen.mako')

        with open(filename, 'w') as fh:
            fh.write(modelgen.render(model=ccmodel))

        self.tstmodels = filename

        # parse model
        model = Model(filename)

        # check parsed models for expected values
        self.assertEqual(model.form, ccmodel.ftype)
        self.assertEqual(model.funct3, ccmodel.funct3)
        self.assertEqual(model.funct7, ccmodel.funct7)
        self.assertEqual(model.name, ccmodel.name)
        self.assertEqual(model.opc, ccmodel.opc)

    def testITypeModel(self):
        # map itype.cc
        name = 'itype'
        filename = 'test_models/' + name + '.cc'

        ccmodel = self.Model(
            name, self.ftype, self.inttype, self.opc, self.funct3)

        # generate .cc models
        modelgen = Template(filename='test_models/model-gen.mako')

        with open(filename, 'w') as fh:
            fh.write(modelgen.render(model=ccmodel))

        self.tstmodels = filename

        # parse model
        model = Model(filename)

        # check parsed models for expected values
        self.assertEqual(model.form, ccmodel.ftype)
        self.assertEqual(model.funct3, ccmodel.funct3)
        self.assertEqual(model.name, ccmodel.name)
        self.assertEqual(model.opc, ccmodel.opc)

    def testNoRdModel(self):
        # no opcode specified
        name = 'nord'
        filename = 'test_models/' + name + '.cc'

        ccmodel = self.Model(name,
                             self.ftype,
                             self.inttype,
                             self.opc,
                             self.funct3,
                             faults=['nord'])

        # generate .cc models
        modelgen = Template(filename='test_models/model-gen.mako')

        with open(filename, 'w') as fh:
            fh.write(modelgen.render(model=ccmodel))

        self.tstmodels = filename

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testNoRs1Model(self):
        # no rs1 specified
        name = 'nors1'
        filename = 'test_models/' + name + '.cc'

        ccmodel = self.Model(name,
                             self.ftype,
                             self.inttype,
                             self.opc,
                             self.funct3,
                             faults=['noop1'])

        # generate .cc models
        modelgen = Template(filename='test_models/model-gen.mako')

        with open(filename, 'w') as fh:
            fh.write(modelgen.render(model=ccmodel))

        self.tstmodels = filename

        with self.assertRaises(ConsistencyError):
            Model(filename)

    def testWrongOpcModel(self):
        # wrong opcode given
        name = 'wrongopc'
        self.opc = 0x10
        self.funct3 = 0x00
        filename = 'test_models/' + name + '.cc'

        ccmodel = self.Model(name,
                             self.ftype,
                             self.inttype,
                             self.opc,
                             self.funct3,
                             faults=['wrongopc'])

        # generate .cc models
        modelgen = Template(filename='test_models/model-gen.mako')

        with open(filename, 'w') as fh:
            fh.write(modelgen.render(model=ccmodel))

        self.tstmodels = filename

        # check whether the exceptions where thrown correctly
        with self.assertRaises(ValueError):
            Model(filename)

    def testWrongFunct3Model(self):
        name = 'wrongfunct3'
        self.funct3 = 0xaa
        filename = 'test_models/' + name + '.cc'

        ccmodel = self.Model(name,
                             self.ftype,
                             self.inttype,
                             self.opc,
                             self.funct3,
                             faults=['wrongfunct3'])

        # generate .cc models
        modelgen = Template(filename='test_models/model-gen.mako')

        with open(filename, 'w') as fh:
            fh.write(modelgen.render(model=ccmodel))

        self.tstmodels = filename

        with self.assertRaises(ValueError):
            Model(filename)

    def testWrongFunct7Model(self):
        name = 'wrongfunct7'
        self.ftype = 'R'
        funct7 = 0xaa
        filename = 'test_models' + name + '.cc'

        ccmodel = self.Model(name,
                             self.ftype,
                             self.inttype,
                             self.opc,
                             self.funct3,
                             funct7,
                             faults=['wrongfunct7'])

        # generate .cc models
        modelgen = Template(filename='test_models/model-gen.mako')

        with open(filename, 'w') as fh:
            fh.write(modelgen.render(model=ccmodel))

        self.tstmodels = filename

        with self.assertRaises(ValueError):
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


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(verbosity=3).run(suite)
