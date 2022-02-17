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

app = Dash(__name__)

merged_disease_summary = pd.read_csv("data/diseases-incidences/diseases_incidence_summary.csv")
filter_disease = list(merged_disease_summary["year"].unique())

app = Dash(__name__)
app.layout = html.Div(
    children=[
        html.Div(dcc.Dropdown(filter_disease, id="filter-disease")),
        html.Div(id="diseases-incidence-per-year"),
    ]
)


@app.callback(
    Output("diseases-incidence-per-year", "children"), Input("filter-disease", "value")
)
def update_output(value):
    if value is None:
        value = '2016'
    sm = pd.read_csv("data/diseases-incidences/diseases_incidence_summary_{}.csv".format(value))
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
