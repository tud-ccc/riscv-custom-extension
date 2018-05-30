// test.cc

/**
 * The allowed types are derived from the
 * base instruction formats, which are descriped
 * in 2.2 Base Instruction Formats of
 * The RISC-V Instruction Set Manual
 * Volume I: User-Level ISA
 * Document Version 2.2
 *
 * The following function types are legit:
 *
 * R-Type  [Register - Register]
 * void fname(uint Rd, uint Rs1, uint Rs2)
 *
 * I-Type  [Register - Immediate]
 * void fname(uint Rd, uint Rs1, uint imm)
 *
 * S-Type [Store]
 * void fname(uint Rs1, uint Rs2, uint imm)
 *
 * U-Type [Upper Immediate]
 * void fname(uint Rd, uint imm)
 *  
 */

#include "binom.hh"

uint8_t cycles = 4;     // cycle count
uint8_t opc    = 0x02;  // opc, 5 bits
uint8_t funct3 = 0x01;  // funct3, 3 bits

void binom(
        uint32_t Rd,
        uint32_t Rs1,
        uint32_t imm
)
{
    uint32_t tmp = Rs1 + imm;
    Rd = tmp * tmp;
}
