from lark import Lark, UnexpectedInput, UnexpectedToken, UnexpectedCharacters
import lark
from math import prod

class Interpreter():
    def __init__(self) -> None:
        self.tree = None
        with open('grammar.lark') as larkfile:
            self.parser = Lark(larkfile, start='program',
                               parser='lalr', lexer='contextual')
        self.symbol_table = dict()

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
            elif node.type == 'ID':
                if node.value not in self.symbol_table:
                    raise Exception(f'variable {node.value} not define')
                return self.symbol_table[node.value]
            return int(node)
                
        elif node.data == 'program':
            ret = list()
            for child in node.children:
                comparison = self.interpret_ast(child)
                if isinstance(comparison, str):
                    ret.append(comparison)
            return ret
        elif node.data == 'print_num':
            # print_num children 只有一個list
            return self.print_num(node.children[0])
        elif node.data == 'print_bool':
            return self.print_num(node.children[0])
        elif node.data == 'plus':
            comparison = []
            for child in node.children:
                comparison.append(self.interpret_ast(child))
            return sum(comparison)
        elif node.data == 'minus':
            return self.interpret_ast(node.children[0]) - self.interpret_ast(node.children[1])
        elif node.data == 'multiply':
            comparison = []
            for child in node.children:
                comparison.append(self.interpret_ast(child))
            return prod(comparison)
        elif node.data == 'divide':
            return int(self.interpret_ast(node.children[0]) / self.interpret_ast(node.children[1]))
        elif node.data == 'modulus':
            return self.interpret_ast(node.children[0]) % self.interpret_ast(node.children[1])
        elif node.data == 'and_op':
            comparison = []
            for child in node.children:
                comparison.append(self.interpret_ast(child))
            return all(comparison)
        elif node.data == 'or_op':
            comparison = []
            for child in node.children:
                comparison.append(self.interpret_ast(child))
            return any(comparison)
        elif node.data == 'not_op':
            return not self.interpret_ast(node.children[0])
        elif node.data == 'if_exp':
            condition = self.interpret_ast(node.children[0])
            if condition:
                return self.interpret_ast(node.children[1])
            else:
                return self.interpret_ast(node.children[2])
        elif node.data == 'equal':
            comparison = (self.interpret_ast(node.children[0]))
            flag = True
            for child in node.children[1:]:
                # TODO: type checking
                if comparison != self.interpret_ast(child):
                    flag = False
                    break
            return flag
        elif node.data == 'smaller':
            return self.interpret_ast(node.children[0]) < self.interpret_ast(node.children[1])
        elif node.data == 'greater':
            return self.interpret_ast(node.children[0]) > self.interpret_ast(node.children[1])
        elif node.data == 'def_stmt':
            self.symbol_table[node.children[0]] = self.interpret_ast(node.children[1])

    def print_num(self, node):
        return str(self.interpret_ast(node))