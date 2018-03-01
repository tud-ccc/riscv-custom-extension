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

        self.assertEquals(len(ext.models), 1)

        insts = ext.instructions

        self.assertEquals(len(insts), 1)

        self.assertEquals(insts[0].form, 'I')
        self.assertEquals(insts[0].mask, '#define MASK_ITYPE  0x707f\n')
        self.assertEquals(insts[0].maskname, 'MASK_ITYPE')
        self.assertEquals(insts[0].maskvalue, 0x707f)
        self.assertEquals(insts[0].match, '#define MATCH_ITYPE 0xb\n')
        self.assertEquals(insts[0].matchname, 'MATCH_ITYPE')
        self.assertEquals(insts[0].matchvalue, 0xb)
        self.assertEquals(insts[0].name, 'itype')
        self.assertEquals(insts[0].operands, 'd,s,j')
        self.assertEquals(insts[-1].form, 'I')
        self.assertEquals(insts[-1].mask, '#define MASK_ITYPE  0x707f\n')
        self.assertEquals(insts[-1].maskname, 'MASK_ITYPE')
        self.assertEquals(insts[-1].maskvalue, 0x707f)
        self.assertEquals(insts[-1].match, '#define MATCH_ITYPE 0xb\n')
        self.assertEquals(insts[-1].matchname, 'MATCH_ITYPE')
        self.assertEquals(insts[-1].matchvalue, 0xb)
        self.assertEquals(insts[-1].name, 'itype')
        self.assertEquals(insts[-1].operands, 'd,s,j')

    def testExtensionsInstructionsRType(self):
        name = 'rtype'
        self.form = 'R'
        funct7 = 0x02
        models = [self.Model(name, self.form, self.opc, self.funct3, funct7)]

        ext = Extensions(models)

        self.assertEquals(len(ext.models), 1)

        insts = ext.instructions

        self.assertEquals(len(insts), 1)

        self.assertEquals(insts[0].form, 'R')
        self.assertEquals(insts[0].mask, '#define MASK_RTYPE  0xfe00707f\n')
        self.assertEquals(insts[0].maskname, 'MASK_RTYPE')
        self.assertEquals(insts[0].maskvalue, 0xfe00707f)
        self.assertEquals(insts[0].match, '#define MATCH_RTYPE 0x400000b\n')
        self.assertEquals(insts[0].matchname, 'MATCH_RTYPE')
        self.assertEquals(insts[0].matchvalue, 0x400000b)
        self.assertEquals(insts[0].name, 'rtype')
        self.assertEquals(insts[0].operands, 'd,s,t')
        self.assertEquals(insts[-1].form, 'R')
        self.assertEquals(insts[-1].mask, '#define MASK_RTYPE  0xfe00707f\n')
        self.assertEquals(insts[-1].maskname, 'MASK_RTYPE')
        self.assertEquals(insts[-1].maskvalue, 0xfe00707f)
        self.assertEquals(insts[-1].match, '#define MATCH_RTYPE 0x400000b\n')
        self.assertEquals(insts[-1].matchname, 'MATCH_RTYPE')
        self.assertEquals(insts[-1].matchvalue, 0x400000b)
        self.assertEquals(insts[-1].name, 'rtype')
        self.assertEquals(insts[-1].operands, 'd,s,t')

    def testExtensionsInstructionsMultipleITypes(self):
        name = 'itype'
        models = [self.Model(name, self.form, self.opc, self.funct3)]

        name = 'itype0'
        self.funct3 = 0x01
        models.append(self.Model(name, self.form, self.opc, self.funct3))

        ext = Extensions(models)

        self.assertEquals(len(ext.models), 2)

        insts = ext.instructions

        self.assertEquals(len(insts), 2)

        self.assertEquals(insts[0].form, 'I')
        self.assertEquals(insts[0].mask, '#define MASK_ITYPE  0x707f\n')
        self.assertEquals(insts[0].maskname, 'MASK_ITYPE')
        self.assertEquals(insts[0].maskvalue, 0x707f)
        self.assertEquals(insts[0].match, '#define MATCH_ITYPE 0xb\n')
        self.assertEquals(insts[0].matchname, 'MATCH_ITYPE')
        self.assertEquals(insts[0].matchvalue, 0xb)
        self.assertEquals(insts[0].name, 'itype')
        self.assertEquals(insts[0].operands, 'd,s,j')
        self.assertEquals(insts[-2].form, 'I')
        self.assertEquals(insts[-2].mask, '#define MASK_ITYPE  0x707f\n')
        self.assertEquals(insts[-2].maskname, 'MASK_ITYPE')
        self.assertEquals(insts[-2].maskvalue, 0x707f)
        self.assertEquals(insts[-2].match, '#define MATCH_ITYPE 0xb\n')
        self.assertEquals(insts[-2].matchname, 'MATCH_ITYPE')
        self.assertEquals(insts[-2].matchvalue, 0xb)
        self.assertEquals(insts[-2].name, 'itype')
        self.assertEquals(insts[-2].operands, 'd,s,j')
        self.assertEquals(insts[1].form, 'I')
        self.assertEquals(insts[1].mask, '#define MASK_ITYPE0  0x707f\n')
        self.assertEquals(insts[1].maskname, 'MASK_ITYPE0')
        self.assertEquals(insts[1].maskvalue, 0x707f)
        self.assertEquals(insts[1].match, '#define MATCH_ITYPE0 0x100b\n')
        self.assertEquals(insts[1].matchname, 'MATCH_ITYPE0')
        self.assertEquals(insts[1].matchvalue, 0x100b)
        self.assertEquals(insts[1].name, 'itype0')
        self.assertEquals(insts[1].operands, 'd,s,j')
        self.assertEquals(insts[-1].form, 'I')
        self.assertEquals(insts[-1].mask, '#define MASK_ITYPE0  0x707f\n')
        self.assertEquals(insts[-1].maskname, 'MASK_ITYPE0')
        self.assertEquals(insts[-1].maskvalue, 0x707f)
        self.assertEquals(insts[-1].match, '#define MATCH_ITYPE0 0x100b\n')
        self.assertEquals(insts[-1].matchname, 'MATCH_ITYPE0')
        self.assertEquals(insts[-1].matchvalue, 0x100b)
        self.assertEquals(insts[-1].name, 'itype0')
        self.assertEquals(insts[-1].operands, 'd,s,j')

    def testExtensionsInstructionsMultipleRTypes(self):
        models = []

        name = 'rtype0'
        self.form = 'R'
        funct7 = 0x00
        models.append(self.Model(name,
                                 self.form,
                                 self.opc,
                                 self.funct3,
                                 funct7))

        name = 'rtype1'
        funct7 = 0x01
        models.append(self.Model(name,
                                 self.form,
                                 self.opc,
                                 self.funct3,
                                 funct7))

        name = 'rtype2'
        self.funct3 = 0x01
        funct7 = 0x00
        models.append(self.Model(name,
                                 self.form,
                                 self.opc,
                                 self.funct3,
                                 funct7))

        ext = Extensions(models)

        self.assertEquals(len(ext.models), 3)

        insts = ext.instructions

        self.assertEquals(len(insts), 3)

        self.assertEquals(insts[0].form, 'R')
        self.assertEquals(insts[0].mask, '#define MASK_RTYPE0  0xfe00707f\n')
        self.assertEquals(insts[0].maskname, 'MASK_RTYPE0')
        self.assertEquals(insts[0].maskvalue, 0xfe00707f)
        self.assertEquals(insts[0].match, '#define MATCH_RTYPE0 0xb\n')
        self.assertEquals(insts[0].matchname, 'MATCH_RTYPE0')
        self.assertEquals(insts[0].matchvalue, 0xb)
        self.assertEquals(insts[0].name, 'rtype0')
        self.assertEquals(insts[0].operands, 'd,s,t')
        self.assertEquals(insts[-3].form, 'R')
        self.assertEquals(insts[-3].mask, '#define MASK_RTYPE0  0xfe00707f\n')
        self.assertEquals(insts[-3].maskname, 'MASK_RTYPE0')
        self.assertEquals(insts[-3].maskvalue, 0xfe00707f)
        self.assertEquals(insts[-3].match, '#define MATCH_RTYPE0 0xb\n')
        self.assertEquals(insts[-3].matchname, 'MATCH_RTYPE0')
        self.assertEquals(insts[-3].matchvalue, 0xb)
        self.assertEquals(insts[-3].name, 'rtype0')
        self.assertEquals(insts[-3].operands, 'd,s,t')
        self.assertEquals(insts[1].form, 'R')
        self.assertEquals(insts[1].mask, '#define MASK_RTYPE1  0xfe00707f\n')
        self.assertEquals(insts[1].maskname, 'MASK_RTYPE1')
        self.assertEquals(insts[1].maskvalue, 0xfe00707f)
        self.assertEquals(insts[1].match, '#define MATCH_RTYPE1 0x200000b\n')
        self.assertEquals(insts[1].matchname, 'MATCH_RTYPE1')
        self.assertEquals(insts[1].matchvalue, 0x200000b)
        self.assertEquals(insts[1].name, 'rtype1')
        self.assertEquals(insts[1].operands, 'd,s,t')
        self.assertEquals(insts[-2].form, 'R')
        self.assertEquals(insts[-2].mask, '#define MASK_RTYPE1  0xfe00707f\n')
        self.assertEquals(insts[-2].maskname, 'MASK_RTYPE1')
        self.assertEquals(insts[-2].maskvalue, 0xfe00707f)
        self.assertEquals(insts[-2].match, '#define MATCH_RTYPE1 0x200000b\n')
        self.assertEquals(insts[-2].matchname, 'MATCH_RTYPE1')
        self.assertEquals(insts[-2].matchvalue, 0x200000b)
        self.assertEquals(insts[-2].name, 'rtype1')
        self.assertEquals(insts[-2].operands, 'd,s,t')
        self.assertEquals(insts[2].form, 'R')
        self.assertEquals(insts[2].mask, '#define MASK_RTYPE2  0xfe00707f\n')
        self.assertEquals(insts[2].maskname, 'MASK_RTYPE2')
        self.assertEquals(insts[2].maskvalue, 0xfe00707f)
        self.assertEquals(insts[2].match, '#define MATCH_RTYPE2 0x100b\n')
        self.assertEquals(insts[2].matchname, 'MATCH_RTYPE2')
        self.assertEquals(insts[2].matchvalue, 0x100b)
        self.assertEquals(insts[2].name, 'rtype2')
        self.assertEquals(insts[2].operands, 'd,s,t')
        self.assertEquals(insts[-1].form, 'R')
        self.assertEquals(insts[-1].mask, '#define MASK_RTYPE2  0xfe00707f\n')
        self.assertEquals(insts[-1].maskname, 'MASK_RTYPE2')
        self.assertEquals(insts[-1].maskvalue, 0xfe00707f)
        self.assertEquals(insts[-1].match, '#define MATCH_RTYPE2 0x100b\n')
        self.assertEquals(insts[-1].matchname, 'MATCH_RTYPE2')
        self.assertEquals(insts[-1].matchvalue, 0x100b)
        self.assertEquals(insts[-1].name, 'rtype2')
        self.assertEquals(insts[-1].operands, 'd,s,t')

    def testExtensionsInstructionsMultipleIRTypes(self):
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

        self.assertEquals(len(ext.models), 2)

        insts = ext.instructions

        self.assertEquals(len(insts), 2)

        self.assertEquals(insts[0].form, 'I')
        self.assertEquals(insts[0].mask, '#define MASK_ITYPE  0x707f\n')
        self.assertEquals(insts[0].maskname, 'MASK_ITYPE')
        self.assertEquals(insts[0].maskvalue, 0x707f)
        self.assertEquals(insts[0].match, '#define MATCH_ITYPE 0xb\n')
        self.assertEquals(insts[0].matchname, 'MATCH_ITYPE')
        self.assertEquals(insts[0].matchvalue, 0xb)
        self.assertEquals(insts[0].name, 'itype')
        self.assertEquals(insts[0].operands, 'd,s,j')
        self.assertEquals(insts[-2].form, 'I')
        self.assertEquals(insts[-2].mask, '#define MASK_ITYPE  0x707f\n')
        self.assertEquals(insts[-2].maskname, 'MASK_ITYPE')
        self.assertEquals(insts[-2].maskvalue, 0x707f)
        self.assertEquals(insts[-2].match, '#define MATCH_ITYPE 0xb\n')
        self.assertEquals(insts[-2].matchname, 'MATCH_ITYPE')
        self.assertEquals(insts[-2].matchvalue, 0xb)
        self.assertEquals(insts[-2].name, 'itype')
        self.assertEquals(insts[-2].operands, 'd,s,j')
        self.assertEquals(insts[1].form, 'R')
        self.assertEquals(insts[1].mask, '#define MASK_RTYPE  0xfe00707f\n')
        self.assertEquals(insts[1].maskname, 'MASK_RTYPE')
        self.assertEquals(insts[1].maskvalue, 0xfe00707f)
        self.assertEquals(insts[1].match, '#define MATCH_RTYPE 0x400100b\n')
        self.assertEquals(insts[1].matchname, 'MATCH_RTYPE')
        self.assertEquals(insts[1].matchvalue, 0x400100b)
        self.assertEquals(insts[1].name, 'rtype')
        self.assertEquals(insts[1].operands, 'd,s,t')
        self.assertEquals(insts[-1].form, 'R')
        self.assertEquals(insts[-1].mask, '#define MASK_RTYPE  0xfe00707f\n')
        self.assertEquals(insts[-1].maskname, 'MASK_RTYPE')
        self.assertEquals(insts[-1].maskvalue, 0xfe00707f)
        self.assertEquals(insts[-1].match, '#define MATCH_RTYPE 0x400100b\n')
        self.assertEquals(insts[-1].matchname, 'MATCH_RTYPE')
        self.assertEquals(insts[-1].matchvalue, 0x400100b)
        self.assertEquals(insts[-1].name, 'rtype')
        self.assertEquals(insts[-1].operands, 'd,s,t')

    def testExtensionsInstructionsMultipleRITypes(self):
        name = 'rtype'
        self.form = 'R'
        self.funct3 = 0x01
        funct7 = 0x02
        models = [self.Model(name,
                             self.form,
                             self.opc,
                             self.funct3,
                             funct7)]

        name = 'itype'
        self.form = 'I'
        self.funct3 = 0x00
        models.append(self.Model(name, self.form, self.opc, self.funct3))

        ext = Extensions(models)

        self.assertEquals(len(ext.models), 2)

        insts = ext.instructions

        self.assertEquals(len(insts), 2)

        self.assertEquals(insts[1].form, 'I')
        self.assertEquals(insts[1].mask, '#define MASK_ITYPE  0x707f\n')
        self.assertEquals(insts[1].maskname, 'MASK_ITYPE')
        self.assertEquals(insts[1].maskvalue, 0x707f)
        self.assertEquals(insts[1].match, '#define MATCH_ITYPE 0xb\n')
        self.assertEquals(insts[1].matchname, 'MATCH_ITYPE')
        self.assertEquals(insts[1].matchvalue, 0xb)
        self.assertEquals(insts[1].name, 'itype')
        self.assertEquals(insts[1].operands, 'd,s,j')
        self.assertEquals(insts[-1].form, 'I')
        self.assertEquals(insts[-1].mask, '#define MASK_ITYPE  0x707f\n')
        self.assertEquals(insts[-1].maskname, 'MASK_ITYPE')
        self.assertEquals(insts[-1].maskvalue, 0x707f)
        self.assertEquals(insts[-1].match, '#define MATCH_ITYPE 0xb\n')
        self.assertEquals(insts[-1].matchname, 'MATCH_ITYPE')
        self.assertEquals(insts[-1].matchvalue, 0xb)
        self.assertEquals(insts[-1].name, 'itype')
        self.assertEquals(insts[-1].operands, 'd,s,j')
        self.assertEquals(insts[0].form, 'R')
        self.assertEquals(insts[0].mask, '#define MASK_RTYPE  0xfe00707f\n')
        self.assertEquals(insts[0].maskname, 'MASK_RTYPE')
        self.assertEquals(insts[0].maskvalue, 0xfe00707f)
        self.assertEquals(insts[0].match, '#define MATCH_RTYPE 0x400100b\n')
        self.assertEquals(insts[0].matchname, 'MATCH_RTYPE')
        self.assertEquals(insts[0].matchvalue, 0x400100b)
        self.assertEquals(insts[0].name, 'rtype')
        self.assertEquals(insts[0].operands, 'd,s,t')
        self.assertEquals(insts[-2].form, 'R')
        self.assertEquals(insts[-2].mask, '#define MASK_RTYPE  0xfe00707f\n')
        self.assertEquals(insts[-2].maskname, 'MASK_RTYPE')
        self.assertEquals(insts[-2].maskvalue, 0xfe00707f)
        self.assertEquals(insts[-2].match, '#define MATCH_RTYPE 0x400100b\n')
        self.assertEquals(insts[-2].matchname, 'MATCH_RTYPE')
        self.assertEquals(insts[-2].matchvalue, 0x400100b)
        self.assertEquals(insts[-2].name, 'rtype')
        self.assertEquals(insts[-2].operands, 'd,s,t')

    def testExtensionsInstructionsOverlappingIIType(self):
        name = 'itype'
        models = [self.Model(name, self.form, self.opc, self.funct3)]

        name = 'itype0'
        models.append(self.Model(name, self.form, self.opc, self.funct3))

        with self.assertRaises(OpcodeError):
            Extensions(models)

    def testExtensionsInstructionsOverlappingRRType(self):
        name = 'rtype'
        self.form = 'R'
        funct7 = 0x00
        models = [self.Model(name, self.form, self.opc, self.funct3, funct7)]

        name = 'rtype0'
        models.append(self.Model(name, self.form,
                                 self.opc, self.funct3, funct7))

        with self.assertRaises(OpcodeError):
            Extensions(models)

    def testExtensionsInstructionsOverlappingIRType(self):
        name = 'itype'
        models = [self.Model(name, self.form, self.opc, self.funct3)]

        name = 'rtype'
        self.form = 'R'
        funct7 = 0x03
        models.append(self.Model(name,
                                 self.form,
                                 self.opc,
                                 self.funct3,
                                 funct7))

        with self.assertRaises(OpcodeError):
            Extensions(models)

    def testExtensionsInstructionsOverlappingRIType(self):
        name = 'rtype'
        self.form = 'R'
        funct7 = 0x03
        models = [self.Model(name, self.form, self.opc, self.funct3, funct7)]

        name = 'itype'
        self.form = 'I'
        models.append(self.Model(name, self.form, self.opc, self.funct3))

        with self.assertRaises(OpcodeError):
            Extensions(models)

    def testExtensionsHeader(self):
        name = 'itype'
        models = [self.Model(name, self.form, self.opc, self.funct3)]

        ext = Extensions(models)

        self.assertEquals(len(ext.models), 1)

        header_expected = '''/* Automatically generated by parse-opcodes.  */
#ifndef RISCV_CUSTOM_ENCODING_H
#define RISCV_CUSTOM_ENCODING_H
#define MATCH_ITYPE 0xb
#define MASK_ITYPE  0x707f
#define CSR_FFLAGS 0x1
#define CSR_FRM 0x2
#define CSR_FCSR 0x3
#define CSR_CYCLE 0xc00
#define CSR_TIME 0xc01
#define CSR_INSTRET 0xc02
#define CSR_HPMCOUNTER3 0xc03
#define CSR_HPMCOUNTER4 0xc04
#define CSR_HPMCOUNTER5 0xc05
#define CSR_HPMCOUNTER6 0xc06
#define CSR_HPMCOUNTER7 0xc07
#define CSR_HPMCOUNTER8 0xc08
#define CSR_HPMCOUNTER9 0xc09
#define CSR_HPMCOUNTER10 0xc0a
#define CSR_HPMCOUNTER11 0xc0b
#define CSR_HPMCOUNTER12 0xc0c
#define CSR_HPMCOUNTER13 0xc0d
#define CSR_HPMCOUNTER14 0xc0e
#define CSR_HPMCOUNTER15 0xc0f
#define CSR_HPMCOUNTER16 0xc10
#define CSR_HPMCOUNTER17 0xc11
#define CSR_HPMCOUNTER18 0xc12
#define CSR_HPMCOUNTER19 0xc13
#define CSR_HPMCOUNTER20 0xc14
#define CSR_HPMCOUNTER21 0xc15
#define CSR_HPMCOUNTER22 0xc16
#define CSR_HPMCOUNTER23 0xc17
#define CSR_HPMCOUNTER24 0xc18
#define CSR_HPMCOUNTER25 0xc19
#define CSR_HPMCOUNTER26 0xc1a
#define CSR_HPMCOUNTER27 0xc1b
#define CSR_HPMCOUNTER28 0xc1c
#define CSR_HPMCOUNTER29 0xc1d
#define CSR_HPMCOUNTER30 0xc1e
#define CSR_HPMCOUNTER31 0xc1f
#define CSR_SSTATUS 0x100
#define CSR_SIE 0x104
#define CSR_STVEC 0x105
#define CSR_SCOUNTEREN 0x106
#define CSR_SSCRATCH 0x140
#define CSR_SEPC 0x141
#define CSR_SCAUSE 0x142
#define CSR_STVAL 0x143
#define CSR_SIP 0x144
#define CSR_SATP 0x180
#define CSR_MSTATUS 0x300
#define CSR_MISA 0x301
#define CSR_MEDELEG 0x302
#define CSR_MIDELEG 0x303
#define CSR_MIE 0x304
#define CSR_MTVEC 0x305
#define CSR_MCOUNTEREN 0x306
#define CSR_MSCRATCH 0x340
#define CSR_MEPC 0x341
#define CSR_MCAUSE 0x342
#define CSR_MTVAL 0x343
#define CSR_MIP 0x344
#define CSR_PMPCFG0 0x3a0
#define CSR_PMPCFG1 0x3a1
#define CSR_PMPCFG2 0x3a2
#define CSR_PMPCFG3 0x3a3
#define CSR_PMPADDR0 0x3b0
#define CSR_PMPADDR1 0x3b1
#define CSR_PMPADDR2 0x3b2
#define CSR_PMPADDR3 0x3b3
#define CSR_PMPADDR4 0x3b4
#define CSR_PMPADDR5 0x3b5
#define CSR_PMPADDR6 0x3b6
#define CSR_PMPADDR7 0x3b7
#define CSR_PMPADDR8 0x3b8
#define CSR_PMPADDR9 0x3b9
#define CSR_PMPADDR10 0x3ba
#define CSR_PMPADDR11 0x3bb
#define CSR_PMPADDR12 0x3bc
#define CSR_PMPADDR13 0x3bd
#define CSR_PMPADDR14 0x3be
#define CSR_PMPADDR15 0x3bf
#define CSR_TSELECT 0x7a0
#define CSR_TDATA1 0x7a1
#define CSR_TDATA2 0x7a2
#define CSR_TDATA3 0x7a3
#define CSR_DCSR 0x7b0
#define CSR_DPC 0x7b1
#define CSR_DSCRATCH 0x7b2
#define CSR_MCYCLE 0xb00
#define CSR_MINSTRET 0xb02
#define CSR_MHPMCOUNTER3 0xb03
#define CSR_MHPMCOUNTER4 0xb04
#define CSR_MHPMCOUNTER5 0xb05
#define CSR_MHPMCOUNTER6 0xb06
#define CSR_MHPMCOUNTER7 0xb07
#define CSR_MHPMCOUNTER8 0xb08
#define CSR_MHPMCOUNTER9 0xb09
#define CSR_MHPMCOUNTER10 0xb0a
#define CSR_MHPMCOUNTER11 0xb0b
#define CSR_MHPMCOUNTER12 0xb0c
#define CSR_MHPMCOUNTER13 0xb0d
#define CSR_MHPMCOUNTER14 0xb0e
#define CSR_MHPMCOUNTER15 0xb0f
#define CSR_MHPMCOUNTER16 0xb10
#define CSR_MHPMCOUNTER17 0xb11
#define CSR_MHPMCOUNTER18 0xb12
#define CSR_MHPMCOUNTER19 0xb13
#define CSR_MHPMCOUNTER20 0xb14
#define CSR_MHPMCOUNTER21 0xb15
#define CSR_MHPMCOUNTER22 0xb16
#define CSR_MHPMCOUNTER23 0xb17
#define CSR_MHPMCOUNTER24 0xb18
#define CSR_MHPMCOUNTER25 0xb19
#define CSR_MHPMCOUNTER26 0xb1a
#define CSR_MHPMCOUNTER27 0xb1b
#define CSR_MHPMCOUNTER28 0xb1c
#define CSR_MHPMCOUNTER29 0xb1d
#define CSR_MHPMCOUNTER30 0xb1e
#define CSR_MHPMCOUNTER31 0xb1f
#define CSR_MHPMEVENT3 0x323
#define CSR_MHPMEVENT4 0x324
#define CSR_MHPMEVENT5 0x325
#define CSR_MHPMEVENT6 0x326
#define CSR_MHPMEVENT7 0x327
#define CSR_MHPMEVENT8 0x328
#define CSR_MHPMEVENT9 0x329
#define CSR_MHPMEVENT10 0x32a
#define CSR_MHPMEVENT11 0x32b
#define CSR_MHPMEVENT12 0x32c
#define CSR_MHPMEVENT13 0x32d
#define CSR_MHPMEVENT14 0x32e
#define CSR_MHPMEVENT15 0x32f
#define CSR_MHPMEVENT16 0x330
#define CSR_MHPMEVENT17 0x331
#define CSR_MHPMEVENT18 0x332
#define CSR_MHPMEVENT19 0x333
#define CSR_MHPMEVENT20 0x334
#define CSR_MHPMEVENT21 0x335
#define CSR_MHPMEVENT22 0x336
#define CSR_MHPMEVENT23 0x337
#define CSR_MHPMEVENT24 0x338
#define CSR_MHPMEVENT25 0x339
#define CSR_MHPMEVENT26 0x33a
#define CSR_MHPMEVENT27 0x33b
#define CSR_MHPMEVENT28 0x33c
#define CSR_MHPMEVENT29 0x33d
#define CSR_MHPMEVENT30 0x33e
#define CSR_MHPMEVENT31 0x33f
#define CSR_MVENDORID 0xf11
#define CSR_MARCHID 0xf12
#define CSR_MIMPID 0xf13
#define CSR_MHARTID 0xf14
#define CSR_CYCLEH 0xc80
#define CSR_TIMEH 0xc81
#define CSR_INSTRETH 0xc82
#define CSR_HPMCOUNTER3H 0xc83
#define CSR_HPMCOUNTER4H 0xc84
#define CSR_HPMCOUNTER5H 0xc85
#define CSR_HPMCOUNTER6H 0xc86
#define CSR_HPMCOUNTER7H 0xc87
#define CSR_HPMCOUNTER8H 0xc88
#define CSR_HPMCOUNTER9H 0xc89
#define CSR_HPMCOUNTER10H 0xc8a
#define CSR_HPMCOUNTER11H 0xc8b
#define CSR_HPMCOUNTER12H 0xc8c
#define CSR_HPMCOUNTER13H 0xc8d
#define CSR_HPMCOUNTER14H 0xc8e
#define CSR_HPMCOUNTER15H 0xc8f
#define CSR_HPMCOUNTER16H 0xc90
#define CSR_HPMCOUNTER17H 0xc91
#define CSR_HPMCOUNTER18H 0xc92
#define CSR_HPMCOUNTER19H 0xc93
#define CSR_HPMCOUNTER20H 0xc94
#define CSR_HPMCOUNTER21H 0xc95
#define CSR_HPMCOUNTER22H 0xc96
#define CSR_HPMCOUNTER23H 0xc97
#define CSR_HPMCOUNTER24H 0xc98
#define CSR_HPMCOUNTER25H 0xc99
#define CSR_HPMCOUNTER26H 0xc9a
#define CSR_HPMCOUNTER27H 0xc9b
#define CSR_HPMCOUNTER28H 0xc9c
#define CSR_HPMCOUNTER29H 0xc9d
#define CSR_HPMCOUNTER30H 0xc9e
#define CSR_HPMCOUNTER31H 0xc9f
#define CSR_MCYCLEH 0xb80
#define CSR_MINSTRETH 0xb82
#define CSR_MHPMCOUNTER3H 0xb83
#define CSR_MHPMCOUNTER4H 0xb84
#define CSR_MHPMCOUNTER5H 0xb85
#define CSR_MHPMCOUNTER6H 0xb86
#define CSR_MHPMCOUNTER7H 0xb87
#define CSR_MHPMCOUNTER8H 0xb88
#define CSR_MHPMCOUNTER9H 0xb89
#define CSR_MHPMCOUNTER10H 0xb8a
#define CSR_MHPMCOUNTER11H 0xb8b
#define CSR_MHPMCOUNTER12H 0xb8c
#define CSR_MHPMCOUNTER13H 0xb8d
#define CSR_MHPMCOUNTER14H 0xb8e
#define CSR_MHPMCOUNTER15H 0xb8f
#define CSR_MHPMCOUNTER16H 0xb90
#define CSR_MHPMCOUNTER17H 0xb91
#define CSR_MHPMCOUNTER18H 0xb92
#define CSR_MHPMCOUNTER19H 0xb93
#define CSR_MHPMCOUNTER20H 0xb94
#define CSR_MHPMCOUNTER21H 0xb95
#define CSR_MHPMCOUNTER22H 0xb96
#define CSR_MHPMCOUNTER23H 0xb97
#define CSR_MHPMCOUNTER24H 0xb98
#define CSR_MHPMCOUNTER25H 0xb99
#define CSR_MHPMCOUNTER26H 0xb9a
#define CSR_MHPMCOUNTER27H 0xb9b
#define CSR_MHPMCOUNTER28H 0xb9c
#define CSR_MHPMCOUNTER29H 0xb9d
#define CSR_MHPMCOUNTER30H 0xb9e
#define CSR_MHPMCOUNTER31H 0xb9f
#define CAUSE_MISALIGNED_FETCH 0x0
#define CAUSE_FETCH_ACCESS 0x1
#define CAUSE_ILLEGAL_INSTRUCTION 0x2
#define CAUSE_BREAKPOINT 0x3
#define CAUSE_MISALIGNED_LOAD 0x4
#define CAUSE_LOAD_ACCESS 0x5
#define CAUSE_MISALIGNED_STORE 0x6
#define CAUSE_STORE_ACCESS 0x7
#define CAUSE_USER_ECALL 0x8
#define CAUSE_SUPERVISOR_ECALL 0x9
#define CAUSE_HYPERVISOR_ECALL 0xa
#define CAUSE_MACHINE_ECALL 0xb
#define CAUSE_FETCH_PAGE_FAULT 0xc
#define CAUSE_LOAD_PAGE_FAULT 0xd
#define CAUSE_STORE_PAGE_FAULT 0xf
#endif
#ifdef DECLARE_INSN
DECLARE_INSN(itype, MATCH_ITYPE, MASK_ITYPE)
#endif
#ifdef DECLARE_CSR
DECLARE_CSR(fflags, CSR_FFLAGS)
DECLARE_CSR(frm, CSR_FRM)
DECLARE_CSR(fcsr, CSR_FCSR)
DECLARE_CSR(cycle, CSR_CYCLE)
DECLARE_CSR(time, CSR_TIME)
DECLARE_CSR(instret, CSR_INSTRET)
DECLARE_CSR(hpmcounter3, CSR_HPMCOUNTER3)
DECLARE_CSR(hpmcounter4, CSR_HPMCOUNTER4)
DECLARE_CSR(hpmcounter5, CSR_HPMCOUNTER5)
DECLARE_CSR(hpmcounter6, CSR_HPMCOUNTER6)
DECLARE_CSR(hpmcounter7, CSR_HPMCOUNTER7)
DECLARE_CSR(hpmcounter8, CSR_HPMCOUNTER8)
DECLARE_CSR(hpmcounter9, CSR_HPMCOUNTER9)
DECLARE_CSR(hpmcounter10, CSR_HPMCOUNTER10)
DECLARE_CSR(hpmcounter11, CSR_HPMCOUNTER11)
DECLARE_CSR(hpmcounter12, CSR_HPMCOUNTER12)
DECLARE_CSR(hpmcounter13, CSR_HPMCOUNTER13)
DECLARE_CSR(hpmcounter14, CSR_HPMCOUNTER14)
DECLARE_CSR(hpmcounter15, CSR_HPMCOUNTER15)
DECLARE_CSR(hpmcounter16, CSR_HPMCOUNTER16)
DECLARE_CSR(hpmcounter17, CSR_HPMCOUNTER17)
DECLARE_CSR(hpmcounter18, CSR_HPMCOUNTER18)
DECLARE_CSR(hpmcounter19, CSR_HPMCOUNTER19)
DECLARE_CSR(hpmcounter20, CSR_HPMCOUNTER20)
DECLARE_CSR(hpmcounter21, CSR_HPMCOUNTER21)
DECLARE_CSR(hpmcounter22, CSR_HPMCOUNTER22)
DECLARE_CSR(hpmcounter23, CSR_HPMCOUNTER23)
DECLARE_CSR(hpmcounter24, CSR_HPMCOUNTER24)
DECLARE_CSR(hpmcounter25, CSR_HPMCOUNTER25)
DECLARE_CSR(hpmcounter26, CSR_HPMCOUNTER26)
DECLARE_CSR(hpmcounter27, CSR_HPMCOUNTER27)
DECLARE_CSR(hpmcounter28, CSR_HPMCOUNTER28)
DECLARE_CSR(hpmcounter29, CSR_HPMCOUNTER29)
DECLARE_CSR(hpmcounter30, CSR_HPMCOUNTER30)
DECLARE_CSR(hpmcounter31, CSR_HPMCOUNTER31)
DECLARE_CSR(sstatus, CSR_SSTATUS)
DECLARE_CSR(sie, CSR_SIE)
DECLARE_CSR(stvec, CSR_STVEC)
DECLARE_CSR(scounteren, CSR_SCOUNTEREN)
DECLARE_CSR(sscratch, CSR_SSCRATCH)
DECLARE_CSR(sepc, CSR_SEPC)
DECLARE_CSR(scause, CSR_SCAUSE)
DECLARE_CSR(stval, CSR_STVAL)
DECLARE_CSR(sip, CSR_SIP)
DECLARE_CSR(satp, CSR_SATP)
DECLARE_CSR(mstatus, CSR_MSTATUS)
DECLARE_CSR(misa, CSR_MISA)
DECLARE_CSR(medeleg, CSR_MEDELEG)
DECLARE_CSR(mideleg, CSR_MIDELEG)
DECLARE_CSR(mie, CSR_MIE)
DECLARE_CSR(mtvec, CSR_MTVEC)
DECLARE_CSR(mcounteren, CSR_MCOUNTEREN)
DECLARE_CSR(mscratch, CSR_MSCRATCH)
DECLARE_CSR(mepc, CSR_MEPC)
DECLARE_CSR(mcause, CSR_MCAUSE)
DECLARE_CSR(mtval, CSR_MTVAL)
DECLARE_CSR(mip, CSR_MIP)
DECLARE_CSR(pmpcfg0, CSR_PMPCFG0)
DECLARE_CSR(pmpcfg1, CSR_PMPCFG1)
DECLARE_CSR(pmpcfg2, CSR_PMPCFG2)
DECLARE_CSR(pmpcfg3, CSR_PMPCFG3)
DECLARE_CSR(pmpaddr0, CSR_PMPADDR0)
DECLARE_CSR(pmpaddr1, CSR_PMPADDR1)
DECLARE_CSR(pmpaddr2, CSR_PMPADDR2)
DECLARE_CSR(pmpaddr3, CSR_PMPADDR3)
DECLARE_CSR(pmpaddr4, CSR_PMPADDR4)
DECLARE_CSR(pmpaddr5, CSR_PMPADDR5)
DECLARE_CSR(pmpaddr6, CSR_PMPADDR6)
DECLARE_CSR(pmpaddr7, CSR_PMPADDR7)
DECLARE_CSR(pmpaddr8, CSR_PMPADDR8)
DECLARE_CSR(pmpaddr9, CSR_PMPADDR9)
DECLARE_CSR(pmpaddr10, CSR_PMPADDR10)
DECLARE_CSR(pmpaddr11, CSR_PMPADDR11)
DECLARE_CSR(pmpaddr12, CSR_PMPADDR12)
DECLARE_CSR(pmpaddr13, CSR_PMPADDR13)
DECLARE_CSR(pmpaddr14, CSR_PMPADDR14)
DECLARE_CSR(pmpaddr15, CSR_PMPADDR15)
DECLARE_CSR(tselect, CSR_TSELECT)
DECLARE_CSR(tdata1, CSR_TDATA1)
DECLARE_CSR(tdata2, CSR_TDATA2)
DECLARE_CSR(tdata3, CSR_TDATA3)
DECLARE_CSR(dcsr, CSR_DCSR)
DECLARE_CSR(dpc, CSR_DPC)
DECLARE_CSR(dscratch, CSR_DSCRATCH)
DECLARE_CSR(mcycle, CSR_MCYCLE)
DECLARE_CSR(minstret, CSR_MINSTRET)
DECLARE_CSR(mhpmcounter3, CSR_MHPMCOUNTER3)
DECLARE_CSR(mhpmcounter4, CSR_MHPMCOUNTER4)
DECLARE_CSR(mhpmcounter5, CSR_MHPMCOUNTER5)
DECLARE_CSR(mhpmcounter6, CSR_MHPMCOUNTER6)
DECLARE_CSR(mhpmcounter7, CSR_MHPMCOUNTER7)
DECLARE_CSR(mhpmcounter8, CSR_MHPMCOUNTER8)
DECLARE_CSR(mhpmcounter9, CSR_MHPMCOUNTER9)
DECLARE_CSR(mhpmcounter10, CSR_MHPMCOUNTER10)
DECLARE_CSR(mhpmcounter11, CSR_MHPMCOUNTER11)
DECLARE_CSR(mhpmcounter12, CSR_MHPMCOUNTER12)
DECLARE_CSR(mhpmcounter13, CSR_MHPMCOUNTER13)
DECLARE_CSR(mhpmcounter14, CSR_MHPMCOUNTER14)
DECLARE_CSR(mhpmcounter15, CSR_MHPMCOUNTER15)
DECLARE_CSR(mhpmcounter16, CSR_MHPMCOUNTER16)
DECLARE_CSR(mhpmcounter17, CSR_MHPMCOUNTER17)
DECLARE_CSR(mhpmcounter18, CSR_MHPMCOUNTER18)
DECLARE_CSR(mhpmcounter19, CSR_MHPMCOUNTER19)
DECLARE_CSR(mhpmcounter20, CSR_MHPMCOUNTER20)
DECLARE_CSR(mhpmcounter21, CSR_MHPMCOUNTER21)
DECLARE_CSR(mhpmcounter22, CSR_MHPMCOUNTER22)
DECLARE_CSR(mhpmcounter23, CSR_MHPMCOUNTER23)
DECLARE_CSR(mhpmcounter24, CSR_MHPMCOUNTER24)
DECLARE_CSR(mhpmcounter25, CSR_MHPMCOUNTER25)
DECLARE_CSR(mhpmcounter26, CSR_MHPMCOUNTER26)
DECLARE_CSR(mhpmcounter27, CSR_MHPMCOUNTER27)
DECLARE_CSR(mhpmcounter28, CSR_MHPMCOUNTER28)
DECLARE_CSR(mhpmcounter29, CSR_MHPMCOUNTER29)
DECLARE_CSR(mhpmcounter30, CSR_MHPMCOUNTER30)
DECLARE_CSR(mhpmcounter31, CSR_MHPMCOUNTER31)
DECLARE_CSR(mhpmevent3, CSR_MHPMEVENT3)
DECLARE_CSR(mhpmevent4, CSR_MHPMEVENT4)
DECLARE_CSR(mhpmevent5, CSR_MHPMEVENT5)
DECLARE_CSR(mhpmevent6, CSR_MHPMEVENT6)
DECLARE_CSR(mhpmevent7, CSR_MHPMEVENT7)
DECLARE_CSR(mhpmevent8, CSR_MHPMEVENT8)
DECLARE_CSR(mhpmevent9, CSR_MHPMEVENT9)
DECLARE_CSR(mhpmevent10, CSR_MHPMEVENT10)
DECLARE_CSR(mhpmevent11, CSR_MHPMEVENT11)
DECLARE_CSR(mhpmevent12, CSR_MHPMEVENT12)
DECLARE_CSR(mhpmevent13, CSR_MHPMEVENT13)
DECLARE_CSR(mhpmevent14, CSR_MHPMEVENT14)
DECLARE_CSR(mhpmevent15, CSR_MHPMEVENT15)
DECLARE_CSR(mhpmevent16, CSR_MHPMEVENT16)
DECLARE_CSR(mhpmevent17, CSR_MHPMEVENT17)
DECLARE_CSR(mhpmevent18, CSR_MHPMEVENT18)
DECLARE_CSR(mhpmevent19, CSR_MHPMEVENT19)
DECLARE_CSR(mhpmevent20, CSR_MHPMEVENT20)
DECLARE_CSR(mhpmevent21, CSR_MHPMEVENT21)
DECLARE_CSR(mhpmevent22, CSR_MHPMEVENT22)
DECLARE_CSR(mhpmevent23, CSR_MHPMEVENT23)
DECLARE_CSR(mhpmevent24, CSR_MHPMEVENT24)
DECLARE_CSR(mhpmevent25, CSR_MHPMEVENT25)
DECLARE_CSR(mhpmevent26, CSR_MHPMEVENT26)
DECLARE_CSR(mhpmevent27, CSR_MHPMEVENT27)
DECLARE_CSR(mhpmevent28, CSR_MHPMEVENT28)
DECLARE_CSR(mhpmevent29, CSR_MHPMEVENT29)
DECLARE_CSR(mhpmevent30, CSR_MHPMEVENT30)
DECLARE_CSR(mhpmevent31, CSR_MHPMEVENT31)
DECLARE_CSR(mvendorid, CSR_MVENDORID)
DECLARE_CSR(marchid, CSR_MARCHID)
DECLARE_CSR(mimpid, CSR_MIMPID)
DECLARE_CSR(mhartid, CSR_MHARTID)
DECLARE_CSR(cycleh, CSR_CYCLEH)
DECLARE_CSR(timeh, CSR_TIMEH)
DECLARE_CSR(instreth, CSR_INSTRETH)
DECLARE_CSR(hpmcounter3h, CSR_HPMCOUNTER3H)
DECLARE_CSR(hpmcounter4h, CSR_HPMCOUNTER4H)
DECLARE_CSR(hpmcounter5h, CSR_HPMCOUNTER5H)
DECLARE_CSR(hpmcounter6h, CSR_HPMCOUNTER6H)
DECLARE_CSR(hpmcounter7h, CSR_HPMCOUNTER7H)
DECLARE_CSR(hpmcounter8h, CSR_HPMCOUNTER8H)
DECLARE_CSR(hpmcounter9h, CSR_HPMCOUNTER9H)
DECLARE_CSR(hpmcounter10h, CSR_HPMCOUNTER10H)
DECLARE_CSR(hpmcounter11h, CSR_HPMCOUNTER11H)
DECLARE_CSR(hpmcounter12h, CSR_HPMCOUNTER12H)
DECLARE_CSR(hpmcounter13h, CSR_HPMCOUNTER13H)
DECLARE_CSR(hpmcounter14h, CSR_HPMCOUNTER14H)
DECLARE_CSR(hpmcounter15h, CSR_HPMCOUNTER15H)
DECLARE_CSR(hpmcounter16h, CSR_HPMCOUNTER16H)
DECLARE_CSR(hpmcounter17h, CSR_HPMCOUNTER17H)
DECLARE_CSR(hpmcounter18h, CSR_HPMCOUNTER18H)
DECLARE_CSR(hpmcounter19h, CSR_HPMCOUNTER19H)
DECLARE_CSR(hpmcounter20h, CSR_HPMCOUNTER20H)
DECLARE_CSR(hpmcounter21h, CSR_HPMCOUNTER21H)
DECLARE_CSR(hpmcounter22h, CSR_HPMCOUNTER22H)
DECLARE_CSR(hpmcounter23h, CSR_HPMCOUNTER23H)
DECLARE_CSR(hpmcounter24h, CSR_HPMCOUNTER24H)
DECLARE_CSR(hpmcounter25h, CSR_HPMCOUNTER25H)
DECLARE_CSR(hpmcounter26h, CSR_HPMCOUNTER26H)
DECLARE_CSR(hpmcounter27h, CSR_HPMCOUNTER27H)
DECLARE_CSR(hpmcounter28h, CSR_HPMCOUNTER28H)
DECLARE_CSR(hpmcounter29h, CSR_HPMCOUNTER29H)
DECLARE_CSR(hpmcounter30h, CSR_HPMCOUNTER30H)
DECLARE_CSR(hpmcounter31h, CSR_HPMCOUNTER31H)
DECLARE_CSR(mcycleh, CSR_MCYCLEH)
DECLARE_CSR(minstreth, CSR_MINSTRETH)
DECLARE_CSR(mhpmcounter3h, CSR_MHPMCOUNTER3H)
DECLARE_CSR(mhpmcounter4h, CSR_MHPMCOUNTER4H)
DECLARE_CSR(mhpmcounter5h, CSR_MHPMCOUNTER5H)
DECLARE_CSR(mhpmcounter6h, CSR_MHPMCOUNTER6H)
DECLARE_CSR(mhpmcounter7h, CSR_MHPMCOUNTER7H)
DECLARE_CSR(mhpmcounter8h, CSR_MHPMCOUNTER8H)
DECLARE_CSR(mhpmcounter9h, CSR_MHPMCOUNTER9H)
DECLARE_CSR(mhpmcounter10h, CSR_MHPMCOUNTER10H)
DECLARE_CSR(mhpmcounter11h, CSR_MHPMCOUNTER11H)
DECLARE_CSR(mhpmcounter12h, CSR_MHPMCOUNTER12H)
DECLARE_CSR(mhpmcounter13h, CSR_MHPMCOUNTER13H)
DECLARE_CSR(mhpmcounter14h, CSR_MHPMCOUNTER14H)
DECLARE_CSR(mhpmcounter15h, CSR_MHPMCOUNTER15H)
DECLARE_CSR(mhpmcounter16h, CSR_MHPMCOUNTER16H)
DECLARE_CSR(mhpmcounter17h, CSR_MHPMCOUNTER17H)
DECLARE_CSR(mhpmcounter18h, CSR_MHPMCOUNTER18H)
DECLARE_CSR(mhpmcounter19h, CSR_MHPMCOUNTER19H)
DECLARE_CSR(mhpmcounter20h, CSR_MHPMCOUNTER20H)
DECLARE_CSR(mhpmcounter21h, CSR_MHPMCOUNTER21H)
DECLARE_CSR(mhpmcounter22h, CSR_MHPMCOUNTER22H)
DECLARE_CSR(mhpmcounter23h, CSR_MHPMCOUNTER23H)
DECLARE_CSR(mhpmcounter24h, CSR_MHPMCOUNTER24H)
DECLARE_CSR(mhpmcounter25h, CSR_MHPMCOUNTER25H)
DECLARE_CSR(mhpmcounter26h, CSR_MHPMCOUNTER26H)
DECLARE_CSR(mhpmcounter27h, CSR_MHPMCOUNTER27H)
DECLARE_CSR(mhpmcounter28h, CSR_MHPMCOUNTER28H)
DECLARE_CSR(mhpmcounter29h, CSR_MHPMCOUNTER29H)
DECLARE_CSR(mhpmcounter30h, CSR_MHPMCOUNTER30H)
DECLARE_CSR(mhpmcounter31h, CSR_MHPMCOUNTER31H)
#endif
#ifdef DECLARE_CAUSE
DECLARE_CAUSE("misaligned fetch", CAUSE_MISALIGNED_FETCH)
DECLARE_CAUSE("fetch access", CAUSE_FETCH_ACCESS)
DECLARE_CAUSE("illegal instruction", CAUSE_ILLEGAL_INSTRUCTION)
DECLARE_CAUSE("breakpoint", CAUSE_BREAKPOINT)
DECLARE_CAUSE("misaligned load", CAUSE_MISALIGNED_LOAD)
DECLARE_CAUSE("load access", CAUSE_LOAD_ACCESS)
DECLARE_CAUSE("misaligned store", CAUSE_MISALIGNED_STORE)
DECLARE_CAUSE("store access", CAUSE_STORE_ACCESS)
DECLARE_CAUSE("user_ecall", CAUSE_USER_ECALL)
DECLARE_CAUSE("supervisor_ecall", CAUSE_SUPERVISOR_ECALL)
DECLARE_CAUSE("hypervisor_ecall", CAUSE_HYPERVISOR_ECALL)
DECLARE_CAUSE("machine_ecall", CAUSE_MACHINE_ECALL)
DECLARE_CAUSE("fetch page fault", CAUSE_FETCH_PAGE_FAULT)
DECLARE_CAUSE("load page fault", CAUSE_LOAD_PAGE_FAULT)
DECLARE_CAUSE("store page fault", CAUSE_STORE_PAGE_FAULT)
#endif
'''

        self.assertEquals(header_expected, ext.cust_header)
