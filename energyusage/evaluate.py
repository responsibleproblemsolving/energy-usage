import time
import statistics
from timeit import default_timer as timer
from multiprocessing import Process, Queue
import os
import datetime
import subprocess
import queue
import csv

import utils as utils
import convert as convert
import locate as locate
import report as report
import graph

DELAY = .1 # in seconds

def func(user_func, q, *args):
    """ Runs the user's function and puts return value in queue """

    value = user_func(*args)
    q.put(value)

def energy(user_func, *args, powerLoss = 0.8, year, printToScreen, timeseries):
    """ Evaluates the kwh needed for your code to run

    Parameters:
       user_func (function): user's function

    Returns:
        (process_kwh, return_value, watt_averages)

    """

    baseline_check_seconds = 5
    files, multiple_cpus = utils.get_files()
    is_nvidia_gpu = utils.valid_gpu()
    is_valid_cpu = utils.valid_cpu()

    # GPU handling if Nvidia
    gpu_baseline =[0]
    gpu_process = [0]
    bash_command = "nvidia-smi -i 0 --format=csv,noheader --query-gpu=power.draw"

    time_baseline = []
    reading_baseline_wattage = []

    time_process = []
    reading_process_wattage = []

    with open('baseline_wattage.csv', 'w') as baseline_wattage_file:
        baseline_wattage_writer = csv.writer(baseline_wattage_file)
        baseline_wattage_writer.writerow(["time", "baseline wattage reading"])
        for i in range(int(baseline_check_seconds / DELAY)):
            if is_nvidia_gpu:
                output = subprocess.check_output(['bash','-c', bash_command])
                output = float(output.decode("utf-8")[:-2])
                gpu_baseline.append(output)
            if is_valid_cpu:
                files = utils.measure_files(files, DELAY)
                files = utils.update_files(files)
            else:
                time.sleep(DELAY)
            # Adds the most recent value of GPU; 0 if not Nvidia
            last_reading = utils.get_total(files, multiple_cpus) + gpu_baseline[-1]
            if last_reading >=0 and printToScreen:
                utils.log("Baseline wattage", last_reading)
                time = round(i* DELAY, 1)
                baseline_wattage_writer.writerow([time, last_reading])
                time_baseline.append(time)
                reading_baseline_wattage.append(last_reading)
    if printToScreen:
        utils.newline()

    # Running the process and measuring wattage
    q = Queue()
    p = Process(target = func, args = (user_func, q, *args,))

    start = timer()
    small_delay_counter = 0
    return_value = None
    p.start()
    with open('process_wattage.csv', 'w') as process_wattage_file:
        process_wattage_writer = csv.writer(process_wattage_file)
        process_wattage_writer.writerow(["time", "process wattage reading"])
        while(p.is_alive()):
            # Checking at a faster rate for quick processes
            if (small_delay_counter > DELAY):
                delay = DELAY / 10
                small_delay_counter+=1
            else:
                delay = DELAY
                
            if is_nvidia_gpu:
                output = subprocess.check_output(['bash','-c', bash_command])
                output = float(output.decode("utf-8")[:-2])
                gpu_process.append(output)
            if is_valid_cpu:
                files = utils.measure_files(files, delay)
                files = utils.update_files(files, True)
            else:
                time.sleep(delay)
            # Just output, not added
            last_reading = (utils.get_total(files, multiple_cpus) + gpu_process[-1]) / powerLoss
            if last_reading >=0 and printToScreen:
                utils.log("Process wattage", last_reading)
                time = round(timer()-start, 1)
                process_wattage_writer.writerow([time, last_reading])
                time_process.append(time)
                reading_process_wattage.append(last_reading)
            # Getting the return value of the user's function
            try:
                return_value = q.get_nowait()
                break
            except queue.Empty:
                pass
    p.join()
    end = timer()
    for file in files:
        file.process = file.process[1:-1]
        file.baseline = file.baseline[1:-1]
    if is_nvidia_gpu:
        gpu_baseline_average = statistics.mean(gpu_baseline[2:-1])
        gpu_process_average = statistics.mean(gpu_process[2:-1])
    else:
        gpu_baseline_average = 0
        gpu_process_average = 0

    total_time = end-start # seconds
    # Formatting the time nicely
    timedelta = str(datetime.timedelta(seconds=total_time)).split('.')[0]

    if files[0].process == []:
        raise Exception("Process executed too fast to gather energy consumption")
    files = utils.average_files(files)

    process_average = utils.get_process_average(files, multiple_cpus, gpu_process_average)
    baseline_average = utils.get_baseline_average(files, multiple_cpus, gpu_baseline_average)
    difference_average = process_average - baseline_average
    watt_averages = [baseline_average, process_average, difference_average, timedelta]

    # Subtracting baseline wattage to get more accurate result
    process_kwh = convert.to_kwh((process_average - baseline_average)*total_time) / powerLoss

    if is_nvidia_gpu:
        gpu_file = file("GPU", "")
        gpu_file.create_gpu(gpu_baseline_average, gpu_process_average)
        files.append(file("GPU", ""))

    # Logging
    if printToScreen:
        utils.log("Final Readings", baseline_average, process_average, difference_average, timedelta)
    return (process_kwh, return_value, watt_averages, files, total_time, time_baseline, reading_baseline_wattage, time_process, reading_process_wattage)


