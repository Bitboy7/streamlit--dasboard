import streamlit as st
from streamlit_lottie import st_lottie
import json
import requests
import datetime
from streamlit_card import card

st.set_page_config(
    page_title="Sistema de Gestión de gastos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.caption('This is a string that explains something above.')


def get(path: str):
    with open(path, "r") as p:
        return json.load(p)


path = get("./ani.json")

# Crear dos columnas
col1, col2 = st.columns(2)

# Colocar un título en la primera columna
with col1:
    st.header("Bienvenido al gestor de gastos.")
    st.subheader("Agricola de la Costa San Luis S.A. de C.V.")
    st.write("Este sistema permite llevar un control de los gastos de la empresa, así como de los egresos de la misma.")
with col2:
    st_lottie(path)

    
