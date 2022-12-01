import subprocess
import shlex
from enum import Enum
from datetime import datetime
from random import randint

def sys_command(command):
    x = subprocess.Popen(shlex.split(command),
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         )
    try:
        out, err = x.communicate(timeout=5)
    except TimeoutExpired:
        x.kill()
        out, err = x.communicate()

    out = out.rstrip()
    err = err.rstrip()
    return out.decode("ascii")

def run_testfloat(function, round_mode, seed, timeout_value, test_file=''):

    pk = sys_command('which pk')
    testfloat_gen = sys_command('which testfloat_gen')
    if (seed == 0):
        seed = randint(1, 65000)
    #command = 'spike {0} {1} -r{2} -seed {3} -level 2 {4}'.format(pk, testfloat_gen, 
    #                                                 round_mode, seed, function)
    if test_file:
        fp = open(test_file, 'r')
        gen = fp.read()
        fp.close()
    else:
#        command = 'qemu-riscv64 {0} {1}'.format( testfloat_gen, function)
        command = 'qemu-riscv64 {0} -r{1} -seed {2} -level 2 {3}'.format( testfloat_gen, 
                                                         round_mode, seed, function)
        print(command)
        proc = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        gen = ''
        try:
            out, err = proc.communicate(timeout=timeout_value)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
            gen = out.decode('ascii')
            stampnow = datetime.now()
            filename = 'tf_{0}_{1}_{2}.test'.format(function, seed, stampnow.strftime("%Y%m%d%H%M%S%f"))
            fp = open(filename, 'w')
            fp.write(gen)
            fp.close()
    
    tests = gen.splitlines()
    #print(tests)

    input_list = []
    expected_list = []
    for test in tests:
        inp = ''
        if test != 'bbl loader':
            tlist = test.split(' ')
            if function == 'f32_add':
               inp = bin(int((tlist[0]+tlist[1]), 16))[2:]
               flag = bin(int((tlist[3]), 16))[2:]  #flag bits from testfloat 8 bit
               if(round_mode=='near_even') :
                   rmode='000'

               if(round_mode=='near_maxMag') :
                   rmode='100'

               if(round_mode=='minMag') :
                   rmode='001'

               if(round_mode=='min') :
                   rmode='010'

               if(round_mode=='max') :
                   rmode='011'

               inp=int(inp+rmode,2)
               flag=flag.zfill(8)
               flag=flag[3:] 
               exp = bin(int((tlist[2]), 16))[2:]
               exp=exp.zfill(32) 
               exp=int('1'+exp+flag,2)
               input_list.append(inp)
               expected_list.append(exp)


            if function == 'f32_sub':
                flag = bin(int((tlist[3]), 16))[2:]  #flag bits from testfloat 8 bit
                inp1 = bin(int((tlist[0]), 16))[2:]  #inp1  bit from testfloat
                inp2 = bin(int((tlist[1]), 16))[2:]  #inp2  bit from testfloat
                inp1=inp1.zfill(32)
                inp2=inp2.zfill(32)
                inp_t=inp2.zfill(32)
                inp2_A4=inp2[:1]
                if inp2_A4=='1':
                    inp_msb='0' 
                if inp2_A4=='0': 
                    inp_msb='1' 
                inp_t = inp_t[1:]  #inp2  bit from testfloat


                if(round_mode=='near_even') :
                    rmode='000'

                if(round_mode=='near_maxMag') :
                    rmode='100'

                if(round_mode=='minMag') :
                    rmode='001'

                if(round_mode=='min') :
                    rmode='010'

                if(round_mode=='max') :
                    rmode='011'

                inp = int((inp1+inp_msb+inp_t+rmode), 2)
                input_list.append(inp)
                flag=flag.zfill(8)
                flag=flag[3:] 
                exp = bin(int((tlist[2]), 16))[2:]
                exp=exp.zfill(32) 
                exp=int('1'+exp+flag,2)
                expected_list.append(exp)


    
    return input_list, expected_list

if __name__ == "__main__":
    run_testfloat('f32_add', 'near_even', 1,1)