def energy_mix(location, year = 2016):
    """ Gets the energy mix information for a specific location

        Parameters:
            location (str): user's location
            location_of_default (str): Specifies which average to use if
            	location cannot be determined

        Returns:
            breakdown (list): percentages of each energy type
    """
    if location == "Unknown":
        location = "United States"

    if locate.in_US(location):
        # Default to U.S. average for unknown location

        data = utils.get_data("data/json/energy-mix-us_" + year + ".json")
        s = data[location]['mix'] # get state
        coal, oil, gas = s['coal'], s['oil'], s['gas']
        nuclear, hydro, biomass, wind, solar, geo, = \
        s['nuclear'], s['hydro'], s['biomass'], s['wind'], \
        s['solar'], s['geothermal']

        low_carbon = sum([nuclear,hydro,biomass,wind,solar,geo])
        breakdown = [coal, oil, gas, low_carbon]

        return breakdown # list of % of each

    else:
        data = utils.get_data("data/json/energy-mix-intl_" + year + ".json")
        c = data[location] # get country
        total, breakdown =  c['total'], [c['coal'], c['petroleum'], \
        c['naturalGas'], c['lowCarbon']]

        # Get percentages
        breakdown = list(map(lambda x: 100*x/total, breakdown))

        return breakdown # list of % of each


def emissions(process_kwh, breakdown, location, year, printToScreen):
    """ Calculates the CO2 emitted by the program based on the location

        Parameters:
            process_kwh (int): kWhs used by the process
            breakdown (list): energy mix corresponding to user's location
            location (str): location of user

        Returns:
            emission (float): kilograms of CO2 emitted
            state_emission (float): lbs CO2 per MWh; 0 if international location

    """

    if process_kwh < 0:
        raise OSError("Process wattage lower than baseline wattage. Do not run other processes"
         " during the evaluation, or try evaluating a more resource-intensive process.")
    if printToScreen:
        utils.log("Energy Data", breakdown, location)
    state_emission = 0

    # Case 1: Unknown location, default to US data
    if location == "Unknown":
        location = "United States"
    # Case 2: United States location
    if locate.in_US(location):
        # US Emissions data is in lbs/Mwh
        data = utils.get_data("data/json/us-emissions_" + year + ".json")
        state_emission = data[location]
        emission = convert.lbs_to_kgs(state_emission*convert.to_MWh(process_kwh))

    # Case 3: International location
    else:
        # Breaking down energy mix
        coal, petroleum, natural_gas, low_carbon = breakdown
        breakdown = [convert.coal_to_carbon(process_kwh * coal/100),
                     convert.petroleum_to_carbon(process_kwh * petroleum/100),
                     convert.natural_gas_to_carbon(process_kwh * natural_gas/100), 0]
        emission = sum(breakdown)
    if printToScreen:
        utils.log("Emissions", emission)
    return (emission, state_emission)


