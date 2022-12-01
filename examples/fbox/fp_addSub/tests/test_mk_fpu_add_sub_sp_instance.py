import cocotb
from cocotb.result import TestFailure, TestSuccess
from cocotb.triggers import Timer, RisingEdge
from cocotb.clock import Clock
import subprocess
import shlex
from cocotb.binary import BinaryValue
from cocotb.binary import BinaryRepresentation
from random import randint
import random
import sys
import math 
from cocotb.decorators import coroutine
import random

N = 1000 # No. of testcases 
validBit = BinaryValue(int("10000000000000000000000000000000000000",2),n_bits=38,bigEndian=False)

#=========== FPU AddSub design Interface ==========================
#  Ports:
#  Name                         I/O  size props
#  CLK                            I     1 clock
#  RST_N                          I     1 reset
#  send_operands                  I    67
#  EN_send                        I     1
#  RDY_send                       O     1 const
#  receive                        O    38 reg  
#  RDY_receive                    O     1 const
#==================================================================


def sys_command(command):
    x = subprocess.Popen(shlex.split(command),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         )
    try:
        out, err = x.communicate(timeout=100)
    except TimeoutError:
        x.kill()
        out, err = x.communicate()

    out = out.rstrip()
    err = err.rstrip()
    return out.decode("ascii")

def run_testfloat(function, round_mode, level, file_name):
    testfloat_gen_path = sys_command("which testfloat_gen")
    seed = randint(1,2)
    command = "qemu-riscv64 {0} -r{1} -seed {2} -level {3} {4}".format(testfloat_gen_path,round_mode,seed,level,function)    
    
    testgen = sys_command(command)
    fp = open(file_name,"w")
    fp.write(testgen)
    fp.close()

# ========================================= Round_Mode = Near Even ===================================================

@cocotb.test()
def basic_test_near_even(dut):
    rmode = BinaryValue(int("000",2),n_bits=3,bigEndian=False) 
    cocotb.fork(Clock(dut.CLK, 10,).start())
    clkedge = RisingEdge(dut.CLK)
    dut.RST_N = 0
    dut.EN_send = 1

    for i in range (2):
        yield clkedge
    dut.RST_N <= 1
    yield clkedge

    for i in range (2):
        yield clkedge

    binOp1 = BinaryValue(int("38FFDFEE",16),n_bits=32,bigEndian=False)
    binOp2 = BinaryValue(int("4001FFFF",16),n_bits=32,bigEndian=False)
    ExOp   = BinaryValue(int("400201FF",16),n_bits=32,bigEndian=False)
    ExFlag = BinaryValue(int("01",16),n_bits=5,bigEndian=False)
    binInput = BinaryValue((((binOp2 << 32) + binOp1)<<3)+rmode,n_bits=67,bigEndian=False)
    binExOp = BinaryValue(((ExOp << 5) + ExFlag)+validBit,n_bits=38,bigEndian=False)
    
    dut.send_operands <= binInput

    for i in range (5):
        yield clkedge
    
    receive = dut.receive.value
    dut.EN_send = 0
    yield clkedge
    
    if(receive == binExOp):
        raise TestSuccess
    else:
        raise TestFailure
    
run_testfloat("f32_add","near_even",1,"near_even_input.txt")

@cocotb.test()
def run_test_near_even(dut):
    count = 1
    rmode = BinaryValue(int("000",2),n_bits=3,bigEndian=False) 
    fp = open("near_even_input.txt","r")
    fp1 = open("near_even_result.txt","w")
    head = [next(fp) for x in range(N)]
    fp1.write("Operand_1    Operand_2    Expected_result    Expected_flag    Test_result    DUT_result    DUT_flag\n-----------------------------------------------------------------------------------------------------\n")
    for line in range(N):
        field  = head[line].split()
        operand_1 = field[0]
        operand_2 = field[1]
        expected_out = field[2]
        exception_flag = field[3]

        cocotb.fork(Clock(dut.CLK, 10,).start())
        clkedge = RisingEdge(dut.CLK)
        dut.RST_N <= 0
        dut.EN_send <= 0

        for i in range (5):
            yield clkedge
        
        dut.RST_N <= 1
        yield clkedge

        dut.EN_send <= 1

        for i in range (5):
            yield clkedge

        binOp1 = BinaryValue(int(operand_1,16),n_bits=32,bigEndian=False)
        binOp2 = BinaryValue(int(operand_2,16),n_bits=32,bigEndian=False)
        ExOp   = BinaryValue(int(expected_out,16),n_bits=32,bigEndian=False)
        ExFlag = BinaryValue(int(exception_flag,16),n_bits=5,bigEndian=False)
        binInput = BinaryValue((((binOp2 << 32) + binOp1)<<3)+rmode,n_bits=67,bigEndian=False)
        binExOp = BinaryValue(((ExOp << 5) + ExFlag)+validBit,n_bits=38,bigEndian=False)
                      
        dut.send_operands = binInput
        for i in range (50):
            yield clkedge
        
        receive = dut.receive.value
        
        dut.RST_N = 0
        yield clkedge
        dut.RST_N = 1
        yield clkedge

        temp0  = receive.binstr
        dutExFlag = BinaryValue(int(temp0[33:],2),n_bits=5,bigEndian=False)

        temp = BinaryValue(receive>>5,n_bits=33,bigEndian=False)
        dutExOut = temp.binstr
        dutExOut = BinaryValue(int(dutExOut[1:],2),n_bits=32,bigEndian=False)

        dutExOutHex = ((hex(dutExOut))[2:]).upper()
        dutExFlagHex = ((hex(dutExFlag))[2:]).upper()

        dutExOutHex = "0"* (8-len(dutExOutHex))+ dutExOutHex    # 0 padding to match fixed length of 8
        dutExFlagHex = "0"* (2-len(dutExFlagHex))+ dutExFlagHex # 0 padding to match fixed length of 8

        if(receive != binExOp):
            result = "FAIL"
        else:
            result = "PASS"
        print("Testcase No. : ",count," Tested..")
        count +=1
        fp1.write(operand_1 +"     " + operand_2 +"     "+ expected_out + "           " + exception_flag + "               "+ 
        result+"           "+dutExOutHex + "      "+dutExFlagHex +"\n") 


