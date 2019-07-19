import math
import sys
import operator
import time
import json
import os
import re
import statistics

import convert
import locate
from RAPLFile import RAPLFile



# TO DO: Function to convert seconds into more reasonable time
# TO DO: Having something to relate to

# MSR_*FILE*_ENERGY_STATUS
# Total amount of energy consumed since that last time this register was
# cleared
BASE = "/sys/class/powercap/"

PKG = "/sys/class/powercap/intel-rapl:0/energy_uj"
CORE = "/sys/class/powercap/intel-rapl:0:0/energy_uj"
UNCORE = "/sys/class/powercap/intel-rapl:0:1/energy_uj"

DRAM = "/sys/class/powercap/intel-rapl:1:0/energy_uj"# if has_multiple_cpus() \
    #else "/sys/class/powercap/intel-rapl:0:2/energy_uj"


## MULTIPLE processors
# DRAM = "/sys/class/powercap/intel-rapl:1:0/energy_uj"

DELAY = .1 # in seconds
DIR_PATH = os.path.dirname(os.path.realpath(__file__))


""" MEASUREMENT UTILS """

def read(file):
    """ Opens file and reads energy measurement """
    if file == "":
        return 0
    else:
        with open(file, 'r') as f:
            return convert.to_joules(int(f.read()))

def average_files(raplfiles):
    for file in raplfiles:
        file.process_average = statistics.mean(file.process)
        file.baseline_average = statistics.mean(file.baseline)
    return raplfiles

def measure(file, delay=1):
    """ Measures the energy output of FILE """

    start, end = 0, 0
    start = read(file)
    time.sleep(delay)
    end = read(file)

    return end-start
def get_process_average(raplfiles, multiple_cpus):
    if multiple_cpus:
        for file in raplfiles:
            if file.name.contains("CPU"):
                total+= file.process_average
        return total
    else:
        for file in raplfiles:
            if file.name == "Package":
                return file.process_average
    return -1
def get_baseline_average(raplfiles, multiple_cpus):
    if multiple_cpus:
        for file in raplfiles:
            if file.name.contains("CPU"):
                total+= file.baseline_average
        return total
    else:
        for file in raplfiles:
            if file.name == "Package":
                return file.baseline_average
    return -1

def get_total(raplfiles, multiple_cpus):
    total = 0
    if multiple_cpus:
        for file in raplfiles:
            if file.name.contains("CPU"):
                total+= file.recent
        return total
    else:
        for file in raplfiles:
            if file.name == "Package":
                return file.recent
    return -1

def update_files(raplfiles, process = False):
    if process:
        for file in raplfiles:
            if file.recent >= 0:
                file.process.append(file.recent)
    else:
        for file in raplfiles:
            if file.recent >= 0:
                file.baseline.append(file.recent)
    return raplfiles


### CHECK NEGATIVE VALUES
def start(raplfile):
    measurement = read(raplfile.path)
    raplfile.recent = measurement
    return raplfile

def end(raplfile, delay):
    measurement = read(raplfile.path)
    raplfile.recent = (measurement -raplfile.recent) / delay
    return raplfile


def measure_files(files, delay = 1):
    """ Measures the energy output of all packages which should give total power usage

    Parameters:
        files (list): list of RAPLFiles
        delay (int): RAPL file reading rate in ms

    Returns:
        files (list): list of RAPLfiles with updated measurements
    """

    files = list(map(start, files))
    time.sleep(delay)
    files = list(map(lambda x: end(x, delay), files))
    return files

    '''
    for k,v in files.items():
        files[k][2] = read(files[k][0])
    time.sleep(delay)
    for k,v in files.items():
        files[k][2] = read(files[k][0]) - files[k][2]
        files[k][1] += files[k][2]

    return files
'''
#deprecated
def measure_packages(packages, delay):
    start = list(map(read, packages))
    time.sleep(delay)
    end = list(map(read, packages))
    measurement = sum(map(round_up,(map(operator.sub, end, start))))
    return measurement

# kinda deprecated
def measure_all(delay=1):
    """ Measures the energy output of all files in a single processor setup """

    files = [PKG, CORE, UNCORE, DRAM]
    start = list(map(read, files))
    time.sleep(delay)
    end = list(map(read,files))
    # Calculates end - start for each file, then rounds result
    measurement = map(round_up,(map(operator.sub, end, start)))

    return measurement

def reformat(name, multiple_cpus):
    if 'package' in name:
        if multiple_cpus:
            name = "CPU" + name[-1] # renaming it to CPU-x
        else:
            name = "Package"
    if name == 'core':
        name = "CPU"
    elif name == 'uncore':
        name = "GPU"
    elif name == 'dram':
        name = name.upper()

    return name


def get_files():
    """ Gets all the intel-rapl files with their names

        Returns:
            filenames (list): list of RAPLFiles
    """
    # Removing the intel-rapl folder that has no info
    files = list(filter(lambda x: ':' in x, os.listdir(BASE)))
    names = {}
    multiple_cpus = has_multiple_cpus()
    for file in files:
        path = BASE + '/' + file + '/name'
        with open(path) as f:
           name = f.read()[:-1]
           renamed = reformat(name, multiple_cpus)
        names[renamed] = BASE + file + '/energy_uj'

    filenames = []
    for name, path in names.items():

        name = RAPLFile(name, path)
        filenames.append(name)

    return filenames, multiple_cpus



