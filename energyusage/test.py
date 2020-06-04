def linear(n):
    for i in range(n):
        for j in range(50000000):
            num = 1+1
            
def exp(n):
    for i in range(2**n):
        linear(1)
        
import energyusage
energyusage.evaluate(exp, 10)
                                                        
