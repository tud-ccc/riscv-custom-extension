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

import logging
import os

logger = logging.getLogger(__name__)


class Compiler:
    '''
    Class that provides necessary functions to extend
    the riscv compiler
    '''

    def __init__(self, exts, args):
        self._exts = exts

        # header file that needs to be edited
        self.opch = os.path.abspath(
            os.path.join(
                args.toolchain,
                'riscv-binutils-gdb/include/opcode/riscv-opc.h'))
        # custom opc.h file
        self.opch_cust = os.path.abspath(
            os.path.join(
                args.toolchain,
                'riscv-binutils-gdb/include/opcode/riscv-custom-opc.h'))
        # c source file that needs to be edited
        self.opcc = os.path.abspath(
            os.path.join(
                args.toolchain,
                'riscv-binutils-gdb/opcodes/riscv-opc.c'))

        assert os.path.exists(self.opch)
        assert os.path.exists(os.path.dirname(self.opch_cust))
        assert os.path.exists(self.opcc)

    def restore(self):
        '''
        Restore the original header and source files.
        '''

        self.restore_header()
        self.restore_source()

    def restore_header(self):
        '''
        Remove all custom extensions.
        Restores the saved old header.
        '''

        logger.info('Restore original header file')
        opchold = self.opch + '_old'
        if os.path.exists(opchold):
            logger.info('Restore contents from file {}'.format(opchold))

            with open(opchold, 'r') as fh:
                content = fh.read()

            with open(self.opch, 'w') as fh:
                fh.write(content)

            logger.info('Original header restored')

            try:
                logger.info('Remove {} from system'.format(opchold))
                os.remove(opchold)
            except OSError:
                pass
            # remove custom file
            try:
                logger.info('Remove {} from system'.format(self.opch_cust))
                os.remove(self.opch_cust)
            except OSError:
                pass
        else:
            logger.info('Nothing to do')

    def restore_source(self):
        '''
        Restores the saved old source.
        '''

        logger.info('Restore original source file')
        opccold = self.opcc + '_old'
        if os.path.exists(opccold):
            logger.info('Restore contents from file {}'.format(opccold))
            with open(opccold, 'r') as fh:
                content = fh.read()

            with open(self.opcc, 'w') as fh:
                fh.write(content)

            logger.info('Original source restored')

            try:
                logger.info('Remove {} from system'.format(opccold))
                os.remove(opccold)
            except OSError:
                pass
        else:
            logger.info('Nothing to do')

    def extend_compiler(self):
        '''
        Calls functions to extend necessary header and c files.
        Also creates intrinsics for access to custom registers.
        '''

        self.extend_header()
        self.extend_source()
        self.extend_stdlibs()

    def extend_header(self):
        '''
        Extend the header file riscv-opc.h with the generated masks and matches
        of the custom instructions.
        '''

        # read the content of riscv opc header
        with open(self.opch, 'r') as fh:
            content = fh.read()

        # if not existing
        # copy the old header file
        # basically generate new file with old content
        opchold = self.opch + '_old'
        if not os.path.exists(opchold):
            logger.info('Copy original {}'.format(self.opch))
            with open(opchold, 'w') as fh:
                fh.write(content)

        # we include a whole directory
        # at first, we create our own custom opc header file
        # write file
        with open(self.opch_cust, 'w') as fh:
            fh.write(self._exts.cust_header)

        # write the include statement for our custom header
        if '#include "riscv-custom-opc.h"\n' not in content:
            content = '#include "riscv-custom-opc.h"\n' + content

        # write back generated header file
        with open(self.opch, 'w') as fh:
            fh.write(content)

    def extend_source(self):
        '''
        Extend the source file riscv-opc.c with information about the
        custom instructions.
        '''

        # read source file
        with open(self.opcc, 'r') as fh:
            content = fh.readlines()

        # if not existing
        # copy the old source file
        # basically generate new file with old content
        opccold = self.opcc + '_old'
        if not os.path.exists(opccold):
            logger.info('Copy original {}'.format(self.opcc))
            with open(opccold, 'w') as fh:
                data = ''.join(content)
                fh.write(data)

        for inst in self._exts.instructions:
            # build string that has to be added to the content of the file
            dfn = '{{"{}",  "I",  "{}", {}, {}, match_opcode, 0 }},\n'.format(
                inst.name, inst.operands, inst.matchname, inst.maskname)

            if dfn in content:
                logger.warn('Instruction already taken, skip')
                continue

            # we simply add the instruction right before the termination of the
            # list in riscv-opc.c
            try:
                line = content.index('/* Terminate the list.  */\n') - 1
            except ValueError:
                # choose random line number near the end of the file
                line = len(content) - 4

            logger.info('Adding instruction {}'.format(inst.name))
            content.insert(line, dfn)

        # write back modified content
        with open(self.opcc, 'w') as fh:
            content = ''.join(content)
            fh.write(content)

    def extend_stdlibs(self):
        pass

    @property
    def exts(self):
        return self._exts

    @exts.setter
    def exts(self, exts):
        self._exts = exts
