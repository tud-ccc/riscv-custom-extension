import sys
import unittest

sys.path.append('..')
from modelparsing.exceptions import OpcodeError
from modelparsing.parser import Extensions
sys.path.remove('..')


class TestExtensions(unittest.TestCase):
    '''
    Tests for all functions in the class Extensions
    '''

    class Model:
        def __init__(self, name, form, opc, funct3, funct7=0xff):
            self._name = name
            self._form = form
            self._opc = opc
            self._funct3 = funct3
            self._funct7 = funct7

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

    def setUp(self):
        self.form = 'I'
        self.opc = 0x02
        self.funct3 = 0x00

    def testExtensionsInstructionsIType(self):
        name = 'itype'
        models = [self.Model(name, self.form, self.opc, self.funct3)]

        ext = Extensions(models)
        insts = ext.instructions

        self.assertEquals(len(insts), 1)

        self.assertEquals(insts[0].form, 'I')
        self.assertEquals(insts[0].mask, '#define MASK_ITYPE  0x707f\n')
        self.assertEquals(insts[0].maskname, 'MASK_ITYPE')
        self.assertEquals(insts[0].maskvalue, '0x707f')
        self.assertEquals(insts[0].match, '#define MATCH_ITYPE 0xb\n')
        self.assertEquals(insts[0].matchname, 'MATCH_ITYPE')
        self.assertEquals(insts[0].matchvalue, '0xb')
        self.assertEquals(insts[0].name, 'itype')
        self.assertEquals(insts[0].operands, 'd,s,j')
        self.assertEquals(insts[-1].form, 'I')
        self.assertEquals(insts[-1].mask, '#define MASK_ITYPE  0x707f\n')
        self.assertEquals(insts[-1].maskname, 'MASK_ITYPE')
        self.assertEquals(insts[-1].maskvalue, '0x707f')
        self.assertEquals(insts[-1].match, '#define MATCH_ITYPE 0xb\n')
        self.assertEquals(insts[-1].matchname, 'MATCH_ITYPE')
        self.assertEquals(insts[-1].matchvalue, '0xb')
        self.assertEquals(insts[-1].name, 'itype')
        self.assertEquals(insts[-1].operands, 'd,s,j')

    def testExtensionsInstructionsRType(self):
        name = 'rtype'
        self.form = 'R'
        funct7 = 0x02
        models = [self.Model(name, self.form, self.opc, self.funct3, funct7)]

        ext = Extensions(models)
        insts = ext.instructions

        self.assertEquals(len(insts), 1)

        self.assertEquals(insts[0].form, 'R')
        self.assertEquals(insts[0].mask, '#define MASK_RTYPE  0xfe00707f\n')
        self.assertEquals(insts[0].maskname, 'MASK_RTYPE')
        self.assertEquals(insts[0].maskvalue, '0xfe00707f')
        self.assertEquals(insts[0].match, '#define MATCH_RTYPE 0x400000b\n')
        self.assertEquals(insts[0].matchname, 'MATCH_RTYPE')
        self.assertEquals(insts[0].matchvalue, '0x400000b')
        self.assertEquals(insts[0].name, 'rtype')
        self.assertEquals(insts[0].operands, 'd,s,t')
        self.assertEquals(insts[-1].form, 'R')
        self.assertEquals(insts[-1].mask, '#define MASK_RTYPE  0xfe00707f\n')
        self.assertEquals(insts[-1].maskname, 'MASK_RTYPE')
        self.assertEquals(insts[-1].maskvalue, '0xfe00707f')
        self.assertEquals(insts[-1].match, '#define MATCH_RTYPE 0x400000b\n')
        self.assertEquals(insts[-1].matchname, 'MATCH_RTYPE')
        self.assertEquals(insts[-1].matchvalue, '0x400000b')
        self.assertEquals(insts[-1].name, 'rtype')
        self.assertEquals(insts[-1].operands, 'd,s,t')

    def testExtensionsInstructionsMultiple(self):
        name = 'itype'
        models = [self.Model(name, self.form, self.opc, self.funct3)]

        name = 'rtype'
        self.form = 'R'
        self.funct3 = 0x01
        funct7 = 0x02
        models.append(self.Model(name,
                                 self.form,
                                 self.opc,
                                 self.funct3,
                                 funct7))

        ext = Extensions(models)
        insts = ext.instructions

        self.assertEquals(len(insts), 2)

        self.assertEquals(insts[0].form, 'I')
        self.assertEquals(insts[0].mask, '#define MASK_ITYPE  0x707f\n')
        self.assertEquals(insts[0].maskname, 'MASK_ITYPE')
        self.assertEquals(insts[0].maskvalue, '0x707f')
        self.assertEquals(insts[0].match, '#define MATCH_ITYPE 0xb\n')
        self.assertEquals(insts[0].matchname, 'MATCH_ITYPE')
        self.assertEquals(insts[0].matchvalue, '0xb')
        self.assertEquals(insts[0].name, 'itype')
        self.assertEquals(insts[0].operands, 'd,s,j')
        self.assertEquals(insts[-2].form, 'I')
        self.assertEquals(insts[-2].mask, '#define MASK_ITYPE  0x707f\n')
        self.assertEquals(insts[-2].maskname, 'MASK_ITYPE')
        self.assertEquals(insts[-2].maskvalue, '0x707f')
        self.assertEquals(insts[-2].match, '#define MATCH_ITYPE 0xb\n')
        self.assertEquals(insts[-2].matchname, 'MATCH_ITYPE')
        self.assertEquals(insts[-2].matchvalue, '0xb')
        self.assertEquals(insts[-2].name, 'itype')
        self.assertEquals(insts[-2].operands, 'd,s,j')
        self.assertEquals(insts[1].form, 'R')
        self.assertEquals(insts[1].mask, '#define MASK_RTYPE  0xfe00707f\n')
        self.assertEquals(insts[1].maskname, 'MASK_RTYPE')
        self.assertEquals(insts[1].maskvalue, '0xfe00707f')
        self.assertEquals(insts[1].match, '#define MATCH_RTYPE 0x400100b\n')
        self.assertEquals(insts[1].matchname, 'MATCH_RTYPE')
        self.assertEquals(insts[1].matchvalue, '0x400100b')
        self.assertEquals(insts[1].name, 'rtype')
        self.assertEquals(insts[1].operands, 'd,s,t')
        self.assertEquals(insts[-1].form, 'R')
        self.assertEquals(insts[-1].mask, '#define MASK_RTYPE  0xfe00707f\n')
        self.assertEquals(insts[-1].maskname, 'MASK_RTYPE')
        self.assertEquals(insts[-1].maskvalue, '0xfe00707f')
        self.assertEquals(insts[-1].match, '#define MATCH_RTYPE 0x400100b\n')
        self.assertEquals(insts[-1].matchname, 'MATCH_RTYPE')
        self.assertEquals(insts[-1].matchvalue, '0x400100b')
        self.assertEquals(insts[-1].name, 'rtype')
        self.assertEquals(insts[-1].operands, 'd,s,t')
