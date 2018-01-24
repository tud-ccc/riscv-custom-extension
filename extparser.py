#!/usr/bin/env python

import clang.cindex
import sys


# List of AST node objects that are function calls
function_calls = []
# List of AST node objects that are fucntion declarations
function_declarations = []


# Traverse the AST tree
def traverse(node):

    # Recurse for children of this node
    for child in node.get_children():
        traverse(child)

    # Add the node to function_calls
    if node.type == clang.cindex.CursorKind.CALL_EXPR:
        function_calls.append(node)

    # Add the node to function_declarations
    if node.type == clang.cindex.CursorKind.FUNCTION_DECL:
        function_declarations.append(node)

    # Print out information about the node
    print('Found %s [line=%s, col=%s]' %
          (node.displayname, node.location.line, node.location.column))


index = clang.cindex.Index.create()
tu = index.parse(
    sys.argv[1], ['-x', 'c++', '-std=c++11', '-D__CODE_GENERATOR__'])

traverse(tu.cursor)
