#!/usr/bin/env python

import argparse
import clang.cindex
import logging
import os
import subprocess
import sys

from mako.template import Template

logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)


class Model:
    '''
    C++ Reference of the custom instruction.
    '''

    def __init__(self, impl):

        clang.cindex.Config.set_library_file('/usr/lib64/llvm/libclang.so')
        # clang.cindex.Config.set_library_file('/usr/lib/llvm-4.0/lib/libclang-4.0.so')

        logger.info("Using libclang at %s" % clang.cindex.Config.library_file)

        index = clang.cindex.Index.create()
        tu = index.parse(impl, ['-x', 'c++', '-std=c++11'])

        self._dfn = ''
        self._form = 'regreg'
        self._funct3 = 0x0
        self._funct7 = 0x0
        self._name = ''
        self._opc = 0x0

        logger.info("Parsing model @ %s" % impl)

        self.parse_model(tu.cursor)

    def parse_model(self, node):
        '''
        Parse the model and search for all necessary information.
        '''
        for child in node.get_children():
            self.parse_model(child)

        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            self._name = node.spelling
            logger.info("Function name: %s" % self._name)

        if node.kind == clang.cindex.CursorKind.COMPOUND_STMT:
            logger.info("Model definition found")
            self.extract_definition(node)

        if node.kind == clang.cindex.CursorKind.VAR_DECL \
                and node.spelling == 'opc':
            logger.info('Model opcode found')
            self._opc = self.extract_value(node)

        if node.kind == clang.cindex.CursorKind.VAR_DECL \
                and node.spelling == 'funct3':
            logger.info('Model funct3 found')
            self._funct3 = self.extract_value(node)

        if node.kind == clang.cindex.CursorKind.VAR_DECL \
                and node.spelling == 'funct3':
            logger.info('Model funct7 found')
            self._funct7 = self.extract_value(node)

    def extract_definition(self, node):
        '''
        Extract a function definition.
        '''
        filename = node.location.file.name
        with open(filename, 'r') as fh:
            contents = fh.read()

        self._dfn = contents[node.extent.start.offset: node.extent.end.offset]

        logger.info("Definintion in %s @ line %d" %
                    (filename, node.location.line))
        logger.info('Definition:\n%s' % self._dfn)

    def extract_value(self, node):
        '''
        Extract a variable value.
        '''
        for entry in list(node.get_tokens()):
            if entry.spelling.startswith("0x"):
                logger.info('Value: %s' % entry.spelling)
                return int(entry.spelling, 0)

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


class Operation:
    '''
    Represents one operation, that is parsed from each model.
    '''

    def __init__(self, form, funct3, funct7, name, opc):
        self._form = form  # format
        self._funct3 = funct3  # funct3 encoding
        self._funct7 = funct7  # funct7 encoding, used by reg reg ops
        self._name = name  # the name that shall occure in the assembler
        self._opc = opc  # opcode - inst[6:2]

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


class Instruction:
    '''
    Class, that represents one single custom instruction.
    Contains the name, the mask and the match.
    '''

    def __init__(self, form, mask, match, name):
        self._form = form  # format
        self._mask = mask  # the mask name
        self._match = match  # the match name
        self._name = name  # the name that shall occure in the assembler

    @property
    def form(self):
        return self._form

    @property
    def mask(self):
        return self._mask

    @property
    def match(self):
        return self._match

    @property
    def name(self):
        return self._name


