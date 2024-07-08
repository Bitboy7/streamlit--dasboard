import streamlit as st

@st.cache_data
def load_css_style():
    with open('style.css') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)