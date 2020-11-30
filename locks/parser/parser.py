from ..lexer.token import Token, TokenType
from ..error import SyntaxErr
from .ast import *
from typing import List

#
# Takes a list of tokens, generates an AST from them. 
#  AST nodes are defined in ast.py
#
class Parser:
    def __init__(self, tokList: List[Token]) -> None:
        self._tokList: List[Token] = tokList

        self._idx: int = 0  # index of token that is currently being processed
        self._curToken: Token = tokList[0]

        self.hadError: bool = False
        self._errList: List[SyntaxErr] = []

    #
    # main parser method that returns the constructed ast
    #
    def getAST(self) -> ASTNode:
        return self._program()

    #
    # move forward by 'advBy' steps
    #
    def _advance(self, advBy: int=1) -> None:
        self._idx += advBy

        if self._idx >= len(self._tokList):
            self._curToken = self._tokList[-1]
            return

        self._curToken = self._tokList[self._idx]


    #
    # Get next token without advancing
    #
    def _peek(self) -> Token:
        if self._idx+1 >= len(self._tokList):
            return self._tokList[-1]
        return self._tokList[self._idx+1]


    #
    # Get previous token
    #
    def _prevToken(self) -> Token:
        return self._tokList[self._idx-1]


    #
    # Adds an error to the error list, and synchronizes parser
    #
    def _error(self, msg: str) -> None:
        self.hadError = True
        self._errList.append(
            SyntaxErr(msg, self._curToken.line, self._curToken.position)
        )
        self._sync()


    # 
    # sync will attempt to discart tokens until the next statement if there is
    #   a syntax error, so that the parser can continue and (hopefully) report
    #   as many errors possible at once
    #
    def _sync(self) -> None:
        while self._curToken.type not in [
            TokenType.SEMI,
            TokenType.EOF,
            TokenType.VAR,
            TokenType.FUNCTION,
            TokenType.R_PAREN,
            TokenType.R_CURLY,
            TokenType.RETURN
        ]:
            self._advance()


    #
    # 'consumes' current token, adds and error if the token is not of type 'tt'
    #
    def _consume(self, tt: TokenType) -> None:
        if self._curToken.type != tt:          
            self.hadError = True

            # missing semi colon
            if tt == TokenType.SEMI:
                self._errList.append(
                    SyntaxErr(f"Expected ';'", self._prevToken().line, self._prevToken().position)
                )

            # unexpected token
            else:
                if self._curToken.value != '':
                    self._errList.append(
                        SyntaxErr(f"Expected {tt.value}, got '{self._curToken.value}'", self._curToken.line, self._curToken.position)
                    )
                else:
                    self._errList.append(
                        SyntaxErr(f"Expected {tt.value}", self._curToken.line, self._curToken.position)
                    )
            self._sync()
            
        self._advance()


    def getError(self) -> List[SyntaxErr]:
        return self._errList


    #######################################################
    # Methods that construct the ast                      #
    #  based on grammar defined in locks/spec/grammar.txt #
    #######################################################

    def _program(self) -> ProgramNode:
        declList: List[ASTNode] = []
        
        while self._curToken.type != TokenType.EOF:
            declList.append(self._declaration())
            
        return ProgramNode(declList)


    #------------Declarations------------#

    def _declaration(self) -> ASTNode:
        if self._curToken.type == TokenType.VAR:
            return self._varDecl()
        elif self._curToken.type == TokenType.FUNCTION:
            return self._funDecl()
        else:
            return self._statement()


    def _varDecl(self) -> ASTNode:
        self._consume(TokenType.VAR)
        id: Token = self._curToken
        exprNode: ASTNode = None
        self._consume(TokenType.ID)
        
        if self._curToken.type == TokenType.ASSIGN:
            self._consume(TokenType.ASSIGN)
            exprNode = self._expression()
        
        self._consume(TokenType.SEMI)
        return VarDeclNode(IdentifierNode(id), exprNode)


    def _funDecl(self) -> ASTNode:
        self._consume(TokenType.FUNCTION)

        id: Token = self._curToken
        self._consume(TokenType.ID)

        self._consume(TokenType.L_PAREN)

        params: List[Token] = []
        if self._curToken.type != TokenType.R_PAREN:
            params = self._parameters()

        self._consume(TokenType.R_PAREN)

        bl: BlockNode = self._block()
        
        return FunDeclNode(IdentifierNode(id), params, bl)


    #------------Statements------------#

    def _statement(self) -> ASTNode:
        if self._curToken.type == TokenType.ID:
            stmt: ASTNode = None
            if self._peek().type in [TokenType.ASSIGN,  TokenType.L_SQUARE]:
                stmt = self._assignStmt()
            else:
                stmt = self._exprStmt()
            return stmt

        elif self._curToken.type == TokenType.IF:
            return self._ifStmt()

        elif self._curToken.type == TokenType.L_CURLY:
            return self._block()

        elif self._curToken.type == TokenType.RETURN:
            return self._return()

        elif self._curToken.type == TokenType.CONTINUE:
            return self._continue()

        elif self._curToken.type == TokenType.BREAK:
            return self._break()

        elif self._curToken.type == TokenType.WHILE:
            return self._while()

        elif self._curToken.type == TokenType.FOR:
            return self._for()

        else:
            return self._exprStmt()
        

    def _exprStmt(self) -> ASTNode:
        stmt: ASTNode = self._expression()
        self._consume(TokenType.SEMI)
        return stmt


    def _assignStmt(self) -> AssignNode:
        id: Token = self._curToken

        # check for subscript
        aac: ArrayAccessNode = None
        if self._peek().type == TokenType.L_SQUARE:
            aac = self._array_access()
        else:
            self._consume(TokenType.ID)

        self._consume(TokenType.ASSIGN)

        exprNode: ASTNode = self._expression()
        
        self._consume(TokenType.SEMI)
        if aac != None:
            return AssignNode(aac, exprNode)
        
        return AssignNode(IdentifierNode(id), exprNode)
    
    
    def _ifStmt(self) -> IfNode:
        # if
        self._consume(TokenType.IF)
        self._consume(TokenType.L_PAREN)

        ifCond: ASTNode = self._expression()

        self._consume(TokenType.R_PAREN)

        ifBlk: BlockNode = self._statement()
        ifst: ConditionalNode = ConditionalNode(ifCond, ifBlk)

        # elsif 
        elsifArr: List[ConditionalNode] = []

        while self._curToken.type == TokenType.ELSEIF:
            self._consume(TokenType.ELSEIF)
            self._consume(TokenType.L_PAREN)

            elifCond = self._expression()

            self._consume(TokenType.R_PAREN)

            elifBlk: BlockNode = self._statement()
            elsifArr.append(ConditionalNode(elifCond, elifBlk))

        # else
        elseSt: BlockNode = None

        if self._curToken.type == TokenType.ELSE:
            self._consume(TokenType.ELSE)
            elseSt = self._statement()

        return IfNode(ifst, elsifArr, elseSt)


    def _return(self) -> ReturnNode:
        t: Token = self._curToken
        self._consume(TokenType.RETURN)

        expr: ASTNode = None

        if self._curToken.type != TokenType.SEMI:
            expr = self._expression()

        self._consume(TokenType.SEMI)

        if expr == None:
            expr = NilNode(t)

        return ReturnNode(expr, t.line)


    def _continue(self) -> ContinueNode:
        t: Token = self._curToken
        self._consume(TokenType.CONTINUE)
        self._consume(TokenType.SEMI)
        return ContinueNode(t)


    def _break(self) -> BreakNode:
        t: Token = self._curToken
        self._consume(TokenType.BREAK)
        self._consume(TokenType.SEMI)
        return BreakNode(t)


    def _while(self) -> WhileNode:
        self._consume(TokenType.WHILE)
        self._consume(TokenType.L_PAREN)

        cond = self._expression()

        self._consume(TokenType.R_PAREN)

        blk: ASTNode = self._statement()

        return WhileNode(cond, blk)

    #
    # for loop is just syntactic sugar for while with a counter
    #
    def _for(self) -> BlockNode:
        self._consume(TokenType.FOR)
        self._consume(TokenType.L_PAREN)

        # first statement/ declaration inside the for loop parentheses
        decl: ASTNode = None
        if self._curToken.type == TokenType.VAR:
            decl = self._varDecl()
        elif self._curToken.type == TokenType.SEMI:
            self._advance()
        elif self._curToken.type == TokenType.ID:
            decl = self._assignStmt()
        else:
            decl = self._exprStmt()

        # second statement inside the for loop parentheses
        cond: ASTNode = None
        if self._curToken.type != TokenType.SEMI:
            cond = self._expression()
        self._consume(TokenType.SEMI)
        
        # third statement inside the for loop parentheses
        update: ASTNode = None
        if self._curToken.type != TokenType.R_PAREN:
            id = self._curToken
            self._consume(TokenType.ID)
            self._consume(TokenType.ASSIGN)
            expr = self._expression()
            update = AssignNode(IdentifierNode(id), expr)
            
        self._consume(TokenType.R_PAREN)

        # desugar for loop
        stmtlist: List[ASTNode] = []

        if decl != None:
            stmtlist.append(decl)

        blk: ASTNode = self._statement()
        if update != None:
            if isinstance(blk, BlockNode):
                blk.stmtList.append(update)
            else:
                blk = BlockNode([blk, update])

        w: WhileNode = None
        if cond != None:
            w = WhileNode(cond, blk)
        else:
            dummyTrue: TrueNode = TrueNode(Token(TokenType.TRUE, "true", 0, 0))
            w = WhileNode(dummyTrue, blk)

        stmtlist.append(w)

        return BlockNode(stmtlist)


    def _parameters(self) -> List[Token]:
        paramList: List[Token] = [self._curToken]
        self._consume(TokenType.ID)

        while self._curToken.type == TokenType.COMMA:
            self._advance()
            paramList.append(self._curToken)
            self._consume(TokenType.ID)

        return paramList


    def _block(self) -> BlockNode:
        self._consume(TokenType.L_CURLY)
        stmtList: List[ASTNode] = []

        while self._curToken.type not in [
            TokenType.R_CURLY, 
            TokenType.EOF
        ]:
            stmtList.append(self._declaration())
            
        self._consume(TokenType.R_CURLY)
        
        return BlockNode(stmtList)


    #------------Expressions------------#

    def _expression(self) -> ASTNode:
        return self._logicOr()


    def _logicOr(self) -> ASTNode:
        l: ASTNode = self._logicAnd()

        while self._curToken.type == TokenType.OR:
            self._advance()
            r: ASTNode = self._logicAnd()
            l = OrNode(l, r)

        return l


    def _logicAnd(self) -> ASTNode:
        l: ASTNode = self._equality()

        while self._curToken.type == TokenType.AND:
            self._advance()
            r: ASTNode = self._equality()
            l = AndNode(l, r)

        return l


    def _equality(self) -> ASTNode:
        l: ASTNode = self._comparison()

        while self._curToken.type in [
            TokenType.EQUAL, 
            TokenType.NOT_EQUAL
        ]:
            opType = self._curToken.type
            self._advance()
            r: ASTNode = self._comparison()

            if opType == TokenType.EQUAL:
                l = EqualNode(l, r)
            elif opType == TokenType.NOT_EQUAL:
                l = NotEqualNode(l, r)

        return l


    def _comparison(self) -> ASTNode:
        l: ASTNode = self._term()

        while self._curToken.type in [
            TokenType.GREATER_THAN, 
            TokenType.GREATER_THAN_EQ,
            TokenType.LESS_THAN,
            TokenType.LESS_THAN_EQ
        ]:
            opType = self._curToken.type
            self._advance()
            r: ASTNode = self._term()

            if opType == TokenType.GREATER_THAN:
                l = GreaterThanNode(l, r)
            elif opType == TokenType.GREATER_THAN_EQ:
                l = GreaterThanEqualNode(l, r)
            elif opType == TokenType.LESS_THAN:
                l = LessThanNode(l, r)
            elif opType == TokenType.LESS_THAN_EQ:
                l = LessThanEqualNode(l, r)

        return l


    def _term(self) -> ASTNode:
        l: ASTNode = self._factor()

        while self._curToken.type in [
            TokenType.PLUS, 
            TokenType.MINUS
        ]:
            opType = self._curToken.type
            self._advance()
            
            r: ASTNode = self._factor()
            
            if opType == TokenType.PLUS:
                l = AddNode(l, r)
            elif opType == TokenType.MINUS:
                l = SubNode(l, r)

        return l


    def _factor(self) -> ASTNode:
        l: ASTNode = self._unary()
        
        while self._curToken.type in [
            TokenType.MUL, 
            TokenType.DIV,
            TokenType.MOD
        ]:
            opType = self._curToken.type
            self._advance()
            r: ASTNode = self._unary()
            
            if opType == TokenType.MUL:
                l = MulNode(l, r)
            elif opType == TokenType.DIV:
                l = DivNode(l, r)
            elif opType == TokenType.MOD:
                l = ModNode(l, r)

        return l


    def _unary(self) -> ASTNode:
        n: ASTNode = None

        if self._curToken.type == TokenType.NOT:
            self._advance()
            n = NotNode(self._unary())
        elif self._curToken.type == TokenType.MINUS:
            self._advance()
            n = NegationNode(self._unary())
        else:
            n = self._array_access()

        return n


    def _array_access(self) -> ASTNode:
        p: ASTNode = self._call()
        
        while self._curToken.type == TokenType.L_SQUARE:
            self._advance()
            expr = self._expression()
            self._consume(TokenType.R_SQUARE)
            p = ArrayAccessNode(p, expr)
        
        return p


    def _call(self) -> ASTNode:
        p: ASTNode = self._primary()

        if self._curToken.type == TokenType.L_PAREN:
            self._advance()
            arg: List[ASTNode] = []

            if self._curToken.type != TokenType.R_PAREN:
                arg = self._arguments()
                
            self._consume(TokenType.R_PAREN)
            p = FunctionCallNode(p, arg)
        
        return p


    def _primary(self) -> ASTNode:
        if self._curToken.type == TokenType.TRUE:
            t: Token = self._curToken
            self._advance()
            return TrueNode(t)

        elif self._curToken.type == TokenType.FALSE:
            t: Token = self._curToken
            self._advance()
            return FalseNode(t)

        elif self._curToken.type == TokenType.NIL:
            t: Token = self._curToken
            self._advance()
            return NilNode(t)

        elif self._curToken.type == TokenType.NUMBER:
            t: Token = self._curToken
            self._advance()
            return NumberNode(t)

        elif self._curToken.type == TokenType.STRING:
            t: Token = self._curToken
            self._advance()
            return StringNode(t)

        elif self._curToken.type == TokenType.ID:
            id: Token = self._curToken
            self._advance()
            return IdentifierNode(id)

        elif self._curToken.type == TokenType.L_PAREN:
            self._advance()
            exp = self._expression()
            self._consume(TokenType.R_PAREN)
            return exp

        elif self._curToken.type == TokenType.L_SQUARE:
            self._advance()

            if self._curToken.type == TokenType.R_SQUARE:
                self._consume(TokenType.R_SQUARE)
                return ArrayNode([])

            a = ArrayNode(self._arguments())
            self._consume(TokenType.R_SQUARE)

            return a

        else:
            self._error("Expected expression")


    def _arguments(self) -> List[ASTNode]:
        argList: List[ASTNode] = [self._expression()]

        while self._curToken.type == TokenType.COMMA:
            self._advance()
            argList.append(self._expression())
            
        return argList

