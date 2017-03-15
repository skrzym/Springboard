import pandas as pd
from math import floor
from xml.etree import ElementTree as ET


document = ET.parse( './data/mondial_database.xml' )

# -----------------------------------------------------
# 10 Countries with the lowest infant mortality rates
#
# The approach here is to go through each country and if it has an 'infant_mortality' tag,
# store that data as a float in a dictionary with the country's name as the key.

# Create a list to hold dicts containing {country, infant_mortality_rate}
imr_list = []

# Extract infant_mortality_rate information
for country in document.iterfind('country'):
    # Store the country's name
    name = country.find('name').text

    # If 'infant_mortality' exists for this country, store its value as a 'float' otherwise as 'None'
    if country.find('infant_mortality') is not None:
        imr = float(country.find('infant_mortality').text)
    else:
        imr = None
    # Add a dict to our 'imr_list' containing the country('name') and infanty_mortality_rate('imr')
    imr_list.append({'country': name, 'infant_mortality_rate': imr})

# convert list of dicts to DataFrame
df_imr = pd.DataFrame.from_records(imr_list)

# sort by population and make a top 10 df using '.head(10)'
top_10_imr = df_imr.sort_values('infant_mortality_rate',ascending=True).head(10)

# reindex top 10 df to show index as ranking from 1-10
top_10_imr.index = range(1,11)


# -----------------------------------------------------
# 10 Cities with largest populaiton
#
# The approach here is to go through each country and find all listed population data.
# Once found, only pick out the latest year's data and compile it into a dictionary containing
# the country, city, and population value.

# Create a list to hold dicts containing {country, city, population}
city_populations = []

# Extract population information
for element in document.iterfind('country'):
    for city in element.iterfind('city'):
        # Create a dict to store all poplulation data found for a city
        pop_dict = {}
        for pop in city.iterfind('population'):
            pop_dict[int(pop.attrib['year'])] = int(pop.text)
        # Pick the city population value with the latest year
        latest_population_count = pop_dict[max(pop_dict.keys())] if pop_dict else None
        # Add a dict to our 'city_populations' list containing the country, city, and population value
        city_populations.append({'country':element.find('name').text,'city':city.find('name').text,'population':latest_population_count})

# convert list of dicts to DataFrame and reorder the columns for clarity
df_city_pop = pd.DataFrame.from_records(city_populations)
df_city_pop = df_city_pop[['country','city','population']]

# sort by population and make a top 10 df using '.head(10)'
top_10_city_populations = df_city_pop.sort_values('population', ascending=False).head(10)

# reindex top 10 df to show index as ranking from 1-10
top_10_city_populations.index = range(1,11)


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

# Create a dictionary containing {ethnicgroup, population}
ethnicgroup_populations = {}

# Find ethnic groups per country and calculate their population
for country in document.iterfind('country'):

    # Find latest country population
    pop_dict = {}
    for pop in country.iterfind('population'):
        pop_dict[int(pop.attrib['year'])] = int(pop.text)
    country_population = pop_dict[max(pop_dict.keys())] if pop_dict else None

    # Find all ethnic groups in a country and compute ethnic population value using
    # 'country_population' and 'percentage' attribute associated with ethnic group
    for egroup in country.iterfind('ethnicgroup'):
        egroup_percent = float(egroup.attrib['percentage']) * .01
        ethnic_population = country_population * egroup_percent

        # Store this computed population in the 'ethnicgroup_populations' dictionary
        if egroup.text in ethnicgroup_populations.keys():
            ethnicgroup_populations[egroup.text] += ethnic_population
        else:
            ethnicgroup_populations[egroup.text] = ethnic_population

# Create a DataFrame using the 'ethnicgroup_populations' dictionary
df_ethnic_populations = pd.DataFrame.from_dict(ethnicgroup_populations,orient='index')

# We use reset_index to put the ethnic groups into a column and then rename the columns for clarity
df_ethnic_populations.reset_index(inplace=True)
df_ethnic_populations.columns = ['ethnicgroup','population']

# Sort the DataFrame by 'population'
df_ethnic_populations.sort_values('population',ascending=False,inplace=True)

# Create a top 10 DataFrame and adjust index to match ranking
top_10_ethnic_groups = df_ethnic_populations.head(10)
top_10_ethnic_groups.index = range(1,11)

# Round population values to whole numbers
top_10_ethnic_groups.population = top_10_ethnic_groups.population.apply(floor)


# -----------------------------------------------------
# Name and country of a) longest river, b) largest lake, and c) airport at highest elevation

# Here we create a 'countries' dictionary to help map country_code information to the actual country name.
# This will be used on each of the three parts of this question
countries = {}
for country in document.iterfind('country'):
    countries[country.attrib['car_code']] = country.find('name').text

#A
rivers = []
for river in document.iterfind('river'):
    name = river.find('name').text
    # Determine Location
    if river.find('located') is not None:
        country = countries[river.find('located').attrib['country']]
    else:
        country = countries[river.find('source').attrib['country']]

    # Determine Length
    if river.find('length') is not None:
        length = float(river.find('length').text)
    else:
        length = None

    # Add dictionary of answers to 'rivers' list
    rivers.append({
        'name': name,
        'country': country,
        'length': length
    })

df_rivers = pd.DataFrame.from_records(rivers).sort_values('length',ascending=False).reset_index(drop=True)
longest_river = df_rivers.iloc[0]


#B
lakes = []
for lake in document.iterfind('lake'):
    name = lake.find('name').text
    # Determine Location
    if lake.find('located') is not None:
        country = countries[lake.find('located').attrib['country']]
    else:
        country = countries[lake.attrib['country'].split(' ')[0]]

    # Determine size
    if lake.find('area') is not None:
        area = float(lake.find('area').text)
    else:
        area = None

    # Add dictionary of answers to 'lakes' list
    lakes.append({
        'name': name,
        'country': country,
        'area': area
    })

df_lakes = pd.DataFrame.from_records(lakes).sort_values('area',ascending=False).reset_index(drop=True)
largest_lake = df_lakes.iloc[0]


#C
airports = []
for airport in document.iterfind('airport'):
    name = airport.find('name').text
    country = countries[airport.attrib['country']]

    # Determine elevation
    if airport.find('elevation').text is not None:
        elevation = float(airport.find('elevation').text)
    else:
        elevation = None

    # Add dictionary of answers to 'airports' list
    airports.append({
        'name': name,
        'country': country,
        'elevation': elevation
    })

df_airports = pd.DataFrame.from_records(airports).sort_values('elevation',ascending=False).reset_index(drop=True)
highest_airport = df_airports.iloc[0]