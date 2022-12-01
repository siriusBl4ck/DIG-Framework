#! /usr/bin/env bluetcl

source ./tcllibs/types.tcl

package require types

namespace import ::Bluetcl::*
namespace import ::utils::*
namespace import types::*

#puts "$argv"
set builddir [lindex $argv 0]

#flags set -bdir $builddir
flags set -verilog

set modlist [lrange $argv 1 end]

#puts "$modlist"

foreach mod $modlist {
  module load $mod
  set m [module methods $mod]
  puts "$m"
}

#set packlist {int_multiplier}
#set packlist {vector_test}
 
#foreach packName $packlist {
  #puts "$packName"
#  bpackage load $packName
#  set types [getNonPolyType $packName]
  #puts "$types"
  
#  foreach t $types {
#    set ft [type full $t]
#    set key [lindex $ft 0]
#    puts "$ft"
    #puts "$key"
#  }
#}
 # }
#      if { $key == "Struct" || $key == "Alias" } {
        # puts "--$t"
        # showTypeSize $t
        # puts "$$$$"
#      }
      #if { $key == "Enum"} {
      #  puts "##$t"
      #  puts $ft
      #  puts [getMembers $t]
      #  showTypeSize $t
      #  puts "===="
      #}
  # }
  #}
