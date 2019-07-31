from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib import colors
from energyusage.RAPLFile import RAPLFile

import energyusage.convert as convert

year = "2016"
equivs = [['Coal', '0.3248635 kg CO2/kwh'],
           ['Petroleum', '0.23 kg CO2/kwh'],
           ['Natural gas', '0.0885960 kg CO2/kwh']]

styles = getSampleStyleSheet()
TitleStyle = ParagraphStyle(name='Normal', fontSize=16, alignment= TA_CENTER)
HeaderStyle = ParagraphStyle(name='Normal',fontSize=14)
SubheaderStyle = ParagraphStyle(name='Normal',fontSize=12)
DescriptorStyle = styles["BodyText"]
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

def descriptor(text, style=DescriptorStyle, klass=Paragraph, sep=0.05, spaceBefore=True, spaceAfter = True):
    """ Creates descriptor text for a (sub)section; sp adds space before text """
    s = Spacer(0, 1.5*sep*inch)
    if spaceBefore:
        Elements.append(s)
    d = klass(text, style)
    Elements.append(d)
    if spaceAfter:
        Elements.append(s)

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


def generate(location, watt_averages, breakdown, emission, state_emission):
    """ Generates pdf report

    Parameters:
        location (str): user's location
        watt_averages (list): list of baseline, total, process wattage averages
        breakdown (list): [% coal, % oil/petroleum, % natural gas, % low carbon]
        emission (float): kgs of CO2 emitted

    """

    # Initializing document
    doc = SimpleDocTemplate("energy-usage-report.pdf",pagesize=letter,
                            rightMargin=1*inch,leftMargin=1*inch,
                            topMargin=1*inch,bottomMargin=1*inch)

    title("Energy Usage Report")
    header("Final Readings")
    descriptor("Readings shown are averages of wattage over the time period", spaceAfter=True)
    baseline_average, process_average, difference_average = watt_averages

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
        coal, oil, natural_gas, low_carbon = breakdown
        energy_mix = [['Energy Source', 'Percentage'],
                      ['Coal', "{}%".format(coal)],
                      ['Oil', "{}%".format(oil)],
                      ['Natural gas', "{}%".format(natural_gas)],
                      ['Low carbon', "{}%".format(low_carbon)]]
        source = "eGRID"
        equivs = [['Carbon Equivalency', str(state_emission) + ' lbs/MWh']]
    else:
        coal, petroleum, natural_gas, low_carbon = breakdown
        energy_mix = [['Coal',  "{}%".format(coal)],
                      ['Petroleum', "{}%".format(petroleum)],
                      ['Natural gas', "{}%".format(natural_gas)],
                      ['Low carbon', "{}%".format(low_carbon)]]
        source = "US EIA"

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
    doc.build(Elements)
