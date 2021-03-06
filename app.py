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

"""
We only analyze NOx for this part
"""
nox_pollutant_summary_file_path = (
    "data/pollutant/summary_of_pollutant_per_borough_NOx.csv"
)
nox_pollutant_summary_df = pd.read_csv(nox_pollutant_summary_file_path)
nox_diseases_incident_file_path = (
    "data/diseases-incidences/diseases_incidence_summary_2016.csv"
)
nox_diseases_incident_file_df = pd.read_csv(nox_diseases_incident_file_path)
merged_pollutant_disease = nox_pollutant_summary_df.copy().merge(
    nox_diseases_incident_file_df.copy(),
    how="inner",
    left_on=["borough", "year"],
    right_on=["borough", "year"],
)
pollutant_disease_correlation = px.scatter(
    merged_pollutant_disease, x="total", y="high_exposure", trendline="ols"
)

# Pollution
pollution_data = pd.read_csv("data/pollutant/summary_of_pollutant_per_borough.csv")
pollution_kind = list(pollution_data["pollutant"].unique())

app = Dash(__name__)
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(dcc.Dropdown(pollution_kind, id="filter-pollution")),
                html.Div(id="pollution-summary-per-borough"),
                html.Div(id="heat-map-per-borough"),
            ]
        ),
        html.Div(children=[dcc.Graph(id="example-graph", figure=green_spaces_geomap)]),
        html.Div(
            children=[
                html.Div(dcc.Dropdown(filter_disease, id="filter-disease")),
                html.Div(id="diseases-incidence-per-year"),
            ]
        ),
        html.Div(
            children=[
                dcc.Graph(
                    id="pollution-and-disease-relationship",
                    figure=pollutant_disease_correlation,
                )
            ]
        ),
    ]
)


@app.callback(
    Output("pollution-summary-per-borough", "children"),
    Input("filter-pollution", "value"),
)
def update_pollutant_graph(value):
    if value is None:
        value = "CO2"
    sm = pd.read_csv(
        "data/pollutant/summary_of_pollutant_per_borough_{}.csv".format(value)
    )
    fig = go.Figure()
    parameters = [
        "motorcycle",
        "taxi",
        "petrol_car",
        "diesel_car",
        "electric_car",
        "petrol_lgv",
        "diesel_lgv",
        "electric_lgv",
        "total",
    ]
    for parameter in parameters:
        fig.add_trace(
            go.Scatter(
                x=sm["borough"], y=sm[parameter], mode="lines+markers", name=parameter
            )
        )
    return dcc.Graph(id="example-graph", figure=fig)


@app.callback(
    Output("heat-map-per-borough", "children"),
    Input("filter-pollution", "value"),
)
def update_pollutant_heat_map(value):
    if value is None:
        value = "CO2"
    sm = pd.read_csv(
        "data/pollutant/summary_of_pollutant_per_borough_{}.csv".format(value)
    )
    pollutant_area_geomap = merge_df_with_gis_data(map_df, sm, "borough")
    fig = px.choropleth(
        pollutant_area_geomap,
        geojson=green_spaces_area_geomap["geometry"],
        locations=green_spaces_area_geomap.index,
        color="total",
        projection="mercator",
        title="Emission of {pollutant} from all vehicles in each borough in Greater London Area (GLA).".format(
            pollutant=value
        ),
    )
    fig.update_geos(fitbounds="locations", visible=False)
    return dcc.Graph(id="example-graph", figure=fig)


@app.callback(
    Output("diseases-incidence-per-year", "children"), Input("filter-disease", "value")
)
def update_disease_incidence_graph(value):
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
