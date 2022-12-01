#! /usr/bin/env bluetcl

source tcllibs/types.tcl

package require types

namespace import ::Bluetcl::*
namespace import ::utils::*
namespace import types::*

if { [info exists env(BSC_BUILDDIR)] } {
  set builddir $env(BSC_BUILDDIR)
} else {
  set builddir "build/hw/intermediate"
}

flags set -bdir $builddir
flags set -verilog

set packlist {fpu_common}

foreach packName $packlist {
  bpackage load $packName
  set types [getNonPolyType $packName]
  
  foreach t $types {
      set ft [type full $t]
      set key [lindex $ft 0]
      #if { $key == "Struct" || $key == "Alias" || $key == "" } {
      puts "--$t"
      showTypeSize $t
      puts "$$$$"
	  #}
      #if { $key == "Enum"} {
      #  puts "##$t"
      #  puts $ft
      #  puts [getMembers $t]
      #  showTypeSize $t
      #  puts "===="
      #}
  }
}
