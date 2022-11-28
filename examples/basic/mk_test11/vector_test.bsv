import Vector::*;
//import Tuple::*;

typedef Tuple2#(Bit#(1), Vector#(5, Bit#(2))) MyType;

interface Ifc_vectest;
	method MyType getVec();
	method ActionValue#(MyType) putVec(MyType a);
endinterface

(* synthesize *)
module mk_test11(Ifc_vectest);
	Reg#(MyType) rg_a <- mkReg(unpack(0));
	
	method MyType getVec;
		return rg_a;
	endmethod
	
	method ActionValue#(MyType) putVec(MyType a);
		rg_a <= a;
		return rg_a;
	endmethod
endmodule

// Vector#(5, Tuple2#(Bit#(1), Bit#(5)))
// Tuple2#(Bit#(1), Vector#(5, Bit#(2)))
// Tuple3#(Bit#(1), Tuple2#(Bit#(2), Bit#(3)), Vector#(5, Bit#(4)))
// Vector#(5, Vector#(5, Bit#(2)))
// Maybe#(Vector#(5, Bit#(2)))
// Maybe#(Tuple2#(Bit#(2), Bit#(3)))
// Tuple2#(Bit#(1), Vector#(5, Tuple2#(Bit#(1), Bit#(2))))
// Maybe#(Tuple2#(Bit#(1), Vector#(5, Tuple2#(Bit#(1), Bit#(2)))))
// Vector#(5, Maybe#(Vector#(5, Bit#(2))))
// Tuple2#(Maybe#(Tuple2#(Bit#(1), Bit#(2))), Bit#(3))

