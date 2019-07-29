""" UNIT OF MEASUREMENT CONVERSIONS """

def to_joules(ujoules):
    """ Converts from microjoules to joules """

    return ujoules*10**(-6)

def to_kwh(joules):
    """ Converts from watts used in a timeframe (in seconds) to kwh """

    watt_hours = joules / 3600
    return watt_hours / 1000

def to_Mwh(kwh):
    """ Converts from kilowatt-hours to megawatt-hours """
    return (kwh / 1000)

def kwh_to_mmbtu(kwh):
    return kwh * 0.003412

def coal_to_carbon(kwh):
    '''
    Coal: 21.11 mmbtu/metric ton coal × 26.05 kg C/mmbtu
     × 44 kg CO2/12 kg C × 90.89 metric tons coal/railcar
     × 1 metric ton/1,000 kg = 183.29 metric tons CO2/railcar

    Source: EPA
    '''

    return (44/12) * ((kwh_to_mmbtu(kwh) / 21.11) * 26.05)

def natural_gas_to_carbon(kwh):
    '''
    Natural gas: 0.1 mmbtu/1 therm × 14.46 kg C/mmbtu
    × 44 kg CO2/12 kg C × 1 metric ton/1,000 kg
    = 0.0053 metric tons CO2/therm

    Source: EPA
    '''

    return (44/12) * kwh_to_mmbtu(kwh) * 14.46

def petroleum_to_carbon(kwh):
    '''
    Petroleum: .23 kgCO2/kWh

    wtf this is the site of some german prof
    Source:https://www.volker-quaschning.de
    '''

    return .23 * kwh

def lbs_to_kgs(lbs):
    return lbs *  0.45359237



""" CARBON EQUIVALENCY """

def carbon_to_miles(kg_carbon):
    '''
    8.89 × 10-3 metric tons CO2/gallon gasoline ×
    1/22.0 miles per gallon car/truck average ×
    1 CO2, CH4, and N2O/0.988 CO2 = 4.09 x 10-4 metric tons CO2E/mile

    Source: EPA
    '''

    return 4.09 * 10**(-7) * kg_carbon # number of miles driven by avg car

def carbon_to_home(kg_carbon):
    '''
    Total CO2 emissions for energy use per home: 5.734 metric tons CO2 for electricity
    + 2.06 metric tons CO2 for natural gas + 0.26 metric tons CO2 for liquid petroleum gas
     + 0.30 metric tons CO2 for fuel oil  = 8.35 metric tons CO2 per home per year / 52 weeks
     = 160.58 kg CO2/week on average

    Source: EPA
    '''

    return kg_carbon * 10**(-3) / 8.35 / 52 / 7 #percent of CO2 used in an avg US household in a week

def carbon_to_tv(kg_carbon):
    '''
    Gives the amount of minutes of watching a 32-inch LCD flat screen tv required to emit and
    equivalent amount of carbon. Ratio is 0.097 kg CO2 / 1 hour tv
    '''
    return kg_carbon * (1 / .097) * 60
