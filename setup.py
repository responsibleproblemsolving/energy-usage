from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

NAME = "energy_usage"
VERSION = "0.0.1"

DESCRIPTION = "Measuring the environmental impact of computation"
LONG_DESCRIPTION = long_description

URL = "https://github.com/responsibleproblemsolving/energy-usage"

AUTHOR = "Sorelle Friedler, Kadan Lottick, Silvia Susai"
AUTHOR_EMAIL = "sorelle@cs.haverford.edu"

LICENSE = "Apache 2.0"

CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
]

PACKAGES = ['energy_usage']

PACKAGE_DATA = {
    'energy_usage.data.csv' : ['*.csv'],
    'energy_usage.data.json' : ['*.json']
}
INCLUDE_PACKAGE_DATA = True

PACKAGE_DIR = {
    'energy_usage.data' : 'data'
}

INSTALL_REQUIRES = [
    'requests'
]

setup(
    name= NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url=URL,
    author=AUTHOR,
    author_email = AUTHOR_EMAIL,
    license = LICENSE,
    classifiers=CLASSIFIERS,
    packages = PACKAGES,
    package_data = PACKAGE_DATA,
    include_package_data = INCLUDE_PACKAGE_DATA,
    package_dir = PACKAGE_DIR,
    install_requires=INSTALL_REQUIRES
)
