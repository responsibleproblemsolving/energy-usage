import sys
sys.path.insert(0, 'energy-meter')
import evaluate


# FUNCTION TO BE EVALUATED
def fib(n):
    if (n<=2): return 1
    else: return fib(n-1) + fib(n-2)


def main():
    evaluate.evaluate(fib,20)


if __name__ == '__main__': main()
