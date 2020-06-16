import unittest
import requests
import evaluate as evaluate
import locate as locate

class Test(unittest.TestCase):
    def test_kwh_to_co2(self):
        printToScreen = False
        process_kwh = 0.1
        breakdown = [10, 20, 30, 40] # [coal, oil, gas, low carbon]
        location = "United States"
        year = 2016
        emission, state_emission = evaluate.emissions(process_kwh, breakdown, location, year, printToScreen)
        self.assertAlmostEqual(emission, 0.04862, places=4)

    def test_ip_to_location(self):
        printToScreen = False
        geo = requests.get("https://get.geojs.io/v1/ip/geo/165.82.47.11.json").json()
        self.assertEqual(locate.get(printToScreen, geo), "Pennsylvania")

    def test_get_local_energy_mix(self):
        location = "Pennsylvania"
        year = "2016"
        self.assertAlmostEqual(evaluate.energy_mix(location, year)[0], 25.4, places=1)
        self.assertAlmostEqual(evaluate.energy_mix(location, year)[1], 0.2, places=1)
        self.assertAlmostEqual(evaluate.energy_mix(location, year)[2], 31.6, places=1)
        self.assertAlmostEqual(evaluate.energy_mix(location, year)[3], 42.5, places=1)


if __name__ == '__main__':
    unittest.main()
