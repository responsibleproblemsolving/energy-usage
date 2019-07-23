import time
import statistics
from timeit import default_timer as timer
from multiprocessing import Process, Queue
import os
import datetime
import subprocess

import energyusage.utils as utils
import energyusage.convert as convert
import energyusage.locate as locate

DELAY = .1 # in seconds

def func(user_func, q, *args):
    """ Runs the user's function and gets return value """

    value = user_func(*args)
    q.put(value)

def energy(user_func, *args):
    """ Evaluates the kwh needed for your code to run

    Parameters:
        func (function): user's function

    """

    baseline_checks_in_seconds = 2
    files, multiple_cpus = utils.get_files()
    # GPU handling if Nvidia
    is_nvidia_gpu = utils.valid_gpu()

    for i in range(int(baseline_checks_in_seconds / DELAY)):
        if is_nvidia_gpu:
            output = subprocess.check_output(['bash','-c', bash_command])
            output = float(output.decode("utf-8")[:-1])

        files = utils.measure_files(files, DELAY)
        files = utils.update_files(files)
        package = utils.get_total(files, multiple_cpus)
        if package >=0:
            utils.log("Baseline wattage", package)
    utils.newline()

    # Running the process and measuring wattage
    q = Queue()
    p = Process(target = func, args = (user_func, q, *args,))

    start = timer()
    p.start()
    while(p.is_alive()):
        if is_nvidia_gpu:
            output = subprocess.check_output(['bash','-c', bash_command])
            output = float(output.decode("utf-8")[:-1])
            gpu_watts.append(output)

        files = utils.measure_files(files, DELAY)
        files = utils.update_files(files, True)
        package = utils.get_total(files, multiple_cpus)
        if package >=0:
            utils.log("Process wattage", package)
    end = timer()
    for file in files:
        file.process = file.process[1:-1]
        file.baseline = file.baseline[1:-1]
    time = end-start # seconds

    files = utils.average_files(files)
    #process_average = statistics.mean(process_watts)
    timedelta = str(datetime.timedelta(seconds=time)).split('.')[0]


    process_average = utils.get_process_average(files, multiple_cpus)
    baseline_average = utils.get_baseline_average(files, multiple_cpus)
    # Subtracting baseline wattage to get more accurate result
    process_kwh = convert.to_kwh((process_average - baseline_average)*time)

    # Getting the return value of the user's function
    return_value = q.get()

    # Logging
    utils.log("Final Readings", baseline_average, process_average, timedelta)
    return (process_kwh, return_value)


def energy_mix(location):
    """ Gets the energy mix information for a specific location

        Parameters:
            location (str): user's location

        Returns:
            breakdown (list): percentages of each energy type
    """

    if (location == "Unknown" or locate.in_US(location)):
        # Default to U.S. average for unknown location
        if location == "Unknown":
            location = "United States"

        data = utils.get_data("data/json/energy-mix-us.json")
        s = data[location]['mix'] # get state
        coal, oil, gas = s['coal'], s['oil'], s['gas']
        nuclear, hydro, biomass, wind, solar, geo, = \
        s['nuclear'], s['hydro'], s['biomass'], s['wind'], \
        s['solar'], s['geothermal']

        low_carbon = sum([nuclear,hydro,biomass,wind,solar,geo])
        breakdown = [coal, oil, gas, low_carbon]

        return breakdown # list of % of each

    else:
        data = utils.get_data('data/json/energy-mix-intl.json')
        c = data[location] # get country
        total, breakdown =  c['total'], [c['coal'], c['naturalGas'], \
            c['petroleum'], c['lowCarbon']]

        # Get percentages
        breakdown = list(map(lambda x: 100*x/total, breakdown))

        return breakdown # list of % of each


def emissions(process_kwh, breakdown, location):
    """ Calculates the CO2 emitted by the program based on the location

        Parameters:
            process_kwh (int): kWhs used by the process
            breakdown (list): energy mix corresponding to user's location
            location (str): location of user

        Returns:
            emission (float): kilograms of CO2 emitted

    """

    if process_kwh < 0:
        raise OSError("Process wattage lower than baseline wattage. Do not run other processes"
         " during the evaluation, or try evaluating a more resource-intensive process.")

    utils.log("Energy Data", breakdown, location)

    # Case 1: Unknown location, default to US data
    # Case 2: United States location
    if location == "Unknown" or locate.in_US(location):
        if location == "Unknown":
            location = "United States"
        # US Emissions data is in lbs/Mwh
        data = utils.get_data("data/json/us-emissions.json")
        emission = convert.lbs_to_kgs(data[location]*convert.to_Mwh(process_kwh))

    # Case 3: International location
    else:
        # Breaking down energy mix
        coal, natural_gas, petroleum, low_carbon = breakdown
        breakdown = [convert.coal_to_carbon(process_kwh * coal/100),
                     convert.natural_gas_to_carbon(process_kwh * natural_gas/100),
                     convert.petroleum_to_carbon(process_kwh * petroleum/100), 0]
        emission = sum(breakdown)

    utils.log("Emissions", emission)
    return emission

def evaluate(user_func, *args):
    """ Calculates effective emissions of the function

        Parameters:
            func: user inputtted function
    """

    if (utils.valid_cpu()):
        location = locate.get()
        result, return_value = energy(user_func, *args)
        breakdown = energy_mix(location)
        emission = emissions(result, breakdown, location)
        utils.log("Assumed Carbon Equivalencies")
        return result, return_value
    else:
        utils.log("The energy-usage package only works on Linux kernels "
        "with Intel processors that support the RAPL interface. Please try again"
        " on a different machine.")
