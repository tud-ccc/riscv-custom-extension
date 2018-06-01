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

logger = logging.getLogger(__name__)


class Instruction:
    '''
    Class, that represents one single custom instruction.
    Contains the name, the mask and the match.
    '''

    def __init__(self, form, mask, match, name):
        self._form = form  # format
        self._mask = mask  # the whole mask string
        self._match = match  # the whole match string
        self._name = name  # the name that shall occure in the assembler
        # the mask name
        self._maskname = mask.split()[-2]
        # the mask value
        self._maskvalue = int(mask.split()[-1], 16)
        # the match name
        self._matchname = match.split()[-2]
        # the match value
        self._matchvalue = int(match.split()[-1], 16)

        # set right operands that are used in binutils' opc parsing
        # d -> Rd
        # s -> Rs1
        # t -> Rs2
        # j -> imm
        if form == 'R':
            # operands for Rd, Rs1, Rs2
            self._operands = 'd,s,t'
        elif form == 'I':
            # operands for Rd, Rs1, imm
            self._operands = 'd,s,j'
        else:
            logger.warn('Instruction format unnokwn. ' +
                        'Leaving operands field empty.')
            self.operands = ''

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
