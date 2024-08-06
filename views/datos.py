import streamlit as st
import time
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
from helpers.download_files import *
from controllers.querys import *
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

from models.db import create_connection
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu

conn = create_connection()
cursor = conn.cursor()
 
# Check if connection is established
if conn.is_connected():
    st.write("Connected to database")
else:
    st.write("Not connected to database")

# Mostrar datos
st.subheader("Datos.")

registros = obtener_registros_df()

# Mostrar la tabla en Streamlit
if not registros:
    st.write("No hay registros disponibles.")
else:
    # Mostrar la tabla en Streamlit
    expander = st.sidebar.expander("Filtros.", expanded=False)

    # Obtener los nombres de categoría únicos
    categorias = fetch_all("SELECT DISTINCT nombre FROM gastos_catgastos")
    filtro_categoria = expander.selectbox("Por categoria:", ["Todas"] + [categoria[0] for categoria in categorias])

    if filtro_categoria == "Todas":
        filtro_categoria = None

    # Componente de filtrado
    sucursales = fetch_all("SELECT DISTINCT nombre FROM catalogo_sucursal")
    filtro_sucursal = expander.selectbox("Por sucursal:", ["Todas"] + [sucursal[0] for sucursal in sucursales])

    if filtro_sucursal == "Todas":
        filtro_sucursal = None

    # Componente de filtrado
    cuentas = fetch_all("SELECT DISTINCT numero_cuenta FROM gastos_cuenta")
    filtro_cuenta = expander.selectbox("Por cuenta de banco:", ["Todas"] + [cuenta[0] for cuenta in cuentas])

    if filtro_cuenta == "Todas":
        filtro_cuenta = None

    # Filtrar el dataframe por categoría seleccionada, fecha, sucursal y cuenta de banco
    df_filtrado = registros.copy()
    if filtro_categoria:
        df_filtrado = [registro for registro in df_filtrado if registro[2] == filtro_categoria]
    if filtro_sucursal:
        df_filtrado = [registro for registro in df_filtrado if registro[3] == filtro_sucursal]
    if filtro_cuenta:
        df_filtrado = [registro for registro in df_filtrado if registro[4] == filtro_cuenta]

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
            df_filtrado = [registro for registro in df_filtrado if start_date <= registro[0] <= end_date]

    if filtro_sucursal:
        df_filtrado = [registro for registro in df_filtrado if registro[3] == filtro_sucursal]

    # Formatear la columna "monto" como moneda
    df_filtrado = [[registro[0], f'${registro[1]:,.2f}', registro[2], registro[3], registro[4], registro[5]] for registro in df_filtrado]

# Mostrar el dataframe filtrado
st.dataframe(pd.DataFrame(df_filtrado, columns=['Fecha', 'Monto', 'Categoria', 'Sucursal','Numero de cuenta', 'Banco']))

# Obtener el tipo de estadística seleccionada por el usuario
filtro_estadistica = expander.selectbox(
    "Tipo de estadística:", ["Suma", "Promedio", "Mínimo", "Máximo"])

if filtro_estadistica:
    # Convertir la columna "monto" a números
    df_filtrado = [[registro[0], float(registro[1][1:].replace(',', '')), registro[2], registro[2], registro[3], registro[4], registro[5]] for registro in df_filtrado]

    if filtro_estadistica == "Suma":
        # Calcular la suma de la columna "monto"
        suma_monto = sum([registro[1] for registro in df_filtrado])
        
    elif filtro_estadistica == "Promedio":
        # Calcular el promedio de la columna "monto"
        promedio_monto = sum([registro[1] for registro in df_filtrado]) / len(df_filtrado)
        
    elif filtro_estadistica == "Mínimo":
        # Obtener el valor mínimo de la columna "monto"
        minimo_monto = min([registro[1] for registro in df_filtrado])
        
    elif filtro_estadistica == "Máximo":
        # Obtener el valor máximo de la columna "monto"
        maximo_monto = max([registro[1] for registro in df_filtrado])
   

# Crear las card metrics
col1, col2, col3, col4 = st.columns(4)
# Obtener el número total de transacciones
num_transacciones = len(df_filtrado)

if num_transacciones > 0:
    # Obtener el monto total de todas las transacciones
    monto_total = sum([registro[1] for registro in df_filtrado])

    # Obtener el monto promedio de las transacciones
    monto_promedio = monto_total / num_transacciones

    # Obtener el monto máximo y mínimo de las transacciones
    monto_maximo = max([registro[1] for registro in df_filtrado])
    monto_minimo = min([registro[1] for registro in df_filtrado])
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

df_filtrado = pd.DataFrame(df_filtrado, columns=['Fecha', 'Monto', 'Categoria', 'Sucursal','Numero de cuenta', 'Banco', 'Extra Column'])

# Crear gráfico interactivo con Plotly
fig = px.bar(df_filtrado, x='Categoria', y='Monto', title="Gráfico por Categoría.", hover_data=['Categoria', 'Monto'], color='Sucursal', text_auto=True, labels={'Monto': 'Monto'}, height=500)

# Crear gráfico interactivo con Plotly
fig2 = px.bar(df_filtrado, x='Monto', y='Sucursal', title="Gráfico por Sucursal.",
              hover_data=['Sucursal', 'Monto'], color='Categoria', text_auto=True,
              labels={'gastos': 'Gráfico de Montos por Sucursal.'}, height=500)

fig3 = px.pie(df_filtrado, values='Monto', names='Categoria', title='Gastos por Categoría', color='Sucursal')

fig4 = px.pie(df_filtrado, values='Monto', names='Numero de cuenta', title='Gastos por Sucursal',color="Sucursal" ,width=800, height=500)

st.subheader("Gráficas.", divider=True)
# Obtener el tipo de gráfico seleccionado por el usuario
filtro_grafico = st.selectbox(
    "Tipo de gráfico:", ["Gráfico de Montos por Categoría (Bar)", "Gráfico de Montos por Sucursal (Bar)",
                         "Gráfico de Montos por Categoría (Pie)", "Gráfico de Montos por Sucursal (Pie)"])

if filtro_grafico == "Gráfico de Montos por Categoría (Bar)":
    # Mostrar gráfico de Montos por Categoría en Streamlit
    st.plotly_chart(fig, use_container_width=True)
elif filtro_grafico == "Gráfico de Montos por Sucursal (Bar)":
    # Mostrar gráfico de Montos por Sucursal en Streamlit
    st.plotly_chart(fig2, use_container_width=True)
elif filtro_grafico == "Gráfico de Montos por Categoría (Pie)":
    # Mostrar gráfico de Montos por Categoría (Pie) en Streamlit
    st.plotly_chart(fig3, use_container_width=True)
elif filtro_grafico == "Gráfico de Montos por Sucursal (Pie)":
    st.plotly_chart(fig4)

# Cerrar el cursor y la conexión a la base de datos
cursor.close()
conn.close()
