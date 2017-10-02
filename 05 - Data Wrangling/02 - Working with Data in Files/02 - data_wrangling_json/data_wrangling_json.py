import json
import pandas as pd
from pandas.io.json import json_normalize


# Top 10 Projects by Country

# Generate a DataFrame by reading in the 'world_bank_projects.json' file
df_world_bank_projects = pd.read_json('data/world_bank_projects.json')
# Use the 'countryshortname' column and '.value_counts()' to tally the projects by country.
top_10_project_countries = df_world_bank_projects.countryshortname.value_counts()
# Get the top 10 countries and reset the index to push the country names into their own column
top_10_project_countries = top_10_project_countries.head(10)
top_10_project_countries = top_10_project_countries.reset_index()
# Change the column names and re-index the DataFrame to match each row's ranking
top_10_project_countries.columns = ['country','projectcount']
top_10_project_countries.index = range(1,11)


# Top 10 Project Themes

# Use 'json_normalize()' to pull project theme code and theme name into a DataFrame
world_bank_project_list = json.load(open('data/world_bank_projects.json'))
df_world_bank_project_themes = json_normalize(world_bank_project_list,'mjtheme_namecode')
#Similar to prior quesiton lets:
# Tally up the projects for each theme
# Pick the top 10
# Push the theme code out to its own column
# Rename the columns and re-index to reflect ranking
top_10_project_themes = df_world_bank_project_themes.code.value_counts().head(10).reset_index()
top_10_project_themes.columns = ['code', 'count']
top_10_project_themes.index = range(1,11)


# Find All Names for Project Themes

# Subset the dataframe, removing any row that has a blank name field
namecodes = df_world_bank_project_themes[df_world_bank_project_themes['name']!='']
# Set the dataframe index to the 'code' column and turn the df into a dictionary
namecodes = namecodes.set_index('code').to_dict()
# Create a copy of the project themes dataframe and map the 'namecodes' dictionary
# to the code column, assigning the result to the 'name' column.
df_complete_wbp_themes = df_world_bank_project_themes.copy()
df_complete_wbp_themes.name = df_complete_wbp_themes.code.map(namecodes['name'])


# Fix the missing names in question 2

# Using the 'namecodes' dictionary, map the 'top_10_project_themes' dataframe codes to their corresponding names
top_10_project_themes_with_names = top_10_project_themes.copy()
top_10_project_themes_with_names.code = top_10_project_themes_with_names.code.map(namecodes['name'])
top_10_project_themes_with_names.columns = ['theme_name','count']