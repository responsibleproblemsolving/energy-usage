from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib import colors
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import *
from energyusage.RAPLFile import RAPLFile


import energyusage.convert as convert

year = "2016"

styles = getSampleStyleSheet()
TitleStyle = ParagraphStyle(name='Normal', fontSize=16, alignment= TA_CENTER, fontName="Times-Bold")
SubtitleStyle = ParagraphStyle(name='Normal',fontSize=12, alignment= TA_CENTER, fontName="Times-Roman")
# MonospacedSubtitleStyle = ParagraphStyle(name='Normal',fontSize=12, alignment= TA_CENTER, fontName="Courier")
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

def subtitle(text, style=SubtitleStyle, klass=Paragraph, sep=0.1, spaceBefore=True, spaceAfter = True):
    """ Creates descriptor text for a (sub)section; sp adds space before text """
    s = Spacer(0, 1.5*sep*inch)
    if spaceBefore:
        Elements.append(s)
    d = klass(text, style)
    Elements.append(d)
    if spaceAfter:
        Elements.append(s)


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





def readings_and_mix_table(reading_data, mix_data, breakdown, state_emission):
    no_rows = 1
    no_cols = 1
    col_size = 4.5

    readings_table = Table(reading_data, no_cols*[col_size/2*inch], 5*[0.25*inch],hAlign="LEFT")
    readings_table.setStyle(TableStyle([('FONT', (0,0), (-1,-1), "Times-Roman"),
                                         ('FONT', (0,0), (-1,0), "Times-Bold"),
                                         ('FONTSIZE', (0,0), (-1,-1), 12),
                                         ('FONTSIZE', (0,0), (-1,0), 13),
                                         ('ALIGN', (0,0), (0,-1), "RIGHT"),
                                         ('VALIGN', (-1,-1), (-1,-1), "TOP")]))


    d = Drawing(100, 100)
    pc = Pie()

    data = []
    if state_emission:
        data = ["Coal", "Oil", "Natural Gas", "Low Carbon"]
    else:
        data = ["Coal", "Petroleum", "Natural Gas", "Low Carbon"]

    for i in range(4):
        data[i] += ": " + str(round(breakdown[i], 1)) + "%"

    pc.x = 45
    pc.y = 0
    pc.width = 55
    pc.height = 55
    pc.data = breakdown[:4]
    pc.slices[0].fillColor = colors.black
    pc.slices[1].fillColor = colors.red
    pc.slices[2].fillColor = colors.lemonchiffon
    pc.slices[3].fillColor = colors.green
    pc.labels = data
    pc.slices.strokeWidth=0.5
    pc.sideLabels = True
    d.add(pc)


    mix_data = [['Energy Mix Data'], [d]]
    mix_table = Table(mix_data, no_cols*[col_size/2*inch], [.25*inch, 1*inch], hAlign="RIGHT")
    mix_table.setStyle(TableStyle([('FONT', (0,0), (0,0), "Times-Bold"),
                                    ('FONTSIZE', (0,0), (0,0), 13),
                                    ('ALIGN', (0,0), (0,0), "LEFT")]))


    table_data = [(readings_table, mix_table)]
    t = Table(table_data, no_cols*[col_size*inch], hAlign='CENTER')
    t.setStyle(TableStyle([('VALIGN', (-1,-1), (-1,-1), "TOP")]))
    Elements.append(t)


def kwh_and_emissions_table(data):

    # add some space
    no_rows = 1
    no_cols = 2
    col_size = 4

    t = Table(data, no_cols*[col_size*inch],[.25*inch, .25*inch], hAlign="CENTER")
    t.setStyle([('FONT',(0,0),(-1,-1),"Times-Roman"),
                ('FONT',(0,0),(0,0),"Times-Bold"),
                ('FONTSIZE', (0,0), (-1,-1), 12),
                ('ALIGN', (0,0), (0,-1), "RIGHT"),
                ('ALIGN',(1,1),(1,-1), "LEFT")])
    Elements.append(t)




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


