from lark import Lark, UnexpectedInput, UnexpectedToken, UnexpectedCharacters
import lark
from math import prod

class Interpreter():
    def __init__(self) -> None:
        self.tree = None
        with open('grammar.lark') as larkfile:
            self.parser = Lark(larkfile, start='program',
                               parser='lalr', lexer='contextual')

    def interpret(self, code):
        try:
            self.tree = self.parser.parse(code)
            print(self.tree.pretty())
            print(self.tree)
        except (UnexpectedInput, UnexpectedToken, UnexpectedCharacters) as exception:
            raise SyntaxError('Mini-lisp syntax error.') from exception
        return self.interpret_ast(self.tree)

    def interpret_ast(self, node):
        if node.__class__ == lark.lexer.Token:
            # TODO
            if node == '#t':
                return True
            elif node == '#f':
                return False
            return int(node)
                
        elif node.data == 'program':
            ret = list()
            for child in node.children:
                result = self.interpret_ast(child)
                if isinstance(result, str):
                    ret.append(result)
            return ret
        elif node.data == 'print_num':
            # print_num children 只有一個list
            return self.print_num(node.children[0])
        elif node.data == 'print_bool':
            return self.print_num(node.children[0])
        elif node.data == 'plus':
            result = []
            for child in node.children:
                result.append(self.interpret_ast(child))
            return sum(result)
        elif node.data == 'minus':
            return self.interpret_ast(node.children[0]) - self.interpret_ast(node.children[1])
        elif node.data == 'multiply':
            result = []
            for child in node.children:
                result.append(self.interpret_ast(child))
            return prod(result)
        elif node.data == 'divide':
            return int(self.interpret_ast(node.children[0]) / self.interpret_ast(node.children[1]))
        elif node.data == 'modulus':
            return self.interpret_ast(node.children[0]) % self.interpret_ast(node.children[1])
        elif node.data == 'and_op':
            result = []
            for child in node.children:
                result.append(self.interpret_ast(child))
            return all(result)
        elif node.data == 'or_op':
            result = []
            for child in node.children:
                result.append(self.interpret_ast(child))
            return any(result)
        elif node.data == 'not_op':
            return not self.interpret_ast(node.children[0])
        elif node.data == 'equal':
            pass
        elif node.data == 'smaller':
            pass
        elif node.data == 'equal':
            pass

    def print_num(self, node):
        return str(self.interpret_ast(node))