from ..lexer.token import Token
from typing import List, Union

# base class for all nodes
class ASTNode:
    def __repr__(self) -> str:
        return self.__str__()


class ProgramNode(ASTNode):
    def __init__(self, declList: List[ASTNode]) -> None:
        self.declarationList: List[ASTNode] = declList

    def __str__(self) -> str:
        output: str = ''
        for d in self.declarationList:
            output += str(d) + '\n'
        return output


class BlockNode(ASTNode):
    def __init__(self, stmtlist: List[ASTNode]) -> None:
        self.stmtList: List[ASTNode] = stmtlist

    def __str__(self) -> str:
        output: str = '{\n'
        for s in self.stmtList:
            output += str(s) + '\n'
        output += '}'
        return output


# Declaration Nodes

class VarDeclNode(ASTNode):
    def __init__(self, id: Token, exprNode: ASTNode=None) -> None:
        self.id: IdentifierNode = id
        self.exprNode: ASTNode = exprNode

    def __str__(self) -> str:
        return f"vardecl: {str(self.id)} = {str(self.exprNode)}"


class FunDeclNode(ASTNode):
    def __init__(self, id: Token, pList: List[Token], blk: BlockNode) -> None:
        self.id: IdentifierNode = id
        self.paramList: List[Token] = pList
        self.blockNode: BlockNode = blk

    def __str__(self) -> str:
        output = f"func {self.id}("
        for p in self.paramList:
            output += str(p.value) + ','
        output += ')' + str(self.blockNode)
        return output


# Statement Nodes

class AssignNode(ASTNode):
    def __init__(self, id: Token, exprNode: ASTNode) -> None:
        self.lvalue: Union[IdentifierNode, ArrayAccessNode] = id
        self.exprNode: ASTNode = exprNode

    def __str__(self) -> str:
        return f"assign: {str(self.lvalue)} = {str(self.exprNode)}"


class ConditionalNode(ASTNode):
    def __init__(self, cond: ASTNode, stmt: ASTNode) -> None:
        self.condition: ASTNode =  cond
        self.statement: ASTNode = stmt

    def __str__(self) -> str:
        return f"{str(self.condition)} {str(self.statement)}"


class IfNode(ASTNode):
    def __init__(self, ifBlock: ConditionalNode, elsifBlocks: List[ConditionalNode], elseBlock: ASTNode) -> None:
        self.ifBlock: ConditionalNode = ifBlock
        self.elsifBlocks: List[ConditionalNode] = elsifBlocks
        self.elseBlock: ASTNode = elseBlock

    def __str__(self) -> str:
        output = f"if{str(self.ifBlock)}\n"
        for e in self.elsifBlocks:
            output += "elsif" + str(e) + '\n'
        output += f"else {str(self.elseBlock)}"
        return output


class ReturnNode(ASTNode):
    def __init__(self, exprNode: ASTNode, l: int) -> None:
        self.expr: ASTNode = exprNode
        self.line: int = l

    def __str__(self) -> str:
        return f"return: {str(self.expr)}"


class ContinueNode(ASTNode):
    def __init__(self, t: Token) -> None:
        self.tok = t

    def __str__(self) -> str:
        return "continue"


class BreakNode(ASTNode):
    def __init__(self, t: Token) -> None:
        self.tok = t

    def __str__(self) -> str:
        return "break"


class WhileNode(ConditionalNode):
    def __init__(self, cond: ASTNode, stmt: ASTNode) -> None:
        super().__init__(cond, stmt)

    def __str__(self) -> str:
        return "while:" + super().__str__()


# Binary operation nodes

class BinOpNode(ASTNode):
    def __init__(self, op: str, l: ASTNode, r: ASTNode):
        self.op: str = op
        self.left: ASTNode = l
        self.right: ASTNode = r

    def __str__(self):
        return f"({str(self.left)} {self.op} {str(self.right)})"


class OrNode(BinOpNode):
    def __init__(self, l: ASTNode, r: ASTNode):
        super().__init__('or', l, r)


