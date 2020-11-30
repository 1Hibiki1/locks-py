from enum import Enum


class CallStack:
    def __init__(self):
        self.stack = []

    def push(self, ar):
        self.stack.append(ar)

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]

    def __repr__(self):
        output = 'CALL STACK:\n'
        for a in self.stack:
            output += str(a) + '\n'
        return output


class Environment:
    def __init__(self, enclosing = None) -> None:
        self._members = dict()
        self.enclosingEnv = enclosing

    def get(self, name):
        if self.enclosingEnv == None:
            return self._members.get(name)

        if self._members.get(name) != None:
            return self._members.get(name)

        return self.enclosingEnv.get(name)

    def __getitem__(self, key):
        return self._members[key]

    def __setitem__(self, key, value):
        self._members[key] = value

    def __str__(self) -> str:
        output = ''
        for v in self._members:
            output += f"{v} : {self._members[v]}\n"
        return output


class ARType(Enum):
    def __str__(self) -> str:
        return str(self.value)

    MAIN = 'main'
    FUNCTION = 'function'
    BLOCK = 'block'
    

class ActivationRecord:
    def __init__(self, typ: ARType):
        self.name: str = str(typ)
        self.members: Environment = Environment()
        self.type: ARType = typ

    def get(self, name):
        return self.members.get(name)

    def __getitem__(self, key):
        return self.members[key]

    def __setitem__(self, key, value):
        self.members[key] = value

    def setEnclosingEnv(self, env: Environment) -> None:
        self.members.enclosingEnv = env

    def __repr__(self):
        output = f"AR {self.name}:\n{str(self.members)}"
        return output

    def __str__(self):
        return self.__repr__()

