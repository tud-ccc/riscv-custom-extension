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
 *  
 */

#include "mac.hh"

uint8_t opc    = 0x02;  // opc, 5 bits
uint8_t funct3 = 0x00;  // funct3, 3 bits
uint8_t funct7 = 0x00;  // funct7, 7 bits

void mac(
    uint32_t Rd,
    uint32_t Rs1,
    uint32_t Rs2
)
{
    uint32_t tmp = Rs1 * Rs2;
    Rd = Rd + tmp;
}
