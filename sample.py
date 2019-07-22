from energy_usage.evaluate import evaluate

# User function to be evaluated
def fib(n):
    if (n<=2): return 1
    else: return fib(n-1) + fib(n-2)

def main():
    evaluate(fib,40)

if __name__ == '__main__': main()
