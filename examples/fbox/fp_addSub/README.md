# Setup :
```
# verilog file generation..
 $ make generate_verilog TOP_MODULE=mk_fpu_add_sub_sp_instance TOP_FILE=fpu_add_sub.bsv VERILOGDIR=mk_fpu_add_sub_sp_instance TOP_DIR=./

# move mk_fpu_add_sub_sp_instance.v --> ../..fpuAddSub/hdl/
$ cd ../test
$ make SIM=verilator

```
# Dependencies :

**CoCoTb Verilator**
```
# Python dependency setup:

$ sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev python-openssl git

[1] curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
[2] Add the following at the end of ~/.bashrc
    export PATH="/home/<username>/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
[3] 
$ CONFIGURE_OPTS=--enable-shared pyenv install 3.6.10
$ pyenv virtualenv 3.6.10 py36

Activate env
$ pyenv activate py36

CoCoTb
$ git clone https://github.com/cocotb/cocotb.git
$ pip install -e ./cocotb

Verilator
$ git clone https://git.veripool.org/git/verilator.git 
$ git checkout stable
$ sudo apt-get install --no-install-recommends -y git make autoconf g++ flex bison libfl2 libfl-dev  # Ubuntu only (ignore if gives error)

  # unset VERILATOR_ROOT  # For bash
  $ autoconf        # Create ./configure script
  $ ./configure
  $ make
  $ make install
```
**RiscV tools**
```
$ git clone --recursive https://github.com/riscv/riscv-gnu-toolchain.git 
$ git checkout 9ef0948
$ cd riscv-gnu-toolchain
 
$ mkdir -p build
$ export RISCV=$PWD/build
$ cd build
$ ../configure --prefix=$RISCV
$ make 

# Once done.. 
$ export PATH=<build path>/bin:$PATH
$ export LD_LIBRARY_PATH=<build_path>/lib/:$LD_LIBRARY_PATH
```
**QEMU**
```
$ sudo apt-get install git libglib2.0-dev libfdt-dev libpixman-1-dev zlib1g-dev
$ sudo apt-get install git-email
$ sudo apt-get install libaio-dev libbluetooth-dev libbrlapi-dev libbz2-dev
$ sudo apt-get install libcap-dev libcap-ng-dev libcurl4-gnutls-dev libgtk-3-dev
$ sudo apt-get install libibverbs-dev libjpeg8-dev libncurses5-dev libnuma-dev
$ sudo apt-get install librbd-dev librdmacm-dev
$ sudo apt-get install libsasl2-dev libsdl1.2-dev libseccomp-dev libsnappy-dev libssh2-1-dev
$ sudo apt-get install libvde-dev libvdeplug-dev libvte-2.90-dev libxen-dev liblzo2-dev
$ sudo apt-get install valgrind xfslibs-dev 
$ sudo apt-get install libnfs-dev libiscsi-dev

   - git clone git://git.qemu-project.org/qemu.git
   - mkdir build
   - cd build
   - ../configure --target-list=riscv64-linux-user --enable-debug
   - make 
   - add source path to the PATH in .bashrc
```
**Bluespec Compiler**
```
$ git clone https://github.com/B-Lang-org/bsc.git
$ apt-get install --no-install-recommends -y ghc libghc-regex-compat-dev libghc-syb-dev \
    libghc-old-time-dev libghc-split-dev tcl-dev autoconf gperf flex bison
$ mkdir -p build
$ make -j ${JOBS} all PREFIX=$PWD/build
$ make install

```