class AndNode(BinOpNode):
    def __init__(self, l: ASTNode, r: ASTNode):
        super().__init__('and', l, r)


class EqualNode(BinOpNode):
    def __init__(self, l: ASTNode, r: ASTNode):
        super().__init__('==', l, r)


class NotEqualNode(BinOpNode):
    def __init__(self, l: ASTNode, r: ASTNode):
        super().__init__('!=', l, r)


class GreaterThanNode(BinOpNode):
    def __init__(self, l: ASTNode, r: ASTNode):
        super().__init__('>', l, r)


class GreaterThanEqualNode(BinOpNode):
    def __init__(self, l: ASTNode, r: ASTNode):
        super().__init__('>=', l, r)


class LessThanNode(BinOpNode):
    def __init__(self, l: ASTNode, r: ASTNode):
        super().__init__('<', l, r)


class LessThanEqualNode(BinOpNode):
    def __init__(self, l: ASTNode, r: ASTNode):
        super().__init__('<=', l, r)    


class AddNode(BinOpNode):
    def __init__(self, l: ASTNode, r: ASTNode):
        super().__init__('+', l, r)


class SubNode(BinOpNode):
    def __init__(self, l: ASTNode, r: ASTNode):
        super().__init__('-', l, r)


class MulNode(BinOpNode):
    def __init__(self, l: ASTNode, r: ASTNode):
        super().__init__('*', l, r)


class DivNode(BinOpNode):
    def __init__(self, l: ASTNode, r: ASTNode):
        super().__init__('/', l, r)


class ModNode(BinOpNode):
    def __init__(self, l: ASTNode, r: ASTNode):
        super().__init__('%', l, r)


# unary operation nodes

class UnaryOpNode(ASTNode):
    def __init__(self, op: str, n: ASTNode) -> None:
        self.op: str = op
        self.node: ASTNode = n

    def __str__(self):
        return f"({self.op} {str(self.node)})"


class NotNode(UnaryOpNode):
    def __init__(self, n: ASTNode) -> None:
        super().__init__('!', n)


class NegationNode(UnaryOpNode):
    def __init__(self, n: ASTNode) -> None:
        super().__init__('-', n)


# function call

class FunctionCallNode(ASTNode):
    def __init__(self, name: ASTNode, arg: List[ASTNode]) -> None:
        self.nameNode: ASTNode = name
        self.argList: List[ASTNode] = arg

    def __str__(self) -> str:
        output = f"call: {str(self.nameNode)} "
        for a in self.argList:
            output += str(a) + ' '
        return output


# Primary nodes

class PrimaryNode(ASTNode):
    def __init__(self, tok: Token) -> None:
        self.token: Token = tok

    def __str__(self) -> str:
        return f"{self.token.value}"


class TrueNode(PrimaryNode):
    def __init__(self, tok: Token) -> None:
        super().__init__(tok)


class FalseNode(PrimaryNode):
    def __init__(self, tok: Token) -> None:
        super().__init__(tok)


class NilNode(PrimaryNode):
    def __init__(self, tok: Token) -> None:
        super().__init__(tok)


class NumberNode(PrimaryNode):
    def __init__(self, tok: Token) -> None:
        super().__init__(tok)


class StringNode(PrimaryNode):
    def __init__(self, tok: Token) -> None:
        super().__init__(tok)


class IdentifierNode(PrimaryNode):
    def __init__(self, tok: Token) -> None:
        super().__init__(tok)


class ArrayNode(ASTNode):
    def __init__(self, l: List[ASTNode]) -> None:
        self.elements: List[ASTNode] = l

    def __str__(self) -> str:
        output = f"arr: ["
        for a in self.elements:
            output += str(a) + ', '
        output = output.strip()[:-1]
        output += ']'
        return output


class ArrayAccessNode(ASTNode):
    def __init__(self, b: ASTNode, idx: ASTNode) -> None:
        self.base: ASTNode = b
        self.index: ASTNode = idx

    def __str__(self) -> str:
        return f"(aac: {str(self.base)}[{str(self.index)}])"

