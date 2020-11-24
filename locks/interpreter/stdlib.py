from .types import Nil, String, Number, Array, Boolean
from typing import Union


def locks_print(argList: list) -> None:
    output: str = str(argList[0])

    if type(argList[0]).__name__ == "String":
        output = output[1:-1]

    print(output, end='')
    return Nil()


def locks_println(argList: list) -> None:
    output: str = str(argList[0])

    if type(argList[0]).__name__ == "String":
        output = output[1:-1]

    print(output)
    return Nil()

def locks_input(argList: list) -> str:
    inpstr = argList[0].value
    return String(input(inpstr))

def locks_len(el: list) -> Number:
    e: Union[String, Array] = el[0]
    if type(e).__name__ == "String":
        return Number(len(e.value))

    if type(e).__name__ == "Array":
        return Number(len(e._arr))

    # handle type error

def locks_int(el: list) -> Number:
    s = el[0].value
    if type(el[0]).__name__ == "Boolean":
        if s == "true":
            s = 1
        if s == "false":
            s = 0
    return Number(int(s))

def locks_str(el: list) -> String:
    return String(str(el[0]))


def locks_isinteger(el: list) -> Boolean:
    # check type

    def getBoolObj(b) -> Boolean:
        if b:
            return Boolean("true")
        else:
            return Boolean("false")

    s = el[0].value

    if len(s) == 0:
        return Boolean("false")
    # https://stackoverflow.com/a/1265696
    if s[0] in ('-', '+'):
        return getBoolObj(s[1:].isdigit())

    return getBoolObj(s.isdigit())


builtinFunctionTable = {
    "print" : locks_print,
    "println" : locks_println,
    "input" : locks_input,
    "len" : locks_len,
    "int" : locks_int,
    "str" : locks_str,
    "isinteger" : locks_isinteger
}
