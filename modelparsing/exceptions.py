# Custom Exceptions with more precise name


class ConsistencyError(Exception):
    # exception that is thrown, if c++ model is not consistent
    pass


class OpcodeError(Exception):
    # exception that is thrown, if opcodes could not be generated
    pass
