import dataclasses as dcls
import shlex
import utils
import sys
import re

class module:
	def __init__(self, _name, _methods = [], _clk = None, _rst = None, _vdir = None):
		self.name = _name
		self.methods = _methods
		self.clk = _clk
		self.rst = _rst
		self.vdir = _vdir

	def add_clk(self, _port_name): self.clk = _port_name

	def add_rst(self, _port_name): self.rst = _port_name

	def set_methods(self, _methods = []): self.methods = _methods
	
	def list_ports(self):
		print("*********************************************************")
		print("MODULE:", self.name, end='')
		#print("*********************************************************")
		if (self.clk != None): print(", CLOCK:", self.clk, end='')
		if (self.rst != None): print(", RESET:", self.rst, end='')
		print("\n*********************************************************")
		for m in self.methods:
			m.list_ports()
		print("*********************************************************")
	
	def vdir(self): return self.vdir

	def name(self): return self.name

	def get_methods(self): return self.methods

	def write_dataclasses(self, dcls_dir):
		ifc = "class {0}:\n".format(self.name)
		attribs = []
		ifc += "	def __init__(self):\n"

		f = open(dcls_dir + "/" + self.name + "_dataclasses.py", "w")

		f.write("from cocotb.triggers import FallingEdge\nfrom cocotb.triggers import RisingEdge\n\n")

		for m in self.methods:
			dcls = m.create_dataclasses()
			f.write(dcls[0])
			f.write(dcls[1])
			if len(dcls[0]) != 0: attribs.append(m.get_name() + "_in")
			if len(dcls[1]) != 0: attribs.append(m.get_name() + "_out") 

		for a in attribs:
			ifc += "		self._{0} = {0}()\n".format(a)

		ifc += "\n"
		ifc += "	async def init_dut(self, dut):\n"
		ifc += "		await FallingEdge(dut.CLK)\n"
		ifc += "		dut.RST_N.value = 0\n"
		ifc += "		await RisingEdge(dut.CLK)\n"
		ifc += "		dut.RST_N.value = 1\n\n"

		ifc += "	def sleepall(self):\n"
		for a in attribs:
			if a[-2:] == "in": ifc += "		self._{0}.sleep()\n".format(a)

		ifc += "\n	def drive(self, dut):\n"
		for a in attribs:
			if a[-2:] == "in":
				#ifc += "		if self._{0}.active:\n".format(a)
				ifc += "		self._{0}.drive(dut)\n".format(a)

		ifc += "\n	def catch(self, dut):\n"
		
		
		for a in range(len(attribs)):
			if attribs[a][-3:] == "out":
				ifc += "		self._{0}.catch(dut)\n".format(attribs[a])

		ifc += "\n	def cmp(self, expected):\n"

		cs = []

		for a in range(len(attribs)):
			if attribs[a][-3:] == "out":
				ifc += "		c{0} = self._{1}.cmp(expected._{1})\n".format(a, attribs[a])
				cs.append("c{0}".format(a))

		c_expr = " and ".join(cs)

		ifc += "		return"


		if len(cs) != 0: ifc += " " + c_expr

		ifc += "\n\n"
		
		f.write(ifc)
		f.close()

	def populate_method_vports(self):
		verilogdir = self.vdir
		moduleName = self.name

		#print(self.methods)

		#print("Module name:", moduleName)
		#print("Verilog filepath:", verilogdir + '/' + moduleName + ".v")
		
		with open(verilogdir + '/' + moduleName + ".v", "r") as f:
			found = False
			for line in f:
				#print(line)
				if (not found) and (not ("// Name                         I/O  size props" in line)):
					found = True
					continue
				s = line.split()

				#if len(s) < 4: break
				try:
					if s[0] != "//": break
				except:
					continue

				curr_method = None

				try:
					for m in range(len(self.methods)):
						if self.methods[m].get_name() in s[1]:
							curr_method = m
							break
				except:
					continue

				if curr_method == None:
					try:
						if 'CLK' in s[1]:
							self.clk = s[1]
						elif 'RST' in s[1]:
							self.rst = s[1]
						continue
					except:
						continue

				if (s[2] == "O"):
					self.methods[m].add_vout(s[1], int(s[3]))
				else:
					self.methods[m].add_vinp(s[1], int(s[3]))

	#def run(self, TODO

class method:
	def __init__(self, _name, _out_elab_type):
		self.name = _name
		self.vout_ports = {}
		self.vin_ports = {}
		self.out_elab_type = _out_elab_type

