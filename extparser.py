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


def parse_model():
    '''
    Parse the c++ reference implementation
    of the custom instruction.
    '''

    model = Model()
    return model


def create_opcode(models):
    '''
    Create a temporary file from which the opcode
    of the custom instruction is going to be generated.
    '''

    opcodes_cust = Template(filename='opcodes-cust.mako')

    opc_cust = 'opcodes-cust'
    with open(opc_cust, 'w') as fh:
        fh.write(opcodes_cust.render(models=models))

    with open(opc_cust, 'r') as fh:
        ops = fh.read()

    try:
        os.remove(opc_cust)
    except OSError:
        pass

    p = subprocess.Popen(['riscv-opcodes/parse-opcodes',
                          '-c'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    defines, _ = p.communicate(input=ops)

    d = '\n'
    lines = [e + d for e in defines.split(d)]

    masks = [entry for entry in lines if entry.startswith('#define MASK')]
    matches = [entry for entry in lines if entry.startswith('#define MATCH')]

    assert len(masks) == len(matches), 'Length of mask and match arrays differ'

    print(masks)
    print(matches)

    opc = 'riscv-gnu-toolchain/riscv-binutils-gdb/include/opcode/riscv-opc.h'
    with open(opc, 'r') as fh:
        content = fh.readlines()

    # first line number is 3
    for i in range(0, len(masks)):
        content.insert(i + 3, masks[i])
        content.insert(i + 3, matches[i])

    with open(opc, 'w') as fh:
        content = ''.join(content)
        fh.write(content)


def main():
    models = []
    models.append(parse_model())
    create_opcode(models)


if __name__ == '__main__':
    main()
