import utils as utils
import convert as convert
import locate as locate
import report as report
import evaluate as evaluate

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import *  # not used?
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.textlabels import Label

year = "2016"

styles = getSampleStyleSheet()
Elements = []

def generate(kwh, emission):
    # TODO: remove state_emission and just use location
    # Initializing document
    doc = SimpleDocTemplate("energy-usage-report.pdf",pagesize=landscape(letter), topMargin=.3*inch)

    report.title("Energy Usage Report")

    effective_emission = Paragraph('<font face="times" size=12>{:.2e} kg CO<sub rise = -10 size = 8>2 </sub></font>'.format(emission), style = styles["Normal"])
    # Total kWhs used and effective emissions
    kwh_and_emissions_data = [["Total kilowatt hours used:", "{:.2e} kWh".format(kwh)],
                              ["Effective emissions:", effective_emission]]

    report.kwh_and_emissions_table(kwh_and_emissions_data)

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

    report.equivs_and_emission_equivs(equivs_data, emissions_data)


    printToScreen = True
    location = locate.get(printToScreen)
    locations=["Mongolia", "Iceland", "Switzerland"] # why these countries? Shoule we let user input locations?
    default_location = False
    if locations == ["Mongolia", "Iceland", "Switzerland"]:
        default_location = True
    comparison_values = evaluate.emissions_comparison(kwh, locations, year, default_location, printToScreen)

    default_emissions = evaluate.old_emissions_comparison(kwh, year, default_location, printToScreen)
    report.comparison_graphs(comparison_values, location, emission, default_emissions, default_location)
    doc.build(Elements)
