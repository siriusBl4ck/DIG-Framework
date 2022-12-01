import math
from cocotb.binary import BinaryValue
# undefined1 = str(1111111111111111111111111111111111111111111111111111111111111111)
# undefined2 = str(0000000000000000000000000000000000000000000000000000000000000000)
                 
'''
NOTE: RISC TYPES
typedef enum {
   ADD_1,SUB_2,SLL_3,SLT_4,SLTU,XOR, 		
   SRL,SRA,OR,AND,MUL,MULH,
   MULHSU,MULHU,DIV_14,DIVU_15,REM_16,REMU_17,LUI,AUIPC,
	 NOP
   } ALU_func deriving(Eq,Bits,FShow);

'''
# 18446744073709551599
undefined =  0x1ffffffffffffffff
#----------------------------------------------------------------------------------------------------

#----------------------------------------------------------------------------------------------------

def unsigned_div(a,b):  #15
    if(b==0):
        quotient = undefined
    else:
        quotient = math.floor(a/b)
        quotient = quotient | 2**64
    # print(quotient)
    # print(BinaryValue(value=quotient,n_bits=64,bigEndian=False))
    if(quotient==undefined):
        #return(BinaryValue(value=quotient,bits=65,bigEndian=False,binaryRepresentation=2))
        return(BinaryValue(value=quotient,n_bits=65,bigEndian=False))
    else:
        return(BinaryValue(value=quotient,n_bits=65,bigEndian=False))
#----------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------

def divider_model(a,b,opcode,funct3):
    
    if(opcode == 12 and funct3 == 5):
        return(unsigned_div(a,b))
    elif(opcode==17):
        return unsigned_rem(a,b)
    elif(opcode==14):
        return signed_div(a,b)
    elif(opcode==16):
        return signed_rem(a,b)
#**********************************************
    if(opcode==19):
        return(unsigned_div(a,b))
    elif(opcode==21):
        return unsigned_rem(a,b)
    elif(opcode==18):
    	# return 0
        return signed_div_32_bit(a,b)
    elif(opcode==20):
        return signed_rem(a,b)
    else:
        print("divName Error..")
        return -87        
        # print(BinaryValue(value=remainder,n_bits=64,bigEndian=False))
        # if(remainder >= 0):
        #     return (BinaryValue(value=remainder,n_bits=64,bigEndian=False))
        # else:
        #     return(BinaryValue(value=remainder,bits=64,bigEndian=False,binaryRepresentation=1))


# print(divider_model(-21,-5,15))
