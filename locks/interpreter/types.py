from typing import Union, List

class LObject:
    def __repr__(self) -> str:
        return self.__str__()

class Number(LObject):
    def __init__(self, val: Union[int, float])-> None:
        self.value = val

    def __str__(self) -> str:
        return f"{self.value}"

class Nil(LObject):
    def __init__(self)-> None:
        self.value = "nil"

    def __str__(self) -> str:
        return "nil"

class Boolean(LObject):
    def __init__(self, val: str)-> None:
        self.value = val

    def __str__(self) -> str:
        return f"{self.value}"

class String(LObject):
    def __init__(self, val: str)-> None:
        self.value = val

    def __str__(self) -> str:
        return f'"{self.value}"'

class Array(LObject):
    def __init__(self)-> None:
        self._arr: List[LObject] = []

    def addEl(self, el: LObject) -> None:
        self._arr.append(el)

    def setEL(self, el: LObject, idx: int) -> None:
        self._arr[idx] = el

    def getEL(self, idx: int) -> None:
        return self._arr[idx]

    def getLen(self) -> int:
        return len(self._arr)


    def __str__(self) -> str:
        output: str = '['
        for i in self._arr:
            output += str(i) + ", "
        output = output[:-2]
        output += ']'
        return output


class Function(LObject):
    def __init__(self, n: str, args: list, b)-> None:
        self.name = n
        self.args = args
        self.block = b

    def __str__(self) -> str:
        output = f"<function {self.name}: "

        for a in self.args:
            output += str(a) + ', '

        output = output[:-2] + '>'
        return output

