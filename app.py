import streamlit as st

st.set_page_config(
    page_title="Sistema de Gestión de gastos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
st.title("Benvenido")
st.write("Agricola de la Costa San Luis S.A. de C.V.") 

st.caption('This is a string that explains something above.')
st.caption('A caption with _italics_ :blue[colors] and emojis :sunglasses:')
