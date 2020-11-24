from ..nodevisitor import NodeVisitor

from .memory import CallStack, ActivationRecord, ARType
from .types import LObject, Number, Nil, Array, Boolean, String, Function
from .stdlib import builtinFunctionTable

from ..error import TypeErr, ZeroDivErr, SyntaxErr

class Interpeter(NodeVisitor):
    def __init__(self) -> None:
        self._curFrame: ActivationRecord = None
        self._callStack: CallStack = CallStack()

    
    def _getVarType(self, el: str) -> str:
        return type(self._curFrame[el]).__name__

    def _getObjType(self, el: LObject) -> str:
        return type(el).__name__


    def _isTruthy(self, obj: LObject) -> bool:
        if self._getObjType(obj) == "Number":
            if obj.value == 0:
                return False
            return True

        elif self._getObjType(obj) == "String":
            if len(obj.value) == 0:
                return False
            return True

        elif self._getObjType(obj) == "Nil":
            return False

        elif self._getObjType(obj) == "Boolean":
            if obj.value == "false":
                return False
            return True

        elif self._getObjType(obj) == "Array":
            if obj.getLen() == 0:
                return False
            return True

        # control shouldn't reach this point
        return False

    #
    # Visit methods
    #
    def visit_ProgramNode(self, node) -> None:
        # create and push main frame
        mainFarame = ActivationRecord(ARType.MAIN)
        self._callStack.push(mainFarame)
        self._curFrame = mainFarame

        # execute the code
        for d in node.declarationList:
            self.visit(d)

        # done, pop main frame
        self._callStack.pop()
            
    
    def visit_NumberNode(self, node) -> None:
        return Number(node.token.value)

    def visit_NilNode(self, node) -> None:
        return Nil()

    def visit_TrueNode(self, node) -> None:
        return Boolean("true")

    def visit_FalseNode(self, node) -> None:
        return Boolean("false")

    def visit_StringNode(self, node) -> None:
        return String(node.token.value)

    def visit_ArrayNode(self, node) -> None:
        arr: Array = Array()
        for e in node.elements:
            arr.addEl(self.visit(e))
        return arr


    def visit_ArrayAccessNode(self, node) -> None:
        arrObj = self.visit(node.base)

        # check if variable actually holds an array
        if type(arrObj).__name__ != "Array":
            raise TypeErr(f"Type '{type(arrObj).__name__}' is not subscriptable", node.base.token.line)

        idx = self.visit(node.index)  # array index

        # check if index is an integer
        if type(idx).__name__ != "Number":
            raise TypeErr(f"Array indices must be integers, not '{type(idx).__name__}'", node.base.token.line)

        if type(idx.value).__name__ == "float":
            raise TypeErr(f"Array indices must be integers, not float", node.base.token.line)

        # everything ok
        return arrObj.getEL(idx.value)


    def visit_IdentifierNode(self, node) -> None:
        return self._curFrame.get(node.token.value)
    

    def visit_VarDeclNode(self, node) -> None:
        val = self.visit(node.exprNode) if node.exprNode else Nil()
        self._curFrame[node.id.token.value] = val

    def visit_AssignNode(self, node) -> None:
        val = self.visit(node.exprNode)

        if type(node.lvalue).__name__ == "ArrayAccessNode":
            arrObj = self._curFrame[node.lvalue.base.token.value]
            # check if variable holds an array
            if type(arrObj).__name__ != "Array":
                raise TypeErr(f"Type '{type(arrObj).__name__}' is not subscriptable", node.lvalue.base.token.line)

            idx = self.visit(node.lvalue.index)
            # check if index is an integer
            if type(idx).__name__ != "Number":
                raise TypeErr(f"Array indices must be integers, not '{type(idx).__name__}'", node.lvalue.base.token.line)

            if type(idx.value).__name__ == "float":
                raise TypeErr(f"Array indices must be integers, not float", node.base.token.line)
            
            arrObj.setEL(val, idx.value)

        elif type(node.lvalue).__name__ == "IdentifierNode":
            self._curFrame[node.lvalue.token.value] = val


    # arithmetic nodes
    def visit_NegationNode(self, node) -> Number:
        v = self.visit(node.node)

        if self._getObjType(v) != "Number":
            raise TypeErr(f"Cannot negate {self._getObjType(v)}", node.node.token.line)

        return Number(-v.value)

    def visit_AddNode(self, node) -> Number:
        l = self.visit(node.left)
        r = self.visit(node.right)

        # concat strings
        if self._getObjType(l) == "String":
            if self._getObjType(r) != "String":
                raise TypeErr(f"Cannot add {self._getObjType(r)} to String", node.left.token.line)
            return String(l.value + r.value)

        # check type for numbers
        elif self._getObjType(l) == "Number":
            if self._getObjType(r) != "Number":
                raise TypeErr(f"Cannot add {self._getObjType(r)} to Number", node.left.token.line)
            return Number(l.value + r.value)
        
        # addition is not defined for any other type
        else:
            raise TypeErr(f"Addition not defined for type '{self._getObjType(l)}'", node.left.token.line)


    def visit_SubNode(self, node) -> Number:
        l = self.visit(node.left)
        r = self.visit(node.right)

        # check if both l and r are numbers
        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Cannot subtract {self._getObjType(r)} from {self._getObjType(l)}", node.left.token.line)

        return Number(l.value - r.value)


    def visit_DivNode(self, node) -> Number:
        l = self.visit(node.left)
        r = self.visit(node.right)

        # check if both l and r are numbers
        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Cannot divide {self._getObjType(l)} by {self._getObjType(r)}", node.left.token.line)

        # division by zero
        if r.value == 0:
            raise ZeroDivErr(node.left.token.line)

        return Number(l.value / r.value)


    def visit_MulNode(self, node) -> Number:
        l = self.visit(node.left)
        r = self.visit(node.right)

        # check if both l and r are numbers
        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Cannot multiply {self._getObjType(l)} by {self._getObjType(r)}", node.left.token.line)

        return Number(l.value * r.value)

    def visit_ModNode(self, node) -> Number:
        l = self.visit(node.left)
        r = self.visit(node.right)

        # check if both l and r are numbers
        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Invalid operand type for modulo,{self._getObjType(l)} and {self._getObjType(r)}", node.left.token.line)

        # division by zero
        if r.value == 0:
            raise ZeroDivErr(node.left.token.line)

        return Number(l.value % r.value)


    # comparision nodes
    def visit_GreaterThanNode(self, node) -> Number:
        l = self.visit(node.left)
        r = self.visit(node.right)

        # comparision only valid for numbers
        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Invalid operand type for greater than operator, {self._getObjType(l)} and {self._getObjType(r)}", node.left.token.line)

        if l.value > r.value:
            return Boolean("true")

        return Boolean("false")

    def visit_GreaterThanEqualNode(self, node) -> Number:
        l = self.visit(node.left)
        r = self.visit(node.right)

        # comparision only valid for numbers
        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Invalid operand type for greater than equals operator, {self._getObjType(l)} and {self._getObjType(r)}", node.left.token.line)

        if l.value >= r.value:
            return Boolean("true")

        return Boolean("false")

    def visit_LessThanNode(self, node) -> Number:
        l = self.visit(node.left)
        r = self.visit(node.right)

        # comparision only valid for numbers
        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Invalid operand type for less than operator, {self._getObjType(l)} and {self._getObjType(r)}", node.left.token.line)

        if l.value < r.value:
            return Boolean("true")

        return Boolean("false")

    def visit_LessThanEqualNode(self, node) -> Number:
        l = self.visit(node.left)
        r = self.visit(node.right)

        # comparision only valid for numbers
        if self._getObjType(l) != "Number" or self._getObjType(r) != "Number":
            raise TypeErr(f"Invalid operand type for less than equals operator, {self._getObjType(l)} and {self._getObjType(r)}", node.left.token.line)

        if l.value <= r.value:
            return Boolean("true")

        return Boolean("false")

    def visit_EqualNode(self, node) -> Number:
        l = self.visit(node.left)
        r = self.visit(node.right)

        allowedTypes = [
            "Nil",
            "Number",
            "Boolean",
            "String",
        ]

        if self._getObjType(l) not in allowedTypes or self._getObjType(r) not in allowedTypes:
            raise TypeErr(f"Cannot compare {self._getObjType(l)} and {self._getObjType(r)}", node.left.token.line)

        if l.value == r.value:
            return Boolean("true")

        return Boolean("false")

    def visit_NotEqualNode(self, node) -> Number:
        l = self.visit(node.left)
        r = self.visit(node.right)

        allowedTypes = [
            "Nil",
            "Number",
            "Boolean",
            "String",
        ]

        if self._getObjType(l) not in allowedTypes or self._getObjType(r) not in allowedTypes:
            raise TypeErr(f"Cannot compare {self._getObjType(l)} and {self._getObjType(r)}", node.left.token.line)

        if l.value != r.value:
            return Boolean("true")

        return Boolean("false")

    def visit_NotNode(self, node) -> Boolean:
        val = self.visit(node.node)

        if self._isTruthy(val):
            return Boolean("false")

        return Boolean("true")

    def visit_AndNode(self, node) -> Boolean:
        l = self._isTruthy(self.visit(node.left))
        if not l:
            return Boolean("false")

        r = self._isTruthy(self.visit(node.right))
        if not r:
            return Boolean("false")

        return Boolean("true")

    def visit_OrNode(self, node) -> Boolean:
        l = self._isTruthy(self.visit(node.left))
        if l:
            return Boolean("true")

        r = self._isTruthy(self.visit(node.right))
        if r:
            return Boolean("true")

        return Boolean("false")


    def visit_BlockNode(self, node, typ: ARType = ARType.BLOCK, isFunction = False) -> None:
        # for now isfunction is not used
        # else part will always be executed
        if isFunction:
            newAR = ActivationRecord(typ)
            newAR.setEnclosingEnv(self._callStack.peek().members)

            self._callStack.push(newAR)
            self._curFrame = newAR

            for s in node.stmtList:
                self.visit(s)

            self._callStack.pop()

            self._curFrame = self._callStack.peek()
        else:
            for s in node.stmtList:
                v = self.visit(s)

                if v == "continue":
                    return "continue"
                if v == "break":
                    return "break"
                    
                if v != None and str(v) != "nil":
                    return v

                if type(s).__name__ == "ReturnNode":
                    return v

            return Nil()

    def visit_ContinueNode(self, node) -> None:
        return "continue"

    def visit_BreakNode(self, node) -> None:
        return "break"

    def visit_ConditionalNode(self, node) -> bool:
        cond: LObject = self.visit(node.condition)

        if self._isTruthy(cond):
            r = self.visit(node.statement)

            if r == "continue":
                return "continue"

            if r == "break":
                return "break"

            if type(node.statement).__name__ == "ReturnNode":
                return r
                
            if r != None and str(r) != "nil":
                return r

            return True

        return False

    def visit_IfNode(self, node) -> None:
        res: bool = self.visit(node.ifBlock)

        if not res:
            for b in node.elsifBlocks:
                res = self.visit(b)
                if res == True:
                    break

                # if a return statement is hit
                if bool(res):
                    return res

        if not res and node.elseBlock:
            res = self.visit(node.elseBlock)

        if res not in [True, False]:
            return res

    
    def visit_WhileNode(self, node) -> LObject:
        cond: LObject = self.visit(node.condition)
        while self._isTruthy(cond):
            res: LObject = self.visit(node.statement)
            cond = self.visit(node.condition)
            
            if str(res) not in ["nil", "continue"] and bool(res):
                return res
    
    def visit_ReturnNode(self, node) -> LObject:
        if self._curFrame.type != ARType.FUNCTION:
            raise SyntaxErr("'return' outside function", node.line)
        return self.visit(node.expr)


    def visit_FunDeclNode(self, node) -> None:
        funObj = Function(
            node.id.token.value,
            [a.value for a in node.paramList],
            node.blockNode
        )

        self._curFrame[node.id.token.value] = funObj

    def visit_FunctionCallNode(self, node) -> LObject:
        # check builtin function
        if str(node.nameNode) in builtinFunctionTable:
            argList = []
            for a in node.argList:
                argList.append(self.visit(a))
            return builtinFunctionTable[str(node.nameNode)](argList)

        # create new frame
        newFrame = ActivationRecord(ARType.FUNCTION)
        newFrame.setEnclosingEnv(self._curFrame)
        
        # add params to the new frame as locals
        funObj = self._curFrame.get(node.nameNode.token.value)
        for a,f in zip(funObj.args, node.argList):
            newFrame[a] = self.visit(f)

        # push to call stack
        self._callStack.push(newFrame)
        self._curFrame = self._callStack.peek()

        # execute the function
        retval = self.visit(funObj.block)

        # pop frame
        self._callStack.pop()
        self._curFrame = self._callStack.peek()
        
        return retval
