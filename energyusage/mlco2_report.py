import utils as utils
import convert as convert
import locate as locate
import report as report
import evaluate as evaluate

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def report_header(kwh, emission, Elements):
    report.title("Energy Usage Report", Elements)

    effective_emission = Paragraph('<font face="times" size=12>{:.2e} kg CO<sub rise = -10 size = 8>2 </sub></font>'.format(emission), style = styles["Normal"])
    # Total kWhs used and effective emissions
    kwh_and_emissions_data = [["Total kilowatt hours used:", "{:.2e} kWh".format(kwh)],
                              ["Effective emissions:", effective_emission]]

    report.kwh_and_emissions_table(kwh_and_emissions_data, Elements)

def report_equivalents(emission, Elements):
    # Equivalencies and CO2 emission equivalents
    per_house = Paragraph('<font face="times" size=12>% of CO<sub rise = -10 size = 8>2</sub> per US house/day:</font>'.format(emission), style = styles["Normal"])
    emissions_data = [
                 ['Miles driven:', "{:.2e} miles".format(convert.carbon_to_miles(emission))],
                 ['Min. of 32-in. LCD TV:', "{:.2e} minutes".format(convert.carbon_to_tv(emission))],
                 [per_house, \
                   "{:.2e}%".format(convert.carbon_to_home(emission))]]

    coal_para = Paragraph('<font face="times" size=12>996 kg CO<sub rise = -10 size = 8>2 </sub>/MWh</font>', style = styles["Normal"])
    oil_para = Paragraph('<font face="times" size=12>817 kg CO<sub rise = -10 size = 8>2 </sub>/MWh</font>', style = styles["Normal"])
    gas_para = Paragraph('<font face="times" size=12>744 kg CO<sub rise = -10 size = 8>2 </sub>/MWh</font>', style = styles["Normal"])
    low_para = Paragraph('<font face="times" size=12>0 kg CO<sub rise = -10 size = 8>2 </sub>/MWh</font>', style = styles["Normal"])

    equivs_data = [['Coal:', coal_para],
                   ['Petroleum:', oil_para],
                   ['Natural gas:', gas_para],
                   ['Low carbon:', low_para]]

    report.equivs_and_emission_equivs(equivs_data, emissions_data, Elements)

    utils.log("Assumed Carbon Equivalencies")
    utils.log("Emissions", emission)

def report_comparisons(kwh, emission, comparison_region, Elements):
    """ Generates the comparison bar charts
    Parameters:
        kwh: energy consumption
        emission: co2 emission
        comparison_region: "all", "Global", "Europe", or "United States"
    """
    year = "2016"
    printToScreen = True
    geo = locate.get_location_information()
    location = locate.get(printToScreen, geo)
    locations=["Mongolia", "Iceland", "Switzerland"]
    default_location = False
    if locations == ["Mongolia", "Iceland", "Switzerland"]:
        default_location = True
    comparison_values = evaluate.emissions_comparison(kwh, locations, year, default_location, printToScreen)
    default_emissions = evaluate.old_emissions_comparison(kwh, year, default_location, printToScreen)
    report.comparison_graphs(comparison_values, location, emission, default_emissions, default_location, Elements, comparison_region)

def report_all(kwh, emission):
    # TODO: remove state_emission and just use location
    """ Generates the entire pdf report
    Parameters:
        kwh: energy consumption
        emission: co2 emission
    """
    Elements = []
    # Initializing document
    doc = SimpleDocTemplate("energy-usage-report.pdf",pagesize=landscape(letter), topMargin=.3*inch)

    report_header(kwh, emission, Elements)
    report_equivalents(emission, Elements)
    comparison_region = "all"
    report_comparisons(kwh, emission, comparison_region, Elements)

    doc.build(Elements)

def report_without_charts(kwh, emission):
    """ Generates pdf report with assumed carbon equivalencies and co2 emission equivalents
    Parameters:
        kwh: energy consumption
        emission: co2 emission
    """
    Elements = []
    # Initializing document
    doc = SimpleDocTemplate("energy-usage-report-emission-equivalents.pdf",pagesize=landscape(letter), topMargin=.3*inch)
    report_equivalents(emission, Elements)

    doc.build(Elements)

def report_with_charts(kwh, emission, comparison_region="all"):
    """ Generates pdf report with comparison graphs that shows the co2 emission \
    for the function if the computation had been performed elsewhere
    Parameters:
        kwh: energy consumption
        emission: co2 emission
        comparison_region: "all" (default), "Global", "Europe", or "United States"
    """
    Elements = []
    # Initializing document
    doc = SimpleDocTemplate("energy-usage-report-comparison.pdf",pagesize=landscape(letter), topMargin=.3*inch)
    report_comparisons(kwh, emission, comparison_region, Elements)

    doc.build(Elements)
