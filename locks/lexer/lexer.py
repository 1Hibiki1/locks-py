from .token import TokenType, Token, tokenDict, keywordDict
from ..error import IllegalCharError, SyntaxErr

from typing import Union, List, Tuple


#
# LEXER
# Takes a string and returns a list of tokens.
# The Token class and list of Locks tokens are defined in token.py
#
class Lexer:
    # accepts a string (locks program) tat is to be split into tokens
    def __init__(self, inpstr: str) -> None:
        self._inpstr: str = inpstr

        # index of current character that is being processed, from the beginning of the input string
        self._curAbsIdx: int = 0

        # index of current character that is being processed, from the beginning of the current line
        self._curIdx: int = 0

        self._curLine: int = 1
        if not len(inpstr) == 0:
            self._curChar: str = inpstr[0]
        else:
            self._curChar: str = ""

        self._tokList: List[Token] = []
        self._errList: List[Union[IllegalCharError, SyntaxErr]] = []

        self.hadError: bool = False

        # True if a string is currently being processed. Used to prevent newline chacters inside strings
        #   from incrementing _curLine
        self._inString: bool = False


    def getErrorList(self) -> List[Union[IllegalCharError, SyntaxErr]]:
        return self._errList


    #
    # Moves forward by 'advBy' characters, checks for newlines and sets current position accordingly
    #
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


    #
    # Check next character without advancing
    #
    def _peek(self) -> str:
        if self._curAbsIdx + 1 >= len(self._inpstr):
            return 'eof'
        
        return self._inpstr[self._curAbsIdx+1]


    #
    # Main lexer method that returns the lis of tokens
    #
    def getTokens(self) -> List[Token]:

        while self._curChar != 'eof':
            
            # skip comments
            if self._curChar == '/':
                # single line comments
                if self._peek() == '/':
                    while not self._curChar == '\n':
                        self._advance()
                    continue
                
                # multiline comment
                if self._peek() == '*':
                    while True:
                        self._advance()

                        if self._curChar == '*':
                            self._advance()
                            if self._curChar == "/":
                                self._advance()
                                break
            
            # skip whitespace
            if self._curChar.isspace():
                self._advance()

            # string
            elif self._curChar in ["'", '"']:
                self._tokList.append(Token(TokenType.STRING, self._getString(), self._curLine, self._curIdx))

            # two-character long tokens
            elif self._curChar + self._peek() in tokenDict:
                val = self._curChar + self._peek()
                typ = tokenDict[val]
                self._tokList.append(Token(typ, val, self._curLine, self._curIdx))
                self._advance(2)
            
            # single character tokens
            elif self._curChar in tokenDict:
                typ = tokenDict[self._curChar]
                self._tokList.append(Token(typ, self._curChar, self._curLine, self._curIdx))
                self._advance()

            # number
            elif self._curChar.isdigit():
                self._tokList.append(Token(TokenType.NUMBER, self._getNumber(), self._curLine, self._curIdx))
                self._advance()

            # identifier
            elif self._curChar.isalpha() or self._curChar == '_':
                id = self._getID()
                pos = self._curIdx - len(id)
                if id in keywordDict:
                    self._tokList.append(Token(keywordDict[id], id, self._curLine, pos))
                else:
                    self._tokList.append(Token(TokenType.ID, id, self._curLine, pos))
                self._advance()

            # illegal character
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


    #
    # Process a number. Called when lexer encounters a digit (0-9)
    #
    def _getNumber(self) -> Union[int, float, None]:
        number: str = ''

        # to check for floats. If the user entered something like 1..2, dot_count will be 2 (which will cause a syntax error)
        dot_count: int = 0

        NUM = '0123456789.'  # legal number characters

        # consume characters until a character that is not a number or dot is encountered
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
            # note that '1.' and '.1' are valid floating point numbers in python, so we are ok as long as
            #   dot_count is 1
            return float(number)

        elif dot_count == 0:
            return int(number)

        else:
            self.hadError = True
            self._errList.append(SyntaxErr(
                f"Number contains mmore than 1 decimal point(s)",
                self._curLine,
                self._curIdx
            ))

    #
    # Process an identifier. Called when lexer encounters an alphabet [a-zA-Z]
    #
    def _getID(self) -> str:
        identifier: str = ''

        # consume characters until a character that is not an alphabet or underscore is encountered
        while self._curChar.isalnum() or self._curChar == '_':
            identifier += self._curChar
            if self._peek() == 'eof':
                break
            if not self._peek().isalnum() and self._peek() != '_':
                break
            self._advance()        

        return identifier


    #
    # Process a string. Called when lexer encounters a double or single quote.
    #
    def _getString(self) -> str:
        self._inString = True

        initialPos: Tuple[int, int] = (self._curLine, self._curIdx)
        strn: str = ''

        self._advance()

        while self._curChar not in ["'", '"'] and self._curChar != "eof" :
            strn += self._curChar
            self._advance()

        # if we reached the end of program, there is an unmatched quote
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

