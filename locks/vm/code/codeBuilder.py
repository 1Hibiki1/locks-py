from .code import Code, Tag, func_info, cp_info
from ...error import InvalidBytecodeError

class CodeBuilder:
    def __init__(self, codeArr):
        self._code = Code()
        self._code_array = codeArr

    
    def getCodeObj(self) -> Code:
        self._initCode()
        self._makeConstPool()
        self._makeFuncPool()
        return self._code

    def _removeFromFront(self, n: int) -> None:
        self._code_array = self._code_array[n:]

    
    def _initCode(self) -> None:
        if len(self._code_array) < 10:
            raise InvalidBytecodeError()

        magic: int =                        \
            (self._code_array[0] << 24) +   \
            (self._code_array[1] << 16) +   \
            (self._code_array[2] << 8) +    \
            (self._code_array[3])

        if magic != Code.magic_number:
            raise InvalidBytecodeError()
        
        self._removeFromFront(4)

    
    def _makeConstPool(self) -> None:
        cp_count: int = (self._code_array[0] << 8) + (self._code_array[1])
        self._removeFromFront(2)
        
        for _ in range(cp_count):
            t: Tag = self._code_array[0]
            self._removeFromFront(1)

            if t == Tag.CONSTANT_Integer:
                self._makeInteger()
            elif t == Tag.CONSTANT_Double:
                self._makeDouble()
            elif t == Tag.CONSTANT_String:
                self._makeString()

    def _makeInteger(self) -> None:
        i: int =                            \
            (self._code_array[0] << 56) +   \
            (self._code_array[1] << 48) +   \
            (self._code_array[2] << 40) +   \
            (self._code_array[3] << 32) +   \
            (self._code_array[4] << 24) +   \
            (self._code_array[5] << 16) +   \
            (self._code_array[6] << 8) +    \
            (self._code_array[7])

        s_test: int = (i & 0xf000000000000000) >> 60

        if s_test > 7:
            i -= 1  # sub 1
            i = i ^ (0xffffffffffffffff)  # flip bits
            i = -i  # negate

        self._removeFromFront(8)
        self._code.addToCP(cp_info(Tag.CONSTANT_Integer, i))

    
    def _makeDouble(self) -> None:
        v = self._code_array

        sign: int = (v[0] & 0b10000000) >> 7
        exp: int = (((v[0] << 8) + (v[1])) & 0b0111111111110000) >> 4
        mantissa: int = ((v[1] & 0x0f) << 48) + \
            (v[2] << 40) +    \
            (v[3] << 32) +    \
            (v[4] << 24) +    \
            (v[5] << 16) +    \
            (v[6] << 8) +     \
            (v[7])            

        d: float = mantissa/(10**exp)

        if sign == 1:
            d = -d

        self._removeFromFront(8)
        self._code.addToCP(cp_info(Tag.CONSTANT_Double, d))

    def _makeString(self) -> None:
        s: str = ""

        while self._code_array[0] != 0x00:
            s += chr(self._code_array[0])
            self._removeFromFront(1)

        self._removeFromFront(1)
        self._code.addToCP(cp_info(Tag.CONSTANT_String, s))

    def _makeFuncPool(self) -> None:
        fp_count: int = (self._code_array[0] << 8) + (self._code_array[1])
        self._removeFromFront(2)
        for _ in range(fp_count):
            self._code.addToFP(self._makeFunc())

    def _makeFunc(self) -> func_info:
        f = func_info()

        argc: int = (self._code_array[0] << 8) + (self._code_array[1])
        self._removeFromFront(2)
        f.argc = argc

        code_count: int = (self._code_array[0] << 8) + (self._code_array[1])
        self._removeFromFront(2)
        
        for _ in range(code_count):
            f.code.append(self._code_array[0])
            self._removeFromFront(1)

        return f
        