#OLD VERSION: US, EU, Rest comparison
def old_emissions_comparison(process_kwh, year, default_location, printToScreen):
      # Calculates emissions in different locations

    intl_data = utils.get_data("data/json/energy-mix-intl_" + year + ".json")
    global_emissions, europe_emissions, us_emissions = [], [], []
    # Handling international
    for country in intl_data:
           c = intl_data[country]
           total, breakdown = c['total'], [c['coal'], c['petroleum'], \
           c['naturalGas'], c['lowCarbon']]
           if isinstance(total, float) and float(total) > 0:
               breakdown = list(map(lambda x: 100*x/total, breakdown))
               coal, petroleum, natural_gas, low_carbon = breakdown
               breakdown = [convert.coal_to_carbon(process_kwh * coal/100),
                    convert.petroleum_to_carbon(process_kwh * petroleum/100),
                    convert.natural_gas_to_carbon(process_kwh * natural_gas/100), 0]
               emission = sum(breakdown)
               if locate.in_Europe(country):
                   europe_emissions.append((country,emission))
               else:
                   global_emissions.append((country,emission))

    global_emissions.sort(key=lambda x: x[1])
    europe_emissions.sort(key=lambda x: x[1])

    # Handling US
    us_data = utils.get_data("data/json/us-emissions_" + year + ".json")
    for state in us_data:
        if ((state != "United States") and state != "_units"):
            if us_data[state] != "lbs/MWh":
                emission = convert.lbs_to_kgs(us_data[state]*convert.to_MWh(process_kwh))
                us_emissions.append((state, emission))
    us_emissions.sort(key=lambda x: x[1])

    max_global, max_europe, max_us = global_emissions[len(global_emissions)-1], \
        europe_emissions[len(europe_emissions)-1], us_emissions[len(us_emissions)-1]
    median_global, median_europe, median_us = global_emissions[len(global_emissions)//2], \
        europe_emissions[len(europe_emissions)//2], us_emissions[len(us_emissions)//2]
    min_global, min_europe, min_us= global_emissions[0], europe_emissions[0], us_emissions[0]
    if default_location and printToScreen:
        utils.log('Emissions Comparison default', max_global, median_global, min_global, max_europe, \
            median_europe, min_europe, max_us, median_us, min_us)
    default_emissions = [max_global, median_global, min_global, max_europe, \
        median_europe, min_europe, max_us, median_us, min_us]
    return default_emissions


def emissions_comparison(process_kwh, locations, year, default_location, printToScreen):
    # TODO: Disambiguation of states such as Georgia, US and Georgia
    intl_data = utils.get_data("data/json/energy-mix-intl_" + year + ".json")
    us_data = utils.get_data("data/json/us-emissions_" + year + ".json")
    emissions = [] # list of tuples w/ format (location, emission)

    for location in locations:
        if locate.in_US(location):
            emission = convert.lbs_to_kgs(us_data[location]*convert.to_MWh(process_kwh))
            emissions.append((location, emission))
        else:
             c = intl_data[location]
             total, breakdown = c['total'], [c['coal'], c['petroleum'], \
             c['naturalGas'], c['lowCarbon']]
             if isinstance(total, float) and float(total) > 0:
                 breakdown = list(map(lambda x: 100*x/total, breakdown))
                 coal, petroleum, natural_gas, low_carbon = breakdown
                 breakdown = [convert.coal_to_carbon(process_kwh * coal/100),
                      convert.petroleum_to_carbon(process_kwh * petroleum/100),
                      convert.natural_gas_to_carbon(process_kwh * natural_gas/100), 0]
                 emission = sum(breakdown)
                 emissions.append((location,emission))

    if emissions != [] and not default_location and printToScreen:
        utils.log('Emissions Comparison', emissions)
    return emissions


def get_comparison_data(result, locations, year, printToScreen):
    geo = locate.get_location_information()
    location = locate.get(printToScreen, geo)
    default_location = False
    if locations == ["Mongolia", "Iceland", "Switzerland"]:
        default_location = True
    comparison_values = emissions_comparison(result, locations, year, default_location, printToScreen)
    default_emissions = old_emissions_comparison(result, year, default_location, printToScreen)
    return (location, default_location, comparison_values, default_emissions)

def png_bar_chart(location, emission, default_emissions):
    default_emissions_list = []
    for i in range(0, 9):
        rounded_default_emission = float(format((default_emissions[i])[1], '.3g'))
        default_emissions_list.append(rounded_default_emission)
    global_dict = {"Mongolia" : default_emissions_list[0], "South Korea": default_emissions_list[1], "Bhutan" : default_emissions_list[2]}
    eu_dict = {"Kosovo" : default_emissions_list[3], "Ukraine" : default_emissions_list[4], "Iceland" : default_emissions_list[5]}
    us_dict = {"Wyoming" : default_emissions_list[6], "Mississippi" : default_emissions_list[7], "Vermont" : default_emissions_list[8]}
    graph.make_comparison_bar_charts(location, emission, us_dict, eu_dict, global_dict)

def evaluate(user_func, *args, pdf=False, png = False, timeseries=False, powerLoss=0.8, energyOutput=False, \
locations=["Mongolia", "Iceland", "Switzerland"], year="2016", printToScreen = True):
    """ Calculates effective emissions of the function

        Parameters:
            user_func: user's function + associated args
            pdf (bool): whether a PDF report should be generated
            powerLoss (float): PSU efficiency rating
            energyOutput (bool): return value also includes information about energy usage, not just function's return
            locations (list of strings): list of locations to be compared
            year (str): year of dataset to be used
            printToScreen (bool): get information in the command line

    """
    try:
        utils.setGlobal(printToScreen)
        if (utils.valid_cpu() or utils.valid_gpu()):
            result, return_value, watt_averages, files, total_time, time_baseline, reading_baseline_wattage, time_process, reading_process_wattage = energy(user_func, *args, powerLoss = powerLoss, year = year, \
                                                                            printToScreen = printToScreen, timeseries = timeseries)
            location, default_location, comparison_values, default_emissions = get_comparison_data(result, locations, year, printToScreen)
            breakdown = energy_mix(location, year = year)
            emission, state_emission = emissions(result, breakdown, location, year, printToScreen)
            if printToScreen:
                utils.log("Assumed Carbon Equivalencies")
            if printToScreen:
                utils.log("Process Energy", result)
            func_info = [user_func.__name__, *args]
            kwh_and_emissions = [result, emission, state_emission]
            if pdf:
                #pass
                report.generate(location, watt_averages, breakdown, kwh_and_emissions, \
                            func_info, comparison_values, default_emissions, default_location)
            if png:
                # generate energy mix pie chart
                energy_dict = {"Coal" : breakdown[0], "Petroleum"  : breakdown[1], "Natural Gas" : breakdown[2], "Low Carbon" : breakdown[3]}
                figtitle = "Location: " + location
                location_split = location.split()
                filename = location_split[0]
                for i in range(1, len(location_split)):
                    filename += "_" + location_split[i]
                    filename += ".png"
                if locate.in_US(location):
                    energy_dict["Oil"] = energy_dict.pop("Petroleum")
                    figtitle = figtitle + ", USA"
                graph.pie_chart(energy_dict, figtitle, filename)
                # generate emissions comparison bar charts
                png_bar_chart(location, emission, default_emissions)
            if timeseries:
                graph.timeseries(time_baseline, reading_baseline_wattage, "Baseline Wattage Timeseries")
                graph.timeseries(time_process, reading_process_wattage, "Process Wattage Timeseries")
            if energyOutput:
                return (total_time, result, return_value)
            else:
                return return_value
            
        else:
            utils.log("The energy-usage package only works on Linux kernels "
                      "with Intel processors that support the RAPL interface and/or machines with"
        " an Nvidia GPU. Please try again on a different machine.")
    except Exception as e:
        print("\n" + str(e) + ". Try running a more GPU-intensive program.")
