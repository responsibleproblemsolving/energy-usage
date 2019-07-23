import requests

STATES = ['Alabama','Alaska','Arizona','Arkansas','California','Colorado', \
'Connecticut','Delaware', 'Florida','Georgia','Hawaii','Idaho', \
'Illinois','Indiana','Iowa','Kansas','Kentucky','Louisiana', \
'Maine','Maryland','Massachusetts','Michigan','Minnesota', \
'Mississippi','Missouri','Montana','Nebraska','Nevada', \
'New Hampshire','New Jersey','New Mexico','New York', \
'North Carolina','North Dakota','Ohio','Oklahoma','Oregon', \
'Pennsylvania', 'Rhode Island','South Carolina','South Dakota', \
'Tennessee','Texas','Utah','Vermont','Virginia','Washington', \
'West Virginia','Wisconsin','Wyoming']


""" LOCATION UTILS """

def get():
    """ Gets user's location via GeoJS API

    Returns:
        location (str): location of user's IP address
    """

    location = "Unknown"
    geo = requests.get("https://get.geojs.io/v1/ip/geo.json").json()
    try:
        if geo["country"] == "United States":
            try:
                location = geo["region"]
            except:
                location = "United States"
        else:
            location = geo['country']
    except:
        pass
    print("Location: {:>70}".format(location))
    return location

def in_US(location):
    return (location in STATES or location == "United States")
