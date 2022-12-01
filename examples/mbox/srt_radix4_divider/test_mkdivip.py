import random
import sys
import cocotb
import logging as log
from cocotb.decorators import coroutine
from cocotb.triggers import Timer, RisingEdge
from cocotb.monitors import BusMonitor
from cocotb.drivers import BusDriver
from cocotb.binary import BinaryValue
from cocotb.regression import TestFactory
from cocotb.scoreboard import Scoreboard
from cocotb.result import TestFailure
from cocotb.clock import Clock

from mkintegerModel import divider_model



class InputDriver(BusDriver):
    """Drives inputs to DUT."""
    _signals = ["ma_start_opcode", "ma_start_funct3",
                "ma_start_dividend", "ma_start_divisor", "EN_ma_start"]

    def __init__(self, dut):
        BusDriver.__init__(self, dut, None, dut.CLK)


class InputTransaction(object):
    """Transactions to be sent by InputDriver"""
    def __init__(self, tb, ma_start_opcode=0, ma_start_funct3=0,
                    ma_start_dividend =0, ma_start_divisor=0,
                    EN_ma_start=0):
        self.ma_start_opcode = BinaryValue(ma_start_opcode, tb.ma_start_opcode_bits, False)
        self.ma_start_funct3 = BinaryValue(ma_start_funct3, tb.ma_start_funct3_bits, False)
        self. ma_start_dividend = BinaryValue( ma_start_dividend, tb.ma_start_dividend_bits, False)
        self.ma_start_divisor = BinaryValue(ma_start_divisor, tb.ma_start_divisor_bits, False)
        self.EN_ma_start = BinaryValue(EN_ma_start, tb.EN_ma_start_bits, False)

class InputMonitor(BusMonitor):
    """ Passive monitors of DUT."""
    _signals = ["ma_start_opcode", "ma_start_funct3",
                "ma_start_dividend","ma_start_divisor", "EN_ma_start", "RDY_ma_start"]

    def __init__(self, dut, callback=None, event=None):
        BusMonitor.__init__(self, dut, None, dut.CLK, dut.RST_N,
                            callback=callback, event=event)
        self.name = "in"

    @coroutine
    def _monitor_recv(self):
        clkedge = RisingEdge(self.clock)

        while True:
            yield clkedge
            if(self.bus.EN_ma_start ==1 and self.bus.RDY_ma_start == 1):
                vec = ( self.bus.ma_start_opcode.value.integer,
                self.bus.ma_start_funct3.value.integer,
                self.bus.ma_start_dividend.value.integer,
                self.bus.ma_start_divisor.value.integer,
                self.bus.EN_ma_start.value.integer)
                self._recv(vec)

class OutputTransaction(object):
    """Transaction to be expected / received by OutputMonitor."""

    def __init__(self, tb=None, mav_result=0):
        """For expected transactions, value 'None' means don't care.
        tb must be an instance of the Testbench class."""
        if mav_result is not None and isinstance(mav_result, int):
            mav_result = mav_result

        self.value = (mav_result)


class OutputMonitor(BusMonitor):
    """Observes outputs of DUT."""
    _signals = ["mav_result","EN_mav_result"]

    def __init__(self, dut, tb, callback=None, event=None):
        BusMonitor.__init__(self, dut, None, dut.CLK, dut.RST_N, callback=callback, event=event)
        self.name = "out"
        self.tb = tb

    @coroutine
    def _monitor_recv(self):
        clkedge = RisingEdge(self.clock)
        while True:
            yield clkedge
            if (self.bus.mav_result.value[0] == 1):

                recieved_mav_result = self.bus.mav_result.value
#                dutResultBin1 = "".join((str(recieved_mav_result)))
#                print(dutResultBin1,"-------------dut value--------------")
                self._recv(OutputTransaction(self.tb, recieved_mav_result))

class Testbench(object):
    class MyScoreboard(Scoreboard):
        def compare(self, got,exp,log, **_):
            got_output = got.value
            exp_output = exp.value
            if got_output == exp_output:
                #print("dut value: {0!s}. exp value: {1!s}.".format( hex(got_output), hex(exp_output)))
                log.warning('test passed')
                
            else:
                log.warning("ERROR value: {0!s}. exp value: {1!s}.".format( hex(got_output), hex(exp_output)))
                print(" value: {0!s}. exp value: {1!s}.".format( hex(got_output), hex(exp_output)))
                exit(1)
    
    def __init__(self, dut):
        self.dut = dut
        self.stopped = False
        self.ma_start_opcode_bits = 4
        self.ma_start_funct3_bits = 3
        self.ma_start_dividend_bits = 64
        self.ma_start_divisor_bits = 64
        self.EN_ma_start_bits = 1
        self.mav_result_bits = 65
        self.input_mon = InputMonitor(dut, callback=self.model)

        init_val = OutputTransaction(self)

        self.input_drv = InputDriver(dut)
        self.output_mon = OutputMonitor(dut, self)

        # scoreboard on the outputs
        self.expected_output = []
        self.scoreboard = Testbench.MyScoreboard(dut)
        self.scoreboard.add_interface(self.output_mon, self.expected_output)


        #self.input_mon = InputMonitor(dut, callback=self.model)

    def model(self, transaction):
        """Model """
        ma_start_opcode, ma_start_funct3, ma_start_dividend, ma_start_divisor, EN_ma_start = transaction
       
        mav_result = divider_model(ma_start_dividend, ma_start_divisor, ma_start_opcode, ma_start_funct3)
        
        self.expected_output.append( OutputTransaction(self, mav_result) )
 #       dutResultBin = "".join((str(mav_result)))
 #       print(dutResultBin,"-------------model value--------------")

    def stop(self):
        """
        Stop generation of expected output transactions.
        One more clock cycle must be executed afterwards, so that, output of
        D-FF can be checked.
        """
        self.stopped = True





@cocotb.coroutine
def clock_gen(signal):
    while True:
        signal <= 0
        yield Timer(10) # ps
        signal <= 1
        yield Timer(10) # ps

@cocotb.test()
def run_test(dut):
    cocotb.fork(clock_gen(dut.CLK))
    tb = Testbench(dut)
    #input_gen = random_input_gen(tb)
    clkedge = RisingEdge(dut.CLK)
    dut.ma_set_flush_c =1
    dut.EN_ma_set_flush = 1
    dut.RST_N = 0
    for i in range(1):
        yield clkedge
    dut.RST_N = 1

 
    for i in range(1000):
        ma_start_opcode = 12
        ma_start_funct3 = 5
        ma_start_dividend = random.randrange(0,18446744073709551615,100)
        ma_start_divisor = random.randrange(0,18446744073709551615,100)
        EN_ma_start = 1
        yield tb.input_drv.send(InputTransaction(tb, ma_start_opcode, ma_start_funct3,
                                ma_start_dividend, ma_start_divisor,
                                EN_ma_start ))
    
    
        for j in range(125):
            #if(j==124):
                #print("%d",i)
            yield clkedge
    tb.stop()

   # raise tb.scoreboard.result

  #  factory = TestFactory(run_test)
  #  factory.generate_tests()
    ##print coverage report
    
