import os
import streamlit as st
from dotenv import load_dotenv
load_dotenv() 

from tjx_style_demo.quiz import Quiz
from tjx_style_demo.catalog import load_or_buildCatalog
from tjx_style_demo.llm import prefilter, compose_outfit

st.set_page_config(page_title="TJX Style Quiz", page_icon="🛍️", layout="wide")
st.title("🛍️ TJX Style Quiz — Outfit Recommender")

col1, col2, col3, col4 = st.columns(4)
with col1:
    season = st.selectbox("Season", ["spring","summer","fall","winter"], index=2)
with col2:
    vibe = st.selectbox("Vibe", ["minimalist","sporty","boho","cozy","edgy","classic"], index=3)
with col3:
    palette = st.selectbox("Palette", ["neutrals","brights","earth tones","pastels"], index=0)
with col4:
    budget = st.number_input("Budget (USD)", min_value=20.0, max_value=1000.0, value=150.0, step=5.0)

quiz = Quiz(season=season, vibe=vibe, palette=palette, budget=budget)

catalog = load_or_buildCatalog(max_products=40)
st.caption(f"Catalog size: {len(catalog)} items")

if st.button("✨ Generate Outfit"):
    sample = prefilter(catalog, quiz)
    md = compose_outfit(quiz, sample)
    st.markdown(md)

    st.subheader("Items considered")
    cols = st.columns(3)
    for i, it in enumerate(sample):
        with cols[i % 3]:
            if it.get("image"):
                st.image(it["image"], use_column_width=True)
            st.markdown(f"**{it.get('name','')}**")
            st.markdown(f"${it.get('price',0):.2f} — [{it.get('url','(link)')}]({it.get('url','#')})")
