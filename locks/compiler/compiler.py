from typing import List, Union, Dict

from ..parser.ast import ASTNode
from ..nodevisitor import NodeVisitor
from ..stdlib import builtinFunctionInfo


class Compiler(NodeVisitor):
    def __init__(self) -> None:
        self._constantPool: List[str] = []

        self._functions: Dict[str] = {
            "main": ""
        }
        self._currentFn: str = "main"

        self._globalVars: List[str] = []
        self._labelCtr: int = -1
        
        self._initCode()


    def getCode(self) -> str:
        cpStr: str = f"cpc {len(self._constantPool)}\n"
        for s in self._constantPool:
            cpStr += s + '\n'

        output: str = cpStr + '\n'  

        self._functions["main"] += "    END"
        for f in self._functions:
            output += self._functions[f] + '\n\n'

        return output


    def _initCode(self) -> None:
        self._functions[self._currentFn] += "fn main\nargc 0\n"


    def _emit(self, c: str, fmt: bool = True) -> None:
        if fmt:
            self._functions[self._currentFn] += f"    {c}\n"
        else:
            self._functions[self._currentFn] += f"    {c}\n"


    def _addConstant(self, c: str) -> None:
        self._constantPool.append(c)


    def _generateLabel(self) -> str:
        self._labelCtr += 1
        return f"L{self._labelCtr}"


    def visit_ProgramNode(self, node) -> None:
        for d in node.declarationList:
            self.visit(d)


    def visit_NumberNode(self, node) -> None:
        v: Union[int, float] = node.token.value
        if type(v).__name__ == "float":
            self._addConstant(f"d {v}")
            self._emit(f"LOAD_CONST {len(self._constantPool)-1}")
            return

        if v < 256:
            self._emit(f"BIPUSH {v}")
        else:
            self._addConstant(f"i {v}")
            self._emit(f"LOAD_CONST {len(self._constantPool)-1}")


    def visit_StringNode(self, node) -> None:
        self._addConstant(f's "{node.token.value}"')
        self._emit(f"LOAD_CONST {len(self._constantPool)-1}")


    def visit_NilNode(self, node) -> None:
        self._emit("LOAD_NIL")


    def visit_TrueNode(self, node) -> None:
        self._emit("LOAD_TRUE")


    def visit_FalseNode(self, node) -> None:
        self._emit("LOAD_FALSE")


    def visit_ArrayNode(self, node) -> None:
        for i in node.elements:
            self.visit(i)
        self._emit(f"BUILD_LIST {len(node.elements)}")


    def visit_IdentifierNode(self, node) -> None:
        if node.token.value in self._globalVars:
            self._emit(f"LOAD_GLOBAL {node.token.value}")
        else:
            self._emit(f"LOAD_LOCAL {node.token.value}")


    def visit_ArrayAccessNode(self, node) -> None:
        self.visit(node.base)
        self.visit(node.index)
        self._emit("BINARY_SUBSCR")


    def visit_NotNode(self, node) -> None:
        self.visit(node.node)
        self._emit("UNARY_NOT")


    def visit_NegationNode(self, node) -> None:
        if type(node.node).__name__ == "NumberNode":
            if type(node.node.token.value).__name__ == "float":
                self._addConstant(f"d -{node.node.token.value}")
            else:
                self._addConstant(f"i -{node.node.token.value}")
            self._emit(f"LOAD_CONST {len(self._constantPool)-1}")
        else:
            self.visit(node.node)
            self._emit("UNARY_NEGATIVE")


    def visit_AddNode(self, node) -> None:
        self.visit(node.left)
        self.visit(node.right)
        self._emit("BINARY_ADD")

    def visit_SubNode(self, node) -> None:
        self.visit(node.left)
        self.visit(node.right)
        self._emit("BINARY_SUBTRACT")

    def visit_MulNode(self, node) -> None:
        self.visit(node.left)
        self.visit(node.right)
        self._emit("BINARY_MULTIPLY")

    def visit_DivNode(self, node) -> None:
        self.visit(node.left)
        self.visit(node.right)
        self._emit("BINARY_DIVIDE")

    def visit_ModNode(self, node) -> None:
        self.visit(node.left)
        self.visit(node.right)
        self._emit("BINARY_MODULO")


    def visit_VarDeclNode(self, node) -> None:
        if node.exprNode != None:
            self.visit(node.exprNode)
        else:
            self._emit("LOAD_NIL")

        if self._currentFn == "main":
            self._globalVars.append(node.id.token.value)

        self._emit(f"STORE_LOCAL {node.id.token.value}")


    def visit_AssignNode(self, node) -> None:
        self.visit(node.exprNode)

        if type(node.lvalue).__name__ == "IdentifierNode":
            n: str = node.lvalue.token.value
            if n in self._globalVars:
                self._emit(f"STORE_GLOBAL {n}")
            else:
                self._emit(f"STORE_LOCAL {n}")
        elif type(node.lvalue).__name__ == "ArrayAccessNode":
            self.visit(node.lvalue.base)
            self.visit(node.lvalue.index)
            self._emit("STORE_SUBSCR")


    def visit_BlockNode(self, node, startLabl: str = None, endLabl: str = None) -> None:
        for s in node.stmtList:
            if type(s).__name__ == "ContinueNode":
                self._emit(f"GOTO {startLabl}")
                continue

            if type(s).__name__ == "BreakNode":
                self._emit(f"GOTO {endLabl}")
                continue
            
            if type(s).__name__ == "IfNode":
                self.visit_IfNode(s, startLabl, endLabl)
            else:
                self.visit(s)


    def visit_EqualNode(self, node) -> None:
        self.visit(node.left)
        self.visit(node.right)
        self._emit("CMPEQ")

    def visit_NotEqualNode(self, node) -> None:
        self.visit(node.left)
        self.visit(node.right)
        self._emit("CMPNE")

    def visit_GreaterThanNode(self, node) -> None:
        self.visit(node.left)
        self.visit(node.right)
        self._emit("CMPGT")

    def visit_LessThanNode(self, node) -> None:
        self.visit(node.left)
        self.visit(node.right)
        self._emit("CMPLT")

    def visit_GreaterThanEqualNode(self, node) -> None:
        self.visit(node.left)
        self.visit(node.right)
        self._emit("CMPGE")

    def visit_LessThanEqualNode(self, node) -> None:
        self.visit(node.left)
        self.visit(node.right)
        self._emit("CMPLE")

    def visit_AndNode(self, node) -> str:
        self.visit(node.left)
        self.visit(node.right)
        self._emit("BINARY_AND")

    def visit_OrNode(self, node) -> str:
        self.visit(node.left)
        self.visit(node.right)
        self._emit("BINARY_OR")


    def visit_ConditionalNode(self, node, startLabl: str = None, endLabl: str = None) -> str:
        next: str = self._generateLabel()
        n = self.visit(node.condition)
        if not n:
            self._emit(f"POP_JMP_IF_FALSE {next}")

        
        if type(node.statement).__name__ == "ContinueNode":
            assert startLabl != None
            self._emit(f"GOTO {startLabl}")

        elif type(node.statement).__name__ == "BreakNode":
            assert endLabl != None
            self._emit(f"GOTO {endLabl}")

        elif type(node.statement).__name__ == "BlockNode":
            self.visit_BlockNode(node.statement, startLabl, endLabl)

        else:
            self.visit(node.statement)

        if n:
            return n

        return next


    def visit_IfNode(self, node, startLabl: str = None, endLabl: str = None) -> None:
        endifLabl: str = self._generateLabel()

        skipIfLabl: str = self.visit_ConditionalNode(node.ifBlock, startLabl, endLabl)
        self._emit(f"GOTO {endifLabl}")
        self._emit(f".{skipIfLabl}")

        for cs in node.elsifBlocks:
            skipElsifLabl: str = self.visit_ConditionalNode(cs, startLabl, endLabl)
            self._emit(f"GOTO {endifLabl}")
            self._emit(f".{skipElsifLabl}")

        if node.elseBlock:
            if type(node.elseBlock).__name__ == "ContinueNode":
                assert startLabl != None
                self._emit(f"GOTO {startLabl}")

            elif type(node.elseBlock).__name__ == "BreakNode":
                assert startLabl != None
                self._emit(f"GOTO {endLabl}")

            elif type(node.elseBlock).__name__ == "BlockNode":
                self.visit_BlockNode(node.elseBlock, startLabl, endLabl)

            else:
                self.visit(node.elseBlock)

        self._emit(f".{endifLabl}")


    def visit_WhileNode(self, node) -> None:
        loop: str = self._generateLabel()
        endLoop: str = self._generateLabel()

        self._emit(f".{loop}")
        self.visit(node.condition)
        self._emit(f"POP_JMP_IF_FALSE {endLoop}")

        if type(node.statement).__name__ in ["BlockNode", "IfNode"]:
            self.visit_BlockNode(node.statement, loop, endLoop)
        else:
            self.visit(node.statement)

        self._emit(f"GOTO {loop}")

        self._emit(f".{endLoop}")


    def visit_ReturnNode(self, node) -> None:
        self.visit(node.expr)
        self._emit("RETURN_VALUE")


    def visit_FunDeclNode(self, node) -> None:
        oldFn: str = self._currentFn
        self._currentFn = node.id.token.value

        self._functions[self._currentFn] = f"fn {self._currentFn}\nargc {len(node.paramList)}\n"

        for a in node.paramList:
            self._emit(f"STORE_LOCAL {a.value}")
        self.visit(node.blockNode)

        if "RETURN_VALUE" not in self._functions[self._currentFn]:
            self._emit("LOAD_NIL")
            self._emit("RETURN_VALUE")

        self._currentFn = oldFn


    def visit_FunctionCallNode(self, node) -> None:

        for a in node.argList:
            self.visit(a)

        if str(node.nameNode) in builtinFunctionInfo:
            self._emit(f"CALL_NATIVE {builtinFunctionInfo[node.nameNode.token.value][0]}")
            return

        self._emit(f"CALL_FUNCTION {node.nameNode.token.value}")
        
