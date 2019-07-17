import evaluate

# FUNCTION TO BE EVALUATED
def fib(n):
    if (n<=2): return 1
    else: return fib(n-1) + fib(n-2)

def main():
    return evaluate.evaluate(fib,40)

if __name__ == '__main__': main()
