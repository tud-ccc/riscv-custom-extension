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

import clang.cindex
import logging
import subprocess

from exceptions import ConsistencyError

logger = logging.getLogger(__name__)


class Model:
    '''
    C++ Reference of the custom instruction.
    '''

    def __init__(self, impl=None, read=False, write=False):
        '''
        Init method, that takes the location of
        the implementation as an argument.
        '''

        if impl is None:
            # we generate a model for read and write
            self._cycles = 1
            self._form = 'R'
            self._opc = 0x1e
            self._funct3 = 0x7
            # checks
            self._check_rd = True      # check if rd is defined
            self._check_rs1 = True     # check if rs1 is defined
            self._check_op2 = True
            self._rettype = 'void'

            if read is True:
                self._funct7 = 0x7e
                self._name = 'read_custreg'
                self._dfn = '''{
    Rd = xc->readMiscReg(Rs2);
}'''
            elif write is True:
                self._funct7 = 0x7f
                self._name = 'write_custreg'
                self._dfn = '''{
    xc->setMiscReg(Rs2, Rs1);
}'''
            else:
                raise ConsistencyError(
                    'If no file is given, either write or read must be true.')

            self.check_consistency()

        else:
            logger.info("Using libclang at %s" %
                        clang.cindex.Config.library_file)

            self.compile_model(impl)

            index = clang.cindex.Index.create()
            tu = index.parse(impl, ['-x', 'c++', '-c', '-std=c++11'])

            # information to retrieve form model
            self._cycles = 1            # cycle count for the instruction
            self._dfn = ''              # definition
            self._form = ''             # format
            self._funct3 = 0xff         # funct3 bit field
            self._funct7 = 0xff         # funct7 bit field
            self._name = ''             # name
            self._opc = 0x0             # opcode
            # model consistency checks
            self._check_rd = False      # check if rd is defined
            self._check_rs1 = False     # check if rs1 is defined
            self._check_op2 = False
            self._rettype = ''

            logger.info("Parsing model @ %s" % impl)

            self.parse_model(tu.cursor)
            self.check_consistency()

    def compile_model(self, file):
        logger.info('Compile model {}'.format(file))
        p = subprocess.Popen([r'g++',
                              '-fsyntax-only',
                              '-Wall',
                              '-std=c++11',
                              '-c',
                              file],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        (_, ret) = p.communicate()

        if ret:
            logger.error(ret)
            raise ConsistencyError(file, 'Compile error.')

    def parse_model(self, node):
        '''
        Parse the model and search for all necessary information.
        '''
        for child in node.get_children():
            self.parse_model(child)

        # only set name if it's unset
        # due to parsing of included header the function definition occures
        # twice
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL \
                and self._name == '':
            # save name
            self._name = node.spelling
            # save rettype for consistency check
            self._rettype = list(node.get_tokens())[0].spelling
            logger.info("Function name: {}".format(self._name))

        if node.kind == clang.cindex.CursorKind.COMPOUND_STMT:
            self.extract_definition(node)

        if node.kind == clang.cindex.CursorKind.VAR_DECL:
            # process all variable declarations
            # opcode
            if node.spelling == 'opc':
                logger.debug('Model opcode:')
                self._opc = self.extract_value(node)
            # funct3 bitfield
            if node.spelling == 'funct3':
                logger.debug('Model funct3:')
                self._funct3 = self.extract_value(node)
            # funct7 bitfield, only for R-Type
            if node.spelling == 'funct7':
                logger.debug('Model funct7:')
                self._funct7 = self.extract_value(node)
            # cycle count
            if node.spelling == 'cycles':
                logger.debug('Model cycles:')
                self._cycles = self.extract_value(node)

        if node.kind == clang.cindex.CursorKind.PARM_DECL:
            # process all parameter declarations
            # check if Rd and Rs1 exists
            if node.spelling.startswith('Rd'):
                self._check_rd = True
            if node.spelling.startswith('Rs1'):
                self._check_rs1 = True

            # determine, if function is R-Type or I-Type
            if node.spelling.startswith('Rs2'):
                logger.debug('Model is of format R-Type')
                self._form = 'R'
                self._check_op2 = True
            if node.spelling.startswith('imm'):
                logger.debug('Model is of format I-Type')
                self._form = 'I'
                self._check_op2 = True

    def extract_definition(self, node):
        '''
        Extract a function definition.
        '''
        filename = node.location.file.name
        with open(filename, 'r') as fh:
            contents = fh.read()

        self._dfn = contents[node.extent.start.offset: node.extent.end.offset]

        logger.info("Definintion in {} @ line {}".format(
            filename, node.location.line))
        logger.debug('Definition:\n%s' % self._dfn)

    def extract_value(self, node):
        '''
        Extract a variable value.
        '''
        for entry in list(node.get_tokens()):
            if entry.spelling[0].isdigit():
                logger.debug('Value: %s' % entry.spelling)
                return int(entry.spelling, 0)

    def check_consistency(self):
        '''
        Check whether a model fulfills all consistency requirements.
        '''
        logger.info('Check consistency of model definition')

        # check function definition
        # does rd and rs1 exist?
        # both are required for R and I type
        if not self._check_rd:
            raise ConsistencyError(
                self._check_rd, 'Model definition requires parameter Rd')
        if not self._check_rs1:
            raise ConsistencyError(
                self._check_rs1, 'Model definition requires parameter Rs1')
        # check if operand 2 was defined
        if not self._check_op2:
            raise ConsistencyError(
                self._check_op2, 'Model definition requires parameter Op2')

        # check return type of function
        if not self._rettype == 'void':
            raise ConsistencyError(
                self._rettype, 'Function has to be of type void.')

        if self._opc not in [0x02, 0x0a, 0x16, 0x1e]:
            raise ValueError(self._opc, 'Invalid opcode.')

        # funct3 --> 3 bits
        if self._funct3 > 0x7:
            raise ValueError(self._funct3, 'Invalid funct3.')
        # funct7 --> 7 bits
        if self._form == 'R' and self._funct7 > 0x7f:
            raise ValueError(self._funct7, 'Invalid funct7.')

        # check, if cycles where added
        if self._cycles == 0:
            raise ValueError(self._cycles, 'Missing cycle information.')

        # does the definition starts and end with a bracket
        if not self._dfn.startswith('{'):
            raise ConsistencyError(
                self._dfn, 'Function definition not found.')
        if not self._dfn.endswith('}'):
            raise ConsistencyError(
                self._dfn, 'Closing bracket missing.')

        logger.info('Model meets requirements')

    @property
    def cycles(self):
        return self._cycles

    @property
    def definition(self):
        return self._dfn

    @property
    def form(self):
        return self._form

    @property
    def funct3(self):
        return self._funct3

    @property
    def funct7(self):
        return self._funct7

    @property
    def name(self):
        return self._name

    @property
    def opc(self):
        return self._opc