def get_packages():
    # this should give us a list of the files needed
    # if single cpu: [core(cpu), uncore(gpu), DRAM ]
    # if multiple cpus: [cpu1, cpu2, .. , cpun , dram]

    num = 0
    files = []
    while True:
        file = BASE + "intel-rapl:" + str(num) +"/energy_uj"
        try:
            read(file)
            num+=1
            files.append(file)
        except:
            break
    return files


def has_multiple_cpus():
    packages = get_packages()
    return len(packages) > 1


# from realpython.com/python-rounding
def round_up(n, decimals=4):
    """ Rounds up if digit is >= 5 """

    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier


""" LOGGING UTILS """

def log_header(text):
    if len(text) > 16:
        sys.stdout.write("-"*80 + "\n" + "-"*25 + " {:^28} ".format(text) +
            "-"*25 + "\n" + "-"*80+ "\n")
    else:
        sys.stdout.write("-"*80 + "\n" + "-"*31 + " {:^16} ".format(text) +
            "-"*31 + "\n" + "-"*80+ "\n")

# from https://stackoverflow.com/a/52590238
def delete_last_lines():
    # Moves cursor up one line
    sys.stdout.write('\x1b[1A')
    sys.stdout.write('\x1b[1A')

def newline():
    sys.stdout.write('\n')

def log(*args):
    # use regex here
    if (re.search("Package|CPU.*|GPU|DRAM", args[0])):
        measurement = args[1]
        sys.stdout.write("\r{:<24} {:>49.2f} {:5<}".format(args[0]+":", measurement, "watts"))


    if args[0] == "Baseline wattage":
        measurement = args[1]
        sys.stdout.write("\r{:<24} {:>49.2f} {:5<}".format(args[0]+":", measurement, "watts"))

    elif args[0] == "Process wattage":
        measurement = args[1]
        sys.stdout.write("\r{:<17} {:>56.2f} {:5<}".format(args[0]+":", measurement, "watts"))

    elif args[0] == "Final Readings":
        newline()
        baseline_average, process_average, timedelta = args[1], args[2], args[3]
        delete_last_lines()
        log_header(args[0])
        sys.stdout.write("{:<25} {:>48.2f} {:5<}\n".format("Average baseline wattage:", baseline_average, "watts"))
        sys.stdout.write("{:<25} {:>48.2f} {:5<}\n".format("Average process wattage:", process_average, "watts"))
        sys.stdout.write("{:<17} {:>62}\n".format("Process duration:", timedelta))

    elif args[0] == "Energy Data":
        location = args[2]
        log_header('Energy Data')
        if location == "Unknown" or locate.in_US(location):
            coal, oil, gas, low_carbon = args[1]
            if location == "Unknown":
                location = "United States"
                sys.stdout.write("{:^80}\n{:<13}{:>66.2f}%\n{:<13}{:>66.2f}%\n{:<13}{:>66.2f}%\n"
                    "{:<13}{:>66.2f}%\n".format("Location unknown, default energy mix in "+location+":", "Coal:", coal, "Oil:", oil,
                    "Natural Gas:", gas, "Low Carbon:", low_carbon))
            elif locate.in_US(location):
                sys.stdout.write("{:^80}\n{:<13}{:>66.2f}%\n{:<13}{:>66.2f}%\n{:<13}{:>66.2f}%\n"
                    "{:<13}{:>66.2f}%\n".format("Energy mix in "+location, "Coal:", coal, "Oil:", oil,
                    "Natural Gas:", gas, "Low Carbon:", low_carbon))
        else:
            coal, natural_gas, petroleum, low_carbon = args[1]
            sys.stdout.write("{:^80}\n{:<13}{:>66.2f}%\n{:<13}{:>66.2f}%\n{:<13}{:>66.2f}%\n"
                    "{:<13}{:>66.2f}%\n".format("Energy mix in "+location, "Coal:", coal, "Petroleum:", petroleum,
                    "Natural Gas:", natural_gas, "Low Carbon:", low_carbon))

    elif args[0] == "Emissions":
        emission = args[1]
        log_header('Emissions')
        sys.stdout.write("{:<19}{:>54.2e} kg CO2\n".format("Effective emission:", \
            emission))
        sys.stdout.write("{:<37}{:>42.2e}%\n".format("% of CO2 used in a US"
        " household/day:",convert.carbon_to_home(emission)))
        sys.stdout.write("{:<24}{:>56.2e}\n".format("Equivalent miles driven:", \
            convert.carbon_to_miles(emission)))

    elif args[0] == "Assumed Carbon Equivalencies":
        log_header('Assumed Carbon Equivalencies')
        sys.stdout.write("{:<14} {:>65}\n".format("Coal:", ".3248635 kg CO2/kWh"))
        sys.stdout.write("{:<14} {:>65}\n".format("Oil/Petroleum:", ".23 kg CO2/kWh"))
        sys.stdout.write("{:<14} {:>65}\n".format("Natural gas:", ".0885960 kg CO2/kwh"))



""" MISC UTILS """

def get_data(file):
    file = os.path.join(DIR_PATH, file)
    with open(file) as f:
            data = json.load(f)
    return data

def valid_cpu():
    return os.path.exists(BASE) and bool(os.listdir(BASE))

def valid_gpu():

    # checks that there is a valid gpu: either integrated graphics
    # or nvidia

    try:
        bash_command = "nvidia-smi > /dev/null 2>&1" #we must pipe to ignore error message
        output = subprocess.check_call(['bash','-c', bash_command])
        return True

    except:
        return False
