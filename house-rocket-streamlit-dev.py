import pandas    as pd
import streamlit as st
import numpy     as np
import datetime  as datetime

import folium

from streamlit_folium import folium_static
from folium.plugins   import MarkerCluster

import plotly.express as px

#General Settings
st.set_page_config(layout='wide')

#Helper Functions

@st.cache(allow_output_mutation=True)
def get_data (path):
    data = pd.read_csv(path)
    return data

def set_attributes(data):
    data['price_m2'] = data['price'] / data['sqft_lot'] 
    return data

def data_overview(data):
    f_attributes = st.sidebar.multiselect('Select columns', data.columns) 
    f_zipcode = st.sidebar.multiselect('Enter zipcode(s)', data['zipcode'].unique())

    st.title('General Market Data')

    if ( f_zipcode != [] ) & ( f_attributes != [] ):
        data = data.loc[data['zipcode'].isin( f_zipcode ), f_attributes]

    elif ( f_zipcode != [] ) & ( f_attributes == [] ):
        data = data.loc[data['zipcode'].isin( f_zipcode ), :]

    elif ( f_zipcode == [] ) & ( f_attributes != [] ):
        data = data.loc[:, f_attributes]

    else:
        data = data.copy()

    st.write(data.head())

    c1, c2 = st.beta_columns((1, 1) )  

    # Average metrics
    df1 = data[['id', 'zipcode']].groupby( 'zipcode' ).count().reset_index()
    df2 = data[['price', 'zipcode']].groupby( 'zipcode').mean().reset_index()
    df3 = data[['sqft_living', 'zipcode']].groupby( 'zipcode').mean().reset_index()
    df4 = data[['price_m2', 'zipcode']].groupby( 'zipcode').mean().reset_index()

    # merge
    m1 = pd.merge( df1, df2, on='zipcode', how='inner' )
    m2 = pd.merge( m1, df3, on='zipcode', how='inner' )
    df = pd.merge( m2, df4, on='zipcode', how='inner' )

    df.columns = ['ZIPCODE', 'TOTAL HOUSES', 'PRICE', 'SQRT LIVING', 'PRICe/M2']

    c1.header('Average Values')
    c1.dataframe( df, height=600 )

    # Descriptive Statistics
    num_attributes = data.select_dtypes( include=['int64', 'float64'] )
    media = pd.DataFrame( num_attributes.apply( np.mean ) )
    mediana = pd.DataFrame( num_attributes.apply( np.median ) )
    std = pd.DataFrame( num_attributes.apply( np.std ) )

    max_ = pd.DataFrame( num_attributes.apply( np.max ) ) 
    min_ = pd.DataFrame( num_attributes.apply( np.min ) ) 

    df1 = pd.concat([max_, min_, media, mediana, std], axis=1 ).reset_index()
    df1.columns = ['attributes', 'max', 'min', 'mean', 'median', 'std'] 

    c2.header( 'Descriptive Analysis' )
    c2.dataframe( df1, height=800 )

    return None

def price_level(data):

    for i in range(len(data)):
        if data.loc[i, 'price'] <= 321950:
            data.loc[i, 'level'] = 0

        elif (data.loc[i, 'price'] > 321950) & (data.loc[i, 'price'] <= 450000):
            data.loc[i, 'level'] = 1

        elif (data.loc[i, 'price'] > 450000) & (data.loc[i, 'price'] <= 645000):
            data.loc[i, 'level'] = 2

        else:
            data.loc[i, 'level'] = 3
    return data

