import geojson
import geopandas as gpd
import pandas as pd
import plotly.express as px
import csv

departement = gpd.read_file('./geojson/departements.geojson')
x, y = departement.geometry[0].exterior.coords.xy

characteristics = pd.read_csv('./csv/accident/caracteristiques-2019.csv', sep=';')

name_department = pd.DataFrame(departement).loc[:, 'code':'nom']
nb_accident_dep = characteristics.dep.astype(str).str.zfill(2).value_counts().rename_axis('code').reset_index(name='counts')

accident_dep = pd.merge(nb_accident_dep, name_department, on='code');


defaultFig = px.choropleth_mapbox(accident_dep, geojson=departement, 
                           featureidkey='properties.code', locations='code', 
                           hover_name =accident_dep.nom,
                           color='counts', color_continuous_scale="Viridis",
                           range_color=(min(accident_dep.counts), max(accident_dep.counts)),
                           mapbox_style="carto-positron",
                           zoom=7, center = {"lat": 49.453533722068, "lon": 3.608257387098},
                           opacity=0.5,
                           labels={'code':'departement', 'counts': 'nombre d\'accident'}
                          )

defaultFig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
# defaultFig.show()





import dash
import flask
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
f_app = flask.Flask(__name__)
app = dash.Dash(__name__, server=f_app)
app.layout = html.Div([
   dcc.Graph(figure=defaultFig, id='map')
])

@app.callback(
   Output("map", "figure"), 
   [Input("map", "clickData")])

def display_click_data(clickData):
   if(clickData == None): return (defaultFig)
   location = clickData['points'][0]['location']
   print(location)
   test = madeFig(location)
   return (test)

def madeFig(location):
   communes = gpd.read_file('./geojson/communes.geojson')
   characteristics = pd.read_csv('./csv/accident/caracteristiques-2019.csv', sep=';')

   name_communes = pd.DataFrame(communes).loc[:, 'insee_com':'nom_comm']
   accident_communes = characteristics.com.value_counts().rename_axis('insee_com').reset_index(name='counts')
   accident_communes = pd.merge(accident_communes, name_communes, on='insee_com')
   accident_communes = accident_communes.query("code_dept=='{}'".format(location))

   returnFig = px.choropleth_mapbox(accident_communes, geojson=communes, 
                              featureidkey='properties.insee_com', locations='insee_com', 
                              hover_name =accident_communes.nom_comm,
                              hover_data=[accident_communes.postal_code, accident_communes.counts],
                              color='counts', color_continuous_scale="Viridis",
                              range_color=(min(accident_communes.counts), max(accident_communes.counts)),
                              mapbox_style="carto-positron",
                              zoom=6, center = {"lat": 46.4252134, "lon": 2.5},
                              opacity=0.5,
                              labels={'insee_com':'Code INSEE', 'postal_code':'Code postal', 'counts': 'Nombre d\'accidents'},
                           )
   return(returnFig)

app.run_server(debug=True)  # Turn off reloader if inside Jupyter