from typing import List, Union, Tuple

from ..nodevisitor import NodeVisitor
from ..error import NameErr, TypeErr, SyntaxErr
from ..lexer.token import Token, TokenType

from .symboltable import SymbolTable
from .symboltable import TypeSymbol, VariableSymbol, FunctionSymbol


#
# Checks if all names are defined, and performs some minimal static type checking
# Inherits from NodeVisitor class, defined in locks/nodevisitor.py
#
class SemanticAnalyzer(NodeVisitor):
    def __init__(self) -> None:
        self._mainST: SymbolTable = None
        self._currentST: SymbolTable = None

        self._tempArgs = []

        self.hadError: bool = False
        self._errList: List[Union[NameErr, TypeErr, SyntaxErr]] = []

        # to check if break and continue are outside loop
        self._inLoop: bool = False 
    

    def getErrorList(self) -> List[Union[NameErr, TypeErr, SyntaxErr]]:
        return self._errList
    
    #
    # add error
    #
    def _error(self, typ: str, msg: str, tok: Token) -> None:
        self.hadError = True

        # name error
        if typ == 'n':
            self._errList.append(NameErr(msg, tok.line, tok.position))

        # type error
        elif typ == 't':
            self._errList.append(TypeErr(msg, tok.line))

        # syntax error
        elif typ == 's':
            # the only syntax error that can occur is continue
            #   or break outside loop
            self._errList.append(SyntaxErr(msg, tok.line))


    #
    # add builtin symbols to global symbol table
    #
    def _initMainST(self) -> None:
        self._mainST.add(TypeSymbol("int"))
        self._mainST.add(TypeSymbol("float"))
        self._mainST.add(TypeSymbol("double"))
        self._mainST.add(TypeSymbol("string"))

        builtinFunctions: List[str] = [
            "print", "println", "input",
            "len",
            "int", "str",
            "isinteger"
        ]

        for f in builtinFunctions:
            self._mainST.add(FunctionSymbol(f, None, [VariableSymbol("s")]))


    def visit_ProgramNode(self, node) -> None:
        self._mainST = SymbolTable("main")
        self._currentST = self._mainST
        self._initMainST()

        for d in node.declarationList:
            self.visit(d)


    def visit_VarDeclNode(self, node) -> None:
        if self._currentST.get(node.id.token.value, True) != None:
            self._error('n', f"duplicate definition of name '{node.id.token.value}'", node.id.token)
            return 

        self._currentST.add(VariableSymbol(node.id.token.value))

        if node.exprNode != None:
            typ, tok = self.visit(node.exprNode)
            if typ == "function":
                self._error('t', f"cannot assign function {tok.value} to variable", tok)


    def visit_AssignNode(self, node) -> None:
        self.visit(node.lvalue)
        typ, tok = self.visit(node.exprNode)

        if typ == "function":
            self._error('t', f"cannot assign function '{tok.value}' to variable", tok)


    def visit_IdentifierNode(self, node) -> Tuple[TokenType, TokenType]:
        if self._currentST.get(node.token.value) == None:
            self._error('n', f"name '{node.token.value}' not declared", node.token)
            return "identifier", node.token

        return self._currentST.get(node.token.value).type, node.token


    def visit_ArrayNode(self, node) -> Tuple[str, TokenType]:
        tok = None
        for e in node.elements:
            typ, tok = self.visit(e)

        return "array", tok


    def visit_ArrayAccessNode(self, node) -> Tuple[str, str]:
        typ, tok = self.visit(node.base)

        if typ != "array" and typ != "variable":
            self._error('t', f"Type '{typ}' is not subscriptable", tok)

        self.visit(node.index)
        return "variable", ""


    def visit_NumberNode(self, node) -> Tuple[str, TokenType]:
        return "number", node.token


    def visit_TrueNode(self, node) -> Tuple[str, TokenType]:
        return "boolean", node.token


    def visit_FalseNode(self, node) -> Tuple[str, TokenType]:
        return "boolean", node.token


    def visit_NilNode(self, node) -> Tuple[str, TokenType]:
        return "nil", node.token


    def visit_StringNode(self, node) -> Tuple[str, TokenType]:
        return "string", node.token


    def visit_AddNode(self, node) -> Tuple[TokenType, TokenType]:
        typl, tokl = self.visit(node.left)
        typr, tokr = self.visit(node.right)
        
        if typl not in ["variable", "call"] and typr not in ["variable", "call"]:
            if typr != typl:
                self._error('t', f"cannot add '{typl}' to '{typr}'", tokl)

        return typl, tokl  


    def visit_SubNode(self, node) -> Tuple[TokenType, TokenType]:
        typl, tokl = self.visit(node.left)
        typr, tokr = self.visit(node.right)
        
        if typl != "variable" and typr != "variable":
            if typr != typl:
                self._error('t', f"cannot subtract '{typr}' from '{typl}'", tokl)

        return typl, tokl


    def visit_MulNode(self, node) -> Tuple[TokenType, TokenType]:
        typl, tokl = self.visit(node.left)
        typr, tokr = self.visit(node.right)

        if typl != "variable" and typr != "variable":
            if typr != typl:
                self._error('t', f"cannot multiply '{typl}' by '{typr}'", tokl)

        return typl, tokl


    def visit_DivNode(self, node) -> Tuple[TokenType, TokenType]:
        typl, tokl = self.visit(node.left)
        typr, tokr = self.visit(node.right)

        if typl != "variable" and typr != "variable":
            if typr != typl:
                self._error('t', f"cannot divide '{typl}' by '{typr}'", tokl)

        return typl, tokl


    def visit_ModNode(self, node) -> Tuple[TokenType, TokenType]:
        typl, tokl = self.visit(node.left)
        typr, tokr = self.visit(node.right)

        if typl != "variable" and typr != "variable":
            if typr != typl:
                self._error('t', f"cannot modulo '{typl}' by '{typr}'", tokl)

        return typl, tokl


    def visit_EqualNode(self, node) -> Tuple[TokenType, TokenType]:
        typl, tokl = self.visit(node.left)
        self.visit(node.right)
        return typl, tokl


    def visit_NotEqualNode(self, node) -> Tuple[TokenType, TokenType]:
        typl, tokl = self.visit(node.left)
        self.visit(node.right)
        return typl, tokl


    def visit_GreaterThanNode(self, node) -> Tuple[TokenType, TokenType]:
        typl, tokl = self.visit(node.left)
        self.visit(node.right)
        return typl, tokl


    def visit_LessThanNode(self, node) -> Tuple[TokenType, TokenType]:
        typl, tokl = self.visit(node.left)
        self.visit(node.right)
        return typl, tokl


    def visit_GreaterThanEqualNode(self, node) -> Tuple[TokenType, TokenType]:
        typl, tokl = self.visit(node.left)
        self.visit(node.right)
        return typl, tokl


    def visit_LessThanEqualNode(self, node) -> Tuple[TokenType, TokenType]:
        typl, tokl = self.visit(node.left)
        self.visit(node.right)
        return typl, tokl


    def visit_AndNode(self, node) -> Tuple[TokenType, TokenType]:
        typl, tokl = self.visit(node.left)
        self.visit(node.right)
        return typl, tokl


    def visit_OrNode(self, node) -> Tuple[TokenType, TokenType]:
        typl, tokl = self.visit(node.left)
        self.visit(node.right)
        return typl, tokl


    def visit_NegationNode(self, node) -> Tuple[TokenType, TokenType]:
        typ, tok = self.visit(node.node)
        return typ, tok


    def visit_NotNode(self, node) -> Tuple[str, str]:
        self.visit(node.node)
        return "variable", ""

    
    def visit_IfNode(self, node) -> None:
        self.visit(node.ifBlock)
        for b in node.elsifBlocks:
            self.visit(b)
        if node.elseBlock != None:
            self.visit(node.elseBlock)


    def visit_ConditionalNode(self, node) -> None:
        self.visit(node.condition)
        self.visit(node.statement)


    def visit_WhileNode(self, node) -> None:
        self._inLoop = True
        self.visit(node.condition)
        self.visit(node.statement)
        self._inLoop = False


    def visit_BlockNode(self, node, isFunction = False) -> None:
        if isFunction:
            s: SymbolTable = SymbolTable("block")
            s.setEnclosingScope(self._currentST)

            for a in self._tempArgs:
                s.add(a)

            self._tempArgs = []
            self._currentST = s

            for st in node.stmtList:
                self.visit(st)

            self._currentST = s.getEnclosingScope()
        else:
            for st in node.stmtList:
                self.visit(st)


    def visit_ReturnNode(self, node) -> None:
        typ, tok = self.visit(node.expr)
        if typ == "function":
            self._error('t', f"Cannot return function '{tok.value}' from function", tok)


    def visit_ContinueNode(self, node) -> None:
        if not self._inLoop:
            self._error('s', "'continue' outside loop", node.tok)


    def visit_BreakNode(self, node) -> None:
        if not self._inLoop:
            self._error('s', "'break' outside loop", node.tok)


    def visit_FunDeclNode(self, node) -> None:
        if self._currentST.get(node.id.token.value) != None:
            self._error('n', f"duplicate definition of name '{node.id.token.value}'", node.id.token)
            return

        for a in node.paramList:
            self._tempArgs.append(VariableSymbol(a.value))

        self._currentST.add(FunctionSymbol(node.id.token.value, node.blockNode, self._tempArgs))
        
        self.visit_BlockNode(node.blockNode, True)


    def visit_FunctionCallNode(self, node) -> Tuple[str, TokenType]:
        t, tok = self.visit(node.nameNode)

        if t != "function":
            self._error('t', f"Symbol '{tok.value}' of type '{t}' is not callable", tok)
            return "call", tok

        argc: int = 0
        for a in node.argList:
            self.visit(a)
            argc += 1

        assert type(node.nameNode).__name__ == "IdentifierNode"
            
        count: int = len(self._currentST.get(node.nameNode.token.value).argSymbols)

        if count != argc:
            self._error('t', f"Expected {count} positional argument(s) for '{tok.value}', got {argc}", tok)

        return "call", tok

