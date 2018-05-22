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

from stat import *

from compiler import Compiler
from decoder import Decoder
from extensions import Extensions
from model import Model
from registers import Registers

logger = logging.getLogger(__name__)


class Parser:
    '''
    This class stepwise calls all the functions necessary to parse modules
    and retrieve the information necessary to extend gnu binutils and gem5.
    '''

    def __init__(self, args):
        self._args = args
        self._models = []
        self._exts = None
        self._decoder = Decoder([])
        self._compiler = None

    def restore(self):
        '''
        Restore the toolchain to its defaults.
        '''

        logger.info('Remove custom instructions from GNU binutils files')
        self._compiler = Compiler(None, self._args)
        self._compiler.restore()
        self._decoder.restore()

    def parse_models(self):
        '''
        Parse the c++ reference implementation
        of the custom instruction.
        '''

        logger.info('Determine if modelpath is a folder or a single file')
        if os.path.isdir(self._args.modelpath):
            # restore the toolchain to its defaults
            self.restore()
            logger.info('Traverse over directory')
            self.treewalk(self._args.modelpath)
        else:
            logger.info('Single file, start parsing')
            model = Model(self._args.modelpath)
            self._models.append(model)

        self._exts = Extensions(self._models)

    def treewalk(self, top):
        logger.info('Search for models in {}'.format(top))
        logger.debug('Directory content: {}'.format(os.listdir(top)))
        for file in os.listdir(top):
            pathname = os.path.join(top, file)
            mode = os.stat(pathname)[ST_MODE]

            if S_ISDIR(mode):
                # directory
                self.treewalk(pathname)
            elif S_ISREG(mode):
                # file
                if pathname.endswith('.cc'):
                    logger.info(
                        'Model definition in file {}'.format(pathname))
                    model = Model(pathname)

                    self._models.append(model)
                # registers
                if pathname.endswith('registers.hh'):
                    logger.info('Custom registers in file {}'.format(pathname))
                    self._regs = Registers(pathname)
            else:
                # unknown file type
                logger.info('Unknown file type, skip')

    def extend_compiler(self):
        '''
        Extend the riscv compiler.
        '''

        self._compiler = Compiler(self._exts, self._args)
        self._compiler.extend_compiler()

    def extend_gem5(self):
        '''
        Extend the gem5 decoder.
        '''
        self._decoder = Decoder(self._models, self._regs)
        self._decoder.extend_decoder()

    @property
    def args(self):
        return self._args

    @property
    def compiler(self):
        return self._compiler

    @property
    def decoder(self):
        return self._decoder

    @property
    def extensions(self):
        return self._exts

    @property
    def models(self):
        return self._models

    @property
    def regs(self):
        return self._regs
