import energyusage

# user function to be evaluated
def recursive_fib(n):
    if (n<=2): return 1
    else: return recursive_fib(n-1) + recursive_fib(n-2)

def main():
    energyusage.evaluate_region("Alabama", 2, "TPU2", region_info = True, pdf=False, energyOutput=False)
    # returns 102,334,155

if __name__ == '__main__': main()
