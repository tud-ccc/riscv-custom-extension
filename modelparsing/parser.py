import clang.cindex
import logging
import os
import subprocess

from exceptions import ConsistencyError
from exceptions import OpcodeError
from mako.template import Template
from stat import *


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
        self._check_op2 = False
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
                self._check_op2 = True
            if node.spelling.startswith('imm'):
                logger.info('Model is of format I-Type')
                self._form = 'I'
                self._check_op2 = True

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
        logger.debug('Definition:\n%s' % self._dfn)

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
        if not self._check_op2:
            raise ConsistencyError(
                self._check_op2, 'Model definition requires parameter Op2')

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

    def __init__(self, form, mask, match, name):
        self._form = form  # format
        self._mask = mask  # the whole mask string
        self._match = match  # the whole match string
        self._name = name  # the name that shall occure in the assembler
        # the mask name
        self._maskname = mask.split()[-2]
        # the mask value
        self._maskvalue = mask.split()[-1]
        # the match name
        self._matchname = match.split()[-2]
        # the match value
        self._matchvalue = match.split()[-1]

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
    def maskvalue(self):
        return self._maskvalue

    @property
    def match(self):
        return self._match

    @property
    def matchname(self):
        return self._matchname

    @property
    def matchvalue(self):
        return self._matchvalue

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

        # riscv-opcodes path
        self._rv_opc = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '../riscv-opcodes')

        self._opc_templ = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'opcodes-custom.mako')

        # files of riscv-opcodes project
        self._rv_opc_parser = os.path.join(self._rv_opc, 'parse-opcodes')

        # opcode files
        self._rv_opc_files = []
        self._rv_opc_files.append(os.path.join(self._rv_opc, 'opcodes'))
        self._rv_opc_files.append(os.path.join(self._rv_opc, 'opcodes-custom'))
        self._rv_opc_files.append(os.path.join(self._rv_opc, 'opcodes-pseudo'))
        self._rv_opc_files.append(os.path.join(self._rv_opc, 'opcodes-rvc'))
        self._rv_opc_files.append(os.path.join(
            self._rv_opc, 'opcodes-rvc-pseudo'))

        self.models_to_ops()
        self.ops_to_insts()

    def models_to_ops(self):
        logger.info('Generate operations from models')

        for model in self._models:
            op = Operation(model.form,
                           model.funct3,
                           model.funct7,
                           model.name,
                           model.opc)
            self._ops.append(op)

    def ops_to_insts(self):
        logger.info('Generate instructions from operations')
        # use a mako template to generate files, that are equal to the ones
        # in the riscv-opcodes project
        opcodes_cust = Template(filename=self._opc_templ)
        # opcodes custom is the file, that was generated
        opc_cust = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), 'opcodes-custom')
        self._rv_opc_files.append(opc_cust)

        # render custom opcodes template
        with open(opc_cust, 'w') as fh:
            fh.write(opcodes_cust.render(operations=self._ops))

        with open(opc_cust, 'r') as fh:
            content = fh.read()

        # start parse_opcodes script with our custom instructions
        p = subprocess.Popen([self._rv_opc_parser,
                              '-c'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        defines, err = p.communicate(input=content)

        if not defines or err:
            # an error occured
            logger.error(err.rstrip())
            try:
                os.remove(opc_cust)
            except OSError:
                pass
            raise OpcodeError('Function opcode could not be generated')

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
        assert len(masks) == len(
            self._ops), 'Opcodes of some operations overlapped'

        # create instructions
        for i in range(0, len(self._ops)):
            inst = Instruction(self._models[i].form,
                               masks[i],
                               matches[i],
                               self._models[i].name)
            self._insts.append(inst)

        # join the content of all opcode files
        # used to generate a single riscv-opc.h containing all operations
        opcodes = ''.join([open(f).read() for f in self._rv_opc_files])

        p = subprocess.Popen([self._rv_opc_parser,
                              '-c'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        # for now just save the output string, used later
        self._rv_opc_header, err = p.communicate(input=opcodes)

        try:
            logger.error(err.rstrip())
            os.remove(opc_cust)
        except OSError:
            pass

        if not self._rv_opc_header or err:
            raise OpcodeError('Function opcode could not be generated')

    @property
    def models(self):
        return self._models

    @property
    def operations(self):
        return self._ops

    @property
    def instructions(self):
        return self._insts

    @property
    def opc_header(self):
        return self._rv_opc_header


class Parser:
    '''
    This class stepwise calls all the functions necessary to parse modules
    and retrieve the information necessary to extend gnu binutils and gem5.
    '''

    def __init__(self, args):
        self._args = args
        self._models = []

        # header file that needs to be edited
        self.opch = os.path.dirname(
            os.path.realpath(__file__)) + '/../riscv-gnu-toolchain/'\
            + 'riscv-binutils-gdb/include/opcode/riscv-opc.h'
        # c source file that needs to be edited
        self.opcc = os.path.dirname(
            os.path.realpath(__file__)) + '/../riscv-gnu-toolchain/'\
            + 'riscv-binutils-gdb/opcodes/riscv-opc.c'

    def restore(self):
        '''
        Restore the toolchain to its defaults.
        '''

        logger.info('Remove custom instructions from GNU binutils files')

        self.restore_header()
        self.restore_source()

    def restore_header(self):
        '''
        Remove all custom extensions.
        Restores the saved old header.
        '''

        logger.info('Restore original header file')
        opchold = self.opch + '_old'
        if os.path.exists(opchold):
            logger.info('Restore contents from file {}'.format(opchold))
            with open(opchold, 'r') as fh:
                content = fh.read()

            with open(self.opch, 'w') as fh:
                fh.write(content)

            logger.info('Original header restored')

            try:
                logger.info('Remove {} from system'.format(opchold))
                os.remove(opchold)
            except OSError:
                pass
        else:
            logger.info('Nothing to do')

    def restore_source(self):
        '''
        Restores the saved old source.
        '''

        logger.info('Restore original source file')
        opccold = self.opcc + '_old'
        if os.path.exists(opccold):
            logger.info('Restore contents from file {}'.format(opccold))
            with open(opccold, 'r') as fh:
                content = fh.read()

            with open(self.opcc, 'w') as fh:
                fh.write(content)

            logger.info('Original source restored')

            try:
                logger.info('Remove {} from system'.format(opccold))
                os.remove(opccold)
            except OSError:
                pass
        else:
            logger.info('Nothing to do')

    def parse_models(self):
        '''
        Parse the c++ reference implementation
        of the custom instruction.
        '''

        logger.info('Determine if modelpath is a folder or a single file')
        if os.path.isdir(self._args.modelpath):
            logger.info('Traverse over directory')
            self.treewalk(self._args.modelpath)
        else:
            logger.info('Single file, start parsing')
            model = Model(self._args.modelpath)
            self._models.append(model)

        self._exts = Extensions(self._models)
        self._insts = self._exts.instructions

    def treewalk(self, top):
        logger.info('Search for models in {}'.format(top))
        for file in os.listdir(top):
            pathname = os.path.join(top, file)
            mode = os.stat(pathname)[ST_MODE]

            if S_ISDIR(mode):
                # directory
                self.treewalk(pathname)
            elif S_ISREG(mode):
                # file
                if pathname.endswith('.cc'):
                    logger.info(
                        'Found model definition in file {}'.format(pathname))
                    model = Model(pathname)
                    self._models.append(model)
            else:
                # unknown file type
                logger.info('Unknown file type, skip')

    def extend_compiler(self):
        '''
        Calls functions to extend necessary header and c files.
        After that, the toolchain will be rebuild.
        Then the compiler should know the custom instructions.
        '''

        # in the meantime instructions may been deletet from the list
        # insts = extend_header(insts)
        self.extend_header()

        # return value should be the same as the function parameter because in
        # extend_headers all previously included instructions should have been
        # removed.
        # insts = extend_source(insts)
        self.extend_source()

    def extend_header(self):
        '''
        Extend the header file riscv-opc.h with the generated masks and matches
        of the custom instructions.
        '''

        # check if custom opc header was already included
        with open(self.opch, 'r') as fh:
            content = fh.readlines()

        # if not existing
        # copy the old header file
        # basically generate new file with old content
        opchold = self.opch + '_old'
        if not os.path.exists(opchold):
            logger.info('Copy original {}'.format(self.opch))
            with open(opchold, 'w') as fh:
                data = ''.join(content)
                fh.write(data)

        # TODO: define some error cases
        # TODO: better in extension class

        # write back generated header file
        with open(self.opch, 'w') as fh:
            fh.write(self._exts.opc_header)

    def extend_source(self):
        '''
        Extend the source file riscv-opc.c with information about the
        custom instructions.
        '''

        # read source file
        with open(self.opcc, 'r') as fh:
            content = fh.readlines()

        # if not existing
        # copy the old source file
        # basically generate new file with old content
        opccold = self.opcc + '_old'
        if not os.path.exists(opccold):
            logger.info('Copy original {}'.format(self.opcc))
            with open(opccold, 'w') as fh:
                data = ''.join(content)
                fh.write(data)

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
        with open(self.opcc, 'w') as fh:
            content = ''.join(content)
            fh.write(content)

    @property
    def args(self):
        return self._args

    @property
    def models(self):
        return self._models

    @property
    def instructions(self):
        return self._insts
