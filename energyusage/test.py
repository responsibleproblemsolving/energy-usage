import unittest
import requests
import evaluate as evaluate
import locate as locate

YEAR = "2016"
PROCESS_KWH = 0.1
printToScreen = False

class Test(unittest.TestCase):
    def test_kwh_to_co2(self):
        # US locations
        breakdown = [5.868023799, 1.321624392, 66.17474207, 26.63395815]
        location = "Massachusetts"
        emission, state_emission = evaluate.emissions(PROCESS_KWH, breakdown, \
        location, YEAR, printToScreen)
        self.assertAlmostEqual(emission, 0.037254766047499006)
        self.assertEqual(state_emission, 821.327)

        # Unknown and international location
        breakdown = [5.572323934, 36.95920652, 20.30010129, 37.16836826]
        location = "New Zealand"
        emission, state_emission = evaluate.emissions(PROCESS_KWH, breakdown, \
        location, YEAR, printToScreen)
        self.assertAlmostEqual(emission, 0.05083272721075440)
        self.assertEqual(state_emission, 0)


    def test_ip_to_location(self):
        geo = requests.get("https://get.geojs.io/v1/ip/geo/165.82.47.11.json").json()
        self.assertEqual(locate.get(printToScreen, geo), "Pennsylvania")


    def test_get_local_energy_mix(self):
        output_pennsylvania_mix = []
        output_unknown_mix = []

        pennsylvania_mix = [25.4209872, 0.1686522923, 31.640982, 42.51657052]
        unknown_mix = [14.34624948, 39.45439942, 28.64046947, 17.55888163]
        # breadown from function
        pennsylvania_breakdown = evaluate.energy_mix("Pennsylvania", YEAR)
        unknown_breadown = evaluate.energy_mix("Unknown", YEAR)

        for i in range(0, 4):
            # US locations
            pennsylvania_mix[i] = round(pennsylvania_mix[i], 5)
            output_pennsylvania_mix.append(round(pennsylvania_breakdown[i], 5))

            # Unknown (default to US) or international locations
            unknown_mix[i] = round(unknown_mix[i], 5)
            output_unknown_mix.append(round(unknown_breadown[i], 5))

        self.assertListEqual(output_pennsylvania_mix, pennsylvania_mix)
        self.assertListEqual(output_unknown_mix, unknown_mix)


    def test_emissions_comparison(self):
        locations = ["New Zealand"]
        default_location = False

        comparison_values = evaluate.emissions_comparison(PROCESS_KWH, locations, \
        YEAR, default_location, printToScreen)
        comparison_values_list = list(comparison_values[0])
        comparison_value = comparison_values_list[1]
        self.assertAlmostEqual(comparison_value, 0.05083272721075440)


    def test_old_emissions_comparison(self):
        default_location = True
        rounded_default_emissions_list = []

        default_emissions = evaluate.old_emissions_comparison(PROCESS_KWH, YEAR,\
         default_location, printToScreen)
        for value in default_emissions:
            default_emissions_list = list(value)
            rounded_default_emissions = round(default_emissions_list[1], 11)
            rounded_default_emissions_list.append(rounded_default_emissions)

        self.assertListEqual(rounded_default_emissions_list, [0.09233947591, \
        0.07541226821, 0.01049881617, 0.09433027569, 0.06590723112, 0.01697252192, \
        0.09190960756, 0.04500865546, 0.00258048699])

        
    def test_small_energy_consumption_exception(self):        
        def small_function(n):
            n+1

        with self.assertRaises(Exception) as e:
            evaluate.evaluate(small_function(), 10)
            self.assertTrue("Process executed too fast to gather energy consumption" in e.exception)


if __name__ == '__main__':
    unittest.main()
