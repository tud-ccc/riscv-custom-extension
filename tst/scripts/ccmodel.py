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

        if 'nocycles' not in faults:
            self.cycles = 1
        else:
            self.cycles = 0
