import streamlit as st
import pandas as pd

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

# Crear un widget de carga de archivos
archivo = st.file_uploader("Cargar archivo CSV", type="csv")

# Verificar si se cargó un archivo
if archivo is not None:
    # Leer los datos del archivo CSV
    df = pd.read_csv(archivo)

    # Mostrar la tabla utilizando st.dataframe
    st.subheader("Tabla de datos")
    st.dataframe(df)

    # Crear un gráfico a partir del DataFrame
    st.subheader("Gráfico")
    chart_type = st.selectbox("Selecciona el tipo de gráfico", ["Barra", "Línea", "Histograma"])
    chart_column = st.selectbox("Selecciona la columna para el gráfico", df.columns)

    if chart_type == "Barra":
        st.bar_chart(df[chart_column])
    elif chart_type == "Línea":
        st.line_chart(df[chart_column])
    elif chart_type == "Histograma":
        st.histogram(df[chart_column])
    # Agregar filtros con pandas
    st.subheader("Filtros")
    column = st.selectbox("Selecciona la columna para filtrar", df.columns)
    filter_value = st.text_input("Ingresa el valor para filtrar")
    filtered_df = df[df[column] == filter_value]
    st.dataframe(filtered_df)
