import time
import statistics
from timeit import default_timer as timer
from multiprocessing import Process, Queue
import os
import datetime
import subprocess
import queue


import energyusage.utils as utils
import energyusage.convert as convert
import energyusage.locate as locate
import energyusage.report as report
import energyusage.mlco2_report as mlco2_report

mlco2_report.generate(0.56, 1.68)
