from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib import colors
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import *
from reportlab.graphics.charts.barcharts import VerticalBarChart
from energyusage.RAPLFile import RAPLFile

import energyusage.convert as convert

year = "2016"

styles = getSampleStyleSheet()
TitleStyle = ParagraphStyle(name='Normal', fontSize=18, alignment= TA_CENTER, fontName="Times-Roman")
HeaderStyle = ParagraphStyle(name='Normal',fontSize=16)
SubheaderStyle = ParagraphStyle(name='Normal', fontName="Times-Roman")
DescriptorStyle = ParagraphStyle(name='Normal',fontSize=14, alignment= TA_CENTER)
BodyTextStyle = styles["BodyText"]
Elements = []


def bold(text):
    return "<b>"+text+"</b>"

def title(text, style=TitleStyle, klass=Paragraph, sep=0.3):
    """ Creates title of report """
    t = klass(bold(text), style)
    Elements.append(t)

def header(text, style=HeaderStyle, klass=Paragraph, sep=0.3, spaceAfter=False):
    """ Creates a section header """
    s = Spacer(0, sep*inch)
    Elements.append(s)
    h = klass(bold(text), style)
    Elements.append(h)
    if spaceAfter:
        s = Spacer(0, sep/1.5*inch)
        Elements.append(s)

def subheader(text, style=SubheaderStyle, klass=Paragraph, sep=0.2):
    """ Creates a subsection header """
    s = Spacer(0, sep*inch)
    Elements.append(s)
    sh = klass(bold(text), style)
    Elements.append(sh)

def descriptor(text, style=SubheaderStyle, klass=Paragraph, sep=0.05, spaceBefore=True, spaceAfter = True, centered = True):
    """ Creates descriptor text for a (sub)section; sp adds space before text """
    s = Spacer(0, 1.5*sep*inch)
    if spaceBefore:
        Elements.append(s)
    if centered:
        d = klass(text, style)
    else:
        d = klass(text, style)
    Elements.append(d)
    if spaceAfter:
        Elements.append(s)

#def reading_and_mix_table(data):



def table(data, header=True):
    no_cols = len(data[0])
    no_rows = len(data)
    col_size = 6.5/no_cols
    t = Table(data,no_cols*[col_size*inch], hAlign='LEFT')
    t.setStyle(TableStyle([('ALIGN', (0,0), (0,-1), "LEFT"),
                       ('ALIGN', (1,0), (-1,-1), "CENTER"),
                       ('INNERGRID',(0,0),(-1,-1),0.25, colors.black),
                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),]))
    if header:
        t.setStyle(TableStyle([('ALIGN',(0,0), (-1,0), "CENTER"),
                               ('FONT', (0,0), (-1,0), "Helvetica-Bold"),
                               ('ALIGN', (0,1), (0, -1), "LEFT"),
                               ('ALIGN', (1,1), (-1, -1), "CENTER"),]))

    Elements.append(t)
def pie_chart(state_emission, breakdown):
    d = Drawing(200, 100)
    pc = Pie()

    data = []
    if state_emission:
        data = ["Coal", "Oil", "Natural Gas", "Low Carbon"]
    else:
        data = ["Coal", "Petroleum", "Natural Gas", "Low Carbon"]

    for i in range(4):
        data[i] += ": " + str(round(breakdown[i], 1)) + "%"

    pc.x = 65
    pc.y = 15
    pc.width = 70
    pc.height = 70
    pc.data = breakdown[:4]
    pc.slices[0].fillColor = colors.Color(.5,.5,.5)
    pc.slices[1].fillColor = colors.red
    pc.slices[2].fillColor = colors.lemonchiffon
    pc.slices[3].fillColor = colors.green
    pc.labels = data
    pc.slices.strokeWidth=0.5
    pc.sideLabels = True
    d.add(pc)
    Elements.append(d)
