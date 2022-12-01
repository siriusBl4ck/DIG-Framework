from cocotb.triggers import FallingEdge
from cocotb.triggers import RisingEdge

class send_in:
	def __init__(self):
		self.active = False
		self.en_ports = ["EN_send"]
		self.data_ports = { "send_operands" : int(0)}

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

class send_out:
# 
	def __init__(self):
		self.active = False
		self.rdy_ports = ["RDY_send"]
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

class receive_out:
# 
	def __init__(self):
		self.active = False
		self.rdy_ports = ["RDY_receive"]
		self.data_ports = { "receive" : int(0)}

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

class mk_fpu_add_sub_sp_instance:
	def __init__(self):
		self._send_in = send_in()
		self._send_out = send_out()
		self._receive_out = receive_out()

	async def init_dut(self, dut):
		await FallingEdge(dut.CLK)
		dut.RST_N.value = 0
		await RisingEdge(dut.CLK)
		dut.RST_N.value = 1

	def sleepall(self):
		self._send_in.sleep()

	def drive(self, dut):
		self._send_in.drive(dut)

	def catch(self, dut):
		self._send_out.catch(dut)
		self._receive_out.catch(dut)

	def cmp(self, expected):
		c1 = self._send_out.cmp(expected._send_out)
		c2 = self._receive_out.cmp(expected._receive_out)
		return c1 and c2