# ========================================= Round_Mode = Rnd_Nearest_towards_Zero (rnear_minMag)===================================================

run_testfloat("f32_add","minMag",1,"minMag_input.txt")

@cocotb.test()
def run_test_minMag(dut):
    count = 1
    rmode = BinaryValue(int("001",2),n_bits=3,bigEndian=False) 
    fp = open("minMag_input.txt","r")
    fp1 = open("minMag_result.txt","w")
    head = [next(fp) for x in range(N)]
    fp1.write("Operand_1    Operand_2    Expected_result    Expected_flag    Test_result    DUT_result    DUT_flag\n-----------------------------------------------------------------------------------------------------\n")
    for line in range(N):
        field  = head[line].split()
        operand_1 = field[0]
        operand_2 = field[1]
        expected_out = field[2]
        exception_flag = field[3]

        cocotb.fork(Clock(dut.CLK, 10,).start())
        clkedge = RisingEdge(dut.CLK)
        dut.RST_N <= 0
        dut.EN_send <= 0

        for i in range (5):
            yield clkedge
        
        dut.RST_N <= 1
        yield clkedge

        dut.EN_send <= 1

        for i in range (5):
            yield clkedge

        binOp1 = BinaryValue(int(operand_1,16),n_bits=32,bigEndian=False)
        binOp2 = BinaryValue(int(operand_2,16),n_bits=32,bigEndian=False)
        ExOp   = BinaryValue(int(expected_out,16),n_bits=32,bigEndian=False)
        ExFlag = BinaryValue(int(exception_flag,16),n_bits=5,bigEndian=False)
        binInput = BinaryValue((((binOp2 << 32) + binOp1)<<3)+rmode,n_bits=67,bigEndian=False)
        binExOp = BinaryValue(((ExOp << 5) + ExFlag)+validBit,n_bits=38,bigEndian=False)
                      
        dut.send_operands = binInput
        for i in range (5):
            yield clkedge

        receive = dut.receive.value
        
        dut.RST_N = 0
        yield clkedge
        dut.RST_N = 1
        yield clkedge

        temp0  = receive.binstr
        dutExFlag = BinaryValue(int(temp0[33:],2),n_bits=5,bigEndian=False)

        temp = BinaryValue(receive>>5,n_bits=33,bigEndian=False)
        dutExOut = temp.binstr
        dutExOut = BinaryValue(int(dutExOut[1:],2),n_bits=32,bigEndian=False)

        dutExOutHex = ((hex(dutExOut))[2:]).upper()
        dutExFlagHex = ((hex(dutExFlag))[2:]).upper()

        dutExOutHex = "0"* (8-len(dutExOutHex))+ dutExOutHex    # 0 padding to match fixed length of 8
        dutExFlagHex = "0"* (2-len(dutExFlagHex))+ dutExFlagHex # 0 padding to match fixed length of 8

        if(receive != binExOp):
            result = "FAIL"
        else:
            result = "PASS"
        print("Testcase No. : ",count," Tested..")
        count +=1
        fp1.write(operand_1 +"     " + operand_2 +"     "+ expected_out + "           " + exception_flag + "               "+ 
        result+"           "+dutExOutHex + "      "+dutExFlagHex +"\n") 

# ========================================= Round_Mode = towards -infinity (rmin)  ===================================================

