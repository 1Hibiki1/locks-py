from .token import TokenType, Token, tokenDict, keywordDict
from ..error import IllegalCharError, SyntaxErr

from typing import Union, List

#
# LEXER
# Takes a string and makes a list of tokens from it.
#
class Lexer:
    def __init__(self, inpstr: str) -> None:
        self._inpstr: str = inpstr
        self._curAbsIdx: int = 0
        self._curIdx: int = 0
        self._curLine: int = 1
        self._curChar: str = inpstr[0]
        self._tokList: List[Token] = []
        self._errList: List[IllegalCharError] = []
        self.hadError = False
        self._inString = False

    def getErrorList(self) -> List[IllegalCharError]:
        return self._errList

    def _advance(self, advBy: int=1) -> None:
        self._curAbsIdx += advBy
        self._curIdx += advBy

        if self._curAbsIdx >= len(self._inpstr):
            self._curChar = 'eof'
            return

        self._curChar = self._inpstr[self._curAbsIdx]

        if self._curChar == '\n' and not self._inString:
            self._curIdx = 0
            self._curLine += 1

    def _peek(self) -> str:
        if self._curAbsIdx + 1 >= len(self._inpstr):
            return 'eof'
        
        return self._inpstr[self._curAbsIdx+1]

    def _getNumber(self) -> Union[int, float]:
        number = ''
        dot_count = 0

        NUM = '0123456789.'  # legal number characters

        while self._curChar in NUM:
            number += self._curChar
            if self._curChar == '.':
                dot_count += 1
            if self._peek() == 'eof':
                break
            if self._peek() not in NUM:
                break
            self._advance()

        if dot_count == 1:
            return float(number)
        elif  dot_count == 0:
            return int(number)
        else:
            raise Exception("Invalid number")

    def _getID(self):
        identifier = ''

        while self._curChar.isalnum():
            identifier += self._curChar
            if self._peek() == 'eof':
                break
            if not self._peek().isalnum():
                break
            self._advance()        

        return identifier

    def _getString(self):
        self._inString = True
        initialPos = (self._curLine, self._curIdx)
        strn = ''
        self._advance()
        while self._curChar not in ["'", '"'] and self._curChar != "eof" :
            strn += self._curChar
            self._advance()

        if self._curChar == "eof":
            self.hadError = True
            self._errList.append(SyntaxErr(
                f"Unmatched Quote",
                initialPos[0],
                initialPos[1]
            ))

        self._advance()
        self._inString = False

        return strn

    def getTokens(self) -> List[Token]:
        while self._curChar != 'eof':

            if self._curChar == '/':
                if self._peek() == '/':
                    while not self._curChar == '\n':
                        self._advance()
                
                # works, but cleanup required
                if self._peek() == '*':
                    while True:
                        self._advance()
                        if self._curChar == '*':
                            self._advance()
                            if self._curChar == "/":
                                self._advance()
                                break
            
            if self._curChar.isspace():
                self._advance()

            elif self._curChar in ["'", '"']:
                self._tokList.append(Token(TokenType.STRING, self._getString(), self._curLine, self._curIdx))

            elif self._curChar + self._peek() in tokenDict:
                val = self._curChar + self._peek()
                typ = tokenDict[val]
                self._tokList.append(Token(typ, val, self._curLine, self._curIdx))
                self._advance(2)
            
            elif self._curChar in tokenDict:
                typ = tokenDict[self._curChar]
                self._tokList.append(Token(typ, self._curChar, self._curLine, self._curIdx))
                self._advance()

            elif self._curChar.isdigit():
                self._tokList.append(Token(TokenType.NUMBER, self._getNumber(), self._curLine, self._curIdx))
                self._advance()

            elif self._curChar.isalpha():
                id = self._getID()
                pos = self._curIdx - len(id)
                if id in keywordDict:
                    self._tokList.append(Token(keywordDict[id], id, self._curLine, pos))
                else:
                    self._tokList.append(Token(TokenType.ID, id, self._curLine, pos))
                self._advance()

            else:
                self.hadError = True
                self._errList.append(IllegalCharError(
                    f"Unexpected character '{self._curChar}'",
                    self._curLine,
                    self._curIdx
                ))
                self._advance()
                
        self._tokList.append(Token(TokenType.EOF, '', self._curLine, self._curIdx))
        return self._tokList
