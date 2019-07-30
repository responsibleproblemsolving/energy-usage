import math
import sys
import operator
import time
import json
import os
import re
import statistics
import subprocess

import energyusage.convert as convert
import energyusage.locate as locate
from energyusage.RAPLFile import RAPLFile

BASE = "/sys/class/powercap/"
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

def get_process_average(raplfiles, multiple_cpus, gpu):
    total = 0
    if multiple_cpus:

        for file in raplfiles:
            if "CPU" in file.name:
                total+= file.process_average
    else:
        for file in raplfiles:
            if file.name == "Package":
                total+=file.process_average
    return total + gpu

def get_baseline_average(raplfiles, multiple_cpus, gpu):
    total = 0
    if multiple_cpus:
        for file in raplfiles:
            if "CPU" in file.name:
                total+= file.baseline_average
    else:
        for file in raplfiles:
            if file.name == "Package":
                total+=file.baseline_average
    return total + gpu

def get_total(raplfiles, multiple_cpus):
    total = 0
    if multiple_cpus:
        for file in raplfiles:
            if "CPU" in file.name:
                total+= file.recent
    else:
        for file in raplfiles:
            if file.name == "Package":
                total =  file.recent
    if (total):
        return total
    return 0

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
    files = list(map(lambda x: end(x, delay), files)) # need lambda to pass in delay
    return files

def reformat(name, multiple_cpus):
    """ Renames the RAPL files for better readability/understanding """
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
    """ Gets all the RAPL files with their names on the machine

        Returns:
            filenames (list): list of RAPLFiles
    """
    # Removing the intel-rapl folder that has no info
    files = list(filter(lambda x: ':' in x, os.listdir(BASE)))
    names = {}
    cpu_count = 0
    multiple_cpus = False
    for file in files:
        if (re.fullmatch("intel-rapl:.", file)):
            cpu_count += 1

    if cpu_count > 1:
        multiple_cpus = True

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
        baseline_average, process_average, difference_average, timedelta = args[1], args[2], args[3], args[4]
        delete_last_lines()
        log_header(args[0])
        sys.stdout.write("{:<25} {:>48.2f} {:5<}\n".format("Average baseline wattage:", baseline_average, "watts"))
        sys.stdout.write("{:<25} {:>48.2f} {:5<}\n".format("Average total wattage:", process_average, "watts"))
        sys.stdout.write("{:<25} {:>48.2f} {:5<}\n".format("Average process wattage:", difference_average, "watts"))
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
        sys.stdout.write("{:<24}{:>50.2e} miles\n".format("Equivalent miles driven:", \
            convert.carbon_to_miles(emission)))
        sys.stdout.write("{:<45}{:>27.2e} minutes\n".format("Equivalent minutes of 32-inch LCD TV watched:", \
            convert.carbon_to_tv(emission)))
        sys.stdout.write("{:<45}{:>34.2e}%\n".format("Percentage of CO2 used in a US"
        " household/day:",convert.carbon_to_home(emission)))


    elif args[0] == "Assumed Carbon Equivalencies":
        log_header('Assumed Carbon Equivalencies')
        sys.stdout.write("{:<14} {:>65}\n".format("Coal:", "0.3248635 kg CO2/kwh"))
        sys.stdout.write("{:<14} {:>65}\n".format("Petroleum:", "0.23 kg CO2/kwh"))
        sys.stdout.write("{:<14} {:>65}\n".format("Natural gas:", "0.0885960 kg CO2/kwh"))

    else:
        sys.stdout.write(args[0])


""" MISC UTILS """

def get_data(file):
    file = os.path.join(DIR_PATH, file)
    with open(file) as f:
            data = json.load(f)
    return data

def valid_cpu():
    return os.path.exists(BASE) and bool(os.listdir(BASE))

def valid_gpu():
    """ Checks that there is a valid Nvidia GPU """


    try:
        bash_command = "nvidia-smi > /dev/null 2>&1" #we must pipe to ignore error message
        output = subprocess.check_call(['bash','-c', bash_command])
        return True

    except:
        return False