#		for n in range(len(_voutput_ports_names)):
#			self.vout_ports[_voutput_ports_names[n]] = _voutput_ports_bits[n]
#
#		for n in range(len(_vinput_ports_names)):
#			self.vin_ports[_vinput_ports_names[n]] = _vinput_ports_bits[n]
	
	def add_vinp(self, _port_name = None, _port_bits = None): self.vin_ports[_port_name] = _port_bits
	
	def add_vout(self, _port_name = None, _port_bits = None): self.vout_ports[_port_name] = _port_bits

	def get_name(self): return self.name;

	def list_ports(self):
		print("VERILOG METHOD: " + self.name)
		print("**************************")
		print("INPUT_NAME", "BITWIDTH")
		for k in self.vin_ports.keys():
			print(k, self.vin_ports[k])
		print("OUTPUT_NAME", "BITWIDTH")
		for k in self.vout_ports.keys():
			print(k, self.vout_ports[k])
		print("**************************")
	
	def create_dataclasses(self):
		s_in = ""
		s_out = ""

		if len(self.vin_ports.keys()) != 0:
			s_in = "class {0}:\n".format(self.name + "_in")

			total = 0

			for k in self.vin_ports.keys():
			#	if ("RDY" in k) or ("EN" in k): continue
			#	s_in += "	{0}: int = 0\n".format(k)
				total += self.vin_ports[k]

			data_port_dict = "		self.data_ports = {"

			en_port_dict = "		self.en_ports = ["

			for k in self.vin_ports.keys():
				if "EN" in k:
					en_port_dict += "\"" + k + "\","
				else:
					data_port_dict += " \"" + k + "\" : int(0),"

			if en_port_dict[-1] == ",": en_port_dict = en_port_dict[:-1]
			if data_port_dict[-1] == ",": data_port_dict = data_port_dict[:-1]

			en_port_dict += "]\n"
			data_port_dict += "}\n"

			s_in += "	def __init__(self):\n		self.active = False\n"

			s_in += en_port_dict + data_port_dict + "\n"

			s_in += "	def set(self, portname, val): self.data_ports[portname] = val\n\n"

			s_in += "	def get(self, portname): return self.data_ports[portname]\n\n"

			#s_in += "	def __bin__(self):\n"

			#s_in += "		val = \"\"\n"

			#for k in self.vin_ports.keys():
			#	if ("RDY" in k) or ("EN" in k): continue
			#	s_in += "		val += \"{0:0" + str(self.vin_ports[k]) + "b}\"" + ".format({0} & {1})\n".format("self.ports[" + k + "]", hex(pow(2, self.vin_ports[k]) - 1))

			#s_in += "		return val\n\n"

			s_in += "	def wake(self): self.active = True\n\n"

			s_in += "	def sleep(self): self.active = False\n\n"

			s_in += "	def get_ports_raw(self): return [self.en_ports, self.data_ports]\n\n"

			s_in += "	def drive(self, dut):\n"
			s_in += "		for k in self.en_ports:\n"
			s_in += "			dut._log.info(\"DRIVE \" + k + \" \" + hex(self.active))\n"
			s_in += "			dut._id(k, extended=False).value = self.active\n"
			s_in += "		for k in self.data_ports.keys():\n"
			s_in += "			dut._log.info(\"DRIVE \" + k + \" \" + hex(self.data_ports[k]))\n"
			s_in += "			dut._id(k, extended=False).value = self.data_ports[k]\n\n"

			#s_in += "	def size(self) -> int: return {0}\n\n".format(total)

		if len(self.vout_ports.keys()) != 0: # output dataclass
			s_out = "class {0}:\n".format(self.name + "_out")
			s_out += "# " + self.out_elab_type + "\n"

			total = 0

			for k in self.vout_ports.keys():
				#if ("RDY" in k) or ("EN" in k): continue
				#s_out += "	{0}: int = 0\n".format(k)
				total += self.vout_ports[k]

			data_port_dict = "		self.data_ports = {"
			rdy_port_dict = "		self.rdy_ports = ["

			for k in self.vout_ports.keys():
				if "RDY" in k: rdy_port_dict += "\"" + k + "\","
				else: data_port_dict += " \"" + k + "\" : int(0),"

			if data_port_dict[-1] == ",": data_port_dict = data_port_dict[:-1]
			if rdy_port_dict[-1] == ",": rdy_port_dict = rdy_port_dict[:-1]

			data_port_dict += "}\n"
			rdy_port_dict += "]\n"

			s_out += "	def __init__(self):\n		self.active = False\n"

			s_out += rdy_port_dict + data_port_dict + "\n"

			s_out += "	def set(self, portname, val): self.data_ports[portname] = val\n\n"

			s_out += "	def get(self, portname): return self.data_ports[portname]\n\n"

			#s_out += "	def __bin__(self):\n"

			#s_out += "		val = \"\"\n"

			#for k in self.vout_ports.keys():
			#	if ("RDY" in k) or ("EN" in k): continue
			#	s_out += "		val += \"{0:0" + str(self.vout_ports[k]) + "b}\"" + ".format(self.{0} & {1})\n".format(k, hex(pow(2, self.vout_ports[k]) - 1))

			#s_out += "		return val\n\n"

			#s_out += "	def get(self) -> int: return int(self.__bin__(), base=2)\n\n"
			s_out += "	def get_ports_raw(self): return [self.rdy_ports, self.data_ports]\n\n"

			#s_out += "	def size(self) -> int: return {0}\n\n".format(total)

			s_out += "	def catch(self, dut):\n"
			s_out += "		for rdy in self.rdy_ports:\n"
			s_out += "			if dut._id(rdy, extended=False) == 1:\n"
			s_out += "				self.active = True\n"
			s_out += "				for k in self.data_ports.keys():\n"
			s_out += "					if rdy[4:] in k:\n"
			s_out += "						self.data_ports[k] = dut._id(k, extended=False).value\n"
			s_out += "						dut._log.info(\"CATCH \" + k + \" \" + hex(self.data_ports[k]))\n"
			s_out += "			else: self.active = False\n\n"
			
			s_out += "	def cmp(self, expected):\n"
			s_out += "		for k in self.data_ports.keys():\n"
			s_out += "			if self.data_ports[k] != expected.data_ports[k]: return False\n"
			s_out += "		return True\n\n"



		return (s_in, s_out)

