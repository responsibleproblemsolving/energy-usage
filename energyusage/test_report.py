import evaluate
import report
#import energyusage

def linear(n):
    for i in range(n):
        for j in range(50000000):
            num = 1+1
            
def exp(n):
    for i in range(2**n):
        linear(1)

def small_function(n):
    n+1
        
evaluate.evaluate(small_function, 10, pdf=True,  png=True)
#energyusage.evaluate(exp, 10, pdf=True)
#report.generate_mlco2(3, 1.68, png=True)
