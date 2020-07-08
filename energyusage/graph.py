import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

FONTSIZE = 20
TITLESIZE = 30
plt.rcdefaults()

"""
Creates a pie chart based on the energy composition.  Takes a dictionary mapping energy to percent
based on energy types:
- Coal
- Oil/Petroleum
- Natural Gas
- Low Carbon
"""
def pie_chart(energy_dict, figtitle, filename):
    # Pie chart
    labels = ["Coal", "Oil", "Natural Gas", "Low Carbon"]
    if "Petroleum" in energy_dict:
        labels[1] = "Petroleum"
    sizes = [energy_dict[key] for key in labels]
    #colors
    colors = ['#b2182b','#ef8a62','#fddbc7','#2166ac']
    fig1, ax1 = plt.subplots()
    patches, texts, autotexts = ax1.pie(sizes, colors = colors, labels=labels, autopct='%1.1f%%',
                                        startangle=90, labeldistance = 0.8, pctdistance = 0.4)
    for text in texts:
        text.set_color('black')
        text.set_fontsize(FONTSIZE)
        text.set_bbox(dict(facecolor='white', alpha=0.5, linewidth=0.0))
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontsize(FONTSIZE)
            autotext.set_bbox(dict(facecolor='white', alpha=0.5, linewidth=0.0))

    # Equal aspect ratio ensures that pie is drawn as a circle
    ax1.axis('equal')
    ax1.set_title(figtitle, fontsize = TITLESIZE)
    plt.tight_layout()

    bb = (texts, autotexts)
    plt.savefig(filename, bbox_extra_artists = bb) #, bbox_inches = 'tight')
    print("plot saved to: " + filename)
    plt.clf()
    plt.close()

"""
Takes a dictionary mapping "Min", "Median", "Max", and whatever the current location name is
to the kg CO2 values for those locations.  Min/Med/Max will be graphed in grey and current
location in black on the same chart.
"""
def bar_chart(bar_dict, location_key, title, filename, y_step, figsize = None):

    plt.figure(figsize=figsize)

    objects = sorted(bar_dict.keys(), key = bar_dict.get)
    y_pos = np.arange(len(objects))
    co2 = [ bar_dict[key] for key in objects ]
    color_dict = {}
    for key in objects:
        if key == location_key:
            color_dict[key] = 'black'
        else:
            color_dict[key] = 'gray'
    colors = [ color_dict[key] for key in objects ]

    plt.bar(y_pos, co2, align='center', color = colors)
    plt.xticks(y_pos, objects, fontsize = FONTSIZE)
    yticks = []
    plt.yticks([x*y_step for x in range(0, 11)])
    label = plt.ylabel('kg CO2', fontsize = FONTSIZE)
    title = plt.title(title, fontsize = TITLESIZE)

    plt.savefig(filename, bbox_inches = 'tight')
    print("plot saved to: " + filename)
    plt.clf()
    plt.close()

def make_comparison_bar_charts(currlocation_key, currlocation_co2, us_dict, eu_dict, global_dict):
    us_max = modify_dict(us_dict, currlocation_key, currlocation_co2)
    us_y_step = float(format(us_max, '.1g')) / 10
    bar_chart(us_dict, currlocation_key, "US Comparison CO2 Emissions", "us.png", us_y_step, figsize = (10,4))
    eu_max = modify_dict(eu_dict, currlocation_key, currlocation_co2)
    eu_y_step = float(format(eu_max, '.1g')) / 10
    bar_chart(eu_dict, currlocation_key, "Europe Comparison CO2 Emissions", "europe.png",
              eu_y_step, figsize = (10,4))
    global_max = modify_dict(global_dict, currlocation_key, currlocation_co2)
    global_y_step = float(format(global_max, '.1g')) / 10
    bar_chart(global_dict, currlocation_key,
              "Global (Excluding Europe and US)\nComparison CO2 Emissions", "global.png",
              global_y_step, figsize = (10,4))

def modify_dict(comparison_dict, location_key, location_value):
    sorted_keys = sorted(comparison_dict.keys(), key = comparison_dict.get)
    new_key = "Minimum:\n" + sorted_keys[0]
    comparison_dict[new_key] = comparison_dict.pop(sorted_keys[0])
    new_key = "Median:\n" + sorted_keys[1]
    comparison_dict[new_key] = comparison_dict.pop(sorted_keys[1])
    new_key = "Maximum:\n" + sorted_keys[2]
    comparison_dict[new_key] = comparison_dict.pop(sorted_keys[2])
    comparison_dict[location_key] = location_value
    return comparison_dict[new_key]

def timeseries(time, reading, title):
    fig, ax = plt.subplots()
    ax.plot(time, reading)

    if "Baseline" in title:
        ylabel = "baseline wattage (watts)"
        filename = "baseline_wattage.png"
    else:
        ylabel = "process wattage (watts)"
        filename = "process_wattage.png"

    ax.set(xlabel='time (s)', ylabel=ylabel, title=title)
    ax.grid()

    fig.savefig(filename)
    print("plot saved to: " + filename)
    plt.clf()
    plt.close()
        
