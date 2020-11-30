class Error(Exception):
    def __init__(self, typ: str, msg: str, line: int, pos: int) -> None:
        self.type: str = typ
        self.msg: str = msg
        self.line: int = line
        self.pos: int = pos

    def __str__(self) -> str:
        if self.pos == None and self.line == None:
            return f"{self.type}: {self.msg}"
        if self.pos != None:
            return f"{self.type}(line {self.line}): {self.msg} at character {self.pos}"
        return f"{self.type}(line {self.line}): {self.msg}"

    def __repr__(self):
        return self.__str__()


class IllegalCharError(Error):
    def __init__(self, msg: str, line: int, pos: int):
        super().__init__("Illegal Character Error", msg, line, pos)

class SyntaxErr(Error):
    def __init__(self, msg: str, line: int, pos: int = None):
        super().__init__("Syntax Error", msg, line, pos)        

class NameErr(Error):
    def __init__(self, msg: str, line: int, pos: int):
        super().__init__("Name Error", msg, line, pos)

    def __str__(self) -> str:
        return f"{self.type}(line {self.line}): {self.msg}"

class TypeErr(Error):
    def __init__(self, msg: str, line: int = None):
        super().__init__("Type Error", msg, line, None)

class ValueErr(Error):
    def __init__(self, msg: str, line: int = None):
        super().__init__("Value Error", msg, line, None)

class ZeroDivErr(Error):
    def __init__(self, line: int = None):
        super().__init__("Division by Zero Error", "Division or Modulo by zero", line, None)

class IndexErr(Error):
    def __init__(self, line: int = None):
        super().__init__("Index Error", "Array index out of range", line, None)

class InvalidBytecodeError(Error):
    def __init__(self):
        super().__init__("Invalid Bytecode Error", "invalid bytecode", None, None)
