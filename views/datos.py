import streamlit as st
import time
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
from helpers.download_files import *

from models.db import create_connection
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)
from st_pages import show_pages_from_config, add_page_title
show_pages_from_config()
# Importar las funciones de ayuda
from helpers.load_css import load_css_style
# Cargar el estilo CSS
load_css_style()

import os
from dotenv import load_dotenv
load_dotenv()

conn = create_connection()
cursor = conn.cursor()

# Funciones para las consultas a la base de datos
def execute_query(query, params=None):
    cursor.execute(query, params)
    conn.commit()

def fetch_all(query, params=None):
    cursor.execute(query, params)
    return cursor.fetchall()

def fetch_one(query, params=None):
    cursor.execute(query, params)
    return cursor.fetchone()    

# Check if connection is established
if conn.is_connected():
    st.write("Connected to database")
else:
    st.write("Not connected to database")

# Mostrar datos
st.subheader("Datos.")

# Realizar la consulta SQL
def get_registros():
    query = """SELECT r.*, su.nombre AS Sucursal, ca.nombre AS Categoria, es.nombre AS Estado
               FROM registro r, sucursal su, cat_gastos ca, estado es
               WHERE r.id_sucursal = su.id
               AND r.id_cat_gasto = ca.id
               AND su.id_estado = es.id;"""
    return fetch_all(query)

registros = get_registros()

# Mostrar la tabla en Streamlit
if not registros:
    st.write("No hay registros disponibles.")
else:
    # Mostrar la tabla en Streamlit
    expander = st.sidebar.expander("Filtros.", expanded=False)

    # Obtener los nombres de categoría únicos
    categorias = fetch_all("SELECT DISTINCT nombre FROM cat_gastos")
    filtro_categoria = expander.selectbox("Por categoria:", ["Todas"] + [categoria[0] for categoria in categorias])

    if filtro_categoria == "Todas":
        filtro_categoria = None

    # Componente de filtrado
    sucursales = fetch_all("SELECT DISTINCT nombre FROM sucursal")
    filtro_sucursal = expander.selectbox("Por sucursal:", ["Todas"] + [sucursal[0] for sucursal in sucursales])

    if filtro_sucursal == "Todas":
        filtro_sucursal = None

    # Filtrar el dataframe por categoría seleccionada, fecha y sucursal
    df_filtrado = registros.copy()
    if filtro_categoria:
        df_filtrado = [registro for registro in df_filtrado if registro[7] == filtro_categoria]

    # Obtener el rango de fechas seleccionado por el usuario
    filtro_rango_fecha = expander.selectbox(
        "Por rango de fechas:", ["Día", "Semana", "Mes", "Año"])

    if filtro_rango_fecha:
        today = pd.Timestamp.today().normalize()
        if filtro_rango_fecha == "Día":
            start_date = expander.date_input("Fecha inicial:")
            end_date = expander.date_input("Fecha final:", value=today)
        elif filtro_rango_fecha == "Semana":
            start_date = expander.date_input(
                "Semana inicial:", value=today - pd.DateOffset(weeks=1))
            end_date = expander.date_input("Semana final:", value=today)
        elif filtro_rango_fecha == "Mes":
            start_date = expander.date_input(
                "Mes inicial:", value=today - pd.DateOffset(months=1))
            end_date = expander.date_input("Mes final:", value=today)
        elif filtro_rango_fecha == "Año":
            start_date = expander.date_input(
                "Año inicial:", value=today - pd.DateOffset(years=1))
            end_date = expander.date_input("Año final:", value=today)

        # Filtrar el dataframe por rango de fechas seleccionado
        if start_date and end_date:
            df_filtrado = [registro for registro in df_filtrado if start_date <= registro[4].date() <= end_date]

    if filtro_sucursal:
        df_filtrado = [registro for registro in df_filtrado if registro[6] == filtro_sucursal]

    # Formatear la columna "monto" como moneda
    df_filtrado = [[registro[0], registro[1], registro[2], f'${registro[3]:,.2f}', registro[4], registro[5], registro[6], registro[7], registro[8]] for registro in df_filtrado]

# Mostrar el dataframe filtrado
st.dataframe(pd.DataFrame(df_filtrado, columns=['ID', 'ID_sucursal', 'ID_categoria', 'Monto',
                                                          'Fecha registrada', 'Descripcion', 'Sucursal', 'Categoria', 'Estado']))


# Obtener el tipo de estadística seleccionada por el usuario
filtro_estadistica = expander.selectbox(
    "Tipo de estadística:", ["Suma", "Promedio", "Mínimo", "Máximo"])

