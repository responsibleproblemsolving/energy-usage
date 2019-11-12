import statistics
import json
import energyusage
import energyusage.locate as locate
with open("./energyusage/data/json/energy-mix-intl.json") as file:
  data = json.load(file)

max = ""
median = ""
min = ""
countries = []


for country in data:
    c = data[country]
    total, breakdown =  c['total'], [c['coal'], c['petroleum'], \
    c['naturalGas'], c['lowCarbon']]
    if isinstance(c['total'], float) and locate.in_Europe(country):
        #breakdown = list(map(lambda x: 100*x/total, breakdown))
        countries.append((country,breakdown))

coal = 0
petroleum = 0
naturalGas = 0
lowCarbon = 0
length = len(countries)

for country in countries:
	coal+=country[1][0]
	naturalGas+=country[1][1]
	petroleum+=country[1][2]
	lowCarbon+=country[1][3]

coal /= length
petroleum /= length
naturalGas /= length
lowCarbon /= length
total = coal+petroleum+naturalGas+lowCarbon
print("Total: " + str(total) + "\nCoal: " + str(coal) + "\nPetroleum: " + str(petroleum) + "\nNatural Gas: " + str(naturalGas) + "\nLow Carbon: " + str(lowCarbon))



'''
sorted_countries = sorted(countries, key= lambda x: x[1][0], reverse=True)
max = sorted_countries[0]
min = sorted_countries[len(sorted_countries)-1]
median = sorted_countries[len(sorted_countries)//2 + 1]

print("Max is " + max[0])
print("Min is " + min[0])
print("Median is " + median[0])
'''