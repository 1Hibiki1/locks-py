from enum import Enum
from typing import Any, List

class TokenType(Enum):
    ID = "identifier"
    NUMBER = "number"
    STRING = "string"
    EOF = None

    L_PAREN = '('
    R_PAREN = ')'
    L_SQUARE = '['
    R_SQUARE = ']'
    L_CURLY = '{'
    R_CURLY = '}'
    SEMI = ';'
    COMMA = ','
    QUOTE = '"'
    S_QUOTE = "'"

    LESS_THAN = '<'
    GREATER_THAN = '>'
    LESS_THAN_EQ = '<='
    GREATER_THAN_EQ = '>='
    EQUAL = '=='
    NOT_EQUAL = '!='
    NOT = '!'

    PLUS = '+'
    MINUS = '-'
    MUL = '*'
    DIV = '/'
    MOD = '%'
    ASSIGN = '='

    VAR = "var"
    FUNCTION = "fun"
    IF = "if"
    ELSE = "else"
    ELSEIF = "elsif"
    WHILE = "while"
    FOR = "for"
    RETURN = "return"
    CONTINUE = "continue"
    BREAK = "break"
    AND = "and"
    OR = "or"
    TRUE = "true"
    FALSE = "false"
    NIL = "nil"


def makeTokenDict() -> dict:
    d = dict()

    kList: List[TokenType] = list(TokenType)
    endIdx: int = kList.index(TokenType.VAR)

    for i in range(0, endIdx):
        d[kList[i].value] = kList[i]

    return d

def makeKeywordDict() -> dict:
    d = dict()

    kList: List[TokenType] = list(TokenType)
    startIdx: int = kList.index(TokenType.VAR)
    l: int = len(kList)

    for i in range(startIdx, l):
        d[kList[i].value] = kList[i]

    return d


class Token:
    def __init__(self, t: TokenType, v: any, l: int, pos: int):
        self.type: TokenType = t
        self.value: Any = v
        self.line: int = l
        self.position: int = pos

    def __str__(self) -> str:
        return f"({self.line}:{self.position}){self.type}: {self.value}"


tokenDict: dict = makeTokenDict()
keywordDict: dict = makeKeywordDict()
