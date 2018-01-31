#!/usr/bin/env python

import clang.cindex
from mako.template import Template
import sys


class Model:

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
    model = Model()

    name = model.name
    print(name)

    dfn = model.definition
    print(dfn)

    return model


def create_file(model):

    opcodes_cust = Template(filename='opcodes-cust.mako')

    with open('opcodes-cust', 'w') as fh:
        fh.write(opcodes_cust.render(name=model.name))


def main():
    model = parse_model()
    create_file(model)


if __name__ == '__main__':
    main()
