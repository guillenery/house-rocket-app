import folium
import geopandas
import numpy as np
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

st.set_page_config( layout='wide' )

@st.cache( allow_output_mutation=True )
def get_data( path ):
    data = pd.read_csv( path )

    return data

@st.cache( allow_output_mutation=True )
def get_geofile( url ):
    geofile = geopandas.read_file( url )

    return geofile


#Get the data fetched from kaggle
path = 'data/kc_house_data.csv'
data = get_data( path )

#Get the geofile to deal with zipcodes
url = 'https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'
geofile = get_geofile( url )


#Add new features to the dataframe
data['m2_living'] = data['sqft_living']*0.09290304
data['m2_lot'] = data['sqft_lot']*0.09290304
data['price_m2'] = data['price'] / data['m2_lot']

#==========
#Page Layout
#==========
st.title( '🚀 Welcome to House Rocket!' )
st.write('This data is here to help you understand the real estate market around Seattle, WA (USA).')
st.header('Reference Maps')

c1, c2 = st.columns(( 1, 1 ))
c1.header('Portfolio Density')

df = data.copy()

# Base Map - Folium 
density_map = folium.Map( location=[data['lat'].mean(), 
                          data['long'].mean() ],
                          default_zoom_start=15 ) 

marker_cluster = MarkerCluster().add_to(density_map)
for name, row in df.iterrows():
    folium.Marker([row['lat'], row['long']], 
        popup='Price R${0} \n Sold on: {1} \n Lot area: {2} m2\n Living area: {3} m2 \n Bedrooms: {4} \n Bathrooms: {5} \n Built on: {6}'.format(row['price'],
                                     row['date'],
                                     row['m2_lot'],
                                     row['m2_living'],
                                     row['bedrooms'],
                                     row['bathrooms'],
                                     row['yr_built'] ) ).add_to( marker_cluster)


with c1:
    folium_static(density_map)

#Prices heatmap, by region (zipcode)
c2.header('Price Heatmap')

df = data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
df.columns = ['ZIP', 'PRICE']

geofile = geofile[geofile['ZIP'].isin(df['ZIP'].tolist())]

region_price_map = folium.Map(location=[data['lat'].mean(), 
                                data['long'].mean() ],
                                default_zoom_start=15) 

region_price_map.choropleth( data = df,
                             geo_data = geofile,
                             columns=['ZIP', 'PRICE'],
                             key_on='feature.properties.ZIP',
                             fill_color='YlOrRd',
                             fill_opacity = 0.7,
                             line_opacity = 0.2,
                             legend_name='Average Price' )

with c2:
    folium_static(region_price_map)

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
