import pathlib
import subprocess
import operator
import shlex
import os
import re
import textwrap
import datetime
from string import Template

import ruamel
from ruamel.yaml import YAML
import logging

log = logging.getLogger('test-top')
from user_config import *

def get_signals(module, category, alias=None):
    mymap = {}
    alias_map = load_yaml(alias_file)
    if module not in alias_map:
        raise SystemError("No module "+str(module)+" in alias_map")
    if category not in alias_map[module]:
        raise SystemError("No Category "+str(category)+" in " + \
                str(module)+" alias_map")
    if alias is None:
        for s in alias_map[module][category]:
            mymap[s] = alias_map[module][category][s]
    else:
        if not isinstance(alias, list):
            raise SystemError('Alias argument must be a list')
        for a in alias:
            mymap[a] = alias_map[module][category][a]
    return mymap
def load_yaml(foo, no_anchors=False):

    if no_anchors:
        yaml = YAML(typ="safe")
    else:
        yaml = YAML(typ="rt")
    yaml.default_flow_style = False
    yaml.allow_unicode = True
    yaml.compact(seq_seq=False, seq_map=False)
    yaml.indent = 4
    yaml.block_seq_indent = 2
    try:
        with open(foo, "r") as file:
            return yaml.load(file)
    except ruamel.yaml.constructor.DuplicateKeyError as msg:
        error = "\n".join(str(msg).split("\n")[2:-7])
        log.error(error)
        raise SystemExit

class Command():
    """
    Class for command build which is supported
    by :py:mod:`suprocess` module. Supports automatic
    conversion of :py:class:`pathlib.Path` instances to
    valid format for :py:mod:`subprocess` functions.
    """

    def __init__(self, *args, pathstyle='auto', ensure_absolute_paths=False):
        """Constructor.

        :param pathstyle: Determine the path style when adding instance of
            :py:class:`pathlib.Path`. Path style determines the slash type
            which separates the path components. If pathstyle is `auto`, then
            on Windows backslashes are used and on Linux forward slashes are used.
            When backslashes should be prevented on all systems, the pathstyle
            should be `posix`. No other values are allowed.

        :param ensure_absolute_paths: If true, then any passed path will be
            converted to absolute path.

        :param args: Initial command.

        :type pathstyle: str

        :type ensure_absolute_paths: bool
        """
        self.ensure_absolute_paths = ensure_absolute_paths
        self.pathstyle = pathstyle
        self.args = []

        for arg in args:
            self.append(arg)

    def append(self, arg):
        """Add new argument to command.

        :param arg: Argument to be added. It may be list, tuple,
            :py:class:`Command` instance or any instance which
            supports :py:func:`str`.
        """
        to_add = []
        if type(arg) is list:
            to_add = arg
        elif type(arg) is tuple:
            to_add = list(arg)
        elif isinstance(arg, type(self)):
            to_add = arg.args
        elif isinstance(arg, str) and not self._is_shell_command():
            to_add = shlex.split(arg)
        else:
            # any object which will be converted into str.
            to_add.append(arg)

        # Convert all arguments to its string representation.
        # pathlib.Path instances
        to_add = [
            self._path2str(el) if isinstance(el, pathlib.Path) else str(el)
            for el in to_add
        ]
        self.args.extend(to_add)

    def clear(self):
        """Clear arguments."""
        self.args = []

    def run(self, **kwargs):
        """Execute the current command.

        Uses :py:class:`subprocess.Popen` to execute the command.

        :return: The return code of the process     .
        :raise subprocess.CalledProcessError: If `check` is set
                to true in `kwargs` and the process returns
                non-zero value.
        """
        kwargs.setdefault('shell', self._is_shell_command())
        cwd = self._path2str(kwargs.get(
            'cwd')) if not kwargs.get('cwd') is None else self._path2str(
                os.getcwd())
        kwargs.update({'cwd': cwd})
        log.debug(cwd)
        # When running as shell command, subprocess expects
        # The arguments to be string.
        log.debug(str(self))
        cmd = str(self) if kwargs['shell'] else self
        x = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             **kwargs)
        out, err = x.communicate()
        out = out.rstrip()
        err = err.rstrip()
        if x.returncode != 0:
            if out:
                log.error(out.decode("ascii"))
            if err:
                log.error(err.decode("ascii"))
        else:
            if out:
                log.warning(out.decode("ascii"))
            if err:
                log.warning(err.decode("ascii"))
        return x.returncode

    def _is_shell_command(self):
        """
        Return true if current command is supposed to be executed
        as shell script otherwise false.
        """
        return any('|' in arg for arg in self.args)

    def _path2str(self, path):
        """Convert :py:class:`pathlib.Path` to string.

        The final form of the string is determined by the
        configuration of `Command` instance.

        :param path: Path-like object which will be converted
                     into string.
        :return: String representation of `path`
        """
        path = pathlib.Path(path)
        if self.ensure_absolute_paths and not path.is_absolute():
            path = path.resolve()

        if self.pathstyle == 'posix':
            return path.as_posix()
        elif self.pathstyle == 'auto':
            return str(path)
        else:
            raise ValueError(f"Invalid pathstyle {self.pathstyle}")

    def __add__(self, other):
        cmd = Command(self,
                      pathstyle=self.pathstyle,
                      ensure_absolute_paths=self.ensure_absolute_paths)
        cmd += other
        return cmd

    def __iadd__(self, other):
        self.append(other)
        return self

    def __iter__(self):
        """
        Support iteration so functions from :py:mod:`subprocess` module
        support `Command` instance.
        """
        return iter(self.args)

    def __repr__(self):
        return f'<{self.__class__.__name__} args={self.args}>'

    def __str__(self):
        return ' '.join(self.args)


