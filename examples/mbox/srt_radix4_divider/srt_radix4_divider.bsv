/*
see LICENSE.iitm

Author : Shalender Kumar
Email id : cs18m050@smail.iitm.ac.in
Details:

--------------------------------------------------------------------------------------------------
*/
package srt_radix4_divider;
import UniqueWrappers::*;
import Vector::*;
`include "defined_parameters.bsv"
//`include "Logger.bsv"
interface Ifc_sdivider#(numeric type div_width);
   /*doc:method:this method received inputs (dividend and divisor) and operation name */
  method Action ma_sstart(Bit#(div_width) dividend, Bit#(div_width) divisor, Bit#(4) opcode, Bit#(3) funct3);
   /*doc:method:this method returns result*/
  method ActionValue#(Tuple2#(Bit#(1),Bit#(div_width))) mav_sresult();
  /*doc:method: this method is for flush operation*/
  method Action ma_sset_flush(bit c);
endinterface
/*doc:module:this module is for performing actual divisionr*/

module mksdivider(Ifc_sdivider#(div_width))
  provisos(
    Add#(1,div_width,ex_div_width),
    Div#(div_width,2,cycles),
    Add#(1,cycles,ex_cycles),
    Add#(div_width,ex_div_width,total_width),
    Add#(1,msb_div_width,div_width),
    Add#(1,msb_total_width,total_width),
    Add#(2,for_quotient,div_width),
    Log#(div_width, div_width_bits),
    Add#(a__, 32, div_width)
    );
  let v_total_width = valueOf(total_width);
  let v_msb_div_width = valueOf(msb_div_width);
  let v_msb_total_width = valueOf(msb_total_width);
  let v_div_width = valueOf(div_width);
  let v_ex_div_width = valueOf(ex_div_width);
  let v_div_width_bits = valueOf(div_width_bits);
  let v_cycles = valueOf(cycles);  
  let v_ex_cycles = valueOf(ex_cycles);
Reg#(Bit#(3)) rg_cntrl<-mkReg(0);
  /*doc:reg:this register holds divisor*/
  Reg#(Bit#(div_width)) rg_divisor<-mkReg(0);  
  /*doc:reg: this register is working as P and A register */
  Reg#(Bit#(total_width)) rg_p_a <-mkReg(0);  
  /*doc:reg:this register for holding positive quotient digits*/
  Reg#(Bit#(div_width)) rg_q_pos <-mkReg(0);  
  /*doc:reg:this register for holding negative quotient digits*/
  Reg#(Bit#(div_width)) rg_q_neg <-mkReg(0);  
  /*doc:reg: this register indicates how many bits are shifted */
  Reg#(Bit#(div_width_bits)) rg_shift_divisor<-mkReg(0);  
  /*doc:reg: this register counte clock cycles*/
  Reg#(Bit#(7)) rg_state <-mkReg(0);      
  /*doc:reg: this register tells quotient is required or remainder is required*/
  Reg#(Bit#(1)) rg_div_rem <- mkReg(0);  
  /*doc:reg: this register indicates sign of remainder*/  
  Reg#(Bit#(1)) rg_rem_sign <-mkReg(0);    
  /*doc:reg: this register indicates sign of quotient*/
  Reg#(Bit#(1)) rg_div_sign <-mkReg(0);  
  Reg#(Bit#(1)) rg_div_len <- mkReg(0);

  Reg#(Bit#(ex_div_width)) rg_rem <-mkReg(0);
  Reg#(Bit#(div_width)) rg_q <-mkReg(0);  
  Reg#(Bit#(3)) rg_special_case <-mkReg(0);
  
  Reg#(Bit#(div_width)) rg_dividend <- mkReg(0);
  Reg#(Bit#(div_width)) rg_dividend1 <- mkReg(0);
  Reg#(Bit#(1)) rg_div_type <-mkReg(0);

        Wire#(Bit#(1)) wr_flush <- mkDWire(0);
  
function Bit#(div_width) fn_compliment2(Bit#(div_width) lv_input);
  Bit#(div_width) lv_result = signExtend(1'b1);
  bit lv_carry = 1;
  bit lv_new_carry = 1;
  lv_result = lv_input^lv_result;
  for(Integer i = 0; i < v_div_width; i = i+1) begin
    lv_new_carry = lv_carry;
    lv_carry = lv_result[i]&lv_carry;
    lv_result[i] = lv_result[i]^lv_new_carry;
  end
  return lv_result;
endfunction
/*doc:rule: completes one step of SRT division in one clock cycle. In one clock cycle quotient digit is decided and accoding to quotient digit add/sub performed and P, A register are updated */
//rule rl_divide_step(rg_state>=1 && rg_state<=32);
rule rl_divide_step(rg_cntrl == 1);
  rg_state<=rg_state+1;
  //six bits from partial remainder and four bits from divisor will be used for choosing quotient digit.
  Bit#(6) div = rg_p_a[v_msb_total_width:v_msb_total_width-5];
  Bit#(4) divider_4_msb = rg_divisor[v_msb_div_width:v_msb_div_width-3];
  Bit#(2) q = 0;  
  Bit#(1) q_sign = 0;
  //case statement is for choosing quotient digit.
  case(divider_4_msb)
  'b1000:begin
    if(-12<=div && div<=-7)begin q = 2; q_sign =1; end
    else if(-6<=div && div<=-3)begin q = 1; q_sign =1; end
    else if(-2<=div && div<=1)begin q = 0; q_sign =0; end
    else if(2<=div && div<=5)begin q = 1; q_sign =0; end
    else if(6<=div && div<=11)begin q = 2; q_sign =0; end
  end
  'b1001:begin
    if(-14<=div && div<=-8)begin q = 2; q_sign =1; end
    else if(-7<=div && div<=-4)begin q = 1; q_sign =1; end
    else if(-3<=div && div<=2)begin q = 0; q_sign =0; end
    else if(3<=div && div<=6)begin q = 1; q_sign =0; end
    else if(7<=div && div<=13)begin q = 2; q_sign =0; end
  end
  'b1010:begin
    if(-15<=div && div<=-9)begin q = 2; q_sign =1; end
    else if(-8<=div && div<=-4)begin q = 1; q_sign =1; end
    else if(-3<=div && div<=2)begin q = 0; q_sign =0; end
    else if(3<=div && div<=7)begin q = 1; q_sign =0; end
    else if(7<=div && div<=14)begin q = 2; q_sign =0; end
  end
  'b1011:begin
    if(-16<=div && div<=-10)begin q = 2; q_sign =1; end
    else if(-9<=div && div<=-4)begin q = 1; q_sign =1; end
    else if(-3<=div && div<=2)begin q = 0; q_sign =0; end
    else if(3<=div && div<=8)begin q = 1; q_sign =0; end
    else if(9<=div && div<=15)begin q = 2; q_sign =0; end  
  end
  'b1100:begin
    if(-18<=div && div<=-11)begin q = 2; q_sign =1; end
    else if(-10<=div && div<=-5)begin q = 1; q_sign =1; end
    else if(-4<=div && div<=3)begin q = 0; q_sign =0; end
    else if(4<=div && div<=9)begin q = 1; q_sign =0; end
    else if(10<=div && div<=17)begin q = 2; q_sign =0; end
  end
  'b1101:begin
    if(-19<=div && div<=-11)begin q = 2; q_sign =1; end
    else if(-10<=div && div<=-5)begin q = 1; q_sign =1; end
    else if(-4<=div && div<=3)begin q = 0; q_sign =0; end
    else if(4<=div && div<=9)begin q = 1; q_sign =0; end
    else if(10<=div && div<=18)begin q = 2; q_sign =0; end  

  end
  'b1110:begin
    if(-20<=div && div<=-12)begin q = 2; q_sign =1; end
    else if(-11<=div && div<=-5)begin q = 1; q_sign =1; end
    else if(-4<=div && div<=3)begin q = 0; q_sign =0; end
    else if(4<=div && div<=10)begin q = 1; q_sign =0; end
    else if(11<=div && div<=19)begin q = 2; q_sign =0; end
  end
  'b1111:begin
    if(-22<=div && div<=-13)begin q = 2; q_sign =1; end
    else if(-12<=div && div<=-4)begin q = 1; q_sign =1; end
    else if(-5<=div && div<=4)begin q = 0; q_sign =0; end
    else if(3<=div && div<=11)begin q = 1; q_sign =0; end
    else if(11<=div && div<=21)begin q = 2; q_sign =0; end
  end
  endcase  
  Bit#(ex_div_width) lv_ex_divisor = {1'b0,rg_divisor};
  Bit#(div_width) lv_all_zeros = 0;
  Bit#(total_width) y = {lv_ex_divisor,lv_all_zeros};
  Bit#(total_width) p_a = rg_p_a;
  p_a = p_a<<2;
  let lv_q_pos = rg_q_pos;
  let lv_q_neg = rg_q_neg;
  lv_q_pos = lv_q_pos<<2;
  lv_q_neg = lv_q_neg<<2;
  
  //rg_q_neg and rg_q_pos keep negative and positive quotients respectively. so after choosing quotient digit it is added in respective register.
  if(q == 2) 
  begin
    y = y <<1;
    if(q_sign == 1)
    begin
      p_a = p_a + y;
      lv_q_neg[1] = 1;      
    end
    else
    begin
      p_a = p_a - y;
      lv_q_pos[1] = 1;
    end
  end
  else if(q==1)
  begin
    if(q_sign == 1)
    begin
      p_a = p_a + y;
      lv_q_neg[0] = 1;
    end
    else
    begin
      p_a = p_a - y;    
      lv_q_pos[0] = 1;
    end
  end
  let x = fromInteger(v_div_width);
  x = x/2;
  if(rg_state == x)
  begin

    rg_cntrl<=2;
  end
  rg_p_a <= p_a;
  rg_q_pos <= lv_q_pos;
  rg_q_neg <= lv_q_neg;
endrule

//***************************************************************** rules *******************************************
//out1 and out are saperate rules to meet timing constraints. otherwise all computations can be done in rl_divide_step rule.
rule out1(rg_cntrl == 2);        //rule for output
  let lv_shift_divisor = rg_shift_divisor;
  let x = rg_q_pos - rg_q_neg;        		//rg_q_pos - rg_q_neg gives quotient.                
  Bit#(ex_div_width) rem =rg_p_a[v_msb_total_width:v_div_width];
  Bit#(ex_div_width) temp = zeroExtend(rg_divisor);
  if(rem[v_div_width] == 1)           
  begin
    x = x-1;
    rem = rem + temp;
  end
  rg_rem <= rem;
  rg_q <= x;
  rg_cntrl<=5;

endrule
rule out(rg_cntrl == 5);        //rule for output
  let lv_shift_divisor = rg_shift_divisor;

  Bit#(ex_div_width) rem = rg_p_a[v_msb_total_width:v_div_width];
  rg_rem <= rg_rem >> rg_shift_divisor;
  rg_cntrl<=6;
endrule
//shift dividend and divisor by rg_shift_divisor. rg_p_a is a 129 bit long register for 64bit and 65bit long for 32bit division. rg_p_a contains partial remainder.
rule rl_3rd_cycle(rg_cntrl == 7);
  let lv_divisor = rg_divisor;
  let lv_dividend = rg_dividend;

  Bit#(total_width) lv_p_a = zeroExtend(lv_dividend);

  rg_p_a <= lv_p_a<<rg_shift_divisor;
  rg_divisor <= lv_divisor<<rg_shift_divisor;
  rg_cntrl <=1;
  rg_state <=1;
endrule
//counting number of msb zeros in divisor. this value will be used for shifting divisor. count value is put into rg_shift_divisor register. 
rule rl_2nd_cycle(rg_cntrl == 4);
  let lv_divisor = rg_divisor;
  let shift_divisor = countZerosMSB(lv_divisor);
  rg_shift_divisor<=pack(shift_divisor)[v_div_width_bits-1:0];
  rg_cntrl <=7;
endrule
//new rule is added for complement of negative number.
rule rl_1st_cycle(rg_cntrl == 3);
  
  Bit#(1) lv_rem_sign = 0;
  Bit#(1) lv_div_sign = 0;
  let dividend = rg_dividend;
  let divisor = rg_divisor;
  //in signed division if dividend is negative then take it's 2's complement.
  if(dividend[v_msb_div_width] == 1 && rg_div_type == 0)
  begin
    lv_rem_sign = 1;
    dividend = fn_compliment2(dividend[v_msb_div_width:0]);
    lv_div_sign = lv_div_sign ^ 1;
  end

  //in signed division if divisor is negative then take it's 2's complement.
  if(divisor[v_msb_div_width] == 1 && rg_div_type == 0)
  begin
    divisor = fn_compliment2(divisor[v_msb_div_width:0]);
    lv_div_sign = lv_div_sign ^ 1;
  end
  //set condition so that rule rl_2nd_cycle can fire in next clock cycle.
  rg_cntrl<=4;

  rg_div_sign <= lv_div_sign;
  rg_rem_sign <= lv_rem_sign;
  rg_dividend <=dividend;
  rg_divisor <=divisor;
endrule:rl_1st_cycle

//**********************************************method ***************************************************
//ma_sstart method called initially for division. Dividend and Divisor are given to ma_sstart method.
method Action ma_sstart(Bit#(div_width) dividend, Bit#(div_width) divisor,Bit#(4) opcode, Bit#(3) funct3);
    Bit#(1)    lv_div_type=0;      
    Bit#(1)    lv_div_len = 0;        

    Bit#(1) lv_div_sign = 0;    
    Bit#(1) lv_rem_sign = 0;
    Bit#(1)  lv_div_or_rem=0;
    Bit#(3) lv_special_case = 0;
    let dividend_s = dividend;
    let divisor_s = divisor;	

  lv_div_len = pack(opcode == 'b1110);				//32bit division or 64bit division.
  lv_div_or_rem = pack(funct3 == 'b110 || funct3 == 'b111);	//final return result is quotient or remainder.
  lv_div_type = pack(funct3 == 'b101 || funct3 == 'b111);	//signed or unsigned

  Bit#(div_width) caseK = 0;
  caseK[v_msb_div_width] = 1;

  //lv_div_len == 1 indicates 32bit division. so sign extend or zero extend lower 32bits of input.
  if(lv_div_len == 1)
  begin
    caseK = 'hffffffff80000000;
    if(lv_div_type == 0)
    begin
      dividend = signExtend(dividend[31:0]);
      divisor = signExtend(divisor[31:0]);
    end
    else
    begin
      dividend = zeroExtend(dividend[31:0]);
      divisor = zeroExtend(divisor[31:0]);    
    end
  end
//********************************************************************************************************************************************
if (divisor=='d0) 
  begin        //special case divisor is zero
    lv_special_case = 1;	
  end
  else if (dividend==caseK && divisor== 'd-1 && lv_div_type==0)  //Special case (dividend=-2^(64-1) and divisor=-1).
  begin  
    lv_special_case = 2;
  end
  else if(dividend == divisor) begin       //special case divisor and dividend are equal
    lv_special_case = 3;
  end
  else if(divisor == 1)			//special case when divisor is 1.
  begin
    lv_special_case = 4;
  end	
  //if flush input is 0 then only division proceed further.
  if(wr_flush==0) begin		//to flush current division in between when flush input enabled.
    rg_dividend <=dividend;
    rg_dividend1 <=dividend;
    rg_divisor <= divisor;
    
    rg_cntrl<=3;
    rg_q_pos <= 0;
    rg_q_neg <=0;
//*******************************************************************************************************
  rg_special_case <= lv_special_case;
  rg_div_rem <= lv_div_or_rem;
  rg_div_type <= lv_div_type;
  rg_div_sign <= lv_div_sign;
  rg_rem_sign <= lv_rem_sign;
  rg_div_len <= lv_div_len;
  end
endmethod  


//mav_sresult method returns final result.
method ActionValue#(Tuple2#(Bit#(1),Bit#(div_width))) mav_sresult();
  Bit#(1) lv_valid = pack(rg_cntrl==6);
  Bit#(div_width) lv_out = 0;
  if(rg_cntrl == 6) begin
      rg_cntrl<=0;
      Bit#(ex_div_width) lv_rem = 0;
      Bit#(div_width) lv_q = 0;
      lv_rem = rg_rem;
      lv_q = rg_q;
	//special case divide by zero.
	if(rg_special_case == 1)
	begin
		lv_rem = {1'b0,rg_dividend1};
		lv_q = 'd-1;
		if(rg_div_rem == 1) 
			lv_out = lv_rem[v_msb_div_width:0];
		else 
			lv_out = lv_q;
		if(rg_div_len == 1)
			lv_out = signExtend(lv_out[31:0]);
	end
	//special case signed overflow.
	else if(rg_special_case == 2)
	begin
		lv_rem = 'd0;
		lv_q = rg_dividend1;
		if(rg_div_rem == 1) 
			lv_out = lv_rem[v_msb_div_width:0];
		else 
			lv_out = lv_q;
	end
	//special case dividend and divisor are equal.
	else if(rg_special_case == 3)
	begin
		lv_rem = 0;
		lv_q ='d1;
		if(rg_div_rem == 1) 
			lv_out = lv_rem[v_msb_div_width:0];
		else 
			lv_out = lv_q;
	end
	//special case divisor is 1;
	else if(rg_special_case ==4)
	begin
		if(rg_div_rem == 1) 
			lv_out = 0;
		else 
			lv_out = rg_dividend1;
	end
	else
	//if none of the above test cases are matching that means it is regular division. so pick result from rg_q or rg_rem. rg_q contains quotient and rg_rem contains remainder.
	begin
		// for true condition return remainder. 
		if(rg_div_rem == 1)
		begin
			//negative result, so take complement.
			if(rg_rem_sign == 1)
			begin
				lv_out = fn_compliment2(rg_rem[v_msb_div_width:0]);
			end
			else
			begin
				lv_out = rg_rem[v_msb_div_width:0];
				if(rg_div_len == 1)
					lv_out = signExtend(lv_out[31:0]);
			end
		end
		//for false condition return quotient.
		else
		begin
			//for negative number take complement.
			if(rg_div_sign == 1)
			begin  
				lv_out = fn_compliment2(rg_q);
			end
			else
			begin
				//for 32bit division sign extend 32LSBs.
				if(rg_div_len == 1)
				begin
					lv_out = signExtend(rg_q[31:0]);
				end
				else
				begin
					lv_out = rg_q;
				end
			end
		end
	end
  end
	if(rg_div_len == 1)
		lv_out = signExtend(lv_out[31:0]);
  return tuple2(lv_valid,lv_out);
endmethod:mav_sresult


    method Action ma_sset_flush(bit c);
      if(c==1) //when flush input goes high
      begin
                                wr_flush <= '1;
        rg_cntrl <= 0;
        rg_shift_divisor<=0;  
      end
    endmethod
endmodule
interface Ifc_srt_radix4_divider;
  method Action ma_start(Bit#(`XLEN) dividend, Bit#(`XLEN) divisor, Bit#(4) opcode, Bit#(3) funct3);
  method ActionValue#(Tuple2#(Bit#(1),Bit#(`XLEN))) mav_result();
  method Action ma_set_flush(bit c);
endinterface
(*synthesize*)
(*conflict_free="mav_result,div_instance_rl_divide_step"*)
(*conflict_free="mav_result,div_instance_out1"*)
(*conflict_free="mav_result,div_instance_out"*)
(*conflict_free="mav_result,div_instance_rl_3rd_cycle"*)
(*conflict_free="mav_result,div_instance_rl_1st_cycle"*)
(*conflict_free="mav_result,div_instance_rl_2nd_cycle"*)
module mk_srt_radix4_divider(Ifc_srt_radix4_divider);
  Ifc_sdivider#(`XLEN)  div_instance<- mksdivider;
  method Action ma_start(Bit#(`XLEN) dividend, Bit#(`XLEN) divisor, Bit#(4) opcode, Bit#(3) funct3);
    div_instance.ma_sstart(dividend,divisor, opcode, funct3);
  endmethod
  method ActionValue#(Tuple2#(Bit#(1),Bit#(`XLEN))) mav_result();
    match {.valid,.out} <- div_instance.mav_sresult();
    return tuple2(valid,out);
  endmethod
  method Action ma_set_flush(bit c);
    div_instance.ma_sset_flush(c);
  endmethod
endmodule
endpackage

