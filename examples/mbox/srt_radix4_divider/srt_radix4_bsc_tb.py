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

@cocotb.test()
async def test(dut):
	data = dcls.mk_srt_radix4_divider()
	OP1 = 0xce9e3519a12fe4a4
	OP2 = 0x00000000312fe4a4
	opcode = 0xc
	data._ma_start_in.set("ma_start_dividend", OP1)
	data._ma_start_in.set("ma_start_divisor", OP2)
	data._ma_start_in.set("ma_start_opcode", opcode)
	data.sleepall()
	
	expected = [dcls.mk_srt_radix4_divider() for i in range(8)]

	expected[0]._mav_result_out.set("mav_result", 0x1fffffffefefc4adb)
	expected[1]._mav_result_out.set("mav_result", 0x100000004335e2bbb)
	expected[2]._mav_result_out.set("mav_result", 0x1ffffffffebafe458)
	expected[3]._mav_result_out.set("mav_result", 0x100000000079454d8)
	expected[4]._mav_result_out.set("mav_result", 0x1ffffffffffffffff)
	expected[5]._mav_result_out.set("mav_result", 0x10000000000000003)
	expected[6]._mav_result_out.set("mav_result", 0x1ffffffffd25fc948)
	expected[7]._mav_result_out.set("mav_result", 0x1000000000da036b8)

	clock = Clock(dut.CLK, 10)
	cocotb.start_soon(clock.start())

	await data.init_dut(dut)

	rg_cnt = 0
	cmp_index = 0

	for rg_cycle in range(400):
		data.sleepall()
		opcode = -1
		funct3 = -1
		# rl_stagei1
		#if (rg_cycle % 39 == 0 and rg_cnt < 9): #if rg_cycle == 0:
		#	if rg_cycle != 0: data._ma_start_in.wake()

		if (rg_cycle % 39 == 0 and rg_cnt < 9):
			if (rg_cnt == 0):
				data._ma_start_in.wake()
				opcode = 0xc
				funct3 = 0x4
				data._ma_start_in.set("ma_start_opcode", 0xc)
				data._ma_start_in.set("ma_start_funct3", 0x4)
				rg_cnt += 1
			elif (rg_cnt == 1):
				data._ma_start_in.wake()
				opcode = 0xc
				funct3 = 0x4
				data._ma_start_in.set("ma_start_opcode", 0xc)
				data._ma_start_in.set("ma_start_funct3", 0x5)
				rg_cnt += 1
			elif (rg_cnt == 2):
				data._ma_start_in.wake()
				opcode = 0xc
				funct3 = 0x5
				data._ma_start_in.set("ma_start_opcode", 0xc)
				data._ma_start_in.set("ma_start_funct3", 0x6)
				rg_cnt += 1
			elif (rg_cnt == 3):
				data._ma_start_in.wake()
				opcode = 0xc
				funct3 = 0x6
				data._ma_start_in.set("ma_start_opcode", 0xc)
				data._ma_start_in.set("ma_start_funct3", 0x7)
				rg_cnt += 1
			elif (rg_cnt == 4):
				data._ma_start_in.wake()
				opcode = 0xc
				funct3 = 0x7
				data._ma_start_in.set("ma_start_opcode", 0xe)
				data._ma_start_in.set("ma_start_funct3", 0x4)
				rg_cnt += 1
			elif (rg_cnt == 5):
				data._ma_start_in.wake()
				opcode = 0xc
				funct3 = 0x4
				data._ma_start_in.set("ma_start_opcode", 0xe)
				data._ma_start_in.set("ma_start_funct3", 0x5)
				rg_cnt += 1
			elif (rg_cnt == 6):
				data._ma_start_in.wake()
				opcode = 0xe
				funct3 = 0x5
				data._ma_start_in.set("ma_start_opcode", 0xe)
				data._ma_start_in.set("ma_start_funct3", 0x6)
				rg_cnt += 1
			elif (rg_cnt == 7):
				opcode = 0xe
				funct3 = 0x6
				data._ma_start_in.wake()
				data._ma_start_in.set("ma_start_opcode", 0xe)
				data._ma_start_in.set("ma_start_funct3", 0x7)
				rg_cnt += 1
			elif (rg_cnt == 8):
				opcode = 0xe
				funct3 = 0x7
				data._ma_start_in.wake()
				rg_cnt += 1

		# rl_recieve
		data._mav_result_in.wake()

		# drive
		data.drive(dut)
		
		await FallingEdge(dut.CLK)
		# catch + verify
		data.catch(dut)
		if (data._mav_result_out.get("mav_result") >> 64 == 1 and cmp_index < 8):
			dut._log.info("MODEL " + str(model.divider_model(OP1, OP2, opcode, funct3)))
			dut._log.info("VERIF mav_result " + hex(data._mav_result_out.get("mav_result")) + " expected " + hex(expected[cmp_index]._mav_result_out.get("mav_result")))
			assert data._mav_result_out.cmp(expected[cmp_index]._mav_result_out)
			cmp_index += 1
		await RisingEdge(dut.CLK)

if __name__ == "__main__":
	toplevel_lang = os.getenv("TOPLEVEL_LANG", "verilog")
	sim = os.getenv("SIM", "icarus")

	runner = get_runner(sim)()
	runner.build(
		verilog_sources=[
			Path("/mnt/5a853c24-31e3-4d80-9826-512f6bd995e7/saurav/siriusBl4ck/EE_Core/MiniProject_2/mbox/test/mk_srt_radix4_divider.v")
		],
		toplevel="mk_srt_radix4_divider"
	)

	runner.test(toplevel="mk_srt_radix4_divider", py_module="srt_radix4_bsc_tb")
