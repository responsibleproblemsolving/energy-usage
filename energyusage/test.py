import unittest
import requests
import evaluate as evaluate
import locate as locate

class Test(unittest.TestCase):
    def test_kwh_to_co2(self):
        process_kwh = 0.1
        year = "2016"
        printToScreen = False

        # US locations
        breakdown = [5.868023799, 1.321624392, 66.17474207, 26.63395815]
        location = "Massachusetts"
        emission, state_emission = evaluate.emissions(process_kwh, breakdown, \
        location, year, printToScreen)
        self.assertAlmostEqual(emission, 0.037254766047499006)
        self.assertEqual(state_emission, 821.327)

        # Unknown and international location
        breakdown = [5.572323934, 36.95920652, 20.30010129, 37.16836826]
        location = "New Zealand"
        year = "2016"
        printToScreen = False
        emission, state_emission = evaluate.emissions(process_kwh, breakdown, \
        location, year, printToScreen)
        self.assertAlmostEqual(emission, 0.05083272721075440)
        self.assertEqual(state_emission, 0)

    def test_ip_to_location(self):
        printToScreen = False
        geo = requests.get("https://get.geojs.io/v1/ip/geo/165.82.47.11.json").json()
        self.assertEqual(locate.get(printToScreen, geo), "Pennsylvania")

    def test_get_local_energy_mix(self):
        year = "2016"

        # US locations
        location = "Pennsylvania"
        self.assertAlmostEqual(evaluate.energy_mix(location, year)[0], 25.4209872)
        self.assertAlmostEqual(evaluate.energy_mix(location, year)[1], 0.1686522923)
        self.assertAlmostEqual(evaluate.energy_mix(location, year)[2], 31.640982)
        self.assertAlmostEqual(evaluate.energy_mix(location, year)[3], 42.51657052)

        # Unknown or international locations
        location = "Unknown"
        self.assertAlmostEqual(evaluate.energy_mix(location, year)[0], 14.34624948)
        self.assertAlmostEqual(evaluate.energy_mix(location, year)[1], 39.45439942)
        self.assertAlmostEqual(evaluate.energy_mix(location, year)[2], 28.64046947)
        self.assertAlmostEqual(evaluate.energy_mix(location, year)[3], 17.55888163)

    def test_emissions_comparison(self):
        process_kwh = 0.1
        locations = ["New Zealand"]
        year = "2016"
        default_location = False
        printToScreen = False

        comparison_values = evaluate.emissions_comparison(process_kwh, locations, \
        year, default_location, printToScreen)
        comparison_values_list = list(comparison_values[0])
        rounded_comparison_values = round(comparison_values_list[1], 7)
        self.assertAlmostEqual(rounded_comparison_values, 0.05083272721075440)

    def test_old_emissions_comparison(self):
        process_kwh = 0.1
        year = "2016"
        default_location = True
        printToScreen = False
        rounded_default_emissions_list = []

        default_emissions = evaluate.old_emissions_comparison(process_kwh, year,\
         default_location, printToScreen)
        for i in range(0, 9):
            default_emissions_list = list(default_emissions[i])
            rounded_default_emissions = round(default_emissions_list[1], 11)
            rounded_default_emissions_list.append(rounded_default_emissions)

        self.assertListEqual(rounded_default_emissions_list, [0.09233947591, \
        0.07541226821, 0.01049881617, 0.09433027569, 0.06590723112, 0.01697252192, \
                                                              0.09190960756, 0.04500865546, 0.00258048699])


if __name__ == '__main__':
    unittest.main()
