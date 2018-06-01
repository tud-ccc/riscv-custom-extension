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
from modelparsing.exceptions import ConsistencyError
from modelparsing.compiler import Compiler
from tst import folderpath
sys.path.remove('..')


class TestCompiler(unittest.TestCase):
    '''
    Unit tests for the Compiler class and its functions.
    '''

    class Args():

        def __init__(self):
            self._tc = os.path.join(os.path.expanduser('~'),
                                    'projects/riscv-gnu-toolchain')

        @property
        def toolchain(self):
            return self._tc

    class Extensions():

        def __init__(self, mdls, insts, hdr):
            self._models = mdls
            self._insts = insts
            self._cust_header = hdr

        @property
        def models(self):
            return self._models

        @property
        def instructions(self):
            return self._insts

        @property
        def cust_header(self):
            return self._cust_header

    class Instruction:
        '''
        Class, that represents one single custom instruction.
        Contains the name, the mask and the match.
        '''

        def __init__(self,
                     name, form,
                     mask, maskname, maskval,
                     match, matchname, matchval,
                     operands):
            self._form = form
            self._mask = mask
            self._maskname = maskname
            self._maskvalue = maskval
            self._match = match
            self._matchname = matchname
            self._matchvalue = matchval
            self._name = name
            self._operands = operands

        @property
        def form(self):
            return self._form

        @property
        def mask(self):
            return self._mask

        @property
        def maskname(self):
            return self._maskname

        @property
        def maskvalue(self):
            return self._maskvalue

        @property
        def match(self):
            return self._match

        @property
        def matchname(self):
            return self._matchname

        @property
        def matchvalue(self):
            return self._matchvalue

        @property
        def name(self):
            return self._name

        @property
        def operands(self):
            return self._operands

    class Registers:
        def __init__(self, regmap):
            self._regmap = regmap

        @property
        def regmap(self):
            return self._regmap

    def __init__(self, *args, **kwargs):
        super(TestCompiler, self).__init__(*args, **kwargs)
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
        # prepare a extension object
        inst = self.Instruction('itype', 'I',
                                'MASK', 'MASKNAME', 'MASKKVAL',
                                'MATCH', 'MATCHNAME', 'MATCHVAL',
                                'd,s,j')
        self.exts = self.Extensions([], [inst], 'customheader')

        # prepare header and cc file
        self.opcheader = self.folderpath + 'opcheader.h'
        with open(self.opcheader, 'w') as fh:
            fh.write(
                '/* Automatically generated by parse-opcodes.  */\n' +
                '#ifndef RISCV_ENCODING_H\n' +
                '#define RISCV_ENCODING_H\n')
        self.opcheader_cust = self.folderpath + 'opcheadercust.h'
        self.opcsource = self.folderpath + 'opcsource.c'
        with open(self.opcsource, 'w') as fh:
            fh.write('{\n' +
                     '{ test },\n' +
                     '\n' +
                     '/* Terminate the list.  */\n' +
                     '{0, 0, 0, 0, 0, 0, 0}\n' +
                     '};')

        self.args = self.Args()

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

    def testExtendHeaderCopyOld(self):
        # insert a function (do not care if correctly added or not)
        # and check if old header was copied and stored correctly
        compiler = Compiler(self.exts, self.regs, self.args)
        compiler.opch = self.opcheader
        compiler.opch_cust = self.opcheader_cust
        compiler.extend_header()

        # now the header file should have been copied
        # check in our folder if we have a file
        opch_old = self.opcheader + '_old'
        self.assertTrue(os.path.exists(opch_old))
        self.assertTrue(os.path.isfile(opch_old))

        # check contents of file
        with open(opch_old, 'r') as fh:
            content = fh.readlines()

        self.assertEqual(len(content), 3)
        self.assertEqual(
            content[0], '/* Automatically generated by parse-opcodes.  */\n')
        self.assertEqual(content[1], '#ifndef RISCV_ENCODING_H\n')
        self.assertEqual(content[2], '#define RISCV_ENCODING_H\n')

    def testExtendHeaderRestoreOldHeader(self):
        # try restoring of old header function
        compiler = Compiler(self.exts, self.regs, self.args)
        compiler.opch = self.opcheader
        compiler.opch_cust = self.opcheader_cust

        opchold = self.opcheader + '_old'
        oldcontent = 'old_header'
        with open(opchold, 'w') as fh:
            fh.write(oldcontent)

        compiler.restore_header()

        with open(self.opcheader, 'r') as fh:
            hcontent = fh.readlines()

        self.assertEqual(hcontent[0], oldcontent)
        self.assertEqual(hcontent[-1], oldcontent)

        for file in os.listdir(self.folderpath):
            self.assertNotEqual(file, opchold)
            self.assertNotEqual(file, self.opcheader_cust)

    def testExtendHeaderCreateCustomHeader(self):
        # check if the files was created
        # no necessarity to have the correct content
        # that is part of the extensions class
        compiler = Compiler(self.exts, self.regs, self.args)
        compiler.opch = self.opcheader
        compiler.opch_cust = self.opcheader_cust
        compiler.extend_header()

        self.assertTrue(os.path.exists(self.opcheader_cust))
        self.assertTrue(os.path.isfile(self.opcheader_cust))

    def testExtendHeaderPatchRiscvOpcH(self):
        # check if the include statement was added correctly
        compiler = Compiler(self.exts, self.regs, self.args)
        compiler.opch = self.opcheader
        compiler.opch_cust = self.opcheader_cust
        compiler.extend_header()

        with open(self.opcheader, 'r') as fh:
            hcontent = fh.readlines()

        self.assertEqual(len(hcontent), 4)
        self.assertEqual(hcontent[0], '#include "riscv-custom-opc.h"\n')

    def testExtendHeaderPatchRiscvOpcHMultiple(self):
        # purpose is to check if the include statement is only added once
        compiler = Compiler(self.exts, self.regs, self.args)
        compiler.opch = self.opcheader
        compiler.opch_cust = self.opcheader_cust
        compiler.extend_header()

        compiler1 = Compiler(self.exts, self.regs, self.args)
        compiler1.opch = self.opcheader
        compiler1.opch_cust = self.opcheader_cust
        compiler1.extend_header()

        with open(self.opcheader, 'r') as fh:
            content = fh.readlines()

        self.assertEqual(content[0], '#include "riscv-custom-opc.h"\n')
        self.assertNotEqual(content[1], '#include "riscv-custom-opc.h"\n')

    def testExtendSourceCopyOld(self):
        # insert a function (do not care if correctly added or not)
        # and check if old opc source was copied and stored correctly
        compiler = Compiler(self.exts, self.regs, self.args)
        compiler.opcc = self.opcsource
        compiler.extend_source()

        # now the header file should have been copied
        # check in our folder if we have a file
        opcc_old = self.opcsource + '_old'
        self.assertTrue(os.path.exists(opcc_old))
        self.assertTrue(os.path.isfile(opcc_old))
        # check contents of file
        with open(opcc_old, 'r') as fh:
            content = fh.readlines()

        self.assertTrue(content[0], '{ test }')
        self.assertTrue(content[-1], '{ test }')

    def testExtendSourceRestoreOldSource(self):
        # try restoring of old header function
        compiler = Compiler(self.exts, self.regs, self.args)
        compiler.opcc = self.opcsource

        opccold = self.opcsource + '_old'
        oldcontent = 'old_source'
        with open(opccold, 'w') as fh:
            fh.write(oldcontent)

        compiler.restore_source()

        with open(self.opcsource, 'r') as fh:
            ccontent = fh.readlines()

        self.assertEqual(ccontent[0], oldcontent)
        self.assertEqual(ccontent[-1], oldcontent)

        for file in os.listdir(self.folderpath):
            self.assertNotEqual(file, opccold)

    def testExtendSourceIType(self):
        compiler = Compiler(self.exts, self.regs, self.args)
        compiler.opcc = self.opcsource
        compiler.extend_source()

        with open(self.opcsource, 'r') as fh:
            content = fh.readlines()

        self.assertEqual(len(content), 7)
        self.assertEqual(
            content[2],
            '{"itype",  "I",  "d,s,j", MATCHNAME, MASKNAME, match_opcode, 0 },\n')

    def testExtendSourceRType(self):
        inst = self.Instruction('rtype', 'R',
                                'MASK', 'MASKNAME', 'MASKKVAL',
                                'MATCH', 'MATCHNAME', 'MATCHVAL',
                                'd,s,t')
        exts = self.Extensions([], [inst], 'customheader')

        compiler = Compiler(exts, self.regs, self.args)
        compiler.opcc = self.opcsource
        compiler.extend_source()

        with open(self.opcsource, 'r') as fh:
            content = fh.readlines()

        self.assertEqual(len(content), 7)
        self.assertEqual(
            content[2],
            '{"rtype",  "I",  "d,s,t", MATCHNAME, MASKNAME, match_opcode, 0 },\n')

    def testExtendSourceMultiple(self):
        # extend the source with multiple models
        inst = self.Instruction('test', 'I',
                                'MASK', 'MASKNAME', 'MASKKVAL',
                                'MATCH', 'MATCHNAME', 'MATCHVAL',
                                'd,s,j')
        inst0 = self.Instruction('test0', 'I',
                                 'MASK', 'MASKNAME', 'MASKKVAL',
                                 'MATCH', 'MATCHNAME', 'MATCHVAL',
                                 'd,s,j')
        inst1 = self.Instruction('test1', 'I',
                                 'MASK', 'MASKNAME', 'MASKKVAL',
                                 'MATCH', 'MATCHNAME', 'MATCHVAL',
                                 'd,s,j')
        inst2 = self.Instruction('test2', 'I',
                                 'MASK', 'MASKNAME', 'MASKKVAL',
                                 'MATCH', 'MATCHNAME', 'MATCHVAL',
                                 'd,s,j')
        exts = self.Extensions([], [inst, inst0, inst1, inst2], 'customheader')

        compiler = Compiler(exts, self.regs, self.args)
        compiler.opcc = self.opcsource
        compiler.extend_source()

        with open(self.opcsource, 'r') as fh:
            content = fh.readlines()

        self.assertEqual(len(content), 10)
        self.assertTrue(
            '{"test0",  "I",  "d,s,j", MATCHNAME, MASKNAME, match_opcode, 0 },\n' in content)
        self.assertTrue(
            '{"test1",  "I",  "d,s,j", MATCHNAME, MASKNAME, match_opcode, 0 },\n' in content)
        self.assertTrue(
            '{"test2",  "I",  "d,s,j", MATCHNAME, MASKNAME, match_opcode, 0 },\n' in content)
        self.assertTrue(
            '{"test",  "I",  "d,s,j", MATCHNAME, MASKNAME, match_opcode, 0 },\n' in content)

    def testExtendSourceAddSameTwice(self):
        # should only occure once in source file
        compiler = Compiler(self.exts, self.regs, self.args)
        compiler.opcc = self.opcsource
        compiler.extend_source()

        compiler1 = Compiler(self.exts, self.regs, self.args)
        compiler1.opcc = self.opcsource
        compiler1.extend_source()

        with open(self.opcsource, 'r') as fh:
            content = fh.readlines()

        self.assertEqual(len(content), 7)
