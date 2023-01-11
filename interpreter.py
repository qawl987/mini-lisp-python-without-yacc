from lark import Lark, UnexpectedInput, UnexpectedToken, UnexpectedCharacters
import lark
from math import prod
class typeError(BaseException):
    pass
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
            # print(self.tree.pretty())
            # print(self.tree)
        except (UnexpectedInput, UnexpectedToken, UnexpectedCharacters) as exception:
            raise SyntaxError('Mini-lisp syntax error.') from exception
        return self.interpret_ast(self.tree)

    def interpret_ast(self, node, local_symbol_table=dict()):
        if node.__class__ == lark.lexer.Token:
            # TODO
            if node == '#t':
                return True
            elif node == '#f':
                return False
            elif node.type == 'ID':
                if node.value in local_symbol_table:
                    return local_symbol_table[node.value]
                if node.value not in self.symbol_table:
                    raise Exception(f'variable {node.value} not define')
                return self.symbol_table[node.value]
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
                num = self.number_type_checker(self.interpret_ast(child, local_symbol_table))
                result.append(num)
            return sum(result)
        elif node.data == 'minus':
            num1 = self.number_type_checker(self.interpret_ast(node.children[0], local_symbol_table))
            num2 = self.number_type_checker(self.interpret_ast(node.children[1], local_symbol_table))
            return num1 - num2
        elif node.data == 'multiply':
            result = []
            for child in node.children:
                num = self.number_type_checker(self.interpret_ast(child, local_symbol_table))
                result.append(num)
            return prod(result)
        elif node.data == 'divide':
            num1 = self.number_type_checker(self.interpret_ast(node.children[0], local_symbol_table))
            num2 = self.number_type_checker(self.interpret_ast(node.children[1], local_symbol_table))
            return int(num1 / num2)
        elif node.data == 'modulus':
            num1 = self.number_type_checker(self.interpret_ast(node.children[0], local_symbol_table))
            num2 = self.number_type_checker(self.interpret_ast(node.children[1], local_symbol_table))
            return num1 % num2
        elif node.data == 'and_op':
            result = []
            for child in node.children:
                result.append(self.interpret_ast(child, local_symbol_table))
            return all(result)
        elif node.data == 'or_op':
            result = []
            for child in node.children:
                result.append(self.interpret_ast(child, local_symbol_table))
            return any(result)
        elif node.data == 'not_op':
            return not self.interpret_ast(node.children[0], local_symbol_table)
        elif node.data == 'if_exp':
            condition = self.interpret_ast(node.children[0], local_symbol_table)
            if condition:
                return self.interpret_ast(node.children[1], local_symbol_table)
            else:
                return self.interpret_ast(node.children[2], local_symbol_table)
        elif node.data == 'equal':
            comparison = (self.interpret_ast(node.children[0]), local_symbol_table)
            flag = True
            for child in node.children[1:]:
                # TODO: type checking
                if comparison != self.interpret_ast(child, local_symbol_table):
                    flag = False
                    break
            return flag
        elif node.data == 'smaller':
            return self.interpret_ast(node.children[0], local_symbol_table) < self.interpret_ast(node.children[1], local_symbol_table)
        elif node.data == 'greater':
            return self.interpret_ast(node.children[0], local_symbol_table) > self.interpret_ast(node.children[1], local_symbol_table)
        elif node.data == 'def_stmt':
            self.symbol_table[node.children[0]] = self.interpret_ast(node.children[1], local_symbol_table)
        elif node.data == 'fun_exp':
            return FunctionExpression(node.children[0].children, node.children[1].children[0])
        elif node.data == 'fun_call':
            # func_exp == node
            fun_exp = self.interpret_ast(node.children[0], local_symbol_table)
            if isinstance(fun_exp, FunctionExpression):
                fun_symbol_table = dict()
                for i in range(len(node.children) - 1):
                    fun_symbol_table[fun_exp.fun_args[i]] = self.interpret_ast(node.children[i+1], local_symbol_table)
                return self.interpret_ast(fun_exp.fun_body, fun_symbol_table)
            else:
                def_fun_exp = self.interpret_ast(fun_exp)
                fun_symbol_table = dict()
                for i in range(len(node.children) - 1):
                    fun_symbol_table[def_fun_exp.fun_args[i]] = self.interpret_ast(node.children[i+1], local_symbol_table)
                return self.interpret_ast(def_fun_exp.fun_body, fun_symbol_table)

    def print_num(self, node):
        return str(self.interpret_ast(node))

    @staticmethod
    def number_type_checker(num):
        if not type(num) is int:  # pylint: disable=unidiomatic-typecheck
            raise TypeError("Expect 'number' but got 'boolean'.")
        return num
class FunctionExpression():
    def __init__(self, fun_args, fun_body):
        self.fun_args = fun_args
        self.fun_body = fun_body