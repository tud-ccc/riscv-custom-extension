import logging
import os

from stat import *

from extensions import Extensions
from model import Model

logger = logging.getLogger(__name__)


class Parser:
    '''
    This class stepwise calls all the functions necessary to parse modules
    and retrieve the information necessary to extend gnu binutils and gem5.
    '''

    def __init__(self, args):
        self._args = args
        self._models = []
        self._exts = None
        self._insts = []

        # header file that needs to be edited
        self.opch = os.path.join(os.path.dirname(
            os.path.realpath(__file__)),
            ('../riscv-gnu-toolchain/' +
             'riscv-binutils-gdb/include/opcode/riscv-opc.h'
             ))
        # custom opc.h file
        self.opch_cust = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '../riscv-gnu-toolchain/' +
            'riscv-binutils-gdb/include/opcode/riscv-custom-opc.h')
        # c source file that needs to be edited
        self.opcc = os.path.join(os.path.dirname(
            os.path.realpath(__file__)), '../riscv-gnu-toolchain/' +
            'riscv-binutils-gdb/opcodes/riscv-opc.c')

        assert os.path.exists(self.opch)
        assert os.path.exists(os.path.dirname(self.opch_cust))
        assert os.path.exists(self.opcc)

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
            # remove custom file
            try:
                logger.info('Remove {} from system'.format(self.opch_cust))
                os.remove(self.opch_cust)
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
        self._isfile = False
        if os.path.isdir(self._args.modelpath):
            # restore the toolchain to its defaults
            self.restore()
            logger.info('Traverse over directory')
            self.treewalk(self._args.modelpath)
        else:
            logger.info('Single file, start parsing')
            self._isfile = True
            model = Model(self._args.modelpath)
            self._models.append(model)

        self._exts = Extensions(self._models)
        self._insts = self._exts.instructions

    def treewalk(self, top):
        logger.info('Search for models in {}'.format(top))
        logger.debug('Directory content: {}'.format(os.listdir(top)))
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

        # read the content of riscv opc header
        with open(self.opch, 'r') as fh:
            content = fh.read()

        # if not existing
        # copy the old header file
        # basically generate new file with old content
        opchold = self.opch + '_old'
        if not os.path.exists(opchold):
            logger.info('Copy original {}'.format(self.opch))
            with open(opchold, 'w') as fh:
                fh.write(content)

        # check if we simply want to include a whole directory
        # if so, create a new custom header
        # if not (single file), we extend an existing header if avail
        if self._isfile and os.path.exists(self.opch_cust):
            pass
        else:
            # we include a whole directory
            # at first, we create our own custom opc header file
            # write file
            with open(self.opch_cust, 'w') as fh:
                fh.write(self._exts.cust_header)

        # write the include statement for our custom header
        if '#include "riscv-custom-opc.h"\n' not in content:
            content = '#include "riscv-custom-opc.h"\n' + content

        # write back generated header file
        with open(self.opch, 'w') as fh:
            fh.write(content)

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
            # build string that has to be added to the content of the file
            dfn = '{{"{}",  "I",  "{}", {}, {}, match_opcode, 0 }},\n'.format(
                inst.name, inst.operands, inst.matchname, inst.maskname)

            if dfn in content:
                logger.warn('Instruction already taken, skip')
                continue

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

    def extend_gem5(self):
        '''
        Extend the gem5 decoder. Therefore a new pice of decoder is needed.
        '''
        pass

    @property
    def args(self):
        return self._args

    @property
    def extensions(self):
        return self._exts

    @property
    def instructions(self):
        return self._insts

    @property
    def models(self):
        return self._models
