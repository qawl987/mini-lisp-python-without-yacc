import sys
import interpreter
import os

def main():
    filename = sys.argv[1]
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    ans = interpreter.Interpreter().interpret(text)
    for exp in ans:
        print(exp)
    # filenames = os.listdir('./test_data')
    # for filename in filenames:
    #     if filename != '01_1.lsp' and filename != '01_2.lsp' and filename[0] != 'b':
    #         print(filename)
    #         with open(f'./test_data/{filename}', 'r', encoding='utf-8') as f:
    #             text = f.read()
    #         ans = interpreter.Interpreter().interpret(text)
    #         for exp in ans:
    #             print(exp)
        
if __name__ == '__main__':
    main()
