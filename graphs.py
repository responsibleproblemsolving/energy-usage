import energy_usage
import pandas as pd
import plotly.graph_objects as go
def fib(n):
    if n < 2:
        return 1
    else:
        return fib(n-1) + fib(n-2)


def linear(n):
    for i in range(n):
        for j in range(50000000):
            num = 1+1
def quadratic(n):
    multiplier = 1000
    for i in range(n * multiplier):
        for j in range(n*multiplier):
            num = 1+1


def make_graph(func, start, end, name):
    MyEmptydf = pd.DataFrame()
    x = []
    y = []
    for i in range(start, end):
        result, return_value = energy_usage.evaluate(func, i)
        y.append(result)
        x.append(i)
    fig = go.Figure(
        layout=go.Layout(
            title=go.layout.Title(text=name)
            )
    )
    fig.add_trace(go.Scatter(
        x = x,
        y = y
    ))
    #gapminder = px.data.gapminder().query("country=='Canada'")
    fig.show()

def main():

    make_graph(quadratic, 4, 20, "Quadratic")
    make_graph(fib, 29, 38, "Exponential")
    make_graph(linear, 3, 13, "Linear")



if __name__ == '__main__': main()
