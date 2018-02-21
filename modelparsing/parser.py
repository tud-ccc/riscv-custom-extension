import clang.cindex
import logging
import os
import subprocess

from exceptions import ConsistencyError
from mako.template import Template


logger = logging.getLogger(__name__)


class Model:
    '''
    C++ Reference of the custom instruction.
    '''

    def __init__(self, impl):
        '''
        Init method, that takes the location of
        the implementation as an argument.
        '''

        logger.info("Using libclang at %s" % clang.cindex.Config.library_file)

        self.compile_model(impl)

        index = clang.cindex.Index.create()
        tu = index.parse(impl, ['-x', 'c++', '-c', '-std=c++11'])

        # information to retrieve form model
        self._dfn = ''              # definition
        self._form = ''             # format
        self._funct3 = 0xff         # funct3 bit field
        self._funct7 = 0xff         # funct7 bit field
        self._name = ''             # name
        self._opc = 0x0             # opcode
        # model consistency checks
        self._check_rd = False      # check if rd is defined
        self._check_rs1 = False     # check if rs1 is defined
        self._rettype = ''

        logger.info("Parsing model @ %s" % impl)

        self.parse_model(tu.cursor)
        self.check_consistency()

    def compile_model(self, file):
        logger.info('Compile model {}'.format(file))
        p = subprocess.Popen([r'g++',
                              '-fsyntax-only',
                              '-Wall',
                              '-std=c++11',
                              '-c',
                              file],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        (_, ret) = p.communicate()

        if ret:
            logger.error(ret)
            raise ConsistencyError(file, 'Compile error.')

    def parse_model(self, node):
        '''
        Parse the model and search for all necessary information.
        '''
        for child in node.get_children():
            self.parse_model(child)

        # only set name if it's unset
        # due to parsing of included header the function definition occures
        # twice
        if node.kind == clang.cindex.CursorKind.FUNCTION_DECL \
                and self._name == '':
            # save name
            self._name = node.spelling
            # save rettype for consistency check
            self._rettype = list(node.get_tokens())[0].spelling
            logger.info("Function name: {}".format(self._name))

        if node.kind == clang.cindex.CursorKind.COMPOUND_STMT:
            logger.info("Model definition found")
            self.extract_definition(node)

        if node.kind == clang.cindex.CursorKind.VAR_DECL:
            # process all variable declarations
            # opcode
            if node.spelling == 'opc':
                logger.info('Model opcode found')
                self._opc = self.extract_value(node)
            # funct3 bitfield
            if node.spelling == 'funct3':
                logger.info('Model funct3 found')
                self._funct3 = self.extract_value(node)
            # funct7 bitfield, only for R-Type
            if node.spelling == 'funct7':
                logger.info('Model funct7 found')
                self._funct7 = self.extract_value(node)

        if node.kind == clang.cindex.CursorKind.PARM_DECL:
            # process all parameter declarations
            # check if Rd and Rs1 exists
            if node.spelling.startswith('Rd'):
                self._check_rd = True
            if node.spelling.startswith('Rs1'):
                self._check_rs1 = True

            # determine, if function is R-Type or I-Type
            if node.spelling.startswith('Rs2'):
                logger.info('Model is of format R-Type')
                self._form = 'R'
            if node.spelling.startswith('imm'):
                logger.info('Model is of format I-Type')
                self._form = 'I'

    def extract_definition(self, node):
        '''
        Extract a function definition.
        '''
        filename = node.location.file.name
        with open(filename, 'r') as fh:
            contents = fh.read()

        self._dfn = contents[node.extent.start.offset: node.extent.end.offset]

        logger.info("Definintion in {} @ line {}".format(
            filename, node.location.line))
        logger.info('Definition:\n%s' % self._dfn)

    def extract_value(self, node):
        '''
        Extract a variable value.
        '''
        for entry in list(node.get_tokens()):
            if entry.spelling[0].isdigit():
                logger.info('Value: %s' % entry.spelling)
                return int(entry.spelling, 0)

    def check_consistency(self):
        '''
        Check whether a model fulfills all consistency requirements.
        '''
        logger.info('Check consistency of model definition')

        # check function definition
        # does rd and rs1 exist?
        # both are required for R and I type
        if not self._check_rd:
            raise ConsistencyError(
                self._check_rd, 'Model definition requires parameter Rd')
        if not self._check_rs1:
            raise ConsistencyError(
                self._check_rs1, 'Model definition requires parameter Rs1')
        # check if operand 2 was defined

        # check return type of function
        if not self._rettype == 'void':
            raise ConsistencyError(
                self._rettype, 'Function has to be of type void.')

        if self._opc not in [0x02, 0x0a, 0x16, 0x1e]:
            raise ValueError(self._opc, 'Invalid opcode.')

        # funct3 --> 3 bits
        if self._funct3 > 0x7:
            raise ValueError(self._funct3, 'Invalid funct3.')
        # funct7 --> 7 bits
        if self._form == 'R' and self._funct7 > 0x7f:
            raise ValueError(self._funct7, 'Invalid funct7.')

        # does the definition starts and end with a bracket
        if not self._dfn.startswith('{'):
            raise ConsistencyError(
                self._dfn, 'Function definition not found.')
        if not self._dfn.endswith('}'):
            raise ConsistencyError(
                self._dfn, 'Closing bracket missing.')

        logger.info('Model meets requirements')

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
    This class is just used temporarily on the way to create
    instructions from the models.
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

    def __init__(self, form, mask, maskname, match, matchname, name):
        self._form = form  # format
        self._mask = mask  # the whole mask string
        self._maskname = maskname  # the mask name
        self._match = match  # the whole match string
        self._matchname = matchname  # the match name
        self._name = name  # the name that shall occure in the assembler

        # set right operands that are used in binutils' opc parsing
        # d -> Rd
        # s -> Rs1
        # t -> Rs2
        # j -> imm
        if form == 'R':
            # operands for Rd, Rs1, Rs2
            self._operands = 'd,s,t'
        elif form == 'I':
            # operands for Rd, Rs1, imm
            self._operands = 'd,s,j'
        else:
            logger.warn('Instruction format unnokwn. ' +
                        'Leaving operands field empty.')
            self.operands = ''

    @property
    def form(self):
        return self._form

    @property
    def mask(self):
        return self._mask

    @property
    def maskname(self):
        return self._maskname

    @property
    def match(self):
        return self._match

    @property
    def matchname(self):
        return self._matchname

    @property
    def name(self):
        return self._name

    @property
    def operands(self):
        return self._operands


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
        opcodes_cust = Template(filename='modelparsing/opcodes-custom.mako')

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
        masknames = [
            entry for entry in masks for entry in entry.split()
            if entry.startswith('MASK')]
        matches = [
            entry for entry in lines if entry.startswith('#define MATCH')]
        matchnames = [
            entry for entry in matches for entry in entry.split()
            if entry.startswith('MATCH')]

        assert len(masks) == len(
            matches), 'Length of mask and match arrays differ'

        for i in range(0, len(self._ops)):
            inst = Instruction(self._models[i].form,
                               masks[i],
                               masknames[i],
                               matches[i],
                               matchnames[i],
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


class Parser:
    '''
    This class stepwise calls all the functions necessary to parse modules
    and retrieve the information necessary to extend gnu binutils and gem5.
    '''

    def __init__(self, args):
        self._args = args
        self._models = []

        # start parsing the models
        self.parse_models()
        # extend comiler with models
        self.extend_compiler()

    def parse_models(self):
        '''
        Parse the c++ reference implementation
        of the custom instruction.
        '''
        model = Model(self._args.model)
        self._models.append(model)

    def extend_header(self):
        '''
        Extend the header file riscv-opc.h with the generated masks and matches
        of the custom instructions.
        '''

        # header file that needs to be edited
        opch = 'riscv-gnu-toolchain/riscv-binutils-gdb/include/opcode/riscv-opc.h'
        # the mask and match defines has to be added in the header file
        with open(opch, 'r') as fh:
            content = fh.readlines()

        for inst in self._insts:
            # check if entry exists
            # skip this instruction if so
            # prevents double define for old custom extensions, if new one was
            # added
            if inst.mask in content and inst.match in content:
                logger.info(
                    'Mask {!r} and match {!r} '.format(inst.mask, inst.match) +
                    'already in riscv-opc.h. Therefore skip instertion')
                # remove instruction from list to prevent generating duplicates
                # insts.remove(inst)
                continue

            # check whether a mask or a match entry exists but not the
            # corresponding other
            if inst.mask in content or inst.match in content:
                logger.warn(
                    "Mask or match already existing, but the other not. " +
                    "Skip insertion")
                # remove instruction from list to prevent generating duplicates
                self._insts.remove(inst)
                continue

            # first line number, where the new opcode can be inserted is 3
            # insert every entry at line number 3 --> push back the remaining
            # content
            logger.info("Adding mask %s" % inst.mask)
            content.insert(3, inst.mask)
            logger.info("Adding match %s" % inst.match)
            content.insert(3, inst.match)

        # write back modified content
        with open(opch, 'w') as fh:
            content = ''.join(content)
            fh.write(content)

    def extend_source(self):
        '''
        Extend the source file riscv-opc.c with information about the
        custom instructions.
        '''

        # c source file that needs to be edited
        opcc = 'riscv-gnu-toolchain/riscv-binutils-gdb/opcodes/riscv-opc.c'
        # read source file
        with open(opcc, 'r') as fh:
            content = fh.readlines()

        for inst in self._insts:
            # check if entry exists
            # skip this instruction if so
            # prevents double define for old custom extensions, if new one was
            # added
            if any(inst.name in string for string in content):
                logger.info(
                    'Instruction {} already defined. Skip instertion'.format(
                        inst.name))
                # remove instruction from list
                self._insts.remove(inst)
                continue

            # build string that has to be added to the content of the file
            dfn = '{{"{}",  "I",  "{}", {}, {}, match_opcode, 0 }},\n'.format(
                inst.name, inst.operands, inst.matchname, inst.maskname)

            # we simply add the instruction right before the termination of the
            # list in riscv-opc.c
            try:
                line = content.index('/* Terminate the list.  */\n') - 1
            except ValueError:
                # choose random line number near the end of the file
                line = len(content) - 4

            logger.info('Adding instruction {}'.format(inst.name))
            content.insert(line, dfn)

        # write back modified content
        with open(opcc, 'w') as fh:
            content = ''.join(content)
            fh.write(content)

    def extend_compiler(self):
        '''
        Calls functions to extend necessary header and c files.
        After that, the toolchain will be rebuild.
        Then the compiler should know the custom instructions.
        '''
        self._insts = Extensions(self._models).instructions

        # in the meantime instructions may been deletet from the list
        # insts = extend_header(insts)
        self.extend_header()

        # return value should be the same as the function parameter because in
        # extend_headers all previously included instructions should have been
        # removed.
        # insts = extend_source(insts)
        self.extend_source()
