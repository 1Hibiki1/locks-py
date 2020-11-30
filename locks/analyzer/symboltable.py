from typing import List


class Symbol:
    def __init__(self, n: str, t: str = None) -> None:
        self.name: str = n
        self.type: Symbol = t

    def __str__(self) -> str:
        if self.type != None:
            return f"<{self.type}:{self.name}>"
        return f"<{self.name}>"

    def __repr__(self) -> str:
        return self.__str__()


class TypeSymbol(Symbol):
    def __init__(self, t: str) -> None:
        super().__init__(t)


class VariableSymbol(Symbol):
    def __init__(self, n: str) -> None:
        super().__init__(n, "variable")

    def setType(self, t: TypeSymbol) -> None:
        self.type = t


class FunctionSymbol(Symbol):
    def __init__(self, n: str, b, args: List[Symbol] = []) -> None:
        super().__init__(n, "function")
        self.block = b
        self.argSymbols: List[Symbol] = args


class SymbolTable:
    def __init__(self, n: str) -> None:
        self.name: str = n
        self._table = dict()
        self._enclosingTable: SymbolTable = None


    def get(self, s: str, restrict=False) -> Symbol:
        if restrict:
            return self._table.get(s)

        if self._table.get(s) != None:
            return self._table.get(s)
        
        if self._enclosingTable == None:
            return None

        return self._enclosingTable.get(s)


    def add(self, s: Symbol) -> None:
        self._table[s.name] = s


    def setEnclosingScope(self, s) -> None:
        self._enclosingTable = s


    def getEnclosingScope(self):
        return self._enclosingTable


    def __str__(self) -> str:
        output = ""
        for e in self._table:
            output += f"{self._table[e]}: {e}\n"

        return output


    def __repr__(self) -> str:
        return self.__str__()