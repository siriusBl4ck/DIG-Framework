/*
see LICENSE.iitm
--------------------------------------------------------------------------------------------------
*/
`define NUM_INSTRS 20200 
`define MEM_INIT_SIZE 1048576
`define STOP 100000


`define TOTAL_THREADS 4
`define XLEN 64
`define REGFILE_SIZE 32
`define PRF_SIZE 128
`define Addr_width 64

`define RV64

`define CONFIG_RV64 
`ifdef RV32
`define Multiplier32
`define Multiplier16
`define divider32
`endif

`ifdef RV64
`define Multiplier64
`define Multiplier32
`define Multiplier16
`define divider64
`endif

