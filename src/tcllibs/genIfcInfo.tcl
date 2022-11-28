#! /usr/bin/env bluetcl

source tcllibs/types.tcl

package require types
package require Bluetcl
namespace import ::Bluetcl::*
namespace import ::utils::*
namespace import types::*


set builddir ".."

flags set -bdir $builddir
flags set -verilog

set module_list {mk_test10}

foreach module $module_list {
	module load $module
}
