import sys
import time
import statistics
from timeit import default_timer as timer
from multiprocessing import Process
import datetime
import os

import utils
import convert
import locate

DELAY = .1 # in seconds



""" EMISSION UTILS """

#TO DO: refactor the code
def energy(func, *args):
    """ Evaluates the kwh needed for your code to run """

    packages = utils.get_num_packages()
    # Get baseline wattage reading (FOR WHAT? PKG for now, DELAY? default .1 second)
    baseline_watts = []
    for i in range(50):
        measurement = utils.measure_packages(packages, DELAY) / DELAY # dividing by delay to give per second reading
        # LOGGING
        sys.stdout.write("\r{:<17} {:>56.2f} {:5<}".format("Baseline wattage:", measurement, "watts"))
        baseline_watts.append(measurement)
    sys.stdout.write("\n")

    baseline_average = statistics.mean(baseline_watts)

    # Running the process and measuring wattage
    p = Process(target = func, args = (*args,))
    process_watts = []
    start = timer()
    p.start()
    while(p.is_alive()):
        measurement = utils.measure_packages(packages, DELAY) / DELAY
        if measurement > 0: # in case file reaches end D:
            # LOGGING
            sys.stdout.write("\r{:<17} {:>56.2f} {:5<}".format("Process wattage:", measurement, "watts"))
            process_watts.append(measurement)
    sys.stdout.write("\n")
    end = timer()
    time = end-start # seconds
    process_average = statistics.mean(process_watts)


    # Subtracting baseline wattage to get more accurate result
    process_kwh = convert.to_kwh((process_average - baseline_average)*time, time)

    # LOGGING
    utils.delete_last_lines()
    utils.log_header('Final Readings')
    sys.stdout.write("{:<25} {:>48.2f} {:5<}\n".format("Average baseline wattage:", baseline_average, "watts"))
    sys.stdout.write("{:<25} {:>48.2f} {:5<}\n".format("Average process wattage:", process_average, "watts"))
    sys.stdout.write("{:<17} {:>62}\n".format("Process duration:", str(datetime.timedelta(seconds=time)).split('.')[0]))

    return process_kwh

def emissions(process_kwh, breakdown, location):
    """ Calculates the CO2 emitted by the program based on the location

        Parameters:
            process_kwh (int)
            breakdown (list)
            location (str)

        Returns:
            emission (float): kilograms of CO2 emitted

    """

    if process_kwh < 0:
        raise OSError("Process wattage lower than baseline wattage. Do not run other processes"
         " during the evaluation, or try evaluating a more resource-intensive process.")


    # Case 1: Unknown location, default to US data
    # Case 2: United States location
    if location == "Unknown" or locate.in_US(location):
        coal, oil, gas, low_carbon = breakdown

        # Breaking down energy mix
        if location == "Unknown":
            location = "United States"
            utils.log_header('Energy Data')
            sys.stdout.write("{:^80}\n{:<13}{:>66.2f}%\n{:<13}{:>66.2f}%\n{:<13}{:>66.2f}%\n"
                "{:<13}{:>66.2f}%\n".format("Location unknown, default energy mix in "+location+":", "Coal:", coal, "Oil:", oil,
                "Natural Gas:", gas, "Low Carbon:", low_carbon))

        else:
            utils.log_header('Energy Data')
            sys.stdout.write("{:^80}\n{:<13}{:>66.2f}%\n{:<13}{:>66.2f}%\n{:<13}{:>66.2f}%\n"
                "{:<13}{:>66.2f}%\n".format("Energy mix in "+location, "Coal:", coal, "Oil:", oil,
                "Natural Gas:", gas, "Low Carbon:", low_carbon))

        # US Emissions data is in lbs

        data = utils.get_data("../data/json/us-emissions.json")
        emission = convert.lbs_to_kgs(data[location]*convert.to_Mwh(process_kwh))
        utils.log_emission(emission)
        return emission

    # Case 3: International location
    else:
        # Breaking down energy mix
        coal, natural_gas, petroleum, low_carbon = breakdown
        utils.log_header('Energy Data')
        sys.stdout.write("{:^80}\n{:<13}{:>66.2f}%\n{:<13}{:>66.2f}%\n{:<13}{:>66.2f}%\n"
                "{:<13}{:>66.2f}%\n".format("Energy mix in "+location, "Coal:", coal, "Petroleum:", petroleum,
                "Natural Gas:", natural_gas, "Low Carbon:", low_carbon))

        breakdown = [convert.coal_to_carbon(process_kwh * coal/100),
                     convert.natural_gas_to_carbon(process_kwh * natural_gas/100),
                     convert.petroleum_to_carbon(process_kwh * petroleum/100), 0]

        emission = sum(breakdown)
        utils.log_emission(emission)
        return emission


def energy_mix(location):
    """ Gets the energy mix information for a specific location

        Returns:
            breakdown (list): percentages of each energy type
    """

    if (location == "Unknown" or locate.in_US(location)):
        # Default to U.S. average for unknown location
        if location == "Unknown":
            location = "United States"

        
        data = utils.get_data("../data/json/energy-mix-us.json")
        s = data[location]['mix'] # get state
        coal, oil, gas = s['coal'], s['oil'], s['gas']
        nuclear, hydro, biomass, wind, solar, geo, \
        unknown = s['nuclear'], s['hydro'], s['biomass'], \
        s['wind'], s['solar'], s['geothermal'], s['unknown']

        low_carbon = sum([nuclear,hydro,biomass,wind,solar,geo])
        breakdown = [coal, oil, gas, low_carbon]

        return breakdown # list of % of each

    else:
        data = utils.get_data('../data/json/energy-mix-intl.json')
        c = data[location] # get country
        total, breakdown =  c['total'], [c['coal'], c['naturalGas'], \
            c['petroleum'], c['lowCarbon']]

        # Get percentages
        breakdown = list(map(lambda x: 100*x/total, breakdown))

        return breakdown # list of % of each

def evaluate(func, *args):
    if (utils.valid_system()):
        location = locate.get()
        result = energy(func, *args)
        breakdown = energy_mix(location)
        emission = emissions(result, breakdown, location)
        utils.log_formulas()
    else:
        utils.log_invalid_sys()
