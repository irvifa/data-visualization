import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd

# ## Getting GIS for Greater London Area(GLA)
#
# We're using GIS provided inside of this [website](https://data.london.gov.uk/dataset/long-term-health-impacts-of-air-pollution)


def generate_heat_map(df, variable):
    # set the range for the choropleth
    vmin, vmax = 120, 220
    # create figure and axes for Matplotlib
    fig, ax = plt.subplots(1, figsize=(10, 6))
    df.plot(column=variable, cmap="Blues", linewidth=0.8, ax=ax, edgecolor="0.8")


def merge_df_with_gis_data(map_df, df, join_column):
    merged = map_df.copy().set_index("NAME").join(df.copy().set_index(join_column))
    # There will be NAN value for missing dada.
    merged = merged.fillna(0)
    return merged


# ### Getting Information Regarding Air Pollution in GLA


def generate_plot_based_on_pollutant(ax, summary_of_pollutant_per_borough, pollutant):
    df = (
        summary_of_pollutant_per_borough[
            summary_of_pollutant_per_borough["pollutant"] == pollutant
        ]
        .groupby(["borough"], as_index=False)
        .sum()
    )
    x, y = df[["borough"]], df[["total"]]
    return x, y


def get_summary_based_on_pollutant(summary_of_pollutant_per_borough, pollutant):
    sm = (
        summary_of_pollutant_per_borough[
            summary_of_pollutant_per_borough["pollutant"] == pollutant
        ]
        .groupby(["borough", "year"], as_index=False)
        .sum()
    )
    return sm


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
