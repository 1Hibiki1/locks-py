from typing import List
from .stack import Stack
from ...types import LObject, Nil

class Frame:
    def __init__(self, n: str = None):
        self.name = n
        self._operand_stack = Stack()
        self._local_vars: List[LObject] = [Nil()]*256
        self._code: List[int] = []
        self._ret_address: int = 0

    
    def pushOpStack(self, e: LObject) -> None:
        self._operand_stack.push(e)

    def popOpStack(self) -> LObject:
        return self._operand_stack.pop()

    def setReturnAddress(self, a: int):
        self._ret_address = a

    def getReturnAddress(self):
        return self._ret_address 

    def getLocalVarAtIndex(self, i: int) -> LObject:
        return self._local_vars[i]

    def setLocalVarAtIndex(self, i: int, e: LObject):
        self._local_vars[i] = e

    def setCode(self, c: List[int]) -> None:
        self._code = c
    
    def getInsAtIndex(self, i: int) -> int:
        return self._code[i]

    def reset(self):
        self.__init__()

    # f = frame to copy
    def copy(self, f):
        self.name = f.name
        self._operand_stack = f._operand_stack
        self._local_vars = f._local_vars
        self._code = f._code
        self._ret_address = f._ret_address

    def __str__(self) -> str:
        output = "Locals:\n"
        ctr = 0
        for i in self._local_vars:
            output += str(i) + '\n'
            ctr += 1
            if ctr == 10:
                break
        return output

    def __repr__(self) -> str:
        return self.__str__()