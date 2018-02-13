#!/usr/bin/env python2

import unittest
import sys

from mako.template import Template

sys.path.append('..')
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

            self.rd = 'Rd_uw'
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
        self.ccmodels = {}
        # create different models
        # the more the better

        # map rtype.cc -- should be correct
        name = 'rtype'
        ftype = 'R'
        inttype = 'uint32_t'
        opc = 0x02
        funct3 = 0x03
        funct7 = 0x01
        filename = 'test_models/' + name + '.cc'

        self.ccmodels[filename] = self.Model(
            name, ftype, inttype, opc, funct3, funct7)

        # map itype.cc
        name = 'itype'
        ftype = 'I'
        inttype = 'uint32_t'
        opc = 0x0a
        funct3 = 0x07
        filename = 'test_models/' + name + '.cc'

        self.ccmodels[filename] = self.Model(
            name, ftype, inttype, opc, funct3)

        for filename, ccmodel in self.ccmodels.items():
            # generate .cc models
            modelgen = Template(filename='test_models/model-gen.mako')

            with open(filename, 'w') as fh:
                fh.write(modelgen.render(model=ccmodel))

    def testProperModels(self):
        # parse models and check if information have been retrieved correctly
        for filename, ccmodel in self.ccmodels.items():
            # parse models
            if not ccmodel.faults:
                model = Model(filename)

                self.assertEqual(model.form, ccmodel.ftype,
                                 msg='model name = {}'.format(filename))
                self.assertEqual(model.funct3, ccmodel.funct3,
                                 msg='model name = {}'.format(filename))
                if model.form == 'R':
                    self.assertEqual(model.funct7, ccmodel.funct7,
                                     msg='model name = {}'.format(filename))
                self.assertEqual(model.name, ccmodel.name,
                                 msg='model name = {}'.format(filename))
                self.assertEqual(model.opc, ccmodel.opc,
                                 msg='model name = {}'.format(filename))

    def tearDown(self):
        pass


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
