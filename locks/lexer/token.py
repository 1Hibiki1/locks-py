from enum import Enum
from typing import Any, List

#
# Locks tokens
#  To add a keyword, add an entry at the end of the Enum
#
class TokenType(Enum):
    ID = "identifier"
    NUMBER = "number"
    STRING = "string"
    EOF = None

    # punctuation
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

    # operators
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

    # keywords
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


#
# Converts the TokenType enum into a dictionary (except keywords)
#
def makeTokenDict() -> dict:
    d = dict()

    kList: List[TokenType] = list(TokenType)
    endIdx: int = kList.index(TokenType.VAR)

    for i in range(0, endIdx):
        d[kList[i].value] = kList[i]

    return d


#
# Makes a keyword dictionary from the TokenType enum
#
def makeKeywordDict() -> dict:
    d = dict()

    kList: List[TokenType] = list(TokenType)
    startIdx: int = kList.index(TokenType.VAR)
    l: int = len(kList)

    for i in range(startIdx, l):
        d[kList[i].value] = kList[i]

    return d


class Token:
    def __init__(self, t: TokenType, v: any, l: int, pos: int) -> None:
        self.type: TokenType = t
        self.value: Any = v
        self.line: int = l
        self.position: int = pos

    def __str__(self) -> str:
        return f"({self.line}:{self.position}){self.type}: {self.value}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, o) -> bool:
        return (
            self.type.value == o.type.value and
            self.value == o.value and
            self.line == o.line and
            self.position == o.position
        )


tokenDict: dict = makeTokenDict()
keywordDict: dict = makeKeywordDict()
