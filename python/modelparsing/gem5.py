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
import sys

from mako.template import Template

logger = logging.getLogger(__name__)


class Gem5:
    '''
    This class builds the code snippets, that are later integrated in the gem5
    decoder. It builds a custom decoder depending on the previously parsed
    models.
    '''

    def __init__(self, exts, regs):
        self._exts = exts
        self._regs = regs
        self._decoder = ''

        self._gem5_path = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                '../../../..'))
        self._gem5_arch_path = os.path.abspath(
            os.path.join(
                self._gem5_path,
                'src/arch'))
        self._gem5_ply_path = os.path.join(
            self._gem5_path, 'ext/ply')
        self._isa_decoder = os.path.abspath(
            os.path.join(
                self._gem5_arch_path,
                'riscv/isa/decoder/rv32.isa'))
        assert os.path.exists(self._isa_decoder)

        self._buildpath = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                '../../build'))

        self._isamain = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                '../../isa/main.isa'))
        assert os.path.exists(self._isamain)

    def restore(self):
        '''
        Remove the custom extensions from the isa decoder.
        Restore the saved decoder.
        '''
        logger.info('Restore original ISA decoder.')
        decoder_old = self._isa_decoder + '_old'
        if os.path.exists(decoder_old):
            logger.info('Restore contents from file {}'.format(decoder_old))

            with open(decoder_old, 'r') as fh:
                content = fh.read()

            with open(self._isa_decoder, 'w') as fh:
                fh.write(content)

            logger.info('Original decoder restored')

            try:
                logger.info('Remove {} from system'.format(decoder_old))
                os.remove(decoder_old)
            except OSError:
                pass
        else:
            logger.info('Nothing to do')

    def extend_gem5(self):
        '''
        Calls the functions to generate a custom decoder and
        patch the necessary files in gem5.
        '''

        # first: decoder related stuff
        self.gen_decoder()
        self.gen_cxx_files()
        self.patch_decoder()
        # second: create timings for functional units
        self.create_FU_timings()

    def gen_decoder(self):
        assert os.path.exists(self._buildpath)
        assert os.path.exists(self._gem5_arch_path)
        # iterate of all custom extensions and generate a custom decoder
        # first sort models:
        # opcode > funct3 (> funct7)
        logger.info('Generate custom decoder from models.')

        # sort models
        self._exts.models.sort(key=lambda x: (x.opc, x.funct3, x.funct7))

        dec_templ = Template(r"""<%
dfn = {}
for model in models:
    if model.opc in dfn:
        dfn[model.opc].append(model)
    else:
        dfn[model.opc] = [model]
for opc, mdls in dfn.items():
    funct3 = {}
    for mdl in mdls:
        if mdl.form == 'I':
            funct3[mdl.funct3] = mdl
        else:
            if mdl.funct3 in funct3:
                funct3[mdl.funct3].append(mdl)
            else:
                funct3[mdl.funct3] = [mdl]
    dfn[opc] = funct3
%>\
decode OPCODE default Unknown::unknown() {
% for opc,funct3_dict in dfn.items():
${hex(opc)}: decode FUNCT3 {
% for funct3, val in funct3_dict.items():
% if type(val) != list:
${hex(funct3)}: I32Op::${val.name}({${val.definition}}, uint32_t, IntCustOp);
% else:
${hex(funct3)}: decode FUNCT7 {
% for mdl in val:
${hex(mdl.funct7)}: R32Op::${mdl.name}({${mdl.definition}}, IntCustOp);
% endfor
}
% endif
% endfor
}
% endfor
}
""")

        self._decoder = dec_templ.render(models=self._exts.models)
        logger.debug('custom decoder: \n' + self._decoder)

    def gen_cxx_files(self):
        # now generate the cxx files using the isa parser
        isabuildpath = os.path.join(self._buildpath, 'isa')
        if not os.path.exists(isabuildpath):
            os.makedirs(isabuildpath)

        isafile = os.path.join(isabuildpath, 'custom.isa')

        with open(isafile, 'w') as fh:
            fh.write(self._decoder)

        # create a builddir
        gen_build_dir = os.path.join(self._buildpath, 'generated')
        if not os.path.exists(gen_build_dir):
            os.makedirs(gen_build_dir)

        # add some paths to call the gem5 isa parser
        sys.path[0:0] = [self._gem5_arch_path]
        sys.path[0:0] = [self._gem5_ply_path]
        sys.path[0:0] = [os.path.join(self._gem5_path, 'src/python')]
        import isa_parser

        logger.info('Let gem5 isa_parser generate decoder files')
        parser = isa_parser.ISAParser(gen_build_dir)
        parser.parse_isa_desc(self._isamain)

    def patch_decoder(self):
        # patch the gem5 isa decoder

        dec_templ = Template(r"""<%
dfn = {}
for model in models:
    if model.opc in dfn:
        dfn[model.opc].append(model)
    else:
        dfn[model.opc] = [model]
for opc, mdls in dfn.items():
    funct3 = {}
    for mdl in mdls:
        if mdl.form == 'I':
            funct3[mdl.funct3] = mdl
        else:
            if mdl.funct3 in funct3:
                funct3[mdl.funct3].append(mdl)
            else:
                funct3[mdl.funct3] = [mdl]
    dfn[opc] = funct3
%>\
% for opc,funct3_dict in dfn.items():
${hex(opc)}: decode FUNCT3 {
% for funct3, val in funct3_dict.items():
% if type(val) != list:
${hex(funct3)}: I32Op::${val.name}({${val.definition}}, uint32_t, IntCustOp);
% else:
${hex(funct3)}: decode FUNCT7 {
% for mdl in val:
${hex(mdl.funct7)}: R32Op::${mdl.name}({${mdl.definition}}, IntCustOp);
% endfor
}
% endif
% endfor
}
% endfor""")

        decoder_patch = dec_templ.render(models=self._exts.models)

        # for now: always choose rv32.isa
        logger.info("Patch the gem5 isa file " + self._isa_decoder)
        with open(self._isa_decoder, 'r') as fh:
            content = fh.readlines()

        # if not existing
        # copy the old .isa file
        gem5_isa_old = self._isa_decoder + '_old'
        if not os.path.exists(gem5_isa_old):
            logger.info('Copy original {}'.format(self._isa_decoder))
            with open(gem5_isa_old, 'w') as fh:
                data = ''.join(content)
                fh.write(data)

        line = len(content) - 2
        content.insert(line, decoder_patch)

        # write back modified content
        with open(self._isa_decoder, 'w') as fh:
            content = ''.join(content)
            fh.write(content)

    def create_FU_timings(self):
        '''
        Retrieve the cycle count information from the models.
        Together with the mask and match value, create a timing for
        every custom instruction.
        '''

        assert os.path.exists(self._buildpath)
        logger.info("Create custom timing file for Minor CPU.")
        timing_templ = Template(r"""<%
%>\
# === AUTO GENERATED FILE ===

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

from m5.objects import *
% for inst in insts:


class MinorFUTiming${inst.name.title()}(MinorFUTiming):
    description = 'Custom${inst.name.title()}'
    match = ${hex(inst.matchvalue)}
    mask = ${hex(inst.maskvalue)}
    srcRegsRelativeLats = [2]
    extraCommitLat = ${inst.cycles - 1}
% endfor


custom_timings = [
% for inst in insts:
    MinorFUTiming${inst.name.title()}(),
% endfor
]
""")

        _FUtimings = timing_templ.render(insts=self._exts.instructions)

        pythonbuildpath = os.path.join(self._buildpath, 'python')
        if not os.path.exists(pythonbuildpath):
            os.makedirs(pythonbuildpath)

        timingfile = os.path.join(pythonbuildpath, 'minor_custom_timings.py')

        with open(timingfile, 'w') as fh:
            fh.write(_FUtimings)

    @property
    def decoder(self):
        return self._decoder

    @property
    def extensions(self):
        return self._exts

    @property
    def regs(self):
        return self._regs
