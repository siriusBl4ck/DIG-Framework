/*
see LICENSE.iitm

Author : Shalender Kumar, Charulatha Narashiman
Email id : cs18m050@smail.iitm.ac.in, charuswathi112@gmail.com
Details:

--------------------------------------------------------------------------------------------------
*/

package tb_srt_radix4_divider;
import UniqueWrappers::*;
import Vector::*;
import srt_radix4_divider ::*;
`include "defined_parameters.bsv"
//`include "Logger.bsv"

(*synthesize*)
module tb_srt_radix4_divider();
  function Bit#(`XLEN) fn_compliment2(Bit#(`XLEN) lv_input);
    Bit#(`XLEN) lv_result = signExtend(1'b1);
    bit lv_carry = 1;
    bit lv_new_carry = 1;
    lv_result = lv_input^lv_result;
    for(Integer i = 0; i < `XLEN; i = i+1) begin
      lv_new_carry = lv_carry;
      lv_carry = lv_result[i]&lv_carry;
      lv_result[i] = lv_result[i]^lv_new_carry;
    end
    return lv_result;
  endfunction

  Ifc_srt_radix4_divider ifc_div <- mk_srt_radix4_divider();
  Reg#(Bit#(32)) rg_cycle <- mkReg(0);
  Reg#(Bit#(4)) rg_opcode <- mkReg('b1100);
  Reg#(Bit#(3)) rg_funct3 <- mkReg('b101);
  Reg#(Bit#(6)) rg_cnt <- mkReg(0);
	Reg#(Bool) en <- mkReg(True);
  rule rl_cycle;
    rg_cycle <= rg_cycle +1;
    if(rg_cycle==400)
      $finish(0);
  endrule
  rule rl_stage_1((rg_cycle % 39 == 0) && (rg_cycle > 0));
//  rule rl_stage_1;
    Bit#(`XLEN) op1 ='hce9e3519a12fe4a4;
    Bit#(`XLEN) op2 ='h00000000312fe4a4;
    Bit#(`XLEN) dividend = 0;
    Bit#(`XLEN) divisor = 0;    


    if(rg_cnt == 0)
    begin
      dividend = op1;
      divisor = op2;
      ifc_div.ma_start(dividend,divisor,'b1100 , 'b100);
      rg_cnt<=rg_cnt+1;
	$display("%d DRIVE dividend %x", rg_cycle, dividend);
	$display("%d DRIVE divisor %x", rg_cycle, divisor);
    end
    else if(rg_cnt == 1)
    begin
      dividend = op1;
      divisor = op2;
      ifc_div.ma_start(dividend,divisor,'b1100 , 'b101);
      rg_cnt<=rg_cnt+1;
	$display("%d DRIVE dividend %x", rg_cycle, dividend);
	$display("%d DRIVE divisor %x", rg_cycle, divisor);
    end
    else if(rg_cnt == 2)
    begin
      dividend = op1;
      divisor = op2;
      ifc_div.ma_start(dividend,divisor,'b1100 , 'b110);
      rg_cnt<=rg_cnt+1;
	$display("%d DRIVE dividend %x", rg_cycle, dividend);
	$display("%d DRIVE divisor %x", rg_cycle, divisor);
    end
    else if(rg_cnt == 3)
    begin
      dividend = op1;
      divisor = op2;
      ifc_div.ma_start(dividend,divisor,'b1100 , 'b111);
      rg_cnt<=rg_cnt+1;
	$display("%d DRIVE dividend %x", rg_cycle, dividend);
	$display("%d DRIVE divisor %x", rg_cycle, divisor);
    end
//******************************************************************************************
    else if(rg_cnt == 4)
    begin
      dividend = op1;
      divisor = op2;
      ifc_div.ma_start(dividend,divisor,'b1110 , 'b100);
      rg_cnt<=rg_cnt+1;
	$display("%d DRIVE dividend %x", rg_cycle, dividend);
	$display("%d DRIVE divisor %x", rg_cycle, divisor);
    end
    else if(rg_cnt == 5)
    begin
      dividend = op1;
      divisor = op2;
      ifc_div.ma_start(dividend,divisor,'b1110 , 'b101);
      rg_cnt<=rg_cnt+1;
	$display("%d DRIVE dividend %x", rg_cycle, dividend);
	$display("%d DRIVE divisor %x", rg_cycle, divisor);
    end
    else if(rg_cnt == 6)
    begin
      dividend = op1;
      divisor = op2;
      ifc_div.ma_start(dividend,divisor,'b1110 , 'b110);
      rg_cnt<=rg_cnt+1;  
 	$display("%d DRIVE dividend %x", rg_cycle, dividend);
	$display("%d DRIVE divisor %x", rg_cycle, divisor); 
    end
    else if(rg_cnt == 7)
    begin
      dividend = op1;
      divisor = op2;
      ifc_div.ma_start(dividend,divisor,'b1110 , 'b111);
      rg_cnt<=rg_cnt+1;       
 	$display("%d DRIVE dividend %x", rg_cycle, dividend);
	$display("%d DRIVE divisor %x", rg_cycle, divisor);    
    end
//******************************************************************************************

  endrule
  rule rl_receive;
    match {.valid,.out} <- ifc_div.mav_result();
//    `logLevel( tb, 0, $format("Cycle %d => valid %d value %d",rg_cycle,valid,out))
    if(valid == 1)
    begin
	$display($time, " after updation Cycle %d => valid %d value %h",rg_cycle,valid,out);
    end
  endrule
endmodule
endpackage


