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
col1, col2, col3 = st.columns(3)

# Colocar un título en la primera columna
with col1:
    st.header("Benvenido al sistema de gestión de gastos.")
    st.subheader("Agricola de la Costa San Luis S.A. de C.V.")
    st_lottie(path)

with col2:
    st.image("https://images.unsplash.com/photo-1548950308-69fac3b90a45?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MzE2fHxmaW5hbmNlfGVufDB8fDB8fHww")
    
with col3:
    data = "./video.mp4"
    st.video(data, format="video/mp4", start_time=0)
    
