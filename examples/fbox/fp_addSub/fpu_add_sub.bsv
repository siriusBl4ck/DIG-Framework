////////////////////////////////////////////////////////////////////////////////
// Copyright (c) 2011  Bluespec, Inc.   ALL RIGHTS RESERVED.
// $Revision$
// $Date$
////////////////////////////////////////////////////////////////////////////////
// see LICENSE.iitm
////////////////////////////////////////////////////////////////////////////////
/*
-------------------------------------------------------------------------------------------------

Author: Sujay Pandit, Neel Gala, Lokhesh Kumar 
Email id: contact.sujaypandit@gmail.com, neelgala@gmail.com, lokhesh.kumar@gmail.com
--------------------------------------------------------------------------------------------------
*/
package fpu_add_sub;
import fpu_common    ::*;
import Vector            ::*;
import Real              ::*;
import BUtils            ::*;
import DefaultValue      ::*;
import FShow             ::*;
import GetPut            ::*;
import ClientServer      ::*;
import FIFO              ::*;
import FixedPoint        ::*;
import DReg  :: *;
`include "fpu_parameters.bsv"

////////////////////////////////////////////////////////////////////////////////
/// Addition/Subtraction
////////////////////////////////////////////////////////////////////////////////
function Tuple2#(FloatingPoint#(e,m),Exception) fn_fpu_add_sub (Tuple3#(FloatingPoint#(e,m),
																																			FloatingPoint#(e,m),
																																			RoundMode) operands)
//(Maybe#(FloatingPoint#(e,m)) in0, FloatingPoint#(e,m) in1, FloatingPoint#(e,m) in2, RoundMode rmode ) // INTERFACE CHANGES
   provisos(
      // per request of bsc
      Add#(a__, TLog#(TAdd#(1, TAdd#(m, 5))), TAdd#(e, 1))
      );

   function Tuple7#(CommonState#(e,m),
		    Bit#(TAdd#(m,5)),
		    Bit#(TAdd#(m,5)),
		    Bool,
		    Bool,
		    Bit#(e),
				Bit#(e)) s1_stage(Tuple3#(
								FloatingPoint#(e,m),
					      FloatingPoint#(e,m),
					      RoundMode) op);

      match {.opA, .opB, .rmode } = op;

      CommonState#(e,m) s = CommonState {
	 res: tagged Invalid,
	 exc: defaultValue,
	 rmode: rmode
	 };

      Int#(TAdd#(e,2)) expA = isSubNormal(opA) ? fromInteger(minexp(opA)) : signExtend(unpack(unbias(opA)));
      Int#(TAdd#(e,2)) expB = isSubNormal(opB) ? fromInteger(minexp(opB)) : signExtend(unpack(unbias(opB)));

      Bit#(TAdd#(m,5)) sfdA = {1'b0, getHiddenBit(opA), opA.sfd, 3'b0};
      Bit#(TAdd#(m,5)) sfdB = {1'b0, getHiddenBit(opB), opB.sfd, 3'b0};

      Bit#(TAdd#(m,5)) x;
      Bit#(TAdd#(m,5)) y;
      Bool sgn;
      Bool sub;
      Bit#(e) exp;
      Bit#(e) expdiff;

      if ((expB > expA) || ((expB == expA) && (sfdB > sfdA))) begin
	 exp = opB.exp;
	 expdiff = truncate(pack(expB - expA));
	 x = sfdB;
	 y = sfdA;
	 sgn = opB.sign;
	 sub = (opB.sign != opA.sign);
      end
      else begin
	 exp = opA.exp;
	 expdiff = truncate(pack(expA - expB));
	 x = sfdA;
	 y = sfdB;
	 sgn = opA.sign;
	 sub = (opA.sign != opB.sign);
      end

      if (isSNaN(opA)) begin
	 s.res = tagged Valid nanQuiet(opA);
	 s.exc.invalid_op = True;
      end
      else if (isSNaN(opB)) begin
	 s.res = tagged Valid nanQuiet(opB);
	 s.exc.invalid_op = True;
      end
      else if (isQNaN(opA)) begin
	 s.res = tagged Valid opA;
      end
      else if (isQNaN(opB)) begin
	 s.res = tagged Valid opB;
      end
      else if (isInfinity(opA) && isInfinity(opB)) begin
	 if (opA.sign == opB.sign)
	    s.res = tagged Valid infinity(opA.sign);
	 else begin
	    s.res = tagged Valid qnan();
	    s.exc.invalid_op = True;
	 end
      end
      else if (isInfinity(opA)) begin
	 s.res = tagged Valid opA;
      end
      else if (isInfinity(opB)) begin
	 s.res = tagged Valid opB;
      end

      return tuple7(s,
		    x,
		    y,
		    sgn,
		    sub,
		    exp,
		    expdiff);
   endfunction

   function Tuple6#(CommonState#(e,m),
		    Bit#(TAdd#(m,5)),
		    Bit#(TAdd#(m,5)),
		    Bool,
		    Bool,
		    Bit#(e)) s2_stage(Tuple7#(CommonState#(e,m),
					      Bit#(TAdd#(m,5)),
					      Bit#(TAdd#(m,5)),
					      Bool,
					      Bool,
					      Bit#(e),
					      Bit#(e)) op);

      match {.s, .opA, .opB, .sign, .subtract, .exp, .diff} = op;

      if (s.res matches tagged Invalid) begin
	 if (diff < fromInteger(valueOf(m) + 5)) begin
	    Bit#(TAdd#(m,5)) guard = opB;

	    guard = opB << (fromInteger(valueOf(m) + 5) - diff);
	    opB = opB >> diff;
	    opB[0] = opB[0] | (|guard);
	 end
	 else if (|opB == 1) begin
	    opB = 1;
	 end
      end

      return tuple6(s,
		    opA,
		    opB,
		    sign,
		    subtract,
		    exp);
   endfunction

   function Tuple6#(CommonState#(e,m),
		    Bit#(TAdd#(m,5)),
		    Bit#(TAdd#(m,5)),
		    Bool,
		    Bool,
		    Bit#(e)) s3_stage(Tuple6#(CommonState#(e,m),
					      Bit#(TAdd#(m,5)),
					      Bit#(TAdd#(m,5)),
					      Bool,
					      Bool,
					      Bit#(e)) op);

      match {.s, .a, .b, .sign, .subtract, .exp} = op;

      let sum = a + b;
      let diff = a - b;

      return tuple6(s,
		    sum,
		    diff,
		    sign,
		    subtract,
		    exp);
   endfunction

   function Tuple4#(CommonState#(e,m),
		    FloatingPoint#(e,m),
		    Bit#(2),
		    Bool) s4_stage(Tuple6#(CommonState#(e,m),
					   Bit#(TAdd#(m,5)),
					   Bit#(TAdd#(m,5)),
					   Bool,
					   Bool,
					   Bit#(e)) op);

      match {.s, .addres, .subres, .sign, .subtract, .exp} = op;

      FloatingPoint#(e,m) out = defaultValue;
      Bit#(2) guard = 0;

      if (s.res matches tagged Invalid) begin
	 Bit#(TAdd#(m,5)) result;

	 if (subtract) begin
	    result = subres;
	 end
	 else begin
            result = addres;
	 end

	 out.sign = sign;
	 out.exp = exp;

	 // $display("out = ", fshow(out));
	 // $display("result = 'h%x", result);
	 // $display("zeros = %d", countZerosMSB(result));

	 let y = normalize(out, result);
	 out = tpl_1(y);
	 guard = tpl_2(y);
	 s.exc = s.exc | tpl_3(y);
      end

      return tuple4(s,
		    out,
		    guard,
		    subtract);
   endfunction

   function Tuple2#(FloatingPoint#(e,m),
		    Exception) s5_stage(Tuple4#(CommonState#(e,m),
						FloatingPoint#(e,m),
						Bit#(2),
						Bool) op);

      match {.s, .rnd, .guard, .subtract} = op;

      FloatingPoint#(e,m) out = rnd;

      if (s.res matches tagged Valid .x) begin
	 out = x;
      end
      else begin
	 let y = round(s.rmode, out, guard);
	 out = tpl_1(y);
	 s.exc = s.exc | tpl_2(y);
      end

      // adjust sign for exact zero result
      if (isZero(out) && !s.exc.inexact && subtract) begin
	 out.sign = (s.rmode == Rnd_Minus_Inf);
      end

      return tuple2(canonicalize(out),s.exc);
   endfunction

	 //return s5_stage( s4_stage( s3_stage( s2_stage( s1_stage(tuple4(in0,in1,in2,rmode)) ) ) ) );
	 return s5_stage( s4_stage( s3_stage( s2_stage( s1_stage(operands))))); //INTERFACE CHANGES
endfunction
////////////////////////////
////////////////////////////
////////////////////////////
interface Ifc_fpu_add_sub#(numeric type e, numeric type m, numeric type nos);
	method Action send(Tuple3#(FloatingPoint#(e,m),
		 FloatingPoint#(e,m),
		 RoundMode) operands);
//	method Tuple2#(Bit#(1),Tuple2#(FloatingPoint#(e,m),Exception)) receive();
	method ReturnType#(e,m) receive();
endinterface
module mk_fpu_add_sub(Ifc_fpu_add_sub#(e,m,nos))
	provisos(
		 Add#(a__, TLog#(TAdd#(1, TAdd#(TAdd#(m, 1), TAdd#(m, 1)))), TAdd#(e, 1)),
		 Add#(b__, TLog#(TAdd#(1, TAdd#(m, 5))), TAdd#(e, 1))
	);


	Vector#(nos,Reg#(Tuple2#(FloatingPoint#(e,m),Exception))) rg_stage_out <- replicateM(mkReg(tuple2(unpack(0),unpack(0))));
	Vector#(nos,Reg#(Bit#(1))) rg_stage_valid <- replicateM(mkDReg(0));
	rule rl_pipeline;
		 for(Integer i = 1 ; i <= valueOf(nos) -1 ; i = i+1)
		 begin
				rg_stage_out[i] <= rg_stage_out[i-1];
				rg_stage_valid[i] <= rg_stage_valid[i-1];
		 end
	endrule
	method Action send(Tuple3#(FloatingPoint#(e,m),
				FloatingPoint#(e,m),
				RoundMode) operands);		
					 
					 rg_stage_out[0] <= fn_fpu_add_sub(operands);
					 rg_stage_valid[0] <= 1;

	endmethod
//	method Tuple2#(Bit#(1),Tuple2#(FloatingPoint#(e,m),Exception)) receive();
	method ReturnType#(e,m) receive();
		
		let x = ReturnType{valid:rg_stage_valid[valueOf(nos)-1] ,value:tpl_1(rg_stage_out[valueOf(nos)-1]) ,ex:tpl_2(rg_stage_out[valueOf(nos)-1])};
		return x;
//		return tuple2(rg_stage_valid[nos-1],rg_stage_out[nos-1]);
	endmethod 
endmodule

(*synthesize*)
module mk_fpu_add_sub_sp_instance(Ifc_fpu_add_sub#(8,23,`STAGES_FADD_SP));
	let ifc();
	mk_fpu_add_sub _temp(ifc);
	return (ifc);
