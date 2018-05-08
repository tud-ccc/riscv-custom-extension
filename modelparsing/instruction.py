import logging

logger = logging.getLogger(__name__)


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
        self._maskvalue = int(mask.split()[-1], 16)
        # the match name
        self._matchname = match.split()[-2]
        # the match value
        self._matchvalue = int(match.split()[-1], 16)

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
