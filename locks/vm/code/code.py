from typing import List, Any

class Tag:
    CONSTANT_Integer = 0x3
    CONSTANT_Double = 0x6
    CONSTANT_String = 0x8

class func_info:
    def __init__(self):
        self.argc: int = 0
        self.code: List[int] = []

    def __str__(self):
        code = ""
        for i in self.code:
            code += hex(i) + ' '
        code = code.strip()
        return f"{self.argc}-{code}"

    def __repr__(self):
        return self.__str__()

class cp_info:
    def __init__(self, t: int, v: Any):
        self.tag: int = t
        self.info: Any = v

    def __str__(self):
        return f"{hex(self.tag)}: {self.info}"

    def __repr__(self):
        return self.__str__()

class Code:
    magic_number: int = 0x4d69686f

    def __init__(self):
        self.const_pool: List[cp_info] = []
        self.func_pool: List[func_info] = []

    def addToCP(self, c: cp_info) -> None:
        self.const_pool.append(c)

    def getFromCP(self, idx: int) -> cp_info:
        return self.const_pool[idx]

    def addToFP(self, c: func_info) -> None:
        self.func_pool.append(c)

    def getFromFP(self, idx: int) -> func_info:
        return self.func_pool[idx]