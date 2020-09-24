#-----------------------------------------------------------
# IMPORT LIBRARIES
#-----------------------------------------------------------

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import geopandas as gpd
import json
import os
import numpy as np

import plotly.graph_objects as go
import plotly.figure_factory as ff

from matplotlib import cm
import matplotlib

from plotly.offline import plot

#---------------------------------------------------------------------
# LOAD DATA
#--------------------------------------------------------------------
localidades = ['ANTONIO NARIÑO','TUNJUELITO','RAFAEL URIBE URIBE','CANDELARIA','BARRIOS UNIDOS','TEUSAQUILLO','PUENTE ARANDA','LOS MARTIRES','USAQUEN','CHAPINERO','SANTA FE','SAN CRISTOBAL','USME','CIUDAD BOLIVAR','BOSA','KENNEDY','FONTIBON','ENGATIVA','SUBA']

transporte = ['Transmilenio', 'SITP', 'P.Vehiches',
       'Walking', 'Cycling']


comercial = ['Wholesale', 'Used Goods', 'Retail', 'Restaurants, Cafés and Bars',
       'Personal Care', 'Cultural and Entertainment',
       'Banking and Post Offices', 'Commercial Activity']

'''
url = 'https://raw.githubusercontent.com/anacastillonu/kde_commercial_transport_bogota/master/data/kde.geojson'
all_kde = gpd.read_file(url).set_crs(epsg=3116).to_crs(epsg=4326)

url = 'https://raw.githubusercontent.com/anacastillonu/kde_commercial_transport_bogota/master/data/all_hot.geojson'
all_hot = gpd.read_file(url)
'''

url = 'https://raw.githubusercontent.com/anacastillonu/kde_commercial_transport_bogota/master/data/loc_mod.geojson'
loc_shp = gpd.read_file(url)
loc_json = json.loads(loc_shp.set_index('LocNombre').to_json())

url = 'https://raw.githubusercontent.com/anacastillonu/spatial-correlation-transport-commercial-bogota/master/data/corr_localidades.csv'
loc_corrs = pd.read_csv(url, encoding = 'latin1',sep=",")

#---------------------------------------------------------------------
# DASH LAYOUT
#--------------------------------------------------------------------

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([


#TITULO DASH
    html.Div([
    html.H1('Spatial Correlation Between Transport Networks and Commercial Activities in Bogotá, Colombia',
            style={'height': '100px',
                   'width': '600px',
                    'color': 'midnightblue',
                    'font-family': 'verdana',
                   'font-size': "210%",
                   'display': 'inline-block'}),

    html.H6('The spatial correlation was determined through the evaulation of the Kernel Density Estimation for each of the variables. Such density was overlayed in a 50m by 50m grid (+150,000 cells) and the pearson correlation was estimated for the values on a cell-by-cell basis.',
            style={'height': '80px',
                   'width': '600px',
                   'color': 'lightslategray',
                   'font-family': 'verdana',
                   'font-size': "100%",
                   'display': 'inline-block'}),

    ],style={'height': '250px',
             'width': '600px',
             'display': 'inline-block'}),



    #Opciones
    html.Div([
        html.Div([

            html.Button('UPDATE ALL',id='go',
                        style={'height': '40px',
                               'width': '600px',
                               'font-size': "100%",
                               'display': 'inline-block'}),
            html.P('LOCALIDAD',
                   style ={'height': '25px',
                           'width': '600px',
                           'font-size': "100%"}),

            dcc.Dropdown(id='area_option',
                        options=[{'label': i, 'value': i} for i in localidades],
                        value='CHAPINERO',
                        style={'height': '40px',
                               'width': '600px',
                               'font-size': "100%"}),

                    ],style = {'height': '115px',
                             'width': '600px',
                             'display': 'inline-block'}),

        html.Div([
            html.Div([
                html.P('COMMERCIAL ACTIVITY',
                       style={'height': '20px',
                              'width': '600px',
                               'font-size': "100%"}),

                 dcc.Dropdown(id='commercial_activity_option',
                              options=[{'label': i, 'value': i} for i in comercial],
                              value='Restaurants, Cafés and Bars',
                              style={'height': '40px',
                                     'width': '300px',
                                     'font-size': "100%",
                                     'display': 'inline-block'}),

                        ],style={'height': '70px',
                                 'width': '300px',
                                 'display': 'inline-block'}), #comercial


            html.Div([
                html.P('TRANSPORT NETWORK',
                       style={'height': '20px',
                              'width': '600px',
                               'font-size': "100%"}),

                 dcc.Dropdown(id='transport_network_option',
                              options=[{'label': i, 'value': i} for i in transporte],
                              value='Walking',
                              style={'height': '40px',
                                     'width': '300px',
                                     'font-size': "100%",
                                     'display': 'inline-block'}),

                        ],style={'height': '70px',
                                      'width': '300px',
                                      'display': 'inline-block'}), #Transporte


                    ],style={'height': '70px',
                             'width': '600px',
                             'display': 'inline-block'}), #Transp y Comm opciones

    ],style={'height': '185px',
             'width': '600px',
             'display': 'inline-block'}),

    html.Div([
       dcc.Graph(id='polygon_pcorrs',
                style={'display': 'inline-block'}),
                ],style={'height': '800x',
                         'width': '600px',
                         'display': 'inline-block'})

])


