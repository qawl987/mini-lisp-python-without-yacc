import sys
import interpreter

def main():
    filename = sys.argv[1]
    with open(filename, 'r', encoding='utf-8') as f:
        text = f.read()
    ans = interpreter.Interpreter().interpret(text)
    for exp in ans:
        print(exp)


if __name__ == '__main__':
    main()
