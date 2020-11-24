import sys
from time import time

from locks.lexer.lexer import Lexer
from locks.parser.parser import Parser
from locks.analyzer.analyzer import SemanticAnalyzer
from locks.interpreter.interpreter import Interpeter
from locks.error import Error

def main():
    if (len(sys.argv) - 1) != 1:
        print("Usage: python locks.py <path-to-locks-file>")
        return 1

    try:
        program = open(sys.argv[1], 'r', encoding='unicode_escape').read()
    except FileNotFoundError:
        print(f"Error: file '{sys.argv[1]}' not found")
        return 1
    except:
        print(f"Error opening file '{sys.argv[1]}'")
        return 1
        
    # lexer - split into tokens
    l = Lexer(program)
    tokl = l.getTokens()

    if l.hadError:
        for e in l.getErrorList():
            print(e)
        return -1


    # parser - pass in token list and construct ast
    p = Parser(tokl)
    ast = p.getAST()
    
    if p.hadError:
        for i in p.getError():
            print(i)
        return -1


    # semantic analyser - pass in ast to check for semantic errors
    s = SemanticAnalyzer()
    s.visit(ast)
    if s.hadError:
        for e in s.getErrorList():
            print(e)
        return -1

    # tree walk interpreter - execute code
    try:
        i = Interpeter()
        i.visit(ast)
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt")
        return -1
    except Error as e:
        print(e)
        return -1

    return 0


if __name__ == '__main__':
    t0 = time()
    ret = main()
    if ret != 1:
        print(f"\nProcess finished in {time() - t0} seconds with return code {ret}")
        input("Press Enter to continue...")
    