class shellCommand(Command):
    """
        Sub Class of the command class which always executes commands as shell commands.
    """

    def __init__(self, *args, pathstyle='auto', ensure_absolute_paths=False):
        """
        :param pathstyle: Determine the path style when adding instance of
            :py:class:`pathlib.Path`. Path style determines the slash type
            which separates the path components. If pathstyle is `auto`, then
            on Windows backslashes are used and on Linux forward slashes are used.
            When backslashes should be prevented on all systems, the pathstyle
            should be `posix`. No other values are allowed.

        :param ensure_absolute_paths: If true, then any passed path will be
            converted to absolute path.

        :param args: Initial command.

        :type pathstyle: str

        :type ensure_absolute_paths: bool

        """
        return super().__init__(*args,
                                pathstyle=pathstyle,
                                ensure_absolute_paths=ensure_absolute_paths)

    def _is_shell_command(self):
        return True

def create_dataclass_frm_bsv(structfile_path):

    structfile = open(structfile_path , 'r')
    structinfo = structfile.read()
    structfile.close()

    timestamp = datetime.datetime.now()

    bsvstruct_file = open('bsvstruct_class.py' , 'w')

    replace_chars = ['.','[',']']

    bsvstruct_file.write('''
# Generated on {0}
from dataclasses import dataclass'''.format(timestamp))

    temp_setstr = '''
self.{0} = (val.integer >> {1}) & {2}'''

    temp_getstr = Template('''
val += '{0:0${width}b}'.format(self.$name & $mask)''')

    temp_dataclass = '''
@dataclass(init=False)
class {0}:
{1}

    def set(self, val):
{2}
        return

    def __bin__(self) -> str:
{3}

    def get(self) -> int:
        return int(self.__bin__(),base=2)

    def size(self) -> int:
        return {4}

'''

    # regex pattern to extract name of each subfield
    name_pattern = re.compile ('^\.(?P<name>.*?)\s+.*')

    # regex pattern to extract the size and position of each width
    size_pattern = re.compile ('.*\s+(?P<size>\d+?)\s+\[\s(?P<msb>.*?\d+?):(?P<lsb>.*?\d+?)\s+\]')

    # split in the input file from bluetcl in multiple structs
    allstructs = re.findall('--(.*?)\$\$\$\$',structinfo,re.M|re.S)

    # iterate over each struct and convert them to python dataclass
    for struct in allstructs:
        lines = struct.split('\n')
        name = lines[0]
        lines = lines[1:-1]
        subfields = ''
        setstr = ''
        getstr = "val = ''"
        msize = 0
        for i in range(len(lines)):
            subfield = name_pattern.search(lines[i]).group('name')
            for elem in replace_chars:
                subfield = subfield.replace(elem, '_')
            sz_breakdown = size_pattern.search(lines[i])
            width = int(sz_breakdown.group('size'))
            lsb = int(sz_breakdown.group('lsb'))

            subfield = subfield if subfield else name
            msize += width
            subfields += subfield + ': int = 0\n'
            setstr += temp_setstr.format(subfield, lsb, hex((1 << width)-1))
            getstr += temp_getstr.safe_substitute(width=str(width),name=str(subfield),
                                                                        mask=hex((1 << width)-1))
        getstr += "\nreturn val"
        subfields = textwrap.indent(subfields, '    ')
        setstr = textwrap.indent(setstr, '        ')
        getstr = textwrap.indent(getstr, '        ')
        bsvstruct_file.write(temp_dataclass.format(name, subfields, setstr,getstr,msize)+'\n')

    bsvstruct_file.close()

