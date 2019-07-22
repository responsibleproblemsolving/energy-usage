#import energy_usage.evaluate as evaluate
from . import evaluate
import evaluate
import time

"""
import plotly.graph_objects as go
import pandas as pd
"""

# FUNCTION TO BE EVALUATED
def fib(n):
    if (n<=2): return 1
    else: return fib(n-1) + fib(n-2)

def sleep(n):
    time.sleep(n)
    return 1

def linear(n):
    for j in range(n):
        for i in range(100000000):
            num = 1+1
    return 1
"""
def make_graph(func, num_executions):
    MyEmptydf = pd.DataFrame()
    x = []
    y = []
    for i in range(3, 13):
        result, return_value = evaluate.evaluate(linear, i)
        y.append(result)
        x.append(i)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x = x,
        y = y
    ))
    #gapminder = px.data.gapminder().query("country=='Canada'")
    fig.show()
"""
def main():
    evaluate.evaluate(fib,40)






if __name__ == '__main__': main()
