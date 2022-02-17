from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
from plotly.express import data
from data_visualization_utility import *
import pyproj

app = Dash(__name__)

map_file_path = "data/geo-data/statistical-gis-boundaries-london/ESRI/London_Borough_Excluding_MHW.shp"
map_df = gpd.read_file(map_file_path)
map_df.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
merged_disease_summary = pd.read_csv(
    "data/diseases-incidences/diseases_incidence_summary.csv"
)
filter_disease = list(merged_disease_summary["year"].unique())

# https://stackoverflow.com/questions/65507374/plotting-a-geopandas-dataframe-using-plotly
green_spaces_area_count = pd.read_csv(
    "data/green-spaces/green_spaces_count_per_region.csv"
)
filter_borough = list(green_spaces_area_count["borough"])

green_spaces_area_geomap = merge_df_with_gis_data(
    map_df, green_spaces_area_count, "borough"
)
green_spaces_geomap = px.choropleth(
    green_spaces_area_geomap,
    geojson=green_spaces_area_geomap["geometry"],
    locations=green_spaces_area_geomap.index,
    color="count",
    projection="mercator",
    title="Green Spaces Area in Each Borough in Greater London Area (GLA)",
)
green_spaces_geomap.update_geos(fitbounds="locations", visible=False)

app = Dash(__name__)
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(dcc.Dropdown(filter_disease, id="filter-disease")),
                html.Div(id="diseases-incidence-per-year"),
            ]
        ),
        html.Div(children=[dcc.Graph(id="example-graph", figure=green_spaces_geomap)]),
    ]
)


@app.callback(
    Output("diseases-incidence-per-year", "children"), Input("filter-disease", "value")
)
def update_output(value):
    if value is None:
        value = "2016"
    sm = pd.read_csv(
        "data/diseases-incidences/diseases_incidence_summary_{}.csv".format(value)
    )
    fig = px.bar(
        sm,
        x="borough",
        y=["high_exposure", "low_exposure"],
        barmode="group",
        title="Disease's Incidence as High and Low Exposure to Air Pollution (NOX) in {year}".format(
            year=value
        ),
    )
    return dcc.Graph(id="example-graph", figure=fig)


if __name__ == "__main__":
    app.run_server(debug=True)
