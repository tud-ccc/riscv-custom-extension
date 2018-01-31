#!/usr/bin/env python

import clang.cindex
import os
import subprocess
import sys

from mako.template import Template


class Model:
    '''
    C++ Reference of the custom instruction.
    '''

    def __init__(self):
        # clang.cindex.Config.set_library_file('/usr/lib/llvm-4.0/lib/libclang-4.0.so')
        index = clang.cindex.Index.create()
        tu = index.parse(
            sys.argv[1], ['-x', 'c++', '-std=c++11'])

        self._name = ""
        self._dfn = ""

        self.method_name(tu.cursor)
        self.method_definitions(tu.cursor)

    def method_name(self, node):
        for child in node.get_children():
            self.method_name(child)

        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL:
            # print(node.spelling)
            self._name = node.spelling

    def method_definitions(self, node):
        for child in node.get_children():
            self.method_definitions(child)

        if node.kind == clang.cindex.CursorKind.COMPOUND_STMT:
            self.extract_definition(node)

    def extract_definition(self, node):
        filename = node.location.file.name
        with open(filename, 'r') as fh:
            contents = fh.read()
        # print(contents[node.extent.start.offset: node.extent.end.offset])
        self._dfn = contents[node.extent.start.offset: node.extent.end.offset]

    @property
    def name(self):
        return self._name

    @property
    def definition(self):
        return self._dfn


class Instructions:
    '''
    Has all necessary information about the custom instructions
    that is needed to extend the RISC-V assembler.
    '''

    def __init__(self, models):
        self._models = models
        self._names = [model.name for model in models]

        self.generate_opc()

    def generate_opc(self):
        opcodes_cust = Template(filename='opcodes-cust.mako')

        opc_cust = 'opcodes-cust'
        with open(opc_cust, 'w') as fh:
            fh.write(opcodes_cust.render(models=self._models))

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

        self._masks = [
            entry for entry in lines if entry.startswith('#define MASK')]
        self._matches = [
            entry for entry in lines if entry.startswith('#define MATCH')]

        assert len(self._masks) == len(
            self._matches), 'Length of mask and match arrays differ'

    @property
    def models(self):
        return self._models

    @property
    def names(self):
        return self._names

    @property
    def masks(self):
        return self._masks

    @property
    def matches(self):
        return self._matches


def parse_model():
    '''
    Parse the c++ reference implementation
    of the custom instruction.
    '''

    model = Model()
    return model


def extend_assembler(models):
    '''
    Create a temporary file from which the opcode
    of the custom instruction is going to be generated.
    '''
    instructions = Instructions(models)

    masks = instructions.masks
    matches = instructions.matches

    # files that needs to be edited
    opch = 'riscv-gnu-toolchain/riscv-binutils-gdb/include/opcode/riscv-opc.h'
    opcc = 'riscv-gnu-toolchain/riscv-binutils-gdb/opcodes/riscv-opc.c'

    # the mask and match defines has to be added in the header file
    with open(opch, 'r') as fh:
        content = fh.readlines()

    for i in range(0, len(masks)):
        # check if entry exists
        # skip this instruction if so
        # prevents double define for old custom extensions, if new one was
        # added
        if masks[i] in content:
            continue

        # first line number, where the new opcode can be inserted is 3
        content.insert(i + 3, masks[i])
        content.insert(i + 3, matches[i])

    with open(opch, 'w') as fh:
        content = ''.join(content)
        fh.write(content)

    # in the c file the asm instruction is defined
    # build string that has to be inserted


def main():
    models = []
    models.append(parse_model())
    extend_assembler(models)


if __name__ == '__main__':
    main()
