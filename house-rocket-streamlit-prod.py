import pandas    as pd
import numpy     as np
import streamlit as st
import folium
import geopandas

from streamlit_folium import folium_static
from folium.plugins   import MarkerCluster

st.set_page_config( layout='wide' )

@st.cache( allow_output_mutation=True )
def get_data( path ):
    data = pd.read_csv( path )

    return data

# get data
path = 'data/kc_house_data.csv'
data = get_data( path )

#==========
#Page Layout
#==========
st.title( '🚀 Welcome to House Rocket!' )
st.write('This data is here to help you understand the real estate market around Seattle, WA (USA).')
st.header('Reference Maps')
st.info('🛠 Under development')

st.header('General Market Data')
st.info('🛠 Under development')

st.header('Buying Insights')
st.write('What homes should House Rocket buy and for how much?')
st.info('🛠 Under development')
st.header('Selling Insights')
st.write('When should House Rocket sell the homes it bought, and what should the company charge?')
st.info('🛠 Under development')

with st.sidebar:
    st.title('Use these to filter the data')
