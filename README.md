# Design Interface Generation for Verification

![alt text](https://github.com/siriusBl4ck/DIG-Framework/blob/main/DIG_diag.png)

## How to run
```
python3 verilogify.py <verilog_dir> <build_dir> <module_name> <ba_dir> <dataclass_dir>
```
Above command takes the verilog file located in ```verilog_dir```, .ba/.bo files in ```build_dir``` and ```ba_dir```, corresponding to ```module_name``` and creates a file called ```module_name_dataclasses.py``` with the generated dataclasses.

Now, we can create a testbench for the design to be tested, say mk\_tb.py

```
python3 mk_tb.py
```
runs the cocotb simulation

## Objective

One of the major advantages of using Bluespec SystemVerilog for digital design is its rigorous type driven approach. This eliminates the need for handling every signal at the bit level, unlike verilog. It also eliminates the need to worry about handshaking signals. These are derived when the bluespec is compiled into verilog.

As far as verification is concerned, the verification engineer deals with the generated verilog. Elaboration errors from bluespec to verilog are identified this way. However, this also means that verification engineers cannot take advantage of the type abstractions which bluespec offers. A verification engineer has to painstakingly look at how the bluespec methods map to the handshaking signals.

We present in this work, a python package, which integrates with cocotb which allows the verification engineer to take advantage of type abstraction in testing the verilog DUT.

### References
https://gitlab.com/shaktiproject/core-py-verif
https://www.cocotb.org/
