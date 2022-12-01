import cocotb
#from cocotb.binary import BinaryValue
#from cocotb.clock import Clock
#from cocotb.handle import SimHandleBase
#from cocotb.queue import Queue
from cocotb.triggers import RisingEdge
from cocotb.runner import get_runner
from cocotb.triggers import FallingEdge
from cocotb.triggers import Timer
#
from dataclasses import dataclass
import os
#
from pathlib import Path
#
import mk_fpu_add_sub_sp_instance_dataclasses as cls
import bsvstruct_class as dcls

#from cocotb.drivers import BusDriver
#from cocotb.binary import BinaryValue
#from cocotb.regression import TestFactory
#from cocotb.scoreboard import Scoreboard
#from cocotb.result import TestFailure
from testfloat_model import *

import random
import bitstring

fh = open("log_add_sp.txt","w")
# inputdriver -> mk_module_data.drive()
# inputTransaction -> mk_module_data.set()
# outputTransaction -> mk_module_expected.set()
# outputMonitor -> mk_module_data.catch()
# testbench, testbench.compare() -> mk_module_data, mk_module_data.cmp()

def random_input_gen():
    """
    Generate random input data to be applied by InputDriver.
    """
    fh.write('INPUT_GEN')
    func_list = ["f32_add"]
    roundmode_list = ["near_even","near_maxMag","minMag","min","max"]

    for rmode in roundmode_list:
        inp, exp = run_testfloat('f32_add', rmode, 0,1000000)
        if len(inp) == 0 or len(exp) == 0:
            print("\nERROR testfloat did not generate test. Try increasing timeout_value")
        fh.write("\n Test vectors and expected outputs from model")
        fh.write("\n============================================================================")
         
        fh.write("\nadd(sp)  :total expected testcases {0!s} total inp {1!s}  , round_mode {2}".format(len(exp),len(inp),rmode))

		#for e in range(len(exp)):
			#tb.expected_output.append( OutputTransaction(tb, exp[e]) )
		#for i in range(len(inp)):
			#yield InputTransaction(tb, inp[i], 1)

def generate_rand_inp():
	a = dcls.Float()
	b = dcls.Float()
	rnd_mode = "000" #near even

	OP1 = random.randint(-2147483648, 2147483647)
	OP2 = random.randint(-2147483648, 2147483647)

	f1 = bitstring.BitArray(int=OP1, length=32)
	f2 = bitstring.BitArray(int=OP2, length=32)

#	f1 = int_to_float(OP1)
#	f2 = int_to_float(OP2)

	res = f1.float - f2.float
	
	a.set(OP1)
	b.set(OP2)

	data = cls.mk_fpu_add_sub_sp_instance()
	data._send_in.set("send_operands", int(rnd_mode + a.__bin__() + b.__bin__(), 2))

	return data, res

@cocotb.coroutine
def clock_gen(signal):
    while True:
        signal.value = 0
        yield Timer(5) # ps
        signal.value = 1
        yield Timer(5) # ps
    
@cocotb.test()
async def test(dut):
	clk = clock_gen(dut.CLK)
    
	data, expected = generate_rand_inp()

	cocotb.start_soon(clk)

	await data.init_dut(dut)
	#dut.RST_N <= 0
	#yield Timer(10, units='ps')
	#dut.RST_N <= 1
#    input_gen = random_input_gen(tb)
    
    # Issue first transaction immediately.
#    yield tb.input_drv.send(input_gen, False)
	for i in range(100):
		data.sleepall()
		data._send_in.wake()

		data.drive(dut)

		await FallingEdge(dut.CLK)

		data.catch(dut)
		if (data._receive_out.active and data._receive_out.get("receive")[0].integer == 1):
				dut._log.info("CLK " + str(i) + " compare catch " + str(bitstring.BitArray(int=(data._receive_out.get("receive")[1:32].integer), length=32).float) + " " + str(expected))
		await RisingEdge(dut.CLK)
 
if __name__ == "__main__":
	toplevel_lang = os.getenv("TOPLEVEL_LANG", "verilog")
	sim = os.getenv("SIM", "icarus")

	runner = get_runner(sim)()
	runner.build(
		verilog_sources=[
			Path("/mnt/5a853c24-31e3-4d80-9826-512f6bd995e7/saurav/siriusBl4ck/EE_Core/MiniProject_2/DIG-Framework/examples/fbox/fp_addSub/mk_fpu_add_sub_sp_instance.v")
		],
		toplevel="mk_fpu_add_sub_sp_instance"
	)

	runner.test(toplevel="mk_fpu_add_sub_sp_instance", py_module="fpu_add_sub_sp_tb")


