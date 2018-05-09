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

import sys
import unittest

sys.path.append('..')
from modelparsing.instruction import Instruction
sys.path.remove('..')


class TestInstruction(unittest.TestCase):
    '''
    Tests for all functions in class Instruction
    '''

    def setUp(self):
        # set up three different instructions to test all variants of operants
        # R-Type
        self.formr = 'R'
        self.mask = 'MASK_NAME 0x01'
        self.maskname = 'MASK_NAME'
        self.maskvalue = 0x1
        self.match = 'MATCH_NAME 0x02'
        self.matchname = 'MATCH_NAME'
        self.matchvalue = 0x2
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
                                 self.match,
                                 self.name0)
        self.inst1 = Instruction(self.formi,
                                 self.mask,
                                 self.match,
                                 self.name1)
        self.inst2 = Instruction(self.formx,
                                 self.mask,
                                 self.match,
                                 self.name2)

        # create expected operand strings
        self.opsr = 'd,s,t'
        self.opsi = 'd,s,j'
        self.opsx = ''

    def testInstructionRType(self):
        self.assertEqual(self.inst0.form, self.formr)
        self.assertEqual(self.inst0.mask, self.mask)
        self.assertEqual(self.inst0.maskname, self.maskname)
        self.assertEqual(self.inst0.maskvalue, self.maskvalue)
        self.assertEqual(self.inst0.match, self.match)
        self.assertEqual(self.inst0.matchname, self.matchname)
        self.assertEqual(self.inst0.matchvalue, self.matchvalue)
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
