import cocotb
from cocotb.binary import BinaryValue
from cocotb.clock import Clock
from cocotb.handle import SimHandleBase
from cocotb.queue import Queue
from cocotb.triggers import RisingEdge
from cocotb.runner import get_runner
from cocotb.triggers import FallingEdge

from dataclasses import dataclass
import os

from pathlib import Path

import mk_test11_dataclasses as dcls

@cocotb.test()
async def test(dut):
	clock = Clock(dut.CLK, 10)
	cocotb.start_soon(clock.start())  # Start the clock

	data = dcls.mk_test11()
	data._putVec_in.set("putVec_a", 1)
	expected = dcls.mk_test11()

	#	data.sleepall()
	#data.putVec_in.wake()

	await FallingEdge(dut.CLK)  # Synchronize with the clock
	#clk_count += 1
	#if (clk_count == 10): exit()
	for i in range(1, 11):
		clock.log.debug("HELLO")
		data.sleepall()
		data._putVec_in.set("putVec_a", i)
		expected._putVec_out.set("putVec", i)
		data._putVec_in.wake()
		data.drive(dut)
		await FallingEdge(dut.CLK)
		data.catch(dut)
		assert data._putVec_out.cmp(expected._putVec_out), f"output q was incorrect on the {i}th cycle"
		
		#assert dut..value == , f"output q was incorrect on the {i}th cycle"
		# compare with the reference model

if __name__ == "__main__":
	clk_count = 0
	#interfaces = []
	#	InterfaceMaker(interfaces)
	# srt_radix4_divider specific code

	# ifc = interfaces[0]

	toplevel_lang = os.getenv("TOPLEVEL_LANG", "verilog")
	sim = os.getenv("SIM", "icarus")

	runner = get_runner(sim)()
	runner.build(
		verilog_sources=[
			Path("./mk_test11.v")
		],
		toplevel="mk_test11"
	)

	runner.test(toplevel="mk_test11", py_module="mk_test11_tb")
