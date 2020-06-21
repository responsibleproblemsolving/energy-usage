import locate as locate
import report as report
import evaluate as evaluate

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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

    report.title("Energy Usage Report", Elements)

    report.report_header(kwh, emission, Elements)
    report.report_equivalents(emission, Elements)
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
    report.title("Energy Usage Report", Elements)
    report.report_equivalents(emission, Elements)

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
    report.title("Energy Usage Report", Elements)
    report_comparisons(kwh, emission, comparison_region, Elements)

    doc.build(Elements)