#---------------------------------------------------------------------
# APP CALLBACK FUNCTIONS
#--------------------------------------------------------------------
@app.callback(
    Output('polygon_pcorrs','figure'),
    [Input('go', 'n_clicks')],
    [State('commercial_activity_option', 'value'),
     State('transport_network_option', 'value'),
     State('area_option', 'value')])

def update_polygons(n_clicks,comm,trans,area):


    """
    comm = 'Wholesale'
    trans = 'Transmilenio'
    area = 'BARRIOS UNIDOS'
    """

    varjson = loc_json
    corrs_filtered = loc_corrs[(loc_corrs['Commercial']==comm) & (loc_corrs['Transport']==trans) & (loc_corrs['pval']<0.001)]

    highlight = loc_shp[loc_shp['LocNombre']==area]
    highlight = json.loads(highlight.set_index('LocNombre').to_json())

    poly = go.Figure()


    poly.add_trace(go.Choroplethmapbox(geojson=varjson, locations = corrs_filtered['Localidad'],
                                      z = corrs_filtered['pcorr'],
                                      colorscale='Spectral', zmin=-1, zmax=1,
                                      marker_opacity=0.3, marker_line_width=0.1,
                                      colorbar = dict(thickness = 13,
                                                      x=-0.1,
                                                      xanchor = 'left',
                                                      lenmode='fraction',
                                                      len= 0.8,
                                                       outlinewidth =0,
                                                       tickfont = dict(size=10),
                                                       nticks = 6,
                                                       title = dict (text='Pearson Correlation',
                                                                     side = 'right',
                                                                     font = dict(size=12)
                                                                     )
                                                       )
                                                ))
    try:
        poly.add_trace(go.Choroplethmapbox(geojson=highlight, locations = corrs_filtered['Localidad'],
                                          z = corrs_filtered['pcorr'],
                                          colorscale='Spectral', zmin=-1, zmax=1,
                                          marker_opacity=0.9, marker_line_width=0.5,
                                          colorbar = dict(thickness = 13,
                                                          x=-0.1,
                                                          xanchor = 'left',
                                                           lenmode='fraction',
                                                           len= 0.8,
                                                           outlinewidth =0,
                                                           tickfont = dict(size=10),
                                                           nticks = 6,
                                                           title = dict (text='Pearson Correlation',
                                                                         side = 'right',
                                                                         font = dict(size=12)
                                                                         )
                                                           )
                                                    ))
        print(1)
    except:pass

    poly.update_layout(

    title =dict (text = 'Pearson correlation between ' + comm +' and ' + trans,
                 font=dict(size=10)

        ),

        font=dict(
            size = 7),
        autosize=True,
        width=600, height=600,
        margin=dict(l=10, r=10, t=20, b=10
                    , pad=5),

        mapbox=dict(
            style = "carto-positron",
            bearing=0,
            center=dict(
                lat=4.64,
                lon=-74.12
            ),
            pitch=0,
            zoom=10))
    #plot(poly)

    return poly

if __name__ == '__main__':
    app.run_server(debug=True)