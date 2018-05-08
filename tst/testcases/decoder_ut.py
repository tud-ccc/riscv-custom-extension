import unittest


class TestDecoder(unittest.TestCase):
    '''
    Test that checks the decoder class output.
    '''

    def setUp(self):
        # frequently used variables
        self.ftype = 'I'
        self.inttype = 'uint32_t'
        self.opc = 0x0a
        self.funct3 = 0x07
