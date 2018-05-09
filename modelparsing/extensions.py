import logging
import os
import subprocess

from mako.template import Template

from exceptions import OpcodeError
from instruction import Instruction

logger = logging.getLogger(__name__)


class Extensions:
    '''
    Has all necessary information about the custom instructions
    that is needed to extend the RISC-V compiler.
    '''

    def __init__(self, models):
        self._models = models
        self._insts = []

        # riscv-opcodes path
        self._rv_opc = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '../riscv-opcodes')

        self._opc_templ = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'opcodes-custom.mako')

        # files of riscv-opcodes project
        self._rv_opc_parser = os.path.join(self._rv_opc, 'parse-opcodes')

        # opcode files
        self._rv_opc_files = []
        self._rv_opc_files.append(os.path.join(self._rv_opc, 'opcodes-pseudo'))
        self._rv_opc_files.append(os.path.join(self._rv_opc, 'opcodes'))
        self._rv_opc_files.append(os.path.join(
            self._rv_opc, 'opcodes-rvc-pseudo'))
        self._rv_opc_files.append(os.path.join(self._rv_opc, 'opcodes-rvc'))
        self._rv_opc_files.append(os.path.join(self._rv_opc, 'opcodes-custom'))

        self.gen_instructions()

    def check_opcodes(self, inst):
        # check for overlapping opcodes
        # NOTE: Until fix in riscv/riscv-opcodes we have to do it manually.
        # Therefore we do the check here, instead of checking it while adding
        # the model. This way the tests doesn't have to be adapted, once the
        # script is patched.
        logger.info('Checking if opcodes overlap')
        logger.debug('{} {}'.format(inst.name, inst.form))
        for inst2 in self._insts:
            if inst2.name == inst.name:
                # same instruction
                # skip
                continue
            if inst2.form == 'R':
                if (inst2.matchvalue & inst.maskvalue) == inst.matchvalue:
                    logger.debug('{}.match {}'.format(
                        inst.name, hex(inst.matchvalue)))
                    logger.debug('{}.match {}'.format(
                        inst.name, hex(inst.maskvalue)))
                    logger.debug('{}.match {}'.format(
                        inst2.name, hex(inst2.matchvalue)))
                    logger.debug('{}.match {}'.format(
                        inst2.name, hex(inst2.maskvalue)))
                    logger.error('{} and {} overlap'.format(
                        inst.name, inst2.name))
                    raise OpcodeError('Function opcode could not be generated')
            if inst2.form == 'I':
                if (inst2.matchvalue & inst.maskvalue) == (
                        inst.matchvalue & inst2.maskvalue):
                    logger.debug('{}.match {}'.format(
                        inst.name, hex(inst.matchvalue)))
                    logger.debug('{}.match {}'.format(
                        inst.name, hex(inst.maskvalue)))
                    logger.debug('{}.match {}'.format(
                        inst2.name, hex(inst2.matchvalue)))
                    logger.debug('{}.match {}'.format(
                        inst2.name, hex(inst2.maskvalue)))
                    logger.error('{} and {} overlap'.format(
                        inst.name, inst2.name))
                    raise OpcodeError('Function opcode could not be generated')

    def gen_instructions(self):
        logger.info('Generate instructions from operations')
        # use a mako template to generate files, that are equal to the ones
        # in the riscv-opcodes project
        opcodes_cust = Template(r"""<%
%>\
% for operation in operations:
% if operation.form == 'R':
${operation.name} rd rs1 rs2 31..25=${operation.funct7} 14..12=${operation.funct3} 6..2=${operation.opc} 1..0=3
% elif operation.form == 'I':
${operation.name} rd rs1 imm12 14..12=${operation.funct3} 6..2=${operation.opc} 1..0=3
% else:
Format not supported.
<% return STOP_RENDERING %>
%endif
% endfor""")
        # # opcodes custom is the file, that was generated
        # opc_cust = os.path.join(os.path.dirname(
        #     os.path.realpath(__file__)), 'opcodes-custom')
        # self._rv_opc_files.append(opc_cust)

        # # render custom opcodes template
        # with open(opc_cust, 'w') as fh:
        #     fh.write(opcodes_cust.render(operations=self._models))

        # with open(opc_cust, 'r') as fh:
        #     content = fh.read()

        content = opcodes_cust.render(operations=self._models)

        # start parse_opcodes script with our custom instructions
        p = subprocess.Popen([self._rv_opc_parser,
                              '-c'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        defines, err = p.communicate(input=content)

        if not defines or err:
            # an error occured
            # try:
            #     os.remove(opc_cust)
            # except OSError:
            #     pass
            logger.error(err.rstrip())
            raise OpcodeError('Function opcode could not be generated')

        # adapt the defines
        defines = defines.replace(
            'RISCV_ENCODING_H', 'RISCV_CUSTOM_ENCODING_H', 2)
        defines = defines.replace('DECLARE_CSR', 'DECLARE_CUSTOM_CSR')
        defines = defines.replace('DECLARE_CAUSE', 'DECLARE_CUSTOM_CAUSE')
        self._cust_header = defines

        # split the stdout output
        # newline character is used as seperator
        d = '\n'
        lines = [e + d for e in defines.split(d)]

        # collect all masks
        masks = [
            entry for entry in lines if entry.startswith('#define MASK')]
        # collect all entrys
        matches = [
            entry for entry in lines if entry.startswith('#define MATCH')]

        # just for sanity, should never go wrong
        assert len(masks) == len(
            matches), 'Length of mask and match arrays differ'

        # create instructions
        for i in range(0, len(self._models)):
            inst = Instruction(self._models[i].form,
                               masks[i],
                               matches[i],
                               self._models[i].name)
            self._insts.append(inst)

        # check opcodes for not captured errors
        for inst in self._insts:
            self.check_opcodes(inst)

        # # join the content of all opcode files
        # # used to generate a single riscv-opc.h containing all operations
        # opcodes = ''.join([open(f).read() for f in self._rv_opc_files])

        # p = subprocess.Popen([self._rv_opc_parser,
        #                       '-c'],
        #                      stdin=subprocess.PIPE,
        #                      stdout=subprocess.PIPE,
        #                      stderr=subprocess.PIPE)
        # # for now just save the output string, used later
        # self._rv_opc_header, err = p.communicate(input=opcodes)

        # try:
        #     os.remove(opc_cust)
        # except OSError:
        #     pass

        # if not self._rv_opc_header or err:
        #     raise OpcodeError('Function opcode could not be generated')

    @property
    def models(self):
        return self._models

    @property
    def instructions(self):
        return self._insts

    @property
    def cust_header(self):
        return self._cust_header
