# Design Interface Generation for Verification

![alt text](https://github.com/siriusBl4ck/DIG-Framework/blob/main/DIG_diag.png)

## Objective

One of the major advantages of using Bluespec SystemVerilog for digital design is its rigorous type driven approach. This eliminates the need for handling every signal at the bit level, unlike verilog. It also eliminates the need to worry about handshaking signals. These are derived when the bluespec is compiled into verilog.

As far as verification is concerned, the verification engineer deals with the generated verilog. Elaboration errors from bluespec to verilog are identified this way. However, this also means that verification engineers cannot take advantage of the type abstractions which bluespec offers. A verification engineer has to painstakingly look at how the bluespec methods map to the handshaking signals.

We present in this work, a python package, which integrates with cocotb which allows the verification engineer to take advantage of type abstraction in testing the verilog DUT.
