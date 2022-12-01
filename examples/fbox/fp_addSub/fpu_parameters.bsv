///////////////////////////////////////
// see LICENSE.iitm
///////////////////////////////////////
// NOTE: These parameters are based on actual latencies for 1) manually optimized units (both pipelined and multi-cycle blocking)
//       and 2) retiming results for other units.
//       When latencies change, for i-class, check dual-fp optimizations (packet_1 and packet_2 in comments below).
// ------------------------------------
`define LATENCY_FMA_SP 10 // packet_1
`define STAGES_FMA_SP 9 
`define LATENCY_FMA_DP 12 // packet_2
`define STAGES_FMA_DP 11
`define LATENCY_FADD_SP 5 // packet_2
`define STAGES_FADD_SP 4
`define LATENCY_FADD_DP 6 // packet_1
`define STAGES_FADD_DP 5
`ifdef fpu_pipelined
  `define LATENCY_FMUL_SP 6 // packet_1
  `define STAGES_FMUL_SP 5
  `define LATENCY_FMUL_DP 9 // packet_2
  `define STAGES_FMUL_DP 8
`else
  `define LATENCY_FMUL_SP 7 
  `define STAGES_FMUL_SP 6
  `define LATENCY_FMUL_DP 8
  `define STAGES_FMUL_DP 7
`endif
`ifdef fpu_div_sqrt_srt
  `define LATENCY_FDIV_SP  22 // packet_1
  `define LATENCY_FDIV_DP 37 // packet_2
  `define LATENCY_FSQRT_SP 19  // packet_1
  `define LATENCY_FSQRT_DP 34 // packet_2
`else
  `define LATENCY_FDIV_SP  36 // packet_1
  `define LATENCY_FDIV_DP 65 // packet_2
  `define LATENCY_FSQRT_SP 67  // packet_1
  `define LATENCY_FSQRT_DP 123 // packet_2
`endif
`ifdef fpu_pipelined
  `define LATENCY_FCONV_SP_TO_DP 1 // packet_2
  `define LATENCY_FCONV_DP_TO_SP 2 // packet_2
  `define STAGES_FCONV_DP_TO_SP 1  
  `define LATENCY_FCONV_FP_TO_INT 3 // packet_2
  `define STAGES_FCONV_FP_TO_INT 2
  `define LATENCY_FCONV_INT_TO_FP 3 // packet_2
  `define STAGES_FCONV_INT_TO_FP 2
`else
  `define LATENCY_FCONV_FP_TO_INT 4
  `define STAGES_FCONV_FP_TO_INT 3
  `define LATENCY_FCONV_INT_TO_FP 4 
  `define STAGES_FCONV_INT_TO_FP 3
`endif
// default convert latency
`define LATENCY_FCONV 4 
`define STAGES_FCONV 3
`define LATENCY_FREST 1 // packet_1