run_testfloat("f32_add","min",1,"min_input.txt")

@cocotb.test()
def run_test_min(dut):
    count = 1
    rmode = BinaryValue(int("010",2),n_bits=3,bigEndian=False) 
    fp = open("min_input.txt","r")
    fp1 = open("min_result.txt","w")
    head = [next(fp) for x in range(N)]
    fp1.write("Operand_1    Operand_2    Expected_result    Expected_flag    Test_result    DUT_result    DUT_flag\n-----------------------------------------------------------------------------------------------------\n")
    for line in range(N):
        field  = head[line].split()
        operand_1 = field[0]
        operand_2 = field[1]
        expected_out = field[2]
        exception_flag = field[3]

        cocotb.fork(Clock(dut.CLK, 10,).start())
        clkedge = RisingEdge(dut.CLK)
        dut.RST_N <= 0
        dut.EN_send <= 0

        for i in range (5):
            yield clkedge
        
        dut.RST_N <= 1
        yield clkedge

        dut.EN_send <= 1

        for i in range (5):
            yield clkedge

        binOp1 = BinaryValue(int(operand_1,16),n_bits=32,bigEndian=False)
        binOp2 = BinaryValue(int(operand_2,16),n_bits=32,bigEndian=False)
        ExOp   = BinaryValue(int(expected_out,16),n_bits=32,bigEndian=False)
        ExFlag = BinaryValue(int(exception_flag,16),n_bits=5,bigEndian=False)
        binInput = BinaryValue((((binOp2 << 32) + binOp1)<<3)+rmode,n_bits=67,bigEndian=False)
        binExOp = BinaryValue(((ExOp << 5) + ExFlag)+validBit,n_bits=38,bigEndian=False)
                      
        dut.send_operands = binInput
        for i in range (50):
            yield clkedge
        
        receive = dut.receive.value
        
        dut.RST_N = 0
        yield clkedge
        dut.RST_N = 1
        yield clkedge

        temp0  = receive.binstr
        dutExFlag = BinaryValue(int(temp0[33:],2),n_bits=5,bigEndian=False)

        temp = BinaryValue(receive>>5,n_bits=33,bigEndian=False)
        dutExOut = temp.binstr
        dutExOut = BinaryValue(int(dutExOut[1:],2),n_bits=32,bigEndian=False)

        dutExOutHex = ((hex(dutExOut))[2:]).upper()
        dutExFlagHex = ((hex(dutExFlag))[2:]).upper()

        dutExOutHex = "0"* (8-len(dutExOutHex))+ dutExOutHex    # 0 padding to match fixed length of 8
        dutExFlagHex = "0"* (2-len(dutExFlagHex))+ dutExFlagHex # 0 padding to match fixed length of 8

        if(receive != binExOp):
            result = "FAIL"
        else:
            result = "PASS"
        print("Testcase No. : ",count," Tested..")
        count +=1
        fp1.write(operand_1 +"     " + operand_2 +"     "+ expected_out + "           " + exception_flag + "               "+ 
        result+"           "+dutExOutHex + "      "+dutExFlagHex +"\n") 

#========================================= Round_Mode = towards +infinity (rmax)  ===================================================

run_testfloat("f32_add","max",1,"max_input.txt")

@cocotb.test()
def run_test_max(dut):
    count = 1
    rmode = BinaryValue(int("011",2),n_bits=3,bigEndian=False) 
    fp = open("max_input.txt","r")
    fp1 = open("max_result.txt","w")
    head = [next(fp) for x in range(N)]
    fp1.write("Operand_1    Operand_2    Expected_result    Expected_flag    Test_result    DUT_result    DUT_flag\n-----------------------------------------------------------------------------------------------------\n")
    for line in range(N):
        field  = head[line].split()
        operand_1 = field[0]
        operand_2 = field[1]
        expected_out = field[2]
        exception_flag = field[3]

        cocotb.fork(Clock(dut.CLK, 10,).start())
        clkedge = RisingEdge(dut.CLK)
        dut.RST_N <= 0
        dut.EN_send <= 0

        for i in range (5):
            yield clkedge
        
        dut.RST_N <= 1
        yield clkedge

        dut.EN_send <= 1

        for i in range (5):
            yield clkedge

        binOp1 = BinaryValue(int(operand_1,16),n_bits=32,bigEndian=False)
        binOp2 = BinaryValue(int(operand_2,16),n_bits=32,bigEndian=False)
        ExOp   = BinaryValue(int(expected_out,16),n_bits=32,bigEndian=False)
        ExFlag = BinaryValue(int(exception_flag,16),n_bits=5,bigEndian=False)
        binInput = BinaryValue((((binOp2 << 32) + binOp1)<<3)+rmode,n_bits=67,bigEndian=False)
        binExOp = BinaryValue(((ExOp << 5) + ExFlag)+validBit,n_bits=38,bigEndian=False)
                      
        dut.send_operands = binInput
        for i in range (50):
            yield clkedge
        
        receive = dut.receive.value
        
        dut.RST_N = 0
        yield clkedge
        dut.RST_N = 1
        yield clkedge

        temp0  = receive.binstr
        dutExFlag = BinaryValue(int(temp0[33:],2),n_bits=5,bigEndian=False)

        temp = BinaryValue(receive>>5,n_bits=33,bigEndian=False)
        dutExOut = temp.binstr
        dutExOut = BinaryValue(int(dutExOut[1:],2),n_bits=32,bigEndian=False)

        dutExOutHex = ((hex(dutExOut))[2:]).upper()
        dutExFlagHex = ((hex(dutExFlag))[2:]).upper()

        dutExOutHex = "0"* (8-len(dutExOutHex))+ dutExOutHex    # 0 padding to match fixed length of 8
        dutExFlagHex = "0"* (2-len(dutExFlagHex))+ dutExFlagHex # 0 padding to match fixed length of 8

        if(receive != binExOp):
            result = "FAIL"
        else:
            result = "PASS"
        print("Testcase No. : ",count," Tested..")
        count +=1
        fp1.write(operand_1 +"     " + operand_2 +"     "+ expected_out + "           " + exception_flag + "               "+ 
        result+"           "+dutExOutHex + "      "+dutExFlagHex +"\n") 