def set_commercial( data ):
    st.sidebar.title( 'Commercial Options' )
    st.title( 'Commercial Attributes' )

    # ---------- Average Price per year built
    # setup filters
    min_year_built = int( data['yr_built'].min() )
    max_year_built = int( data['yr_built'].max() )

    st.sidebar.subheader( 'Select Max Year Built' )
    f_year_built = st.sidebar.slider( 'Year Built', min_year_built, max_year_built, min_year_built )

    st.header( 'Average price per year built' )

    # get data
    data['date'] = pd.to_datetime( data['date'] ).dt.strftime( '%Y-%m-%d' )

    df = data.loc[data['yr_built'] < f_year_built]
    df = df[['yr_built', 'price']].groupby( 'yr_built' ).mean().reset_index()

    fig = px.line( df, x='yr_built', y='price' )
    st.plotly_chart( fig, use_container_width=True )


    # ---------- Average Price per day
    st.header( 'Average Price per day' )
    st.sidebar.subheader( 'Select Max Date' )

    # setup filters
    min_date = datetime.strptime( data['date'].min(), '%Y-%m-%d' )
    max_date = datetime.strptime( data['date'].max(), '%Y-%m-%d' )

    f_date = st.sidebar.slider( 'Date', min_date, max_date, min_date )

    # filter data
    data['date'] = pd.to_datetime( data['date'] )
    df = data[data['date'] < f_date]
    df = df[['date', 'price']].groupby( 'date' ).mean().reset_index()

    fig = px.line( df, x='date', y='price' )
    st.plotly_chart( fig, use_container_width=True )

    # ---------- Histogram -----------
    st.header( 'Price Distribuition' )
    st.sidebar.subheader( 'Select Max Price' )

    # filters
    min_price = int( data['price'].min() )
    max_price = int( data['price'].max() )
    avg_price = int( data['price'].mean() )

    f_price = st.sidebar.slider( 'Price', min_price, max_price, avg_price )

    df = data[data['price'] < f_price]

    fig = px.histogram( df, x='price', nbins=50 )
    st.plotly_chart( fig, use_container_width=True )

    return None


def set_phisical( data ):
    st.sidebar.title( 'Attributes Options' )
    st.title( 'House Attributes' )

    # filters
    f_bedrooms = st.sidebar.selectbox( 'Max number of bedrooms', 
                                        sorted( set( data['bedrooms'].unique() ) ) )
    f_bathrooms = st.sidebar.selectbox( 'Max number of bath', 
                                        sorted( set( data['bathrooms'].unique() ) ) )

    c1, c2 = st.beta_columns( 2 )

    # Houses per bedrooms
    c1.header( 'Houses per bedrooms' )
    df = data[data['bedrooms'] < f_bedrooms]
    fig = px.histogram( df, x='bedrooms', nbins=19 )
    c1.plotly_chart( fig, use_containder_width=True )

    # Houses per bathrooms
    c2.header( 'Houses per bathrooms' )
    df = data[data['bathrooms'] < f_bathrooms]
    fig = px.histogram( df, x='bathrooms', nbins=10 )
    c2.plotly_chart( fig, use_containder_width=True )

    # filters
    f_floors = st.sidebar.selectbox('Max number of floors', sorted( set( data['floors'].unique() ) ) )
    f_waterview = st.sidebar.checkbox('Only House with Water View' )

    c1, c2 = st.beta_columns( 2 )

    # Houses per floors
    c1.header( 'Houses per floors' )
    df = data[data['floors'] < f_floors]
    fig = px.histogram( df, x='floors', nbins=19 )
    c1.plotly_chart( fig, use_containder_width=True )

    # Houses per water view
    if f_waterview:
        df = data[data['waterfront'] == 1]
    else:
        df = data.copy()

    fig = px.histogram( df, x='waterfront', nbins=10 )
    c2.header( 'Houses per water view' )
    c2.plotly_chart( fig, use_containder_width=True )

    return None



path = 'data/kc_house_data.csv'
data = get_data(path)
data = set_attributes(data=data)
data_overview(data = data)
set_commercial(data=data)
set_phisical(data=data)

#==========
#Page Layout
#==========
st.title( '🚀 Welcome to House Rocket!' )
st.write('This data is here to help you understand the real estate market around Seattle, WA (USA).')
st.header('Reference Maps')
st.info('🛠 Under development')

st.header('General Market Data')
#descriptive_analysis(data)

st.header('Buying Insights')
st.write('What homes should House Rocket buy and for how much?')
st.header('Selling Insights')
st.write('When should House Rocket sell the homes it bought, and what should the company charge?')

with st.sidebar:
    st.title('Use these to filter the data')