def generate(location, watt_averages, breakdown, kwh_and_emissions, func_info):
    # TODO: remove state_emission and just use location
    """ Generates pdf report

    Parameters:
        location (str): user's location
        watt_averages (list): list of baseline, total, process wattage averages
        breakdown (list): [% coal, % oil/petroleum, % natural gas, % low carbon]
        emission (float): kgs of CO2 emitted

    """

    kwh, emission, state_emission = kwh_and_emissions
    baseline_average, process_average, difference_average, process_duration = watt_averages


    # Initializing document
    doc = SimpleDocTemplate("energy-usage-report.pdf",pagesize=landscape(letter))
                        #    rightMargin=1*inch,leftMargin=1*inch,
                        #    topMargin=1*inch,bottomMargin=1*inch)

    title("Energy Usage Report")

    # Handling header with function name and arguments
    func_name, *func_args = func_info
    info_text = " for the function " + func_name
    if len(func_args) > 0:
        if len(func_args) == 1:
            info_text += " with the input " + str(func_args[0]) + "."
        else:
            info_text += " with the inputs "
            for arg in func_args:
                info_text += arg + ","
            info_text = info_text[len(info_text)-1] + "."
    else:
        info_text += "."


    subtitle("Energy usage and carbon emissions" + info_text, spaceBefore=True)

    readings_data = [['Energy Usage Readings', ''],
                ['Average baseline wattage:', "{:.2f} watts".format(baseline_average)],
                ['Average total wattage:', "{:.2f} watts".format(process_average)],
                ['Average process wattage:', "{:.2f} watts".format(difference_average)],
                ['Process duration:', process_duration]]

    if state_emission:
        coal, oil, natural_gas, low_carbon = breakdown
        mix_data = [['Energy Mix Data', ''],
                    ['Coal', "{:.2f}%".format(coal)],
                    ['Oil', "{:.2f}%".format(oil)],
                    ['Natural gas', "{:.2f}%".format(natural_gas)],
                    ['Low carbon', "{:.2f}%".format(low_carbon)]]
        source = "eGRID"
        equivs = [['Carbon Equivalency', str(state_emission) + ' lbs/MWh']]
    else:
        coal, petroleum, natural_gas, low_carbon = breakdown
        mix_data = [['Energy Mix Data', ''],
                    ['Coal',  "{:.2f}%".format(coal)],
                    ['Petroleum', "{:.2f}%".format(petroleum)],
                    ['Natural gas', "{:.2f}%".format(natural_gas)],
                    ['Low carbon', "{:.2f}%".format(low_carbon)]]
        source = "US EIA"
        equivs = [['Coal', '996 kg CO2/MWh'],
                   ['Petroleum', '817 kg CO2/MWh'],
                   ['Natural gas', '744 kg CO2/MWh'],
                   ['Low carbon', '0 kg CO2/MWh']]


    readings_and_mix_table(readings_data, mix_data, breakdown, state_emission)

    kwh_and_emissions_data = [["Total kilowatt hours used:", "{:.2e} kWh".format(kwh)],
                              ["Effective emissions:", "{:.2e} kg CO2".format(emission)]]

    kwh_and_emissions_table(kwh_and_emissions_data)







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
                      ['Coal', "{:.2f}%".format(coal)],
                      ['Oil', "{:.2f}%".format(oil)],
                      ['Natural gas', "{:.2f}%".format(natural_gas)],
                      ['Low carbon', "{:.2f}%".format(low_carbon)]]
        source = "eGRID"
        equivs = [['Carbon Equivalency', str(state_emission) + ' lbs/MWh']]
    else:
        coal, petroleum, natural_gas, low_carbon = breakdown
        energy_mix = [['Energy Source', 'Percentage'],
                      ['Coal',  "{:.2f}%".format(coal)],
                      ['Petroleum', "{:.2f}%".format(petroleum)],
                      ['Natural gas', "{:.2f}%".format(natural_gas)],
                      ['Low carbon', "{:.2f}%".format(low_carbon)]]
        source = "US EIA"
        equivs = [['Coal', '995.725971 kg CO2/MWh'],
                   ['Petroleum', '816.6885263 kg CO2/MWh'],
                   ['Natural gas', '743.8415916 kg CO2/MWh']]

    #table(readings)
    header("Energy Data")
    subtitle("Energy mix in {} based on {} {} data".format(location, year, source))
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
    #descriptor("Formulas used for determining amount of carbon emissions")
    table(equivs, header=False)
    doc.build(Elements)
