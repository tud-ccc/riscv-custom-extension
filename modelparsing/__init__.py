import clang.cindex
import logging

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logger = logging.getLogger(__name__).addHandler(logging.NullHandler())


clang.cindex.Config.set_library_file('/usr/lib64/llvm/libclang.so')
# clang.cindex.Config.set_library_file('/usr/lib/llvm-4.0/lib/libclang-4.0.so')
