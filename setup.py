import sys

from setuptools import find_packages
from setuptools import setup

assert sys.version_info[0] == 3 and sys.version_info[1] >= 10, \
    "Hive DEX requires Python 3.10 or newer"

setup(
    name='hive_dex',
    version='1.0.0',
    description="Market data for the Hive blockchain's internal decentralized exchange.",
    long_description=open('README.md', 'r', encoding='UTF-8').read(),
    packages=find_packages(exclude=['scripts']),
    install_requires=[
        'psycopg2-binary',
        'fastapi',
        'uvicorn'
    ],
    entry_points = {
        'console_scripts': [
            'hive_dex = hive_dex.run_hive_dex:run'
        ]
    }
)
