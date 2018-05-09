import sys
import unittest

sys.path.append('..')
from modelparsing.decoder import Decoder
sys.path.remove('..')


class TestDecoder(unittest.TestCase):
    '''
    Test that checks the decoder class output.
    '''

    class Model:
        def __init__(self, name, form, opc, funct3, definition, funct7=0xff):
            self._name = name
            self._form = form
            self._opc = opc
            self._funct3 = funct3
            self._funct7 = funct7
            self._definition = definition

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

        @property
        def definition(self):
            return self._definition

    def setUp(self):
        # frequently used variables
        self.form = 'I'
        self.opc = 0x02
        self.funct3 = 0x00
        self.definition = '''{
    test;
}'''

    def testITypeDecoder(self):
        # test a simple decoder generation for an i type operation
        name = 'itype'
        models = [self.Model(name, self.form, self.opc,
                             self.funct3, self.definition)]
        decoder = Decoder(models)
        decoder.gen_decoder()

        expect = '''\
0x2: decode FUNCT3 {
0x0: I32Op::itype({{
    test;
}}, uint32_t);
}
'''
        self.assertEqual(decoder.decoder, expect)

    def testRTypeDecoder(self):
        # test a simple decoder generation for a r type operation
        name = 'rtype'
        self.form = 'R'
        funct7 = 0x00
        models = [self.Model(name, self.form, self.opc,
                             self.funct3, self.definition, funct7)]

        decoder = Decoder(models)
        decoder.gen_decoder()

        expect = '''\
0x2: decode FUNCT3 {
0x0: decode FUNCT7 {
0x0: R32Op::rtype({{
    test;
}});
}
}
'''
        self.assertEqual(decoder.decoder, expect)

    def testInsertMultipleDecoder(self):
        name0 = 'itype0'
        name1 = 'itype1'
        name2 = 'rtype2'
        name3 = 'rtype3'
        name4 = 'rtype4'
        name5 = 'rtype5'

        models = [self.Model(name0, 'I', 0x02, 0x0, self.definition),
                  self.Model(name1, 'I', 0x02, 0x1, self.definition),
                  self.Model(name2, 'R', 0x02, 0x2, self.definition, 0x0),
                  self.Model(name3, 'R', 0x02, 0x2, self.definition, 0x1),
                  self.Model(name4, 'R', 0x16, 0x0, self.definition, 0x0),
                  self.Model(name5, 'R', 0x16, 0x0, self.definition, 0x1)]

        decoder = Decoder(models)
        decoder.gen_decoder()

        expect = '''\
0x2: decode FUNCT3 {
0x0: I32Op::itype0({{
    test;
}}, uint32_t);
0x1: I32Op::itype1({{
    test;
}}, uint32_t);
0x2: decode FUNCT7 {
0x0: R32Op::rtype2({{
    test;
}});
0x1: R32Op::rtype3({{
    test;
}});
}
}
0x16: decode FUNCT3 {
0x0: decode FUNCT7 {
0x0: R32Op::rtype4({{
    test;
}});
0x1: R32Op::rtype5({{
    test;
}});
}
}
'''
        self.assertEqual(decoder.decoder, expect)
