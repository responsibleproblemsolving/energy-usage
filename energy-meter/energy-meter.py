import evaluate
import time

# FUNCTION TO BE EVALUATED
def fib(n):
    if (n<=2): return 1
    else: return fib(n-1) + fib(n-2)

def sleep(n):
    time.sleep(n)
    return 1



def main():
    evaluate.evaluate(fib, 40)



if __name__ == '__main__': main()