endmodule
// (*synthesize*)
module mk_fpu_add_sub_dp_instance(Ifc_fpu_add_sub#(11,52,`STAGES_FADD_DP));
	let ifc();
	mk_fpu_add_sub _temp(ifc);
	return (ifc);
endmodule

// module mkTb();
// 	 Ifc_fpu_add_sub#(8,23,4) ifc <- mk_fpu_add_sub();
//    Reg#(int) cycle <- mkReg(0);
//  rule count_cycle;
//    cycle <= cycle + 1;
//    if(cycle>10)
//    begin
//       $finish(0);
//    end
//  endrule
//    rule rl_send_1 (cycle==0);
// 			FloatingPoint#(8,23) op2 = FloatingPoint {
// 				sign:       False,
// 				exp:        8'h0F,
// 				sfd:        23'b11000000000000000000000
// 			};
	
// 			FloatingPoint#(8,23) op1 = FloatingPoint {
// 				sign:       False,
// 				exp:        8'h0F,
// 				sfd:        23'b10000000000000000000000
// 				};
//       RoundMode op4 = Rnd_Nearest_Even;
//       ifc.send(tuple3(op1,op2,op4));
// 	 endrule
// 	//  rule rl_send_2 (cycle==1);
// 	// 		FloatingPoint#(8,23) op2 = FloatingPoint {
// 	// 			sign:       True,
// 	// 			exp:        8'hEF,
// 	// 			sfd:        23'b11000000000000000000000
// 	// 		};
	
// 	// 		FloatingPoint#(8,23) op3 = FloatingPoint {
// 	// 			sign:       False,
// 	// 			exp:        8'hEF,
// 	// 			sfd:        23'b11110000000000000000000
// 	// 			};
// 	// 		FloatingPoint#(8,23) op1 = op2;
//   //     RoundMode op4 = Rnd_Nearest_Even;
//   //     ifc.send(tuple4(tagged Valid op1,op2,op3,op4));
// 	//  endrule
// 	//  rule rl_send_3 (cycle==2);
// 	// 		FloatingPoint#(8,23) op2 = FloatingPoint {
// 	// 			sign:       True,
// 	// 			exp:        8'hEF,
// 	// 			sfd:        23'b11111111111111111111111
// 	// 		};
	
// 	// 		FloatingPoint#(8,23) op3 = FloatingPoint {
// 	// 			sign:       True,
// 	// 			exp:        8'hEF,
// 	// 			sfd:        23'b11110000000000000000000
// 	// 			};
// 	// 		FloatingPoint#(8,23) op1 = op2;
//   //     RoundMode op4 = Rnd_Nearest_Even;
//   //     ifc.send(tuple4(tagged Valid op1,op2,op3,op4));
// 	//  endrule
	 
// 	//  rule rl_send_4 (cycle==3);
// 	// 		FloatingPoint#(8,23) op2 = FloatingPoint {
// 	// 			sign:       True,
// 	// 			exp:        8'hFF,
// 	// 			sfd:        23'b00000000000000000000000
// 	// 		};
	
// 	// 		FloatingPoint#(8,23) op3 = FloatingPoint {
// 	// 			sign:       False,
// 	// 			exp:        8'hEF,
// 	// 			sfd:        23'b11110000000000000000000
// 	// 			};
// 	// 		FloatingPoint#(8,23) op1 = op2;
//   //     RoundMode op4 = Rnd_Nearest_Even;
//   //     ifc.send(tuple4(tagged Valid op1,op2,op3,op4));
// 	//  endrule
// 	//  rule rl_send_5 (cycle==4);
// 	// 		FloatingPoint#(8,23) op2 = FloatingPoint {
// 	// 			sign:       True,
// 	// 			exp:        8'hFF,
// 	// 			sfd:        23'b11000000000000000000000
// 	// 		};
	
// 	// 		FloatingPoint#(8,23) op3 = FloatingPoint {
// 	// 			sign:       False,
// 	// 			exp:        8'hEF,
// 	// 			sfd:        23'b11110000000000000000000
// 	// 			};
// 	// 		FloatingPoint#(8,23) op1 = op2;
//   //     RoundMode op4 = Rnd_Nearest_Even;
//   //     ifc.send(tuple4(tagged Valid op1,op2,op3,op4));
// 	//  endrule
	 
//    rule receive;
// /*      match {.valid, .out} = ifc.receive();
//       $display("%d : Valid %b Value %b",cycle,valid,tpl_1(out));*/
// 	$display("got value");
//    endrule
// endmodule

//Directed tests:

// A=2.888895E-34
// B=3.3703774E-34
// OUT 6.2592723E-34

// A=-9.0865195E33
// B=1.0060075E34
// OUT=9.7355566E32

// A=-1.0384593E34
// B=-1.0060075E34
// OUT=-2.0444669E34

// A = - infinity  (11111111100000000000000000000000)
// B = 1.0060075E34
// OUT = - infinity  (11111111100000000000000000000000)

// A = NAN  (11111111111000000000000000000000)
// B = 1.0060075E34
// OUT = NAN (11111111111000000000000000000000)
endpackage




