import mlco2_report
import evaluate

mlco2_report.report_all(3.6,0.07)
mlco2_report.report_with_charts(3.6,0.07)
mlco2_report.report_without_charts(3.6,0.07)

def linear(n):
    for i in range(n):
        for j in range(50000000):
            num = 1+1

def exp_and_quadratic(n):
    for i in range(2**n):
        linear(1)
    for i in range(n):
        for j in range(n):
            linear(1)

evaluate.evaluate(exp_and_quadratic,10)
