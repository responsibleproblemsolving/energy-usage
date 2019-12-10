import statistics
import json
with open("./energyusage/data/json/energy-mix-intl_2016.json") as file:
  data = json.load(file)

max = ""
median = ""
min = ""
countries = []


for country in data:
    c = data[country]
    total, breakdown =  c['total'], [c['coal'], c['petroleum'], \
    c['naturalGas'], c['lowCarbon']]
    if isinstance(c['total'], float) and c['total'] != 0:
        breakdown = list(map(lambda x: 100*x/total, breakdown))
        countries.append((country,breakdown))

sorted_countries = sorted(countries, key= lambda x: x[1][0], reverse=True)
max = sorted_countries[0]
min = sorted_countries[len(sorted_countries)-1]
median = sorted_countries[len(sorted_countries)//2 + 1]

print("Max is " + max[0])
print("Min is " + min[0])
print("Median is " + median[0])
