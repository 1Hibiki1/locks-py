from ..nodevisitor import NodeVisitor
from ..parser import ast


class VisualizeAST(NodeVisitor):
    def __init__(self) -> None:
        self._pre = ''
        self._outputCode = ''
        self._ctr = 0


    def _emit(self, s: str) -> None:
        self._outputCode += s + '\n'


    def _genUniqueNumber(self) -> int:
        self._ctr += 1
        return self._ctr


    def getDot(self) -> str:
        conf = "digraph G{\n"
        conf += "nodesep=1.0\n"
        conf += "node [color=Red,fontname=Courier,shape=circle]\n"
        conf += "edge [color=Blue]\n"
        return conf + self._pre + '\n' + self._outputCode + '}'
 

    def visit_ProgramNode(self, node: ast.ProgramNode) -> None:
        for s in node.declarationList:
            self._emit(f"ProgramNode -> {self.visit(s)}")


    def visit_BlockNode(self, node: ast.BlockNode) -> None:
        l: str = f'block{self._genUniqueNumber()}'
        self._pre += f'{l} [label="block"];\n'
        for s in node.stmtList:
            self._emit(f"{l} -> {self.visit(s)}")
        return l
    

    def _visitPrimary(self, node, name: str, value: str) -> str:
        l: str = f'{name}{self._genUniqueNumber()}'
        self._pre += f'{l} [label="{value}"];\n'
        return l

    def visit_NumberNode(self, node) -> str:
        return self._visitPrimary(node, "num", str(node))

    def visit_TrueNode(self, node) -> str:
        return self._visitPrimary(node, "true", "true")

    def visit_FalseNode(self, node) -> str:
        return self._visitPrimary(node, "false", "false")

    def visit_NilNode(self, node) -> str:
        return self._visitPrimary(node, "nil", "nil")

    def visit_StringNode(self, node) -> str:
        return self._visitPrimary(node, "str", str(node))

    def visit_IdentifierNode(self, node) -> str:
        return self._visitPrimary(node, "id", str(node))

    def visit_ArrayNode(self, node) -> str:
        l: str = f'arr{self._genUniqueNumber()}'
        self._pre += f'{l} [label="array"];\n'

        for e in node.elements:
            self._emit(f'{l} -> {self.visit(e)}')

        return l

    def visit_ArrayAccessNode(self, node) -> str:
        return f'{self.visit(node.base)} -> {self.visit(node.index)}'


    def _visitBinOpNode(self, node, name: str) -> str:
        l: str = f'"{name}{self._genUniqueNumber()}"'
        self._pre += f'{l} [label="{name}"];\n'
        return f'{l} -> {self.visit(node.left)}\n{l} -> {self.visit(node.right)}'


    def visit_NegationNode(self, node) -> str:
        l: str = f'"unry{self._genUniqueNumber()}"'
        self._pre += f'{l} [label="-"];\n'
        return f'{l} -> {self.visit(node.node)}'

    def visit_NotNode(self, node) -> str:
        l: str = f'"not{self._genUniqueNumber()}"'
        self._pre += f'{l} [label="!"];\n'
        return f'{l} -> {self.visit(node.node)}'


    def visit_AddNode(self, node) -> str:
        return self._visitBinOpNode(node, "+")

    def visit_SubNode(self, node) -> str:
        return self._visitBinOpNode(node, "-")

    def visit_MulNode(self, node) -> str:
        return self._visitBinOpNode(node, "*")

    def visit_DivNode(self, node) -> str:
        return self._visitBinOpNode(node, "/")

    def visit_ModNode(self, node) -> str:
        return self._visitBinOpNode(node, "%")

    def visit_EqualNode(self, node) -> str:
        return self._visitBinOpNode(node, "==")

    def visit_NotEqualNode(self, node) -> str:
        return self._visitBinOpNode(node, "!=")

    def visit_GreaterThanNode(self, node) -> str:
        return self._visitBinOpNode(node, ">")

    def visit_LessThanNode(self, node) -> str:
        return self._visitBinOpNode(node, "<")

    def visit_GreaterThanEqualNode(self, node) -> str:
        return self._visitBinOpNode(node, ">=")

    def visit_LessThanEqualNode(self, node) -> str:
        return self._visitBinOpNode(node, "<=")

    def visit_AndNode(self, node) -> str:
        return self._visitBinOpNode(node, "and")

    def visit_OrNode(self, node) -> str:
        return self._visitBinOpNode(node, "or")


    def visit_VarDeclNode(self, node: ast.VarDeclNode) -> str:
        labl: str = f"vardec{self._genUniqueNumber()}"
        self._pre += f'{labl} [label="VarDecl"];\n'
        return f'{labl} -> {self.visit(node.id)}\n{labl} -> {self.visit(node.exprNode)}'

    def visit_AssignNode(self, node: ast.VarDeclNode) -> str:
        labl: str = f"assign{self._genUniqueNumber()}"
        self._pre += f'{labl} [label="Assign"];\n'
        return f'{labl} -> {self.visit(node.lvalue)}\n{labl} -> {self.visit(node.exprNode)}'

    def visit_FunDeclNode(self, node: ast.FunDeclNode) -> str:
        fnName: str = f'Function{self._genUniqueNumber()}'
        self._pre += f'{fnName} [label="Function {str(node.id)}"];\n'
        for s in node.blockNode.stmtList:
            self._emit(f'"{fnName}" -> {self.visit(s)}')
        return f'{fnName}'

    def visit_FunctionCallNode(self, node: ast.FunctionCallNode) -> str:
        callN: str = f'call{self._genUniqueNumber()}'
        self._pre += f'{callN} [label="call"];\n'
        output = f'{callN} -> {self.visit(node.nameNode)} -> '
        for a in node.argList:
            output += self.visit(a) + ','
        output = output[:-1]
        return output

    def visit_ReturnNode(self, node: ast.ReturnNode) -> str:
        labl: str = f'return{self._genUniqueNumber()}'
        self._pre += f'{labl} [label="return"];\n'
        return f'{labl} -> {self.visit(node.expr)}'

    def visit_ContinueNode(self, node: ast.ContinueNode) -> str:
        labl: str = f'continue{self._genUniqueNumber()}'
        self._pre += f'{labl} [label="continue"];\n'
        return labl

    def visit_BreakNode(self, node: ast.BreakNode) -> str:
        labl: str = f'br{self._genUniqueNumber()}'
        self._pre += f'{labl} [label="break"];\n'
        return labl

    def visit_IfNode(self, node: ast.IfNode) -> str:
        lif: str = f'if{self._genUniqueNumber()}'
        self._pre += f'{lif} [label="if"];\n'

        lcond: str = f'cond{self._genUniqueNumber()}'
        self._pre += f'{lcond} [label="condition"];\n'

        output = f'{lif}->{lcond}->{self.visit(node.ifBlock.condition)}\n'
        self._emit(f'{lif}->{self.visit(node.ifBlock.statement)}')

        for e in node.elsifBlocks:
            lelif: str = f'elif{self._genUniqueNumber()}'
            self._pre += f'{lelif} [label="elsif"];\n'

            lcond: str = f'cond{self._genUniqueNumber()}'
            self._pre += f'{lcond} [label="condition"];\n'

            output += f'{lelif}->{lcond}->{self.visit(e.condition)}\n'
            self._emit(f'{lif}->{lelif}->{self.visit(e.statement)}')

        if node.elseBlock:
            lelse: str = f'else{self._genUniqueNumber()}'
            self._pre += f'{lelse} [label="else"];\n'

            self._emit(f'{lif}->{lelse}->{self.visit(node.elseBlock)}')


        return output

    def visit_ConditionalNode(self, node: ast.IfNode) -> str:
        lcond: str = f'cond{self._genUniqueNumber()}'
        self._pre += f'{lcond} [label="condition"];\n'

    def visit_WhileNode(self, node: ast.IfNode) -> str:
        lwhile: str = f'while{self._genUniqueNumber()}'
        self._pre += f'{lwhile} [label="while"];\n'

        lcond: str = f'cond{self._genUniqueNumber()}'
        self._pre += f'{lcond} [label="condition"];\n'

        output = f'{lwhile}->{lcond}->{self.visit(node.condition)}\n'
        self._emit(f'{lwhile}->{self.visit(node.statement)}')

        return output
