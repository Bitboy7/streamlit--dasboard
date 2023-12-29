import streamlit as st
import pandas as pd

st.title("Carga de archivos excel 📗")
st.markdown("Prototipo 0.1.0")

# Cargar el archivo
@st.cache_data
def load_data(file):
    data = pd.read_excel(file)
    return data

uploaded_file = st.sidebar.file_uploader("Cargar archivo excel.", type=["xlsx"])

# Validar que el archivo no esté vacío
if uploaded_file is None:
    st.info("Por favor carga un archivo...", icon="⚠️")
    st.stop()

# Mostrar los datos
df = load_data(uploaded_file)

with st.expander("Ver datos"):
    st.dataframe(df)
    

