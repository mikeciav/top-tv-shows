import configparser
from pprint import pprint

config = configparser.ConfigParser()

config.read("config.ini")
defaults = config['DEFAULT']
print(defaults['skipDuplicateShows'])
print(defaults.get('skipDuplicateShows'))
print(defaults['numEntries'])
print(defaults.get('numEntries'))
