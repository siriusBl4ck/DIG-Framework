/* 
Copyright (c) 2019, IIT Madras All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted
provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this list of conditions
  and the following disclaimer.  
* Redistributions in binary form must reproduce the above copyright notice, this list of 
  conditions and the following disclaimer in the documentation and/or other materials provided 
  with the distribution.  
* Neither the name of IIT Madras  nor the names of its contributors may be used to endorse or 
  promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT 
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
--------------------------------------------------------------------------------------------------

Author: Neel Gala, Shalender Kumar
Email id: neelgala@gmail.com, cs18m050@smail.iitm.ac.in
Details:

--------------------------------------------------------------------------------------------------
see LICENSE.iitm
--------------------------------------------------------------------------------------------------
*/
package tb_float; 
  import FIFO :: * ;
  import FIFOF :: * ;
  import SpecialFIFOs :: * ;
  import fpu_add_sub :: * ;
  import RegFile :: * ;
  import fpu_common :: * ;

`ifdef FLEN64
  `define FLEN 64	
  `define a1 51
  `define a2 52
  `define a3 62
  `define a4 63
  `define MOD mk_fpu_add_sub_dp_instance
`else
  `define FLEN 32
  `define a1 22
  `define a2 23
  `define a3 30
  `define a4 31
  `define MOD mk_fpu_add_sub_sp_instance
`endif

`define index_size 23
`define entry_size 104
`define stim_size 7496191
`define rounding_mode Rnd_Zero

  (*synthesize*)
  module mktb_float(Empty);
    RegFile#(Bit#(`index_size) , Bit#(`entry_size)) stimulus <- mkRegFileLoad("input.txt", 0, `stim_size-1);
//    let fadd <- mk_fpu_add_sub_sp_instance;
    let fadd <- (`MOD);

    FIFOF#(Tuple2#(Bit#(`FLEN), Bit#(5))) ff_golden_output <- mkSizedFIFOF(2);

    Reg#(Bit#(`index_size)) read_index <- mkReg(0);
    Reg#(Bit#(`index_size)) golden_index <- mkReg(0);

    /*doc:rule: */
    rule rl_pick_stimulus_entry;
      
      let _e = stimulus.sub(read_index);
      Bit#(8) _flags = truncate(_e);
      _e = _e >> 8;
      Bit#(`FLEN) _output = truncate(_e);
      _e = _e >> `FLEN;
      Bit#(`FLEN) _inp2 = truncate(_e);
      _e = _e >> `FLEN;
      Bit#(`FLEN) _inp1 = truncate(_e);

      let op1 = FloatingPoint{sign : unpack(_inp1[`a4]), exp: _inp1[`a3:`a2], sfd: _inp1[`a1:0]};
      let op2 = FloatingPoint{sign : unpack(_inp2[`a4]), exp: _inp2[`a3:`a2], sfd: _inp2[`a1:0]};
      $display("TB: Sending inputs[%d]: op1:%h op2:%h, output %h", read_index, op1, op2,_output);
      fadd.send(tuple3(op1, op2, `rounding_mode));
      ff_golden_output.enq(tuple2(_output, truncate(_flags)));
      read_index <= read_index + 1;
//      if(read_index == `stim_size-1)
      if(read_index == 500)
        $finish(0);
    endrule

    /*doc:rule: */
    rule rl_check_output;
//      match {.valid,.out,.flags} = fadd.receive();
      let x = fadd.receive();
      let valid = x.valid;
      let out = x.value;
      let flags = x.ex;
      if(valid==1) begin
        let {e_out, e_flags} = ff_golden_output.first;
        Bit#(`FLEN) _out = {pack(out.sign), out.exp, out.sfd};
        ff_golden_output.deq;
        if( _out != e_out) begin
          $display("TB: Outputs mismatch[%d]. G:%h R:%h,flag %h",golden_index, e_out, _out,flags);
//          $finish(0);
        end
        else begin
            $display("TB: Outputs match [%d], g: %h R: %h", golden_index,e_out, _out);
        end
        golden_index <= golden_index + 1;
        if( flags != unpack(e_flags)) begin
          $display("TB: Flags mismatch. G:%h R:%h", e_flags, flags);
//          $finish(0);
        end
      end
    endrule
  endmodule
endpackage

