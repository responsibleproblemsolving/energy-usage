import math
import sys
import operator
import time
import json

import convert

# TO DO: Function to convert seconds into more reasonable time
# TO DO: Having something to relate to

# MSR_*FILE*_ENERGY_STATUS 
# Total amount of energy consumed since that last time this register was
# cleared
PKG = "/sys/class/powercap/intel-rapl:0/energy_uj"
CORE = "/sys/class/powercap/intel-rapl:0:0/energy_uj"
UNCORE = "/sys/class/powercap/intel-rapl:0:1/energy_uj"
DRAM = "/sys/class/powercap/intel-rapl:0:2/energy_uj"

DELAY = .1 # in seconds



""" MEASUREMENT UTILS """

def read(file):
    """ Opens file and reads energy measurement """

    with open(file, 'r') as f:
        return convert.to_joules(int(f.read()))

def measure(file, delay=1):
    """ Measures the energy output of FILE """

    start, end = 0, 0
    start = read(file)
    time.sleep(delay)
    end = read(file)
   
    return end-start

def measure_packages(packages, delay = 1):
    """ Measures the energy output of all packages which should give total CPU power usage """

    start = list(map(read, packages))
    time.sleep(delay)
    end = list(map(read, packages))
    measurement = sum(list(map(round_up,(map(operator.sub, end, start)))))
    return measurement


def measure_all(delay=1):
    """ Measures the energy output of all files in a single processor setup """

    files = [PKG, CORE, UNCORE, DRAM]
    start = list(map(read, files))
    time.sleep(delay)
    end = list(map(read,files))
    # Calculates end - start for each file, then rounds result
    measurement = list(map(round_up,(map(operator.sub, end, start))))

    return measurement

def get_num_packages():
    num = 0
    files = [] 
    while True:
        file = "/sys/class/powercap/intel-rapl:" + str(num) +"/energy_uj"
        try: 
            read(file)
            num+=1
            files.append(file)
        except:
            break
    return files

# from realpython.com/python-rounding
def round_up(n, decimals=4):
    """ Rounds up if digit is >= 5 """

    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier



""" MISC UTILS """

def get_data(file):
    with open(file) as f:
            data = json.load(f)
    return data

def log_header(text):
    sys.stdout.write("-"*80 + "\n" + "-"*31 + " {:^16} ".format(text) +
        "-"*31 + "\n" + "-"*80+ "\n"
       )

def log_formulas():
    log_header('Formulas Used')
    sys.stdout.write("{:<14} {:>65}\n".format("Coal:", ".3248635 kg CO2/kWh"))
    sys.stdout.write("{:<14} {:>65}\n".format("Oil/Petroleum:", ".23 kg CO2/kWh"))
    sys.stdout.write("{:<14} {:>65}\n".format("Natural gas:", ".0885960 kg CO2/kwh"))
    
def log_emission(emission):
    log_header('Emissions')
    sys.stdout.write("{:<19}{:>54} kg CO2\n".format("Effective emission:", \
        emission))
    sys.stdout.write("{:<37}{:>42}%\n".format("% of CO2 used in a US"
    " household/day:",convert.carbon_to_home(emission)))
    sys.stdout.write("{:<24}{:>56}\n".format("Equivalent miles driven:", \
        convert.carbon_to_miles(emission)))
    

# from https://stackoverflow.com/a/52590238
def delete_last_lines():
    # Moves cursor up one line
    sys.stdout.write('\x1b[1A')
    sys.stdout.write('\x1b[1A')
   