def bar_graph():
    drawing = Drawing(400, 200)
    data = [
    (13, 5, 20, 22, 37, 45, 19, 4)
    ]
    bc = VerticalBarChart()
    bc.x = 50
    bc.y = 50
    bc.height = 125
    bc.width = 300
    bc.data = data
    bc.strokeColor = colors.black
    bc.valueAxis.valueMin = 0
    bc.valueAxis.valueMax = 50
    bc.valueAxis.valueStep = 10
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 8
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 30
    bc.categoryAxis.categoryNames = ['Jan-99','Feb-99','Mar-99',
    'Apr-99','May-99','Jun-99','Jul-99','Aug-99']
    drawing.add(bc)
    Elements.append(drawing)

def generate(location, watt_averages, breakdown, emission, state_emission, func_info):
    """ Generates pdf report

    Parameters:
        location (str): user's location
        watt_averages (list): list of baseline, total, process wattage averages
        breakdown (list): [% coal, % oil/petroleum, % natural gas, % low carbon]
        emission (float): kgs of CO2 emitted

    """

    # Initializing document
    doc = SimpleDocTemplate("energy-usage-report.pdf",pagesize=landscape(letter))
                        #    rightMargin=1*inch,leftMargin=1*inch,
                        #    topMargin=1*inch,bottomMargin=1*inch)

    title("Energy Usage Report")
    descriptor("Energy usage and carbon emissions information")
    #header("Final Readings")
    descriptor("Readings shown are averages of wattage over the time period", spaceAfter=True)
    baseline_average, process_average, difference_average = watt_averages
    # baseline_average, process_average, difference_average, process_duration = watt_averages

    readings = [['Measurement', 'Wattage'],
                ['Baseline', "{:.2f} watts".format(baseline_average)],
                ['Total', "{:.2f} watts".format(process_average)],
                ['Process', "{:.2f} watts".format(difference_average)]]
    '''
    readings = [['Component', 'Baseline', 'Total', 'Process']]
    for file in raplfiles:
        line = ["{}".format(file.name), "{:.2f} watts".format(file.baseline_average),
                "{:.2f} watts".format(file.process_average),
                "{:.2f} watts".format(file.process_average-file.baseline_average)]
        if "Package" in file.name:
            readings.insert(1, line)
        else:
            readings.append(line)
    '''

    if state_emission:
        coal, oil, natural_gas, low_carbon, total_time = breakdown
        energy_mix = [['Energy Source', 'Percentage'],
                      ['Coal', "{:.2f}%".format(coal)],
                      ['Oil', "{:.2f}%".format(oil)],
                      ['Natural gas', "{:.2f}%".format(natural_gas)],
                      ['Low carbon', "{:.2f}%".format(low_carbon)]]
        source = "eGRID"
        equivs = [['Carbon Equivalency', str(state_emission) + ' lbs/MWh']]
    else:
        coal, petroleum, natural_gas, low_carbon, total_time = breakdown
        energy_mix = [['Energy Source', 'Percentage'],
                      ['Coal',  "{:.2f}%".format(coal)],
                      ['Petroleum', "{:.2f}%".format(petroleum)],
                      ['Natural gas', "{:.2f}%".format(natural_gas)],
                      ['Low carbon', "{:.2f}%".format(low_carbon)]]
        source = "US EIA"
        equivs = [['Coal', '995.725971 kg CO2/MWh'],
                   ['Petroleum', '816.6885263 kg CO2/MWh'],
                   ['Natural gas', '743.8415916 kg CO2/MWh']]

    table(readings)
    header("Energy Data")
    descriptor("Energy mix in {} based on {} {} data".format(location, year, source))
    table(energy_mix)
    emissions = [['Emission', 'Amount'],
                 ['Effective emission', "{:.2e} kg CO2".format(emission)],
                 ['Equivalent miles driven', "{:.2e} miles".format(convert.carbon_to_miles(emission))],
                 ['Equivalent minutes of 32-inch LCD TV watched', "{:.2e} minutes".format(convert.carbon_to_tv(emission))],
                 ['Percentage of CO2 used in a US household/day', \
                   "{:.2e}%".format(convert.carbon_to_home(emission))]]
    header("Emissions", spaceAfter=True)
    table(emissions)
    header("Assumed Carbon Equivalencies", spaceAfter=True)
    # descriptor("Formulas used for determining amount of carbon emissions")
    table(equivs, header=False)
    pie_chart(state_emission, breakdown)
    bar_graph()
    doc.build(Elements)
