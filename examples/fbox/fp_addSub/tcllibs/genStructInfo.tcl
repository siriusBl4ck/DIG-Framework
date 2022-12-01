#! /usr/bin/env bluetcl

source tcllibs/types.tcl

package require types

namespace import ::Bluetcl::*
namespace import ::utils::*
namespace import types::*

flags set -verilog

set packlist [lrange $argv 0 end]

foreach packName $packlist {
  bpackage load $packName
  set types [getNonPolyType $packName]
  
  foreach t $types {
      set ft [type full $t]
      set key [lindex $ft 0]
      #if { $key == "Struct" || $key == "Alias" || $key == "" } {
      puts "--$t"
      #showTypeSize $t
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
