import pandas as pd
from math import floor
from xml.etree import ElementTree

document = ElementTree.parse('./data/mondial_database.xml')

# -----------------------------------------------------
# 10 Countries with the lowest infant mortality rates
#
# The approach here is to go through each country and if it has an 'infant_mortality' tag,
# store that data as a float in a dictionary with the country's name as the key.


def element_find(element, prop):
    return element.find(prop).text


def element_exists(element, prop):
    return element.find(prop) is not None

# Generate dictionary with name:imr pairs
imr = dict(
    (element_find(country, 'name'),  # Extract country's name
     float(element_find(country, 'infant_mortality')))  # Extract infant mortality rate
    for country in document.iterfind('country')
    if element_exists(country, 'infant_mortality')  # Filter out countries with no imr
)


def make_top_10(data, col_names, sort_by, asc=False):
    df = pd.DataFrame.from_dict(data, orient='index')
    df.reset_index(inplace=True)
    df.columns = col_names
    df.sort_values(sort_by, ascending=asc, inplace=True)
    df = df.head(10)
    df.index = range(1, 11)
    return df

top_10_imr = make_top_10(imr, ['name', 'infant_mortality_rate'], 'infant_mortality_rate', True)

# -----------------------------------------------------
# 10 Cities with largest population
#
# The approach here is to go through each city and find all listed population data.
# Once found, only pick out the latest year's data and compile it into a dictionary containing
# the city name and population value.


def get_latest_population(element):
    return max((int(population.attrib['year']), int(population.text))
               for population in element.iterfind('population'))[1]

city_populations = dict(
    (city.find('name').text, get_latest_population(city))
    for country in document.iterfind('country')
    for city in country.iterfind('city')
    if element_exists(city, 'population')
)
top_10_city_populations = make_top_10(city_populations, ['city', 'population'], 'population')

# -----------------------------------------------------
# 10 Ethnic groups with the largest overall populations
#
# The approach here is to go through each country and find two things:
# 1. Latest Country Population
# 2. All the ethnic groups
#
# Each ethnic group has a 'percentage' attribute that indicates what percentage of the population in that country
# is made up of that ethnic group. After determining current population value for a country we can multiply those two
# numbers together to determine the total ethnic population in that country. We then add this determined population
# value to the total population tally for that ethnic group. This will let us determine which ethnic groups have the
# largest overall populations.


def get_ethnic_population(country, ethnicgroup):
    return (float(ethnicgroup.attrib['percentage']) * 0.01) * get_latest_population(country)

ethnicgroup_populations = [
    (ethnicgroup.text,
     get_ethnic_population(country, ethnicgroup))
    for country in document.iterfind('country')
    for ethnicgroup in country.iter('ethnicgroup')
]

# Create a DataFrame using the 'ethnicgroup_populations' list and sum the data by ethnic group
df_ethnic_populations = pd.DataFrame.from_records(ethnicgroup_populations, columns=['ethnicgroup', 'population'])
df_ethnic_populations = df_ethnic_populations.groupby('ethnicgroup', sort=True).agg(sum).reset_index()
df_ethnic_populations.sort_values('population', ascending=False, inplace=True)

# Create a top 10 DataFrame
top_10_ethnic_groups = pd.concat([
    df_ethnic_populations.loc[:, 'ethnicgroup'].head(10),
    df_ethnic_populations.loc[:, 'population'].apply(floor).head(10)
    ], axis=1)
top_10_ethnic_groups.index = range(1, 11)

# -----------------------------------------------------
# Name and country of a) longest river, b) largest lake, and c) airport at highest elevation

# Here we create a 'countries' dictionary to help map country_code information to the actual country name.
# This will be used on each of the three parts of this question
countries = dict(
    (country.attrib['car_code'], country.find('name').text)
    for country in document.iterfind('country')
)

# A


def river_location(element):
    if element_exists(element, 'located'):
        return countries[element.find('located').attrib['country']]
    else:
        return countries[element.find('source').attrib['country']]

rivers = [
    {'name': river.find('name').text,
     'country': river_location(river),
     'length': float(river.find('length').text)}
    for river in document.iterfind('river')
    if element_exists(river, 'length')
]

df_rivers = pd.DataFrame.from_records(rivers).sort_values('length', ascending=False).reset_index(drop=True)
longest_river = df_rivers.iloc[0]

# B


def lake_location(element):
    if element.find('located') is not None:
        return countries[element.find('located').attrib['country']]
    else:
        return countries[element.attrib['country'].split(' ')[0]]

lakes = [
    {'name': lake.find('name').text,
     'country': lake_location(lake),
     'area': float(lake.find('area').text)}
    for lake in document.iterfind('lake')
    if element_exists(lake, 'area')
]

df_lakes = pd.DataFrame.from_records(lakes).sort_values('area', ascending=False).reset_index(drop=True)
largest_lake = df_lakes.iloc[0]

# C
airports = [
    {'name': airport.find('name').text,
     'country': countries[airport.attrib['country']],
     'elevation': float(airport.find('elevation').text) if airport.find('elevation').text is not None else 0}
    for airport in document.iterfind('airport')
    if element_exists(airport, 'elevation')
]

df_airports = pd.DataFrame.from_records(airports).sort_values('elevation', ascending=False).reset_index(drop=True)
highest_airport = df_airports.iloc[0]
