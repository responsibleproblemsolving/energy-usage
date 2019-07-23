import energy_usage

# User function to be evaluated
def fib(n):
    if (n<=2): return 1
    else: return fib(n-1) + fib(n-2)

def main():
    energy_usage.evaluate(fib,40)

if __name__ == '__main__': main()
