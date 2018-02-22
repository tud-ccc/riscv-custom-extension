class CCModel:
    '''
    Gather all information that is used to generate a model.
    '''

    def __init__(self, name, ftype, inttype, opc, funct3, funct7, faults):
        self.name = name
        self.ftype = ftype
        self.inttype = inttype
        self.opc = opc
        self.funct3 = funct3
        self.funct7 = funct7
        self.faults = faults

        self.rd = '' if 'nord' in faults else 'Rd_uw'
        self.op1 = '' if 'nors1' in faults else 'Rs1_uw'

        self.rettype = inttype if 'nonvoid' in faults else 'void'

        if 'nodef' in faults:
            self.dfn = ';'
        elif 'noclose' in faults:
            self.dfn = '{\n    // function definition\n'
        elif 'return' in faults:
            self.dfn = '{\n    // function definition\n' \
                + '    return 0;\n}'
        else:
            self.dfn = '{\n    // function definition\n}'

        # inttypes
        if inttype == 'uint32_t':
            opsuf = '_uw'
        elif inttype == 'int32_t':
            opsuf = '_sw'
        elif inttype == 'uint64_t':
            opsuf = '_ud'
        elif inttype == 'int64_t':
            opsuf = '_sd'
        else:
            opsuf = ''

        if 'noop2' not in faults:
            if ftype == 'R':
                self.op2 = 'Rs2' + opsuf
            elif ftype == 'I':
                self.op2 = 'imm'
        else:
            self.op2 = ''