class Extensions:
    '''
    Has all necessary information about the custom instructions
    that is needed to extend the RISC-V compiler.
    '''

    def __init__(self, models):
        self._models = models
        self._ops = []
        self._insts = []

        self.models_to_ops()
        self.ops_to_insts()

    def models_to_ops(self):
        logger.info("Generate operations from models")

        for model in self._models:
            op = Operation(model.form,
                           model.funct3,
                           model.funct7,
                           model.name,
                           model.opc)
            self._ops.append(op)

    def ops_to_insts(self):
        opcodes_cust = Template(filename='opcodes-custom.mako')

        opc_cust = 'opcodes-custom'
        with open(opc_cust, 'w') as fh:
            fh.write(opcodes_cust.render(operations=self._ops))

        with open(opc_cust, 'r') as fh:
            ops = fh.read()

        try:
            os.remove(opc_cust)
        except OSError:
            pass

        p = subprocess.Popen(['riscv-opcodes/parse-opcodes',
                              '-c'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        defines, _ = p.communicate(input=ops)

        d = '\n'
        lines = [e + d for e in defines.split(d)]

        masks = [
            entry for entry in lines if entry.startswith('#define MASK')]
        matches = [
            entry for entry in lines if entry.startswith('#define MATCH')]

        assert len(masks) == len(
            matches), 'Length of mask and match arrays differ'

        for i in range(0, len(self._ops)):
            inst = Instruction(self._models[i].form,
                               masks[i],
                               matches[i],
                               self._models[i].name)
            self._insts.append(inst)

    @property
    def models(self):
        return self._models

    @property
    def operations(self):
        return self._ops

    @property
    def instructions(self):
        return self._insts


def parse_models(args):
    '''
    Parse the c++ reference implementation
    of the custom instruction.
    '''
    model = Model(args.model)
    return [model]


def extend_assembler(models):
    '''
    Create a temporary file from which the opcode
    of the custom instruction is going to be generated.
    '''
    extensions = Extensions(models)

    insts = extensions.instructions

    # files that needs to be edited
    opch = 'riscv-gnu-toolchain/riscv-binutils-gdb/include/opcode/riscv-opc.h'
    opcc = 'riscv-gnu-toolchain/riscv-binutils-gdb/opcodes/riscv-opc.c'

    # the mask and match defines has to be added in the header file
    with open(opch, 'r') as fh:
        content = fh.readlines()

    for inst in insts:
        # check if entry exists
        # skip this instruction if so
        # prevents double define for old custom extensions, if new one was
        # added
        if inst.mask in content and inst.match in content:
            logger.info(
                "Mask already in riscv-opc.h, therefore skip instertion")
            continue

        # check whether a mask or a match entry exists but not the
        # corresponding other
        if inst.mask in content or inst.match in content:
            logger.warn(
                "Mask or match already existing, but the other not. " +
                "Skip insertion")
            continue

        # first line number, where the new opcode can be inserted is 3
        # insert every entry at line number 3 --> push back the remaining
        # content
        content.insert(3, inst.mask)
        content.insert(3, inst.match)

    with open(opch, 'w') as fh:
        content = ''.join(content)
        fh.write(content)

    # in the c file the asm instruction is defined
    # build string that has to be inserted

    inst_def_templ = Template(filename='inst-definition.mako')
    inst_def = 'inst_def'

    with open(inst_def, 'w') as fh:
        fh.write(inst_def_templ.render(extensions=extensions,
                                       opcc=opcc))


def main():
    '''
    Main function.
    '''

    # argparsing
    parser = argparse.ArgumentParser(
        prog='extparser',
        description='Parse reference implementations of custom extension ' +
        'models.')

    parser.add_argument('-v',
                        '--verbosity',
                        default=0,
                        action='count',
                        help='Increase output verbosity.')
    parser.add_argument('-b',
                        '--build',
                        action='store_true',
                        help='If set, Toolchain and Gem5 will be ' +
                        'rebuild.')
    parser.add_argument('-m',
                        '--model',
                        type=str,
                        default=os.path.join(
                            os.path.dirname(__file__),
                            'extensions',
                            'test.cc'),
                        help='Reference implementation')

    args = parser.parse_args()

    logger.setLevel(50 - 10 * args.verbosity)

    # start parsing the models
    models = parse_models(args)
    # extend assembler with models
    extend_assembler(models)


if __name__ == '__main__':
    main()
