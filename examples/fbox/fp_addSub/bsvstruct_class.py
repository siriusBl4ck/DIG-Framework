
# Generated on 2022-11-30 05:32:34.278035
from dataclasses import dataclass
@dataclass(init=False)
class Disorder:
    Disorder: int = 0


    def set(self, val):

        self.Disorder = (val.integer >> 0) & 0x7
        return

    def __bin__(self) -> str:
        val = ''
        val += '{0:03b}'.format(self.Disorder & 0x7)
        return val

    def get(self) -> int:
        return int(self.__bin__(),base=2)

    def size(self) -> int:
        return 3



@dataclass(init=False)
class Double:
    sign: int = 0
    exp: int = 0
    sfd: int = 0


    def set(self, val):

        self.sign = (val.integer >> 63) & 0x1
        self.exp = (val.integer >> 52) & 0x7ff
        self.sfd = (val.integer >> 0) & 0xfffffffffffff
        return

    def __bin__(self) -> str:
        val = ''
        val += '{0:01b}'.format(self.sign & 0x1)
        val += '{0:011b}'.format(self.exp & 0x7ff)
        val += '{0:052b}'.format(self.sfd & 0xfffffffffffff)
        return val

    def get(self) -> int:
        return int(self.__bin__(),base=2)

    def size(self) -> int:
        return 64



@dataclass(init=False)
class DoubleExtended:
    sign: int = 0
    exp: int = 0
    sfd: int = 0


    def set(self, val):

        self.sign = (val.integer >> 79) & 0x1
        self.exp = (val.integer >> 64) & 0x7fff
        self.sfd = (val.integer >> 0) & 0xffffffffffffffff
        return

    def __bin__(self) -> str:
        val = ''
        val += '{0:01b}'.format(self.sign & 0x1)
        val += '{0:015b}'.format(self.exp & 0x7fff)
        val += '{0:064b}'.format(self.sfd & 0xffffffffffffffff)
        return val

    def get(self) -> int:
        return int(self.__bin__(),base=2)

    def size(self) -> int:
        return 80



@dataclass(init=False)
class Exception:
    invalid_op: int = 0
    divide_0: int = 0
    overflow: int = 0
    underflow: int = 0
    inexact: int = 0


    def set(self, val):

        self.invalid_op = (val.integer >> 4) & 0x1
        self.divide_0 = (val.integer >> 3) & 0x1
        self.overflow = (val.integer >> 2) & 0x1
        self.underflow = (val.integer >> 1) & 0x1
        self.inexact = (val.integer >> 0) & 0x1
        return

    def __bin__(self) -> str:
        val = ''
        val += '{0:01b}'.format(self.invalid_op & 0x1)
        val += '{0:01b}'.format(self.divide_0 & 0x1)
        val += '{0:01b}'.format(self.overflow & 0x1)
        val += '{0:01b}'.format(self.underflow & 0x1)
        val += '{0:01b}'.format(self.inexact & 0x1)
        return val

    def get(self) -> int:
        return int(self.__bin__(),base=2)

    def size(self) -> int:
        return 5



@dataclass(init=False)
class Float:
    sign: int = 0
    exp: int = 0
    sfd: int = 0


    def set(self, val):

        self.sign = (val >> 31) & 0x1
        self.exp = (val >> 23) & 0xff
        self.sfd = (val >> 0) & 0x7fffff
        return

    def __bin__(self) -> str:
        val = ''
        val += '{0:01b}'.format(self.sign & 0x1)
        val += '{0:08b}'.format(self.exp & 0xff)
        val += '{0:023b}'.format(self.sfd & 0x7fffff)
        return val

    def get(self) -> int:
        return int(self.__bin__(),base=2)

    def size(self) -> int:
        return 32



@dataclass(init=False)
class Half:
    sign: int = 0
    exp: int = 0
    sfd: int = 0


    def set(self, val):

        self.sign = (val.integer >> 15) & 0x1
        self.exp = (val.integer >> 10) & 0x1f
        self.sfd = (val.integer >> 0) & 0x3ff
        return

    def __bin__(self) -> str:
        val = ''
        val += '{0:01b}'.format(self.sign & 0x1)
        val += '{0:05b}'.format(self.exp & 0x1f)
        val += '{0:010b}'.format(self.sfd & 0x3ff)
        return val

    def get(self) -> int:
        return int(self.__bin__(),base=2)

    def size(self) -> int:
        return 16



@dataclass(init=False)
class RoundMode:
    RoundMode: int = 0


    def set(self, val):

        self.RoundMode = (val.integer >> 0) & 0x7
        return

    def __bin__(self) -> str:
        val = ''
        val += '{0:03b}'.format(self.RoundMode & 0x7)
        return val

    def get(self) -> int:
        return int(self.__bin__(),base=2)

    def size(self) -> int:
        return 3



@dataclass(init=False)
class SingleExtended:
    sign: int = 0
    exp: int = 0
    sfd: int = 0


    def set(self, val):

        self.sign = (val.integer >> 43) & 0x1
        self.exp = (val.integer >> 32) & 0x7ff
        self.sfd = (val.integer >> 0) & 0xffffffff
        return

    def __bin__(self) -> str:
        val = ''
        val += '{0:01b}'.format(self.sign & 0x1)
        val += '{0:011b}'.format(self.exp & 0x7ff)
        val += '{0:032b}'.format(self.sfd & 0xffffffff)
        return val

    def get(self) -> int:
        return int(self.__bin__(),base=2)

    def size(self) -> int:
        return 44


