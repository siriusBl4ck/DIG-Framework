from cocotb.triggers import FallingEdge
from cocotb.triggers import RisingEdge

class ma_start_in:
	def __init__(self):
		self.active = False
		self.en_ports = ["EN_ma_start"]
		self.data_ports = { "ma_start_dividend" : int(0), "ma_start_divisor" : int(0), "ma_start_opcode" : int(0), "ma_start_funct3" : int(0)}

	def set(self, portname, val): self.data_ports[portname] = val

	def get(self, portname): return self.data_ports[portname]

	def wake(self): self.active = True

	def sleep(self): self.active = False

	def get_ports_raw(self): return [self.en_ports, self.data_ports]

	def drive(self, dut):
		for k in self.en_ports:
			dut._log.info("DRIVE " + k + " " + hex(self.active))
			dut._id(k, extended=False).value = self.active
		for k in self.data_ports.keys():
			dut._log.info("DRIVE " + k + " " + hex(self.data_ports[k]))
			dut._id(k, extended=False).value = self.data_ports[k]

class ma_start_out:
# Primary Action
	def __init__(self):
		self.active = False
		self.rdy_ports = ["RDY_ma_start"]
		self.data_ports = {}

	def set(self, portname, val): self.data_ports[portname] = val

	def get(self, portname): return self.data_ports[portname]

	def get_ports_raw(self): return [self.rdy_ports, self.data_ports]

	def catch(self, dut):
		for rdy in self.rdy_ports:
			if dut._id(rdy, extended=False) == 1:
				self.active = True
				for k in self.data_ports.keys():
					if rdy[4:] in k:
						self.data_ports[k] = dut._id(k, extended=False).value
						dut._log.info("CATCH " + k + " " + hex(self.data_ports[k]))
			else: self.active = False

	def cmp(self, expected):
		for k in self.data_ports.keys():
			if self.data_ports[k] != expected.data_ports[k]: return False
		return True

class mav_result_in:
	def __init__(self):
		self.active = False
		self.en_ports = ["EN_mav_result"]
		self.data_ports = {}

	def set(self, portname, val): self.data_ports[portname] = val

	def get(self, portname): return self.data_ports[portname]

	def wake(self): self.active = True

	def sleep(self): self.active = False

	def get_ports_raw(self): return [self.en_ports, self.data_ports]

	def drive(self, dut):
		for k in self.en_ports:
			dut._log.info("DRIVE " + k + " " + hex(self.active))
			dut._id(k, extended=False).value = self.active
		for k in self.data_ports.keys():
			dut._log.info("DRIVE " + k + " " + hex(self.data_ports[k]))
			dut._id(k, extended=False).value = self.data_ports[k]

class mav_result_out:
# Struct {Tuple2#(type a, type b)} {members {{Bit#(1) tpl_1 {width 1}} {Bit#(64) tpl_2 {width 64}}}} {width 65} {position {%/Libraries/Prelude.bs 3297 5 {Library Prelude}}}
	def __init__(self):
		self.active = False
		self.rdy_ports = ["RDY_mav_result"]
		self.data_ports = { "mav_result" : int(0)}

	def set(self, portname, val): self.data_ports[portname] = val

	def get(self, portname): return self.data_ports[portname]

	def get_ports_raw(self): return [self.rdy_ports, self.data_ports]

	def catch(self, dut):
		for rdy in self.rdy_ports:
			if dut._id(rdy, extended=False) == 1:
				self.active = True
				for k in self.data_ports.keys():
					if rdy[4:] in k:
						self.data_ports[k] = dut._id(k, extended=False).value
						dut._log.info("CATCH " + k + " " + hex(self.data_ports[k]))
			else: self.active = False

	def cmp(self, expected):
		for k in self.data_ports.keys():
			if self.data_ports[k] != expected.data_ports[k]: return False
		return True

class ma_set_flush_in:
	def __init__(self):
		self.active = False
		self.en_ports = ["EN_ma_set_flush"]
		self.data_ports = { "ma_set_flush_c" : int(0)}

	def set(self, portname, val): self.data_ports[portname] = val

	def get(self, portname): return self.data_ports[portname]

	def wake(self): self.active = True

	def sleep(self): self.active = False

	def get_ports_raw(self): return [self.en_ports, self.data_ports]

	def drive(self, dut):
		for k in self.en_ports:
			dut._log.info("DRIVE " + k + " " + hex(self.active))
			dut._id(k, extended=False).value = self.active
		for k in self.data_ports.keys():
			dut._log.info("DRIVE " + k + " " + hex(self.data_ports[k]))
			dut._id(k, extended=False).value = self.data_ports[k]

class ma_set_flush_out:
# Primary Action
	def __init__(self):
		self.active = False
		self.rdy_ports = ["RDY_ma_set_flush"]
		self.data_ports = {}

	def set(self, portname, val): self.data_ports[portname] = val

	def get(self, portname): return self.data_ports[portname]

	def get_ports_raw(self): return [self.rdy_ports, self.data_ports]

	def catch(self, dut):
		for rdy in self.rdy_ports:
			if dut._id(rdy, extended=False) == 1:
				self.active = True
				for k in self.data_ports.keys():
					if rdy[4:] in k:
						self.data_ports[k] = dut._id(k, extended=False).value
						dut._log.info("CATCH " + k + " " + hex(self.data_ports[k]))
			else: self.active = False

	def cmp(self, expected):
		for k in self.data_ports.keys():
			if self.data_ports[k] != expected.data_ports[k]: return False
		return True

class mk_srt_radix4_divider:
	def __init__(self):
		self._ma_start_in = ma_start_in()
		self._ma_start_out = ma_start_out()
		self._mav_result_in = mav_result_in()
		self._mav_result_out = mav_result_out()
		self._ma_set_flush_in = ma_set_flush_in()
		self._ma_set_flush_out = ma_set_flush_out()

	async def init_dut(self, dut):
		await FallingEdge(dut.CLK)
		dut.RST_N.value = 0
		await RisingEdge(dut.CLK)
		dut.RST_N.value = 1

	def sleepall(self):
		self._ma_start_in.sleep()
		self._mav_result_in.sleep()
		self._ma_set_flush_in.sleep()

	def drive(self, dut):
		self._ma_start_in.drive(dut)
		self._mav_result_in.drive(dut)
		self._ma_set_flush_in.drive(dut)

	def catch(self, dut):
		self._ma_start_out.catch(dut)
		self._mav_result_out.catch(dut)
		self._ma_set_flush_out.catch(dut)

	def cmp(self, expected):
		c1 = self._ma_start_out.cmp(expected._ma_start_out)
		c3 = self._mav_result_out.cmp(expected._mav_result_out)
		c5 = self._ma_set_flush_out.cmp(expected._ma_set_flush_out)
		return c1 and c3 and c5

