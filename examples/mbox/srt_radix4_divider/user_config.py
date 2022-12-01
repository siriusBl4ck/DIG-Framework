# set this path to where you have cloned c-class
cclass_path='../mbox/'

# provide absolute path of the alias signal file
alias_file='./alias_signal.yaml'

# provide the absolute path of the enables signal file
enables='./enables.yaml'
# set this path the lib directory of your bsc installation
bsclib='mnt/5a853c24-31e3-4d80-9826-512f6bd995e7/saurav/siriusBl4ck/EE_Core/BlueSpec/bsc/inst/bin/'

# provide the absolute path of the patterns yaml file
pattern_decompress_yaml='./mycheckers/pattern_decompress.yaml'


# these are cocotb environment settings. Refer to
# https://docs.cocotb.org/en/stable/building.html for details on what can be set
# here
myenv = {
#        "LIBPYTHON_LOC": "/usr/lib/x86_64-linux-gnu/libpython3.8.so", 
        "COCOTB_REDUCED_LOG_FMT": "TRUE",
#        "COCOTB_LOG_LEVEL": "ERROR"
        }

# there are parameters of the mkTbSoc testbench. Mostly should never change.
#parameters= {"rtldumpfile": '\"rtl.dump\"', 
#             "applogfile": '\"app.log\"', 
#             "inputcodemem": '\"code.mem\"'
#             }

# path to the testlist
testlist_path = './tests/test_list.yaml'

