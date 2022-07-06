import pymysql
import pandas as pd
from pandas.io import sql
from sqlalchemy import Column, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import sqlalchemy
import streamlit as st
import pandas as pd
import plotly.express as px

# set up the app with wide view preset and a title
st.set_page_config(layout="wide")
st.title("Interact with Gapminder Data using SingleStore")

# create connection config
UserName='admin'
Password='ILoveSingleStore12'
DatabaseName='gapminder'

# Creating the database connection
db_connection_str = "mysql+pymysql://"+UserName+ ":" +Password +"@svc-df0ef59a-af3a-4bc5-9ff2-13b5f81c1a46-dml.aws-oregon-2.svc.singlestore.com/"+ DatabaseName
db_connection = create_engine(db_connection_str)

# import our data as a pandas dataframe
df = pd.read_sql('SELECT * FROM gapminder_tidy', con=db_connection)

# get a list of all possible continents and metrics, for the widgets
continent_list = list(df['continent'].unique())
metric_list = list(df['metric'].unique())

# map the actual data values to more readable strings
metric_labels = {"gdpPercap": "GDP Per Capita", "lifeExp": "Average Life Expectancy", "pop": "Population"}

# function to be used in widget argument format_func that maps metric values to readable labels, using dict above
def format_metric(metric_raw):
    return metric_labels[metric_raw]

# put all widgets in sidebar and have a subtitle
with st.sidebar:
    st.subheader("Configure the plot")
    # widget to choose which continent to display
    continent = st.selectbox(label = "Choose a continent", options = continent_list)
    # widget to choose which metric to display
    metric = st.selectbox(label = "Choose a metric", options = metric_list, format_func=format_metric)

# use selected values from widgets to filter dataset down to only the rows we need
query = f"continent=='{continent}' & metric=='{metric}'"
df_filtered = df.query(query)

# create the plot
title = f"{metric_labels[metric]} for countries in {continent}"
fig = px.line(df_filtered, x = "year", y = "value", color = "country", title = title, labels={"value": f"{metric_labels[metric]}"})

# display the plot
st.plotly_chart(fig, use_container_width=True)

# decide to show data or not
with st.sidebar:
    show_data = st.checkbox(label = "Show the data used to generate this plot", value = False)
if show_data:
    st.dataframe(df_filtered)

# Limit the dates displayed in the plot
year_min = int(df_filtered['year'].min())
year_max = int(df_filtered['year'].max())

with st.sidebar:
    years = st.slider(label = "What years should be plotted?", min_value = year_min, max_value = year_max, value = (year_min, year_max))

df_filtered = df_filtered[(df_filtered.year >= years[0]) & (df_filtered.year <= years[1])]
    
    
# Limit the countries displayed in the plot    
countries_list = list(df_filtered['country'].unique())

with st.sidebar:
    countries = st.multiselect(label = "Which countries should be plotted?", options = countries_list, default = countries_list)

df_filtered = df_filtered[df_filtered.country.isin(countries)]

st.markdown(f"This plot shows the {metric_labels[metric]} from {years[0]} to {years[1]} for the following countries in {continent}: {', '.join(countries)}")
