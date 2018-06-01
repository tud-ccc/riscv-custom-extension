# -*- mode:python -*-

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

import sys
import SCons.Node.FS

Import('*')


def GenFile(filename):
    gen_files.append(File('./build/generated/' + filename))


fs = SCons.Node.FS.get_default_fs()
root = fs.Dir('.')
module_python_path = [root.Dir('python').srcnode().abspath]
sys.path[0:0] = module_python_path

for t in BUILD_TARGETS:
    path_dirs = t.split('/')

    if 'RISCV' in path_dirs:
        import modelparser

        parser = modelparser.ModelParser()
        parser.parse()

        gen_files = []

        main.Append(CPPPATH=[Dir('./build/generated'), Dir('../RISCV/')])
        main.Append(CPPDEFINES=['TRACING_ON=1'])

        GenFile('decoder.cc')
        GenFile('inst-constrs.cc')
        GenFile('generic_cpu_exec.cc')

        main.Library('riscv-extensions',
                     [main.SharedObject(f) for f in gen_files])

        main.Append(LIBS=['riscv-extensions'])
        main.Append(LIBPATH=[Dir('.')])
