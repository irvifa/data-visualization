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

diseases_data_prediction_input_file_path = "data/diseases.csv"
diseases_data_prediction = get_diseases_data_prediction(
    diseases_data_prediction_input_file_path
)

merged_disease_summary = get_merged_summary_table(diseases_data_prediction)
merged_disease_summary = merged_disease_summary[merged_disease_summary["year"] <= 2018]


filter_disease = list(merged_disease_summary["year"].unique())

app = Dash(__name__)
app.layout = html.Div(
    children=[
        html.Div(dcc.Dropdown(filter_disease, id="filter-disease")),
        html.Div(id="pandas-output-container-2"),
    ]
)


@app.callback(
    Output("pandas-output-container-2", "children"), Input("filter-disease", "value")
)
def update_output(value):
    merged_disease_summary_on_2016 = merged_disease_summary_for_year(
        merged_disease_summary, value
    )
    sm = merged_disease_summary_on_2016.groupby(["borough"], as_index=False).sum()
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

app.layout = html.Div(
    children=[
        html.H1(children="Data Visualization"),
        html.Div(
            children="""
        Dash: A web application framework for your data.
    """
        ),
        dcc.Graph(id="example-graph", figure=fig),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
