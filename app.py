from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.graph_objects as go

# ## Visualizing the Impact of Air Pollution to Human's Health
#
# We would like to see the relationship betwen air pollution and health in the Greater London Area (GLA) as it was mentioned inside of
# this [report](https://www.london.gov.uk/what-we-do/environment/pollution-and-air-quality/health-and-exposure-pollution).
#
# In general there are two pollutants of concern:
# - Particulate Matter (PM 2.5)
# - Nitrogen Dioxide (NO2)
#
# IN the current implementation we only take a look into NOx (NO2).


def get_diseases_data_prediction(input_file_path):
    df_diseases_data_prediction = pd.read_csv(input_file_path)
    columns_mapping = {
        "Year": "year",
        "Disease": "disease",
        "AgeGroup": "age_group",
        "Incidence": "incidence",
        "95% CL": "above_threshold",
        "Borough": "borough",
    }
    df_diseases_data_prediction = df_diseases_data_prediction.rename(
        columns=columns_mapping
    )
    return df_diseases_data_prediction


def create_plot_on_year(
    diseases_summary_with_high_pollutant, diseases_summary_with_low_pollutant, year
):
    plt.figure(figsize=(25, 10))
    diseases_summary_with_high_pollutant_year = (
        diseases_summary_with_high_pollutant[
            diseases_summary_with_high_pollutant["year"] == year
        ]
        .groupby(["borough"], as_index=False)
        .sum()
    )
    diseases_summary_with_low_pollutant_year = (
        diseases_summary_with_low_pollutant[
            diseases_summary_with_low_pollutant["year"] == year
        ]
        .groupby(["borough"], as_index=False)
        .sum()
    )
    fig, ax = plt.subplots(1, figsize=(20, 6))
    ax = diseases_summary_with_high_pollutant_year.set_index("borough").plot(
        kind="bar", ax=ax, y="incidence", color="C2"
    )
    diseases_summary_with_low_pollutant_year.set_index("borough").plot(
        kind="bar", ax=ax, y="incidence", color="C1"
    )
    ax.set_title(
        "Diseases' Incident Collerated to Pollution Exposure for Each Boroughs in {year}".format(
            year=year
        )
    )
    ax.legend(labels=["Incidence in High Pollution", "Incidence in Low Pollution"])


def get_diseases_insight_based_on_filter(diseases_data_prediction, filters):
    sm = diseases_data_prediction.groupby(filters, as_index=False).sum()
    return sm


def get_merged_summary_table(diseases_summary):
    diseases_summary = get_diseases_insight_based_on_filter(
        diseases_data_prediction, ["borough", "disease", "year", "above_threshold"]
    )
    diseases_summary_with_low_pollutant = diseases_summary[
        diseases_summary["above_threshold"] == 0
    ]
    diseases_summary_with_low_pollutant = diseases_summary_with_low_pollutant.drop(
        ["above_threshold"], axis=1
    )
    diseases_summary_with_low_pollutant = diseases_summary_with_low_pollutant.rename(
        {"incidence": "low"}, axis="index"
    )
    diseases_summary_with_high_pollutant = diseases_summary[
        diseases_summary["above_threshold"] == 1
    ]
    diseases_summary_with_high_pollutant = diseases_summary_with_high_pollutant.drop(
        ["above_threshold"], axis=1
    )
    diseases_summary_with_high_pollutant = diseases_summary_with_high_pollutant.rename(
        {"incidence": "high"}, axis="index"
    )
    merged_disease_summary = diseases_summary_with_high_pollutant.copy().merge(
        diseases_summary_with_low_pollutant.copy(),
        how="inner",
        left_on=["borough", "disease", "year"],
        right_on=["borough", "disease", "year"],
    )
    merged_disease_summary = merged_disease_summary.rename(
        columns={"incidence_x": "high_exposure", "incidence_y": "low_exposure"}
    )
    return merged_disease_summary


app = Dash(__name__)

diseases_data_prediction_input_file_path = "data/diseases.csv"
diseases_data_prediction = get_diseases_data_prediction(
    diseases_data_prediction_input_file_path
)

merged_disease_summary = get_merged_summary_table(diseases_data_prediction)
fig = px.bar(
    merged_disease_summary,
    x="borough",
    y=["high_exposure", "low_exposure"],
    barmode="group",
)

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
