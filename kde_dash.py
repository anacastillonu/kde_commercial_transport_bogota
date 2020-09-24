#-----------------------------------------------------------
# IMPORT LIBRARIES
#-----------------------------------------------------------

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

url = 'https://raw.githubusercontent.com/anacastillonu/kde_commercial_transport_bogota/master/data/kde.geojson'
all_kde = gpd.read_file(url).set_crs(epsg=3116).to_crs(epsg=4326)

url = 'https://raw.githubusercontent.com/anacastillonu/kde_commercial_transport_bogota/master/data/all_hot.geojson'
all_hot = gpd.read_file(url)

url = 'https://raw.githubusercontent.com/anacastillonu/kde_commercial_transport_bogota/master/data/loc_mod.geojson'
loc_shp = gpd.read_file(url)
