from data import DATA_HOME
import csv

_ENCODING = 'utf-8'

DATA_FOLDER = DATA_HOME / 'vispapers'


def read_all():
    with open(DATA_FOLDER / 'vispapers.csv') as file:
        yield from csv.DictReader(file)