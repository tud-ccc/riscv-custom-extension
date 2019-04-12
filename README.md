RISC-V Extension Repo
=====================

This repository is used to develop extensions for the RISC-V ISA.

Please have a look at the [Diploma Thesis of Robert
Sheffel](https://cfaed.tu-dresden.de/publications?pubId=2203) for more
documentation.

## Prerequisites

on Ubuntu:
*  clang-4.0
*  python2
*  libclang-dev
*  make sure to have the clang lib and clang python bindings in sync, same version
	*  pip install https://pypi.python.org/packages/source/c/clang/clang-3.8.tar.gz

## Usage
usage: modelparser [-h] [-v] [-b] [-m MODEL]

Parse reference implementations of custom extension models.

optional arguments:  
  -h, --help                show this help message and exit  
  -v, --verbosity           Increase output verbosity.  
  -b, --build               If set, Toolchain and Gem5 will be rebuild.  
  -m MODEL, --model MODEL   Reference implementation

## Structure
The project is structured as follows:

*  modelparsing/  -  contains model parsing facilities
*  tst/  -  contains unit test for parser modules
*  extensions/  -  default place, where extension models should be defined
*  riscv-opcodes/  -  the riscv opcodes generator project, used by this project
