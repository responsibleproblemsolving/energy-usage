import unittest
import requests
import energyusage.evaluate as evaluate
import energyusage.locate as locate

class Test(unittest.TestCase):
    def test_kwh_to_co2(self):
        printToScreen = False
        kwh = 0.1
        breakdown = [10, 20, 30, 40] # [coal, oil, gas, low carbon]
        location = "United States"
        year = 2016
        emission, state_emission = evaluate.emissions(process_kwh, breakdown, location, year, printToScreen)
        self.assertEqual(emission, 2431/50000)

    def test_ip_to_location(self):
        printToScreen = False
        geo = requests.get("https://get.geojs.io/v1/ip/geo/165.82.47.11.json").json()
        self.assertEqual(locate.get(printToScreen, geo), "Pennsylvania")

    def test_get_local_energy_mix(self):
        location = "Pennsylvania"
        year = 2016
        self.assertEqual(evaluate.energy_mix(location, year), [25.4, 0.2, 31.6, 42.5])


if __name__ == '__main__':
    unittest.main()
