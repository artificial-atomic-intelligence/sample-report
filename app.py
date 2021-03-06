import streamlit as st

import pandas as pd
import numpy as np

import plotly.graph_objects as go
from plotly import tools
import plotly.offline as py
import plotly.express as px
import plotly.io as pio
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

from matminer.datasets import load_dataset
from matminer.featurizers.composition import Meredig
from pymatgen import Composition

# User authentication
st.markdown("Hint: the username is `user` and the password is `password`.")
username = st.text_input("Username: ", "")
pw = st.text_input("Password: ", "")

# Get data and featurize
@st.cache
def load_data(nrows):
    df = load_dataset("matbench_expt_is_metal")
    df = df.sample(nrows, random_state=42)
    featurizer = Meredig()
    df["pmg_composition"] = df["composition"].apply(lambda x: Composition(x))
    df_feat = featurizer.featurize_dataframe(
        df=df, col_id="pmg_composition", ignore_errors=True, pbar=False
    ).drop(columns=["pmg_composition"])
    df_feat["is_metal"] = df_feat["is_metal"].apply(lambda x: 1 if x else 0)
    df_feat["Metal vs Nonmetal"] = df_feat["is_metal"].apply(
        lambda x: "Metal" if x else "Nonmetal"
    )
    return df_feat


if username == "user" and pw == "password":
    data = load_data(100)

# Text header
st.title("AtomicAI Interactive Report")
st.write(
    "This is an example interactive report generated by AtomicAI. "
    "It shows how your company data is processed, visualized, and "
    "analyzed, enabling you to quickly understand your data and make "
    "decisions. We present our findings directly inline with the data "
    "visualizations that support our conclusions."
    "\n "
    "In this simple example, we'll show how we can predict whether a given "
    "crystal composition is a metal or a nonmetal. "
)

# Display data
if st.checkbox("Show data"):
    st.subheader("Raw data statistics")
    st.write(data.describe())
    st.write(
        "There are %d samples and %d descriptors." % (data.shape[0], data.shape[1])
    )

# Set theme
pio.templates.default = "simple_white"

# Histogram of exp. bandgaps
# st.subheader('Metal vs nonmetal')
# st.write("A histogram of our measured variable, metallicity.")
# num_bins = st.sidebar.slider('Number of bins', 0, 100, 12)

# hist_fig = px.histogram(data, x='gap expt', nbins=num_bins)
# st.plotly_chart(hist_fig)

# Correlation matrix
st.subheader("Feature correlation")
st.write(
    "Correlation matrix that shows the features that have highest \
    linear correlation with metallicity. Each quantity is calculated purely \
    based on the crystal composition."
)
corr = data.corr().abs()
top_5 = corr["is_metal"].sort_values(ascending=False).index[:5]
corr = data[top_5].corr().abs()
corr_fig = px.imshow(corr)
st.plotly_chart(corr_fig)

# Feature relationships
top_3 = corr["is_metal"].sort_values(ascending=False).index[1:4]
for idx, col in enumerate(top_3):
    box_fig = px.violin(
        data, x="Metal vs Nonmetal", y=col, box=True, color="Metal vs Nonmetal"
    )
    st.plotly_chart(box_fig)

# Pivot tables
st.subheader("Pivot tables")
st.write(
    "Pivot tables help us understand the statistical relationships "
    "between a target variable and other descriptors of a sample."
)
table = pd.pivot_table(
    data, index="Metal vs Nonmetal", values=top_3, aggfunc=[np.mean, np.median, np.var]
)
st.write(table)
