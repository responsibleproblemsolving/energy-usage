# energyusage

A Python package that measures the environmental impact of computation. Provides a function to
evaluate the energy usage and related carbon emissions of another function.
Emissions are calculated based on the user's location via the GeoJS API and that location's
energy mix data (sources: US E.I.A and eGRID for the year 2016).

## Installation

To install, simply `pip install energyusage`.

## Usage

To evaluate the emissions of a function, just call `energyusage.evaluate` with the function
name and the arguments it requires. 

```python
import energyusage

# User defined function to be evaluated
def power(base, exp):
  return base**exp

energyusage.evaluate(power,10,10)
```

## Notes

Due to the methods in which the energy measurement is being done (through the Intel RAPL
interface and NVIDIA-smi), our package is only available on Linux kernels that have the
RAPL interface and/or machines with an Nvidia GPU.
