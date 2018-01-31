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

#include <cstdint>

void fmod(uint32_t Rd_uw, uint32_t Rs1_uw, uint32_t Rs2_uw);