if filtro_estadistica:
    # Convertir la columna "monto" a números
    df_filtrado = [[registro[0], registro[1], registro[2], float(registro[3][1:].replace(',', '')), registro[4], registro[5], registro[6], registro[7], registro[8]] for registro in df_filtrado]

    if filtro_estadistica == "Suma":
        # Calcular la suma de la columna "monto"
        suma_monto = sum([registro[3] for registro in df_filtrado])
        expander.write(f"Suma de la columna 'monto': ${suma_monto:.2f} pesos.")
    elif filtro_estadistica == "Promedio":
        # Calcular el promedio de la columna "monto"
        promedio_monto = sum([registro[3] for registro in df_filtrado]) / len(df_filtrado)
        expander.write(f"Promedio de la columna 'monto': ${promedio_monto:.2f} pesos.")
    elif filtro_estadistica == "Mínimo":
        # Obtener el valor mínimo de la columna "monto"
        minimo_monto = min([registro[3] for registro in df_filtrado])
        expander.markdown(f"Valor mínimo de la columna 'monto': {minimo_monto:.2f}")
    elif filtro_estadistica == "Máximo":
        # Obtener el valor máximo de la columna "monto"
        maximo_monto = max([registro[3] for registro in df_filtrado])
        expander.markdown(f"Valor máximo de la columna 'monto': {maximo_monto:.2f}")

# Crear las card metrics
col1, col2, col3, col4 = st.columns(4)
# Obtener el número total de transacciones
num_transacciones = len(df_filtrado)

if num_transacciones > 0:
    # Obtener el monto total de todas las transacciones
    monto_total = sum([registro[3] for registro in df_filtrado])

    # Obtener el monto promedio de las transacciones
    monto_promedio = monto_total / num_transacciones

    # Obtener el monto máximo y mínimo de las transacciones
    monto_maximo = max([registro[3] for registro in df_filtrado])
    monto_minimo = min([registro[3] for registro in df_filtrado])
else:
    monto_total = 0
    monto_promedio = 0
    monto_maximo = 0
    monto_minimo = 0

col1.metric(label="Transacciones", value=num_transacciones, delta="Total de transacciones.")

col2.metric(label="Total", value=f"${monto_total:,.2f}", delta="Suma total de todas las transacciones.")

col3.metric(label="Promedio", value=f"${monto_promedio:,.2f}", delta="Promedio de los montos de las transacciones.")

col4.metric(label="Máximo", value=f"${monto_maximo:,.2f}", delta="Monto máximo de las transacciones.")

style_metric_cards(background_color="#3D3B3B", border_left_color="#35A94A")


# Mostrar opciones de descarga
# Crear un archivo Excel con los datos filtrados
expander.markdown(download_excel_file(df_filtrado), unsafe_allow_html=True)

# Crear gráfico interactivo con Plotly
df_filtrado = pd.DataFrame(df_filtrado, columns=['ID', 'ID_sucursal', 'ID_categoria', 'Monto',
                                                  'Fecha registrada', 'Descripcion', 'Sucursal', 'Categoria', 'Estado'])

fig = px.bar(df_filtrado, x='Monto', y='Categoria', title="Gráfico por Categoría.",
             hover_data=['Categoria', 'Monto'], color='Sucursal', text_auto=True,
             labels={'costo': 'categoria'}, height=500)

# Crear gráfico interactivo con Plotly
fig2 = px.bar(df_filtrado, x='Sucursal', y='Monto', title="Gráfico por Sucursal.",
              hover_data=['Sucursal', 'Monto'], color='Categoria', text_auto=True,
              labels={'gastos': 'Gráfico de Montos por Sucursal.'}, height=500)

fig3 = px.pie(df_filtrado, values='Monto', names='Categoria', title='Gastos por Categoría')

fig4 = px.pie(df_filtrado, values='Monto', names='Sucursal', title='Gastos por Sucursal')

st.subheader("Gráficas.")
# Obtener el tipo de gráfico seleccionado por el usuario
filtro_grafico = st.selectbox(
    "Tipo de gráfico:", ["Gráfico de Montos por Categoría (Bar)", "Gráfico de Montos por Sucursal (Bar)",
                         "Gráfico de Montos por Categoría (Pie)", "Gráfico de Montos por Sucursal (Pie)"])

if filtro_grafico == "Gráfico de Montos por Categoría (Bar)":
    # Mostrar gráfico de Montos por Categoría en Streamlit
    st.plotly_chart(fig)
elif filtro_grafico == "Gráfico de Montos por Sucursal (Bar)":
    # Mostrar gráfico de Montos por Sucursal en Streamlit
    st.plotly_chart(fig2)
elif filtro_grafico == "Gráfico de Montos por Categoría (Pie)":
    # Mostrar gráfico de Montos por Categoría (Pie) en Streamlit
    st.plotly_chart(fig3)
elif filtro_grafico == "Gráfico de Montos por Sucursal (Pie)":
    st.plotly_chart(fig4)

# Cerrar el cursor y la conexión a la base de datos
cursor.close()
conn.close()
