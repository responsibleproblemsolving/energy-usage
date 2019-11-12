import energyusage

# user function to be evaluated
def recursive_fib(n):
    if (n<=2): return 1
    else: return recursive_fib(n-1) + recursive_fib(n-2)

def main():
    energyusage.evaluate(recursive_fib, 35, pdf=True, energyOutput=True, locations=["Romania", "Italy", "Iceland", "Colorado"])
    # returns 102,334,155

if __name__ == '__main__': main()
