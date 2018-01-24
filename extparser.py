#!/usr/bin/env python

import clang.cindex
import sys


def method_definitions(node):
    for child in node.get_children():
        method_definitions(child)

    if node.kind == clang.cindex.CursorKind.COMPOUND_STMT:
        extract_definition(node)


def extract_definition(node):
    filename = node.location.file.name
    with open(filename, 'r') as fh:
        contents = fh.read()
    print(contents[node.extent.start.offset: node.extent.end.offset])


index = clang.cindex.Index.create()
tu = index.parse(
    sys.argv[1], ['-x', 'c++', '-std=c++11'])

method_definitions(tu.cursor)
