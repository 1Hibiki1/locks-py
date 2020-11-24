class Error(Exception):
    def __init__(self, typ: str, msg: str, line: int, pos: int) -> None:
        self.type: str = typ
        self.msg: str = msg
        self.line: int = line
        self.pos: int = pos

    def __str__(self) -> str:
        if self.pos != None:
            return f"{self.type}(line {self.line}): {self.msg} at character {self.pos}"
        return f"{self.type}(line {self.line}): {self.msg}"

    def __repr__(self):
        return self.__str__()


class IllegalCharError(Error):
    def __init__(self, msg: str, line: int, pos: int):
        super().__init__("Illegel Character Error", msg, line, pos)

class SyntaxErr(Error):
    def __init__(self, msg: str, line: int, pos: int = None):
        super().__init__("Syntax Error", msg, line, pos)        

class NameErr(Error):
    def __init__(self, msg: str, line: int, pos: int):
        super().__init__("Name Error", msg, line, pos)

    def __str__(self) -> str:
        return f"{self.type}(line {self.line}): {self.msg}"

class TypeErr(Error):
    def __init__(self, msg: str, line: int):
        super().__init__("Type Error", msg, line, None)

class ZeroDivErr(Error):
    def __init__(self, line: int):
        super().__init__("Division by Zero Error", "Division or Modulo by zero", line, None)
