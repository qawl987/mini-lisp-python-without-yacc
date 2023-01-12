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
        # 將node分為tree與token
        if node.__class__ == lark.lexer.Token:
            # TODO
            if node == '#t':
                return True
            elif node == '#f':
                return False
            elif node.type == 'ID':
                # ID代表是define variable 或 define function name
                # 若local找不到去global找，若global也找不到代表沒定義
                if node.value in local_symbol_table:
                    return local_symbol_table[node.value]
                if node.value not in self.symbol_table:
                    raise Exception(f'variable {node.value} not define')
                return self.symbol_table[node.value]
            return int(node)
        elif node.data == 'program':
            ret = list()
            # 遞迴解析children
            for child in node.children:
                result = self.interpret_ast(child)
                # 只有經過print_num()才會回傳字串才會加到輸出中
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
                result.append(self.boolean_type_checker(self.interpret_ast(child, local_symbol_table)))
            return all(result)
        elif node.data == 'or_op':
            result = []
            for child in node.children:
                result.append(self.boolean_type_checker(self.interpret_ast(child, local_symbol_table)))
            return any(result)
        elif node.data == 'not_op':
            return not self.boolean_type_checker(self.interpret_ast(node.children[0], local_symbol_table))
        elif node.data == 'if_exp':
            condition = self.boolean_type_checker(self.interpret_ast(node.children[0], local_symbol_table))
            if condition:
                return self.interpret_ast(node.children[1], local_symbol_table)
            else:
                return self.interpret_ast(node.children[2], local_symbol_table)
        elif node.data == 'equal':
            comparison = self.number_type_checker(self.interpret_ast(node.children[0], local_symbol_table))
            flag = True
            for child in node.children[1:]:
                # TODO: type checking
                if comparison != self.number_type_checker(self.interpret_ast(child, local_symbol_table)):
                    flag = False
                    break
            return flag
        elif node.data == 'smaller':
            return self.number_type_checker(self.interpret_ast(node.children[0], local_symbol_table)) < self.number_type_checker(self.interpret_ast(node.children[1], local_symbol_table))
        elif node.data == 'greater':
            return self.number_type_checker(self.interpret_ast(node.children[0], local_symbol_table)) > self.number_type_checker(self.interpret_ast(node.children[1], local_symbol_table))
        elif node.data == 'def_stmt':
            # 左邊是變數名 右邊可以是 int bool 也可以是 function pointer
            self.symbol_table[node.children[0]] = self.interpret_ast(node.children[1], local_symbol_table)
        elif node.data == 'fun_exp':
            # 第一個是function argument,第二個是function body
            # 取children[0].children 因為 此時node為 Tree(Token('RULE', 'fun_ids'), [Token('ID', 'x')])
            # 取children[1].children 同上 Tree(Token('RULE', 'fun_body'), [Tree(Token('RULE', 'plus'), [Token('ID', 'x'), Token('SIGNED_INT', '1')])])
            # 取children[1].children[0] 因為 children為list 且必只有一個element: exp所以可取[0]
            # 參數定義 以及 function內容存到 function class，且不經解析 因為目前參數內容未知無法解析
            return FunctionExpression(node.children[0].children, node.children[1].children[0])
        elif node.data == 'fun_call':
            # fun_exp 可以是一個function class也就是匿名函式
            # 也可以是 function name在else從table中取得function pointer
            fun_exp = self.interpret_ast(node.children[0], local_symbol_table)
            if isinstance(fun_exp, FunctionExpression):
                # 如果是匿名函式 則node.children[0]以後為所有參數的值，所以將fun_call的變數值與fun_args的變數值對應
                # 最後將fun_body與做好的function_symbol_table一起解析，代表fun_body現在有各個入參的定義了
                fun_symbol_table = dict()
                for i in range(len(node.children) - 1):
                    fun_symbol_table[fun_exp.fun_args[i]] = self.interpret_ast(node.children[i+1], local_symbol_table)
                return self.interpret_ast(fun_exp.fun_body, fun_symbol_table)
            else:
                # 若為function名稱 則將dict 中的 function pointer取出
                def_fun_exp = self.interpret_ast(fun_exp, local_symbol_table)
                fun_symbol_table = dict()
                for i in range(len(node.children) - 1):
                    fun_symbol_table[def_fun_exp.fun_args[i]] = self.interpret_ast(node.children[i+1], local_symbol_table)
                return self.interpret_ast(def_fun_exp.fun_body, fun_symbol_table)

    def print_num(self, node):
        # 回傳字串而非數字辨別哪些是要得output哪些是假輸出
        return str(self.interpret_ast(node))

    @staticmethod
    def number_type_checker(num):
        if not type(num) is int:
            raise TypeError("Expect 'number' but got 'boolean'.")
        return num
    @staticmethod
    def boolean_type_checker(boolean):
        if not type(boolean) is bool:
            raise TypeError("Expect 'boolean' but got 'number'.")
        return boolean
class FunctionExpression():
    def __init__(self, fun_args, fun_body):
        self.fun_args = fun_args
        self.fun_body = fun_body