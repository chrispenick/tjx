# streamlit run app.py

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("Simple Data Explorer")

# File upload
uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Data Preview")
    st.write(df.head())

    # Column selector
    numeric_cols = df.select_dtypes(include=["float", "int"]).columns
    col = st.selectbox("Choose a numeric column to plot", numeric_cols)

    # Histogram
    fig, ax = plt.subplots()
    sns.histplot(df[col], kde=True, ax=ax)
    st.pyplot(fig)

    # Summary stats
    st.subheader("Summary Statistics")
    st.write(df[col].describe())
else:
    st.info("Upload a CSV file to get started.")