#========================================= Round_Mode = towards away from zero (rnear_maxMag)  ===================================================

run_testfloat("f32_add","near_maxMag",1,"near_maxMag_input.txt")

@cocotb.test()
def run_test_near_maxMag(dut):
    count = 1
    rmode = BinaryValue(int("100",2),n_bits=3,bigEndian=False) 
    fp = open("near_maxMag_input.txt","r")
    fp1 = open("near_maxMag_result.txt","w")
    head = [next(fp) for x in range(N)]
    fp1.write("Operand_1    Operand_2    Expected_result    Expected_flag    Test_result    DUT_result    DUT_flag\n-----------------------------------------------------------------------------------------------------\n")
    for line in range(N):
        field  = head[line].split()
        operand_1 = field[0]
        operand_2 = field[1]
        expected_out = field[2]
        exception_flag = field[3]

        cocotb.fork(Clock(dut.CLK, 10,).start())
        clkedge = RisingEdge(dut.CLK)
        dut.RST_N <= 0
        dut.EN_send <= 0

        for i in range (5):
            yield clkedge
        
        dut.RST_N <= 1
        yield clkedge

        dut.EN_send <= 1

        for i in range (5):
            yield clkedge

        binOp1 = BinaryValue(int(operand_1,16),n_bits=32,bigEndian=False)
        binOp2 = BinaryValue(int(operand_2,16),n_bits=32,bigEndian=False)
        ExOp   = BinaryValue(int(expected_out,16),n_bits=32,bigEndian=False)
        ExFlag = BinaryValue(int(exception_flag,16),n_bits=5,bigEndian=False)
        binInput = BinaryValue((((binOp2 << 32) + binOp1)<<3)+rmode,n_bits=67,bigEndian=False)
        binExOp = BinaryValue(((ExOp << 5) + ExFlag)+validBit,n_bits=38,bigEndian=False)
                      
        dut.send_operands = binInput
        for i in range (50):
            yield clkedge
        
        receive = dut.receive.value
        
        dut.RST_N = 0
        yield clkedge
        dut.RST_N = 1
        yield clkedge

        temp0  = receive.binstr
        dutExFlag = BinaryValue(int(temp0[33:],2),n_bits=5,bigEndian=False)

        temp = BinaryValue(receive>>5,n_bits=33,bigEndian=False)
        dutExOut = temp.binstr
        dutExOut = BinaryValue(int(dutExOut[1:],2),n_bits=32,bigEndian=False)

        dutExOutHex = ((hex(dutExOut))[2:]).upper()
        dutExFlagHex = ((hex(dutExFlag))[2:]).upper()

        dutExOutHex = "0"* (8-len(dutExOutHex))+ dutExOutHex    # 0 padding to match fixed length of 8
        dutExFlagHex = "0"* (2-len(dutExFlagHex))+ dutExFlagHex # 0 padding to match fixed length of 8

        if(receive != binExOp):
            result = "FAIL"
        else:
            result = "PASS"
        print("Testcase No. : ",count," Tested..")
        count +=1
        fp1.write(operand_1 +"     " + operand_2 +"     "+ expected_out + "           " + exception_flag + "               "+ 
        result+"           "+dutExOutHex + "      "+dutExFlagHex +"\n") 

#===========================================================================================================================================