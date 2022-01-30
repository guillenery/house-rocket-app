import folium
import geopandas
import numpy            as np
import pandas           as pd
import streamlit        as st
from folium.plugins     import MarkerCluster
from streamlit_folium   import folium_static

#Page layout
st.set_page_config(layout='wide')

# --------------
# Helper Functions
# --------------

@st.cache(allow_output_mutation=True)
def get_data(path):
    data = pd.read_csv(path)

    return data

@st.cache(allow_output_mutation=True)
def get_geofile(url):
    geofile = geopandas.read_file(url)

    return geofile

def set_attributes(data):
#Add new features to the dataframe
    data['m2_living'] = data['sqft_living']*0.09290304
    data['m2_lot'] = data['sqft_lot']*0.09290304
    data['price_m2'] = data['price'] / data['m2_lot']
    
    return data

def headers():
    st.title( '🚀 Welcome to House Rocket!' )
    st.write('This data is here to help you understand the real estate market around Seattle, WA (USA).')
    return None

def set_maps(data, geofile):
    st.header('Reference Maps')
    c1, c2 = st.columns((1,1))
    c1.subheader('Portfolio Density')

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
    c2.subheader('Price Heatmap')

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

    return None

def data_overview(data):
    with st.sidebar:
        st.title('Use these to filter the data')
    f_zipcode = st.sidebar.multiselect( 
        'Enter zipcode', 
        data['zipcode'].unique() )
    f_attributes = st.sidebar.multiselect( 'Choose the columns', data.columns )
    #Data navigation
    st.header('General Market Data')
    st.subheader('Data Navigator')
    # ----- MUST SECURE THE RAW DATA FROM HERE ----
    # So when I filter the columns, the graphs won't be affected.
    if ( f_zipcode != [] ) & ( f_attributes != [] ):
        data = data.loc[data['zipcode'].isin( f_zipcode ), f_attributes]

    elif ( f_zipcode != [] ) & ( f_attributes == [] ):
        data = data.loc[data['zipcode'].isin( f_zipcode ), :]

    elif ( f_zipcode == [] ) & ( f_attributes != [] ):
        data = data.loc[:, f_attributes]

    else:
        data = data.copy()

    st.dataframe(data)

    return None

def data_analysis(data):
    c1, c2 = st.columns((1,1))

    #Metrics using mean
    df1 = data[['id', 'zipcode']].groupby( 'zipcode' ).count().reset_index()
    df2 = data[['price', 'zipcode']].groupby( 'zipcode').mean().reset_index()
    df3 = data[['sqft_living', 'zipcode']].groupby( 'zipcode').mean().reset_index()
    df4 = data[['price_m2', 'zipcode']].groupby( 'zipcode').mean().reset_index()


    #Merge the info
    m1 = pd.merge( df1, df2, on='zipcode', how='inner' )
    m2 = pd.merge( m1, df3, on='zipcode', how='inner' )
    df = pd.merge( m2, df4, on='zipcode', how='inner' )

    df.columns = ['Zipcode', 'Number of Houses', 'Price', 'm2 Living',
                'USD/m2']

    c1.subheader( 'Average Values by Zipcode' )
    c1.dataframe( df, height=600 )

    #Descriptive Statistics
    num_attributes = data.select_dtypes( include=['int64', 'float64'] )
    mean_ = pd.DataFrame( num_attributes.apply( np.mean ) )
    median_ = pd.DataFrame( num_attributes.apply( np.median ) )
    std_ = pd.DataFrame( num_attributes.apply( np.std ) )

    max_ = pd.DataFrame( num_attributes.apply( np.max ) ) 
    min_ = pd.DataFrame( num_attributes.apply( np.min ) ) 

    df1 = pd.concat([max_, min_, mean_, median_, std_], axis=1 ).reset_index()

    df1.columns = ['Variable', 'Max', 'Min', 'Mean', 'Median', 'Std Dev'] 

    c2.subheader( 'Descriptive Analysis' )
    c2.dataframe( df1, height=600 )
    return None

def data_graphs(data):
    #Average prices by the years
    #First, I will group the values to have the axes I need in hands.
    yr_renov_group = df['price'].groupby(df['yr_renovated']).mean().reset_index()
    #Now, filter the data so only renovations after 1930 show up
    yr_renov_group = yr_renov_group.loc[yr_renov_group['yr_renovated']>=1930, :]

    #Also for the yr of building
    yr_built_grouped = df['price'].groupby(df['yr_built']).mean().reset_index()
    return None

def commercial_attributes(data):


    st.header('Commercial Attributes')
    st.subheader('Price distribution')
    st.info('🛠 Under development')

    c2, c1 = st.columns((1, 1))  
    c1.subheader('Average prices by the year of renovation')
    c1.line_chart(yr_renov_group.set_index('yr_renovated'), height=300)
    c2.subheader('Average prices by the year of building')
    c2.line_chart(yr_built_grouped.set_index('yr_built'), height=300)

    return None

def physical_attributes(data):

    st.header('Physical Attributes')
    st.subheader('# or houses by # of bedrooms')
    st.info('🛠 Under development')
    st.subheader('# or houses by # of bathrooms')
    st.info('🛠 Under development')
    st.subheader('# or houses by # of floors')
    st.info('🛠 Under development')
    st.subheader('# or houses by waterview or not')
    st.info('🛠 Under development')

    return None

def buying_insights(data):
    st.header('Buying Insights')
    st.subheader('What homes should House Rocket buy and for how much?')
    st.write('For each region (zipcode), I suggest House Rocket to buy those with prices under the region`s median, in good condition only.')
    st.info('🛠 Under development')
    return None

def selling_insights():
    st.header('Selling Insights')
    st.subheader('When should House Rocket sell the homes it bought, and what should the company charge?')
    st.write('For each region (zipcode), I will analyze the prices transacted by season of the year. The idea is to find the best seasons to buy (lower prices) and to sell (higher prices)')
    st.write('These differences in price should guide House Rocket on pricing strategies.')
    st.write('1 - If the buying price is higher than the region median price in a given season, should sell it for purschase price + 10%')
    st.write('2 - If the buying price is lower than the region median price in a given season, should sell it for purschase price + 30%')

    
    st.info('🛠 Under development')

    return None

if __name__ == "__main__":

    path = 'data/kc_house_data.csv'
    url = 'https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'

    #Extract Data
    data = get_data(path)
    data_2 = data.copy()
    geofile = get_geofile(url)

    #Transform Data
    set_attributes(data)

    #Load Data
    headers()
    set_maps(data, geofile)
    data_overview(data)
    data_analysis(data) #Extend the data filters to the Descriptive Analysis column
    physical_attributes(data)
    buying_insights(data)
    selling_insights()