def outputExpander(ba_name, module_name):
	utils.shellCommand(shlex.split('./tcllibs/genOutputInfo.tcl {0} > type_info.txt'.format(ba_name))).run()
	
	f = open("type_info.txt", "r")
	
	data = f.readlines()
	
	interface_names = []
	methods_bits = []
	methods_port_names = []
	
	i = 0
	
	while True:
		try:
			interface_names.append(re.findall(r'Interface (.*?) {', data[i]))
			methods_bits.append(re.findall(r'method {(.*?) {{\(\* ports', data[i]))
			methods_port_names.append(re.findall(r'ports = \[(.*?)\]', data[i]))
			i += 2
		except IndexError:
			break
	
	types = []
	names = []
	
	for i in range(len(interface_names)):
		for j in range(len(methods_bits[i])):
			method_info = methods_bits[i][j].split()
			ports_info = methods_port_names[i][j].split(',')
	
			for p in range(len(ports_info)):
				if ports_info[p] == '':
					del ports_info[p]
	
			end_bits = len(method_info) - 1
			end_names = len(ports_info) - 1
	
			index_cleanup = end_names
			if index_cleanup < 0: index_cleanup = 0
			
			method_name_type = ' '.join(methods_bits[i][j].split()[:(end_bits - index_cleanup)])
			outType = ''.join(method_name_type.split()[:-1])
			methodName = method_name_type.split()[-1]
	
			while outType[0] == '{': outType = outType[1:]
	
			while outType[-1] == '}': outType = outType[:-1]
	
			print(outType)
	
			if outType.split('#')[0] == 'ActionValue':
				outType = '#'.join(outType.split('#')[1:])[1:-1]
	
			print(outType)
	
			types.append(outType)
			names.append(methodName)
	
	typelist = ' '.join(types)
	
	f = open("typelist.txt", "w")
	
	f.write(typelist)
	
	f.close()
	
	utils.shellCommand('./tcllibs/genTypeInfo.tcl {0} > type_info.txt'.format(module_name)).run()
	
	f = open("./type_info.txt", "r")
	
	expanded = f.readlines()
	
	expanded = [i[:-1] for i in expanded]
	
	expansionMap = dict(zip(names, expanded))
	
	print(expansionMap)

	return expansionMap

def get_module_primitive(verilog_dir, build_dir, module_name, expansionMap):
	utils.log.info('Running bluetcl to capture methods used in the design')
	utils.shellCommand(shlex.split('./tcllibs/genMethodInfo.tcl {0} {1} > {2}'.format(build_dir, module_name,'module_info.txt'))).run()

	f = open('module_info.txt', 'r')
	bluetcl_out = f.readlines()[0]

	print(bluetcl_out)

	br = 0
	method_names = []

	init_pos = -1

	found = False

	for i in range(len(bluetcl_out)):
		if bluetcl_out[i] == '{':
			if br == 0: init_pos = i + 1
			br += 1
		if bluetcl_out[i] == '}':
			br -= 1
		if ((bluetcl_out[i] == ' ') and (br == 1) and (not found)):
			method_names.append(bluetcl_out[init_pos:i])
			found = True
		if br == 0: found = False
	
	methods = []

	for m in method_names:
		try:
			methods.append(method(_name=m, _out_elab_type=expansionMap[m]))
		except:
			methods.append(method(_name=m, _out_elab_type=""))
	
	mod = module(_name=module_name, _methods=methods, _vdir=verilog_dir)

	return mod

#def 

if __name__=="__main__":
	args = sys.argv
	try:
		verilog_dir = args[1]
		build_dir = args[2]
		module_name = args[3]
		ba_name = args[4]
		dcls_dir = args[5]
		print(verilog_dir, module_name)
	except:
		print("[ERROR] Please provide command line arguments for vdir and module_name!")
		exit

	utils.log.info('Running bluetcl to capture structs used in the design')
	utils.shellCommand(shlex.split('./tcllibs/genStructInfo.tcl {0} > {1}'.format(ba_name, 'struct_info.txt'))).run()

	utils.create_dataclass_frm_bsv('./struct_info.txt')

	expansionMap = outputExpander(ba_name, module_name)

	mod = get_module_primitive(verilog_dir, build_dir, module_name, expansionMap)

	mod.populate_method_vports()

	mod.write_dataclasses(dcls_dir)

	mod.list_ports()
