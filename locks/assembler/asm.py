from typing import List, Dict
from ..instruction import opcodeSizeDict, opcodeNameDict


class Assembler:
    def __init__(self, inpstr: str) -> None:
        self._inpCodeList: List[str] = []

        # split inpstr by newline character, except in strings (marked by double quotes)
        i = 0
        s = ''
        while i < len(inpstr):
            if inpstr[i] == '"':
                i += 1
                s += '"'
                while inpstr[i] != '"':
                    s += inpstr[i]
                    i += 1
            
            s += inpstr[i]
            
            if inpstr[i] == '\n':
                self._inpCodeList.append(s)
                s = ""

            i += 1

        self._outputCodeList: List[int] = []

        self._fnDict: Dict[str, int] = dict()
        self._fnCount = 0

        self._labelsDict: Dict[str, int] = dict()


    def getBytecodeList(self) -> List[int]:
        self._initCode()
        self._resolveLabels()
        self._makeConstantPool()
        self._makeCode()

        return self._outputCodeList


    def _emit(self, *args) -> None:
        for i in args:
            self._outputCodeList.append(i)


    def _initCode(self) -> None:
        # remove while space around lines
        for i,v in enumerate(self._inpCodeList):
            self._inpCodeList[i] = v.strip()

        # remove blank lines
        while '' in self._inpCodeList:
            self._inpCodeList.remove('')

        # add magic number for Locks VM
        self._emit(0x4d, 0x69, 0x68, 0x6f)


    #
    # Converts identifiers to indices and lables to memory locations
    # Also counts the number of functions and the code size for each one
    #
    def _resolveLabels(self) -> None:
        # count functions
        # note that this will remove all lines marked by 'fn'
        i = 0
        while i < len(self._inpCodeList):
            l = self._inpCodeList[i].split(' ')
            if l[0] == "fn":
                self._fnDict[l[1]] = self._fnCount
                self._inpCodeList.pop(i)
                self._fnCount += 1

            i += 1

        i = 0
        totalInsSize = 0
        while i < len(self._inpCodeList):
            l = self._inpCodeList[i].split(' ')

            # argc marks the beginning of a function
            if l[0] == "argc":
                totalInsSize = 0
            
            elif l[0][0] == '.':
                self._labelsDict[l[0][1:]] = totalInsSize
                self._inpCodeList.pop(i)
                continue

            else:
                if l[0] in opcodeSizeDict:
                    totalInsSize += opcodeSizeDict[l[0]]

            i += 1
                

    def _removeFromFront(self, n: int) -> None:
        self._inpCodeList = self._inpCodeList[n:]


    def _makeConstantPool(self) -> None:
        # cpc - constants pool size
        size: int = int(self._inpCodeList[0].split(' ')[1])
        self._emit(
            (size & 0xff00) >> 8,
            (size & 0xff)
        )

        self._removeFromFront(1)

        for i in range(size):
            typ: str = self._inpCodeList[i][0]
            ins: List[str] = self._inpCodeList[i][1:].strip()
            
            if typ == 'i':
                self._makeInteger(int(ins))

            elif typ == 'd':
                self._makeDouble(float(ins))

            elif typ == 's':
                self._makeString(ins[1:-1])

        self._removeFromFront(size)


    def _makeInteger(self, i: int) -> None:
        self._emit(0x03)  # integer tag

        # two's complement representation for negative ints
        if i < 0:
            i = -i
            i = i ^ (0xffffffffffffffff)  # flip bits
            i += 1

        # split into 8 bytes
        self._emit(
            (i & 0xff00000000000000) >> 56,
            (i & 0xff000000000000) >> 48,
            (i & 0xff0000000000) >> 40,
            (i & 0xff00000000) >> 32,
            (i & 0xff000000) >> 24,
            (i & 0xff0000) >> 16,
            (i & 0xff00) >> 8,
            i & 0xff,
        )


    def _makeDouble(self, d: float) -> None:
        self._emit(0x06)  # double tag

        # check sign
        sign: int = 0
        if d < 0:
            sign = 1
            d = -d

        exp: int = len(str(d)[str(d).index('.')+1:])
        mantissa: int = int(d*10**exp)

        i = (sign << 63) + (exp << 52) + (mantissa)
        
        # split into 8 bytes
        self._emit(
            (i & 0xff00000000000000) >> 56,
            (i & 0xff000000000000) >> 48,
            (i & 0xff0000000000) >> 40,
            (i & 0xff00000000) >> 32,
            (i & 0xff000000) >> 24,
            (i & 0xff0000) >> 16,
            (i & 0xff00) >> 8,
            i & 0xff,
        )


    def _makeString(self, s: str) -> None:
        self._emit(0x08)  # string tag

        for c in s:
            self._emit(ord(c))

        self._emit(0x00)  # null terminator


    def _makeCode(self) -> None:
        # number of functions
        self._emit(
            self._fnCount >> 8,
            self._fnCount & 0xff
        )

        for _ in range(self._fnCount):
            self._makeFunction()


    def _makeFunction(self) -> None:
        localVarDict: Dict[str, int] = dict()
        localVarCount: int = 0

        argc: int = int(self._inpCodeList[0].split(' ')[1])
        self._emit(
            argc >> 8,
            argc & 0xff
        )
        self._removeFromFront(1)

        # calculate total function size in bytes
        # opcodeSizeDict is defined in locks/instruction.py
        size: int = 0
        for l in self._inpCodeList:
            l = l.split(' ')[0]
            if l == "argc":
                break
            size += opcodeSizeDict[l]

        self._emit(
            size >> 8,
            size & 0xff
        )

        while len(self._inpCodeList) > 0:
            ins = self._inpCodeList[0].split(' ')\

            # argc marks beginnig of new function
            if ins[0] == "argc":
                break

            self._emit(opcodeNameDict[ins[0]])

            argc = opcodeSizeDict[ins[0]] - 1

            if argc > 0 and not ins[1].isnumeric():
                if ins[1] in self._labelsDict:
                    ins[1] = self._labelsDict[ins[1]]
                elif ins[1] in self._fnDict:
                    ins[1] = self._fnDict[ins[1]]

            if ins[0] in ["STORE_LOCAL", "LOAD_LOCAL", "STORE_GLOBAL", "LOAD_GLOBAL"]:
                if ins[1] not in localVarDict:
                    localVarDict[ins[1]] = localVarCount
                    ins[1] = localVarCount
                    localVarCount += 1
                else:
                    ins[1] = localVarDict[ins[1]]
                    
            if argc == 1:
                arg: int = int(ins[1])
                self._emit(arg)
            elif argc == 2:
                arg: int = int(ins[1])
                self._emit(
                    arg >> 8,
                    arg & 0xff
                )

            self._removeFromFront(1)
