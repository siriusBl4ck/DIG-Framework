#! /usr/bin/env bluetcl

source tcllibs/types.tcl

package require types

namespace import ::Bluetcl::*
namespace import ::utils::*
namespace import types::*

set packlist [lindex $argv 0 end]
 
foreach packName $packlist {
  #puts "$packName"
  bpackage load $packName
  set types [getNonPolyType $packName]
  #puts "$types"
  
  foreach t $types {
    set ft [type full $t]
    set key [lindex $ft 0]
    puts "$ft"
    #puts "$key"
  }
}
