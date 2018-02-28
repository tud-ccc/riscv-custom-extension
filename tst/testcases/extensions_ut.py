import sys
import unittest

sys.path.append('..')
from modelparsing.exceptions import OpcodeError
from modelparsing.parser import Extensions
sys.path.remove('..')


class TestExtensions(unittest.TestCase):
    '''
    Tests for all functions in the class Extensions
    '''

    class Model:
        def __init__(self, name, form, opc, funct3, funct7=0xff):
            self._name = name
            self._form = form
            self._opc = opc
            self._funct3 = funct3
            self._funct7 = funct7

        @property
        def name(self):
            return self._name

        @property
        def form(self):
            return self._form

        @property
        def opc(self):
            return self._opc

        @property
        def funct3(self):
            return self._funct3

        @property
        def funct7(self):
            return self._funct7

    def setUp(self):
        self.form = 'I'
        self.opc = 0x02
        self.funct3 = 0x00

    def testExtensionsModelToOpsRType(self):
        pass
