#! /usr/bin/env bluetcl

source tcllibs/types.tcl

package require types

namespace import ::Bluetcl::*
namespace import ::utils::*
namespace import types::*

flags set -verilog
set mod [lindex $argv 0]
set fp [open "./typelist.txt" r]
set file_data [read $fp]
close $fp

#puts "$file_data"

set typelist [regexp -inline -all -- {\S+} $file_data]

#puts "$typelist"
 
module load $mod
  
foreach t $typelist {
  set ft [type full $t]
  set key [lindex $ft 0]
  puts "$ft"
  #puts "$key"
}

