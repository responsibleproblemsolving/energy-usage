from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

NAME = "energyusage"
VERSION = "0.0.5"

DESCRIPTION = "Measuring the environmental impact of computation"
LONG_DESCRIPTION = long_description
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'

URL = "https://github.com/responsibleproblemsolving/energy-usage"

AUTHOR = "Sorelle Friedler, Kadan Lottick, Silvia Susai"
AUTHOR_EMAIL = "sorelle@cs.haverford.edu"

LICENSE = "Apache 2.0"

CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
]

PACKAGES = ['energyusage']

PACKAGE_DATA = {
    'energyusage.data.csv' : ['*.csv'],
    'energyusage.data.json' : ['*.json']
}
INCLUDE_PACKAGE_DATA = True

PACKAGE_DIR = {
    'energyusage.data' : 'data'
}

INSTALL_REQUIRES = [
    'requests',
    'reportlab'
]

setup(
    name= NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type = LONG_DESCRIPTION_CONTENT_TYPE,
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
