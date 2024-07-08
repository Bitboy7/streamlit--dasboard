import streamlit as st
import pandas as pd

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)
# Importar las funciones de ayuda
from helpers.load_css import load_css_style
# Cargar el estilo CSS
load_css_style()

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

# Añadir filtros
with st.expander("Filtros"):
    columnas = df.columns.tolist()
    filtro_columna = st.selectbox("Selecciona una columna para filtrar:", columnas)
    filtro_valor = st.text_input("Ingresa el valor para filtrar:")
    if st.button("Aplicar filtro"):
        df = df[df[filtro_columna] == filtro_valor]
        st.dataframe(df)

# Hacer operaciones según el archivo cargado
with st.expander("Operaciones"):
    operacion = st.selectbox("Selecciona una operación:", ["Suma", "Promedio", "Máximo", "Mínimo"])
    columna_operacion = st.selectbox("Selecciona una columna para la operación:", columnas)
    if st.button("Aplicar operación"):
        if operacion == "Suma":
            resultado = df[columna_operacion].sum()
        elif operacion == "Promedio":
            resultado = df[columna_operacion].mean()
        elif operacion == "Máximo":
            resultado = df[columna_operacion].max()
        elif operacion == "Mínimo":
            resultado = df[columna_operacion].min()
        st.write(f"El resultado de la operación {operacion} en la columna {columna_operacion} es: {resultado}")

