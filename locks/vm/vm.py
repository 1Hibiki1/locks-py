from typing import List

from .code.codeBuilder import CodeBuilder
from .code.code import Code, func_info, cp_info, Tag
from ..instruction import opcode, opcodeDict
from .stack.frame import Frame
from .stack.stack import Stack

from ..types import LObject, Number, Nil, Array, Boolean, String
from ..stdlib import builtinFunctionIndex, builtinFunctionTable, builtinFunctionInfo
from ..error import TypeErr, ZeroDivErr, IndexErr, SyntaxErr


class VirtualMachine:
    def __init__(self, code: List[int]) -> None:
        self._code_obj: Code = CodeBuilder(code).getCodeObj()

        self._cur_frame: Frame = Frame()
        self._main_frame: Frame = Frame("main")

        self._call_stack: Stack = Stack()
        self._ip: int = -1
        self._cur_ins: int = None

        self._LOG: bool = False


    def _advance(self, advance_by=1) -> int:
        self._ip += advance_by
        self._cur_ins = self._cur_frame.getInsAtIndex(self._ip)
        return self._cur_ins

    # jump to index 'idx' of the code of currrent executing function
    def _goto(self, idx: int) -> None:
        self._ip = idx
        self._cur_ins = self._cur_frame.getInsAtIndex(self._ip)


    def _pushFrame(self, f: Frame) -> None:
        self._call_stack.push(f)


    def _popFrame(self) -> Frame:
        return self._call_stack.pop()


    def _init_vm(self) -> None:
        main: func_info = self._code_obj.getFromFP(0)
        self._main_frame.setCode(main.code)
        self._cur_frame = self._main_frame
        self._advance()


    def run(self):
        self._init_vm()

        while self._cur_ins != opcode.END.value:
            i = self._cur_ins
            self.execute(i)
            if i not in [
                opcode.GOTO.value,
                opcode.POP_JMP_IF_TRUE.value,
                opcode.POP_JMP_IF_FALSE.value,
            ]:
                self._advance()


    def _getObjType(self, el: LObject) -> str:
        return type(el).__name__


    def _isTruthy(self, obj: LObject) -> bool:
        if self._getObjType(obj) == "Number":
            if obj.value == 0:
                return False
            return True

        elif self._getObjType(obj) == "String":
            if len(obj.value) == 0:
                return False
            return True

        elif self._getObjType(obj) == "Nil":
            return False

        elif self._getObjType(obj) == "Boolean":
            if obj.value == "false":
                return False
            return True

        elif self._getObjType(obj) == "Array":
            if obj.getLen() == 0:
                return False
            return True

        return True


    def execute(self, i: int) -> None:
        fn_name = f"execute_{opcodeDict[i]}"
        fn = getattr(self, fn_name, self._insNotImplemented)
        fn(i)

    def _insNotImplemented(self, i: int) ->  None:
        raise Exception(f"execute_{opcodeDict[i]} method not implemented.")


    def execute_LOAD_NIL(self, i: int) -> None:
        self._cur_frame.pushOpStack(Nil())


    def execute_LOAD_TRUE(self, i: int) -> None:
        self._cur_frame.pushOpStack(Boolean("true"))


    def execute_LOAD_FALSE(self, i: int) -> None:
        self._cur_frame.pushOpStack(Boolean("false"))


    def execute_LOAD_CONST(self, i: int) -> None:
        idx: int = (self._advance() << 8) + self._advance()
        constObj: cp_info = self._code_obj.getFromCP(idx)

        if constObj.tag == Tag.CONSTANT_String:
            self._cur_frame.pushOpStack(String(constObj.info))
            
        elif constObj.tag == Tag.CONSTANT_Integer:
            self._cur_frame.pushOpStack(Number(constObj.info))
            
        elif constObj.tag == Tag.CONSTANT_Double:
            self._cur_frame.pushOpStack(Number(constObj.info))


    def execute_BINARY_ADD(self, i: int) -> None:
        r: LObject = self._cur_frame.popOpStack()
        l: LObject = self._cur_frame.popOpStack()

        # string concat for '+'
        if self._getObjType(l) == "String":
            if self._getObjType(r) != "String":
                raise TypeErr(f"Cannot add {self._getObjType(r)} to String")
            self._cur_frame.pushOpStack(String(l.value + r.value))

        # check type for numbers
        elif self._getObjType(l) == "Number":
            if self._getObjType(r) != "Number":
                raise TypeErr(f"Cannot add {self._getObjType(r)} to Number")
            self._cur_frame.pushOpStack(Number(l.value + r.value))
        
        # addition is not defined for any other type
        else:
            raise TypeErr(f"Addition not defined for type '{self._getObjType(l)}'")


        if self._LOG: print(f"add {l.value}, {r.value}")

    
    def execute_BINARY_SUBTRACT(self, i: int) -> None:
        r: LObject = self._cur_frame.popOpStack()
        l: LObject = self._cur_frame.popOpStack()

        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Cannot subtract {self._getObjType(r)} from {self._getObjType(l)}")

        self._cur_frame.pushOpStack(Number(l.value - r.value))

        if self._LOG: print(f"sub {l.value}, {r.value}")


    def execute_BINARY_MULTIPLY(self, i: int) -> None:
        r: LObject = self._cur_frame.popOpStack()
        l: LObject = self._cur_frame.popOpStack()

        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Cannot multiply {self._getObjType(l)} by {self._getObjType(r)}")

        self._cur_frame.pushOpStack(Number(l.value * r.value))

        if self._LOG: print(f"mul {l.value}, {r.value}")


    def execute_BINARY_DIVIDE(self, i: int) -> None:
        r: LObject = self._cur_frame.popOpStack()
        l: LObject = self._cur_frame.popOpStack()

        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Cannot divide {self._getObjType(l)} by {self._getObjType(r)}")

        # division by zero
        if r.value == 0:
            raise ZeroDivErr()

        self._cur_frame.pushOpStack(Number(l.value / r.value))

        if self._LOG: print(f"div {l.value}, {r.value}")


    def execute_BINARY_MODULO(self, i: int) -> None:
        r: LObject = self._cur_frame.popOpStack()
        l: LObject = self._cur_frame.popOpStack()

        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Invalid operand type for modulo: {self._getObjType(l)} and {self._getObjType(r)}")

        # division by zero
        if r.value == 0:
            raise ZeroDivErr()

        self._cur_frame.pushOpStack(Number(l.value % r.value))

        if self._LOG: print(f"mod {l.value}, {r.value}")


    def execute_BINARY_AND(self, i: int) -> None:
        r: LObject = self._cur_frame.popOpStack()
        l: LObject = self._cur_frame.popOpStack()

        if self._LOG: print(f"and {l.value}, {r.value}")
        
        if not self._isTruthy(l):
            self._cur_frame.pushOpStack(Boolean("false"))
            return
        
        if not self._isTruthy(r):
            self._cur_frame.pushOpStack(Boolean("false"))
            return
            
        self._cur_frame.pushOpStack(Boolean("true"))


    def execute_BINARY_OR(self, i: int) -> None:
        r: LObject = self._cur_frame.popOpStack()
        l: LObject = self._cur_frame.popOpStack()

        if self._isTruthy(l):
            self._cur_frame.pushOpStack(Boolean("true"))
        elif self._isTruthy(r):
            self._cur_frame.pushOpStack(Boolean("true"))
        else:
            self._cur_frame.pushOpStack(Boolean("false"))

        if self._LOG: print(f"or {l.value}, {r.value}")


    def execute_UNARY_NOT(self, i: int) -> None:
        op: LObject = self._cur_frame.popOpStack()
        if self._isTruthy(op):
            self._cur_frame.pushOpStack(Boolean("false"))
        else:
            self._cur_frame.pushOpStack(Boolean("true"))


    def execute_UNARY_NEGATIVE(self, i: int) -> None:
        op: LObject = self._cur_frame.popOpStack()
        
        if not self._getObjType(op) == "Number":
            raise TypeErr(f"Cannot negate {self._getObjType(op)}")

        self._cur_frame.pushOpStack(Number(-(op.value)))


    def execute_STORE_LOCAL(self, i: int) -> None:
        self._cur_frame.setLocalVarAtIndex(
            self._advance(),
            self._cur_frame.popOpStack()
        )


    def execute_STORE_GLOBAL(self, i: int) -> None:
        self._main_frame.setLocalVarAtIndex(
            self._advance(),
            self._cur_frame.popOpStack()
        )


    def execute_BIPUSH(self, i: int) -> None:
        self._cur_frame.pushOpStack(Number(self._advance()))


    def execute_LOAD_LOCAL(self, i: int) -> None:
        self._cur_frame.pushOpStack(self._cur_frame.getLocalVarAtIndex(self._advance()))


    def execute_LOAD_GLOBAL(self, i: int) -> None:
        self._cur_frame.pushOpStack(self._main_frame.getLocalVarAtIndex(self._advance()))


    def execute_CMPEQ(self, i: int) -> None:
        r: LObject = self._cur_frame.popOpStack()
        l: LObject = self._cur_frame.popOpStack()

        if l.value == r.value:
            self._cur_frame.pushOpStack(Boolean("true"))
        else:
            self._cur_frame.pushOpStack(Boolean("false"))

        if self._LOG: print(f"cmpeq {l.value}, {r.value}")


    def execute_CMPNE(self, i: int) -> None:
        r: LObject = self._cur_frame.popOpStack()
        l: LObject = self._cur_frame.popOpStack()

        if l.value != r.value:
            self._cur_frame.pushOpStack(Boolean("true"))
        else:
            self._cur_frame.pushOpStack(Boolean("false"))

        if self._LOG: print(f"cmpne {l.value}, {r.value}")


    def execute_CMPGT(self, i: int) -> None:
        r: LObject = self._cur_frame.popOpStack()
        l: LObject = self._cur_frame.popOpStack()

        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Invalid operand type for greater than operator: {self._getObjType(l)} and {self._getObjType(r)}")

        if l.value > r.value:
            self._cur_frame.pushOpStack(Boolean("true"))
        else:
            self._cur_frame.pushOpStack(Boolean("false"))

        if self._LOG: print(f"cmpgt {l.value}, {r.value}")


    def execute_CMPLT(self, i: int) -> None:
        r: LObject = self._cur_frame.popOpStack()
        l: LObject = self._cur_frame.popOpStack()

        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Invalid operand type for less than operator: {self._getObjType(l)} and {self._getObjType(r)}")
        
        if l.value < r.value:
            self._cur_frame.pushOpStack(Boolean("true"))
        else:
            self._cur_frame.pushOpStack(Boolean("false"))

        if self._LOG: print(f"cmplt {l.value}, {r.value}")


    def execute_CMPGE(self, i: int) -> None:
        r: LObject = self._cur_frame.popOpStack()
        l: LObject = self._cur_frame.popOpStack()

        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Invalid operand type for greater than equals operator: {self._getObjType(l)} and {self._getObjType(r)}")

        if l.value >= r.value:
            self._cur_frame.pushOpStack(Boolean("true"))
        else:
            self._cur_frame.pushOpStack(Boolean("false"))

        if self._LOG: print(f"cmpge {l.value}, {r.value}")


    def execute_CMPLE(self, i: int) -> None:
        r: LObject = self._cur_frame.popOpStack()
        l: LObject = self._cur_frame.popOpStack()

        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Invalid operand type for less than equals operator: {self._getObjType(l)} and {self._getObjType(r)}")

        if l.value <= r.value:
            self._cur_frame.pushOpStack(Boolean("true"))
        else:
            self._cur_frame.pushOpStack(Boolean("false"))

        if self._LOG: print(f"cmple {l.value}, {r.value}")


    def execute_GOTO(self, i: int) -> None:
        loc: int = (self._advance() << 8) + self._advance()
        self._goto(loc)


    def execute_POP_JMP_IF_TRUE(self, i: int) -> None:
        idx: int = (self._advance() << 8) + self._advance()
        if self._isTruthy(self._cur_frame.popOpStack()):
            self._goto(idx)
        else:
            self._advance() # consume second arg


    def execute_POP_JMP_IF_FALSE(self, i: int) -> None:
        idx: int = (self._advance() << 8) + self._advance()
        if not self._isTruthy(self._cur_frame.popOpStack()):
            self._goto(idx)
        else:
            self._advance() # consume second arg


    def execute_CALL_FUNCTION(self, i: int) -> None:
        idx: int = self._advance()
        fnInfo: func_info = self._code_obj.getFromFP(idx)

        f = Frame()
        f.copy(self._cur_frame)
        f.setReturnAddress(self._ip)
        
        self._ip = -1
        self._cur_frame.reset()
        self._cur_frame.setCode(fnInfo.code)

        if f.name == "main":
            self._main_frame._local_vars = f._local_vars

        for i in range(fnInfo.argc):
            self._cur_frame.pushOpStack(f.popOpStack())

        self._pushFrame(f)


    def execute_CALL_NATIVE(self, i: int) -> None:
        idx: int = self._advance()
        fnName = builtinFunctionIndex[idx]
        args: List[LObject] = []
        argc: int = builtinFunctionInfo[fnName][1]
        for _ in range(argc):
            args = [self._cur_frame.popOpStack()] + args

        self._cur_frame.pushOpStack(builtinFunctionTable[fnName](args))


    def execute_RETURN_VALUE(self, i: int) -> None:        
        retVal: LObject = self._cur_frame.popOpStack()

        try:
            ret_f: Frame = self._popFrame()
            self._ip = ret_f.getReturnAddress()
            self._cur_frame.copy(ret_f)
            self._cur_frame.pushOpStack(retVal)
        except:
            pass


    def execute_BUILD_LIST(self, i: int) -> None:
        len: int = (self._advance() << 8) + self._advance()
        arrObj: Array = Array()

        arrElList: list = []
        for _ in range(len):
            arrElList = [self._cur_frame.popOpStack()] + arrElList

        for e in arrElList:
            arrObj.addEl(e)

        self._cur_frame.pushOpStack(arrObj)
        

    def execute_BINARY_SUBSCR(self, i: int) -> None:
        idx: Number = self._cur_frame.popOpStack()

        if type(idx).__name__ != "Number":
            raise TypeErr(f"Array indices must be integers, not '{type(idx).__name__}'")

        if type(idx.value).__name__ == "float":
            raise TypeErr(f"Array indices must be integers, not float")
        
        arr: Array = self._cur_frame.popOpStack()

        if self._getObjType(arr) != "Array":
            raise TypeErr(f"Type '{type(arr).__name__}' is not subscriptable")
        
        if arr.getEL(idx.value) == None:
            raise IndexErr()

        self._cur_frame.pushOpStack(arr.getEL(idx.value))


    def execute_STORE_SUBSCR(self, i: int) -> None:
        idx: Number = self._cur_frame.popOpStack()
        
        if type(idx).__name__ != "Number":
            raise TypeErr(f"Array indices must be integers, not '{type(idx).__name__}'")

        if type(idx.value).__name__ == "float":
            raise TypeErr(f"Array indices must be integers, not float")

        arr: Array = self._cur_frame.popOpStack()
        if self._getObjType(arr) != "Array":
            raise TypeErr(f"Type '{type(arr).__name__}' is not subscriptable")

        val: LObject = self._cur_frame.popOpStack()

        if arr.getEL(idx.value) == None:
            raise IndexErr()

        arr.setEL(val, idx.value)
        self._cur_frame.pushOpStack(arr)

