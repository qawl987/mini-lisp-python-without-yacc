from lark import Lark, UnexpectedInput, UnexpectedToken, UnexpectedCharacters
import lark
class Interpreter():
    def __init__(self) -> None:
        self.tree = None
        with open('grammar.lark') as larkfile:
            self.parser = Lark(larkfile, start='program',
                               parser='lalr', lexer='contextual')

    def interpret(self, code):
        try:
            self.tree = self.parser.parse(code)
            # print(self.tree.pretty())
            # print(self.tree)
        except (UnexpectedInput, UnexpectedToken, UnexpectedCharacters) as exception:
            raise SyntaxError('Mini-lisp syntax error.') from exception
        return self.interpret_ast(self.tree)

    def interpret_ast(self, node):
        if node.__class__ == lark.lexer.Token:
            # TODO
            return int(node)
        elif node.data == 'program':
            ret = list()
            for child in node.children:
                result = self.interpret_ast(child)
                ret.append(result)
            return ret
        elif node.data == 'print_num':
            # print_num children 只有一個list
            return self.print_num(node.children[0])
        elif node.data == 'plus':
            result = []
            for child in node.children:
                result.append(self.interpret_ast(child))
            return sum(result)
        elif node.data == 'minus':
            pass
        elif node.data == 'multiply':
            pass
        elif node.data == 'modulus':
            pass
        elif node.data == 'greater':
            pass
        elif node.data == 'smaller':
            pass
        elif node.data == 'equal':
            pass

    def print_num(self, node):
        return self.interpret_ast(node)