def fill_tup(tup):
    # helper function to return a binary number of fixed width
    return bin(tup[2])[2:].zfill(tup[1] - tup[0] + 1)


def fill_range(ind_ranges):
    # Function to frame the 32 bit opcode from the range details
    ind_ranges.sort(key=lambda x: x[0], reverse=True)
    op = '\''
    c=31
    for i in ind_ranges:
        c=c-i[1]
        op = op+ (('[01]{{{0}}}'.format(c)) if c!=0 else '') + fill_tup(i)
        c=i[0]-1
    return op+'\''

def extract_patterns_from_riscv_opcodes():
    # read the file from riscv-opcodes
    filenames=['opcodes-rv32i','opcodes-rv32a','opcodes-rv32d','opcodes-rv32f','opcodes-rv32m','opcodes-rv64a','opcodes-rv64d','opcodes-rv64f','opcodes-rv64i','opcodes-rv64m','opcodes-system','opcodes-rv32d-zfh','opcodes-rv32q','opcodes-rv32q-zfh','opcodes-rv32zfh','opcodes-rv64q','opcodes-rv64zfh', 'opcodes-pseudo']
    # open the file to write the instructions
    f = open('mycheckers/decoder_inst_defines.py', 'w')
    f.write("from enum import Enum, IntEnum, unique, auto \n\n")
    f.write("class rv64(Enum):\n")
    for fn in filenames :
      _file = open('./riscv-opcodes/'+fn, 'r')
      lines = _file.readlines()
      _file.close()

    
      for line in lines:
        if line[0] == '#' or line[0] == '\n':
            # ignore unnecessary lines
            pass
        else:
            temp = line.split()
            inst = temp.pop(0)  # take out the instruction alone
            if '@' in inst:
               inst=inst.replace('@','')
            if '.' in inst:
               inst=inst.replace('.','_')
            temp.sort()
            ranges = []
            for i in temp:
                # extract the constant data fields alone
                if i[0].isnumeric():
                    [end, beg] = i.split('..')
                    [beg, val] = beg.split('=')
                    if 'ignore' in val:
                       val='0'
                    beg, end, val = int(beg), int(end), (int(val, 16) if '0x' in val else int(val, 10))
                    # append the details to a list of tuples.
                    ranges.append((beg, end, val))
                else:
                    break
            f.write("      {0:<8}={1}\n".format(inst.upper(), fill_range(ranges)))
    f.close()    
