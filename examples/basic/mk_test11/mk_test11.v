//
// Generated by Bluespec Compiler, version 2021.12.1-27-g9a7d5e05 (build 9a7d5e05)
//
// On Tue Nov 15 02:17:52 IST 2022
//
//
// Ports:
// Name                         I/O  size props
// getVec_fst                     O     1 reg
// RDY_getVec_fst                 O     1 const
// getVec_snd                     O    10 reg
// RDY_getVec_snd                 O     1 const
// putVec                         O    11 reg
// RDY_putVec                     O     1 const
// CLK                            I     1 clock
// RST_N                          I     1 reset
// putVec_a                       I    11 reg
// EN_putVec                      I     1
//
// No combinational paths from inputs to outputs
//
//

`ifdef BSV_ASSIGNMENT_DELAY
`else
  `define BSV_ASSIGNMENT_DELAY
`endif

`ifdef BSV_POSITIVE_RESET
  `define BSV_RESET_VALUE 1'b1
  `define BSV_RESET_EDGE posedge
`else
  `define BSV_RESET_VALUE 1'b0
  `define BSV_RESET_EDGE negedge
`endif

module mk_test11(CLK,
		 RST_N,

		 getVec_fst,
		 RDY_getVec_fst,

		 getVec_snd,
		 RDY_getVec_snd,

		 putVec_a,
		 EN_putVec,
		 putVec,
		 RDY_putVec);
  input  CLK;
  input  RST_N;

  // value method getVec_fst
  output getVec_fst;
  output RDY_getVec_fst;

  // value method getVec_snd
  output [9 : 0] getVec_snd;
  output RDY_getVec_snd;

  // actionvalue method putVec
  input  [10 : 0] putVec_a;
  input  EN_putVec;
  output [10 : 0] putVec;
  output RDY_putVec;

  // signals for module outputs
  wire [10 : 0] putVec;
  wire [9 : 0] getVec_snd;
  wire RDY_getVec_fst, RDY_getVec_snd, RDY_putVec, getVec_fst;

  // register rg_a
  reg [10 : 0] rg_a;
  wire [10 : 0] rg_a$D_IN;
  wire rg_a$EN;

  // value method getVec_fst
  assign getVec_fst = rg_a[10] ;
  assign RDY_getVec_fst = 1'd1 ;

  // value method getVec_snd
  assign getVec_snd = rg_a[9:0] ;
  assign RDY_getVec_snd = 1'd1 ;

  // actionvalue method putVec
  assign putVec = rg_a ;
  assign RDY_putVec = 1'd1 ;

  // register rg_a
  assign rg_a$D_IN = putVec_a ;
  assign rg_a$EN = EN_putVec ;

  // handling of inlined registers

  always@(posedge CLK)
  begin
    if (RST_N == `BSV_RESET_VALUE)
      begin
        rg_a <= `BSV_ASSIGNMENT_DELAY 11'd0;
      end
    else
      begin
        if (rg_a$EN) rg_a <= `BSV_ASSIGNMENT_DELAY rg_a$D_IN;
      end
  end

  // synopsys translate_off
  `ifdef BSV_NO_INITIAL_BLOCKS
  `else // not BSV_NO_INITIAL_BLOCKS
  initial
  begin
    rg_a = 11'h2AA;
  end
  `endif // BSV_NO_INITIAL_BLOCKS
  // synopsys translate_on
endmodule  // mk_test11

