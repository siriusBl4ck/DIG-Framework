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

import mk_srt_radix4_divider_dataclasses as dcls

import mkintegerModel as model

import random

@cocotb.test()
async def test(dut):
	data = dcls.mk_srt_radix4_divider()
	OP1 = 0xce9e3519a12fe4a4
	OP2 = 0x00000000312fe4a4
	opcode = 0xc
	funct3 = 5
	data._ma_start_in.set("ma_start_dividend", OP1)
	data._ma_start_in.set("ma_start_divisor", OP2)
	data._ma_start_in.set("ma_start_opcode", opcode)
	data._ma_start_in.set("ma_start_funct3", funct3)
	data.sleepall()
	
	clock = Clock(dut.CLK, 10)
	cocotb.start_soon(clock.start())

	await data.init_dut(dut)

	rg_cnt = 0
	cmp_index = 0

	for rg_cycle in range(2000):
		data.sleepall()
		OP1 = random.randrange(0,18446744073709551615,100)
		OP2 = random.randrange(0,18446744073709551615,100)

		if rg_cycle % 39 == 0:
			data._ma_start_in.wake()
			data._ma_start_in.set("ma_start_dividend", OP1)
			data._ma_start_in.set("ma_start_divisor", OP2)
			#rg_cnt += 1

		data._mav_result_in.wake()

		# drive
		data.drive(dut)
		
		await FallingEdge(dut.CLK)
		# catch + verify
		data.catch(dut)
		if (data._mav_result_out.get("mav_result") >> 64 == 1 and cmp_index < 8):
			dut._log.info("MODEL " + str(model.divider_model(OP1, OP2, opcode, funct3)))
			#dut._log.info("VERIF mav_result " + hex(data._mav_result_out.get("mav_result")) + " expected " + hex(expected[cmp_index]._mav_result_out.get("mav_result")))
			#assert data._mav_result_out.cmp(expected[cmp_index]._mav_result_out)
			cmp_index += 1
		await RisingEdge(dut.CLK)

if __name__ == "__main__":
	toplevel_lang = os.getenv("TOPLEVEL_LANG", "verilog")
	sim = os.getenv("SIM", "icarus")

	runner = get_runner(sim)()
	runner.build(
		verilog_sources=[
			Path("./mk_srt_radix4_divider.v")
		],
		toplevel="mk_srt_radix4_divider"
	)

	runner.test(toplevel="mk_srt_radix4_divider", py_module="srt_radix4_verif_tb")
