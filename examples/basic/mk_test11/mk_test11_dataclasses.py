class getVec_out:
	def __init__(self):
		self.rdy_ports = ["RDY_getVec_fst","RDY_getVec_snd"]
		self.data_ports = { "getVec_fst" : int(0), "getVec_snd" : int(0)}

	def set(self, portname, val): self.data_ports[portname] = val

	def get_ports_raw(self): return [self.rdy_ports, self.data_ports]

	def catch(self, dut):
		for rdy in self.rdy_ports:
			if dut._id(rdy, extended=False) == 1:
				for k in self.data_ports.keys():
					if rdy[4:] in k:
						self.data_ports[k] = dut._id(k, extended=False).value
						dut._log.info("CATCH " + k + " " + hex(self.data_ports[k]))

	def cmp(self, expected):
		for k in self.data_ports.keys():
			if self.data_ports[k] != expected.data_ports[k]: return False
		return True

class putVec_in:
	def __init__(self):
		self.active = False
		self.en_ports = ["EN_putVec"]
		self.data_ports = { "putVec_a" : int(0)}

	def set(self, portname, val): self.data_ports[portname] = val

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

class putVec_out:
	def __init__(self):
		self.rdy_ports = ["RDY_putVec"]
		self.data_ports = { "putVec" : int(0)}

	def set(self, portname, val): self.data_ports[portname] = val

	def get_ports_raw(self): return [self.rdy_ports, self.data_ports]

	def catch(self, dut):
		for rdy in self.rdy_ports:
			if dut._id(rdy, extended=False) == 1:
				for k in self.data_ports.keys():
					if rdy[4:] in k:
						self.data_ports[k] = dut._id(k, extended=False).value
						dut._log.info("CATCH " + k + " " + hex(self.data_ports[k]))

	def cmp(self, expected):
		for k in self.data_ports.keys():
			if self.data_ports[k] != expected.data_ports[k]: return False
		return True

class mk_test11:
	def __init__(self):
		self._getVec_out = getVec_out()
		self._putVec_in = putVec_in()
		self._putVec_out = putVec_out()

	def sleepall(self):
		self._putVec_in.sleep()

	def drive(self, dut):
		self._putVec_in.drive(dut)

	def catch(self, dut):
		self._getVec_out.catch(dut)
		self._putVec_out.catch(dut)

	def cmp(self, expected):
		c0 = self._getVec_out.cmp(expected._getVec_out)
		c2 = self._putVec_out.cmp(expected._putVec_out)
		return c0 and c2

