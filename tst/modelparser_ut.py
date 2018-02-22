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
from modelparsing.parser import Parser
sys.path.remove('..')

folderpath = os.path.dirname(os.path.realpath(__file__)) + '/files/'


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
        if os.path.isdir(self.folderpath) and not os.listdir(self.folderpath):
            try:
                os.rmdir(self.folderpath)
            except OSError:
                pass
        if os.path.isdir(folderpath) and not os.listdir(folderpath):
            try:
                os.rmdir(folderpath)
            except OSError:
                pass

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
        modelgen = Template(filename='model-gen.mako')

        with open(filename, 'w') as fh:
            fh.write(modelgen.render(model=self.ccmodel))

        self.tstmodels.append(filename)

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

    class Args:
        '''
        Represent args, that parser needs.
        '''

        def __init__(self, modelpath):
            self._modelpath = modelpath

        @property
        def modelpath(self):
            return self._modelpath

    def __init__(self, *args, **kwargs):
        super(TestParser, self).__init__(*args, **kwargs)
        # create temp folder
        if not os.path.isdir(folderpath):
            os.mkdir(folderpath)
        # test specific folder in temp folder
        test = self._testMethodName + '/'
        self.folderpath = os.path.join(folderpath, test)
        if not os.path.isdir(self.folderpath):
            os.mkdir(self.folderpath)

    def __del__(self):
        if os.path.isdir(self.folderpath) and not os.listdir(self.folderpath):
            try:
                os.rmdir(self.folderpath)
            except OSError:
                pass
        if os.path.isdir(folderpath) and not os.listdir(folderpath):
            try:
                os.rmdir(folderpath)
            except OSError:
                pass

    def setUp(self):
        # save all models and remove them after the test
        self.tstmodels = []

        self.ftype = 'I'
        self.inttype = 'uint32_t'
        self.opc = 0x02
        self.funct3 = 0x00

        # prepare header and cc file
        self.opcheader = self.folderpath + 'opcheader.h'
        with open(self.opcheader, 'w') as fh:
            fh.write(
                '/* Automatically generated by parse-opcodes.  */\n' +
                '#ifndef RISCV_ENCODING_H\n' +
                '#define RISCV_ENCODING_H\n')
        self.opcsource = self.folderpath + 'opcsource.c'
        with open(self.opcsource, 'w') as fh:
            fh.write('')

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

            os.remove(self.opcheader)
            os.remove(self.opcsource)

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
        modelgen = Template(filename='model-gen.mako')

        with open(filename, 'w') as fh:
            fh.write(modelgen.render(model=self.ccmodel))

        self.tstmodels.append(filename)

    def testExtendHeaderSingle(self):
        # extend the header with a single model
        name = 'singleHeader'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename)

        args = self.Args(filename)

        parser = Parser(args)
        parser.opch = self.opcheader

        parser.extend_header()

        with open(self.opcheader, 'r') as fh:
            hcontent = fh.readlines()

        # first match then mask
        self.assertEqual(hcontent[3], parser.instructions[0].match)
        self.assertEqual(hcontent[4], parser.instructions[0].mask)

    def testExtendHeaderMultiple(self):
        # extend the header with multiple models
        name = 'testHeader0'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename)

        name = 'testHeader1'
        self.funct3 = 0x01
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename)

        name = 'testHeader2'
        self.opc = 0x0a
        self.funct3 = 0x00
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename)

        name = 'testHeader3'
        self.funct3 = 0x01
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename)

        args = self.Args(self.folderpath)

        parser = Parser(args)
        parser.opch = self.opcheader

        parser.extend_header()

        with open(self.opcheader, 'r') as fh:
            hcontent = fh.readlines()

        # basically check if all masks and matches where added
        # maybe extend the test a little? don't know
        for inst in parser.instructions:
            self.assertTrue(inst.match in hcontent)
            self.assertTrue(inst.mask in hcontent)

    def testExtendHeaderSameTwice(self):
        # extend the header two times with the same function
        # should occure only once in header
        name = 'sameFctTwice'
        filename = self.folderpath + name + '.cc'

        self.genModel(name, filename)
        args = self.Args(filename)

        parser1 = Parser(args)
        parser1.opch = self.opcheader
        parser1.extend_header()

        parser2 = Parser(args)
        parser2.opch = self.opcheader
        parser2.extend_header()

        with open(self.opcheader, 'r') as fh:
            hcontent = fh.readlines()

        # only added once
        # therefore header file should have 5 entries
        self.assertEqual(len(hcontent), 5)
        self.assertEqual(hcontent[3], parser1.instructions[0].match)
        self.assertEqual(hcontent[3], parser1.instructions[-1].match)
        self.assertEqual(hcontent[3], parser2.instructions[0].match)
        self.assertEqual(hcontent[3], parser2.instructions[-1].match)
        self.assertEqual(hcontent[4], parser1.instructions[0].mask)
        self.assertEqual(hcontent[4], parser1.instructions[-1].mask)
        self.assertEqual(hcontent[4], parser2.instructions[0].mask)
        self.assertEqual(hcontent[4], parser2.instructions[-1].mask)

    def testExtendHeaderSameName(self):
        # extend the header file with the same name but different opcode
        # the last one should be taken
        # the other ones deleted
        name = 'sameFctName'
        filename = self.folderpath + name + '1.cc'

        self.genModel(name, filename)

        args = self.Args(filename)
        # add first function
        parser = Parser(args)
        parser.opch = self.opcheader
        parser.extend_header()

        inst1 = parser.instructions[-1]

        filename = self.folderpath + name + '3.cc'
        self.opc = 0x0a
        self.funct3 = 0x05
        self.ftype = 'R'
        funct7 = 0x00
        self.genModel(name, filename, funct7=funct7)

        args = self.Args(filename)
        parser3 = Parser(args)
        parser3.opch = self.opcheader
        parser3.extend_header()

        inst3 = parser3.instructions[-1]

        filename = self.folderpath + name + '2.cc'
        self.opc = 0x0a
        self.ftype = 'I'
        self.genModel(name, filename)

        args = self.Args(filename)
        parser2 = Parser(args)
        parser2.opch = self.opcheader
        parser2.extend_header()

        inst2 = parser2.instructions[-1]

        with open(self.opcheader, 'r') as fh:
            hcontent = fh.readlines()

        # check if first function is in but not second one
        self.assertTrue(inst1.match in hcontent)
        self.assertTrue(inst1.mask in hcontent)
        # match is the same
        self.assertFalse(inst2.match in hcontent)
        self.assertFalse(inst2.mask in hcontent)
        self.assertFalse(inst3.match in hcontent)
        self.assertFalse(inst3.mask in hcontent)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(verbosity=3).run(suite)
