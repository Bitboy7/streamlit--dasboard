import streamlit as st
from mysql.connector import Error
from helpers.load_css import load_css_style
from dotenv import load_dotenv
from controllers.querys import *
import pandas as pd
import plotly.express as px
from helpers.download_files import *
from streamlit_extras.metric_cards import style_metric_cards
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)
from st_pages import show_pages_from_config, add_page_title
show_pages_from_config()
# Cargar el estilo CSS
load_css_style()

load_dotenv()
# Check if connection is established
if conn.is_connected():
    st.write("Connected to database")
else:
    st.write("Not connected to database")

# Crear dos columnas
col1, col2 = st.columns({90, 135})

# Columna 1
expand = col1.expander('Ingresar datos de pago', expanded=True)

# Formulario para ingresar datos
with expand.subheader('Ingresar datos de pago'):
    # Obtener las opciones de productores y estados
    productor_options, productor_id_estado = get_productor_options()

    id_productor = expand.selectbox('Productor', productor_options)

    # Find the index of the selected productor
    selected_productor_index = productor_options.index(id_productor)

    # Get the corresponding id_estado for the selected productor
    id_estado = productor_id_estado[selected_productor_index]

    estado_options = get_estado_options()

    id_estado = expand.selectbox('ID del estado', estado_options, index=estado_options.index(id_estado), key='estado_selectbox', disabled=True)

    fecha = expand.date_input('Fecha')
    monto = expand.number_input('Monto')
    metodo_pago = expand.selectbox('Método de pago', ['Transferencia', 'Efectivo'])

    # Botón para guardar los datos ingresados
    if expand.button('Guardar'):
        if conn.is_connected():
            try:
                insert_query = f"INSERT INTO pagos (productor, id_estado, fecha, monto, metodo_pago) VALUES ('{id_productor}', '{id_estado}', '{fecha}', {monto}, '{metodo_pago}')"
                cursor.execute(insert_query)
                conn.commit()
                st.toast(f'Hecho, pago realizado a {id_productor}', icon='🎉')
                expand.success('Datos guardados exitosamente')
            except Error as e:
                expand.error(f"Error al guardar los datos: {e}")
        else:
            expand.error('No se pudo conectar a la base de datos')

            
# Mostrar el dataframe con los datos de la tabla pagos
pagos_df = get_pagos_data()
pagos_df.columns = ['id', 'Productor', 'Estado', 'Fecha', 'Monto', 'Metodo pago']

if not pagos_df.empty:
    expander = st.sidebar.expander("Filtros.", expanded=False)

    # Obtener los nombres de estado únicos
    estados = pagos_df['Estado'].unique()
    filtro_estado = expander.selectbox("Por estado:", ["Todos"] + list(estados))

    if filtro_estado == "Todos":
        filtro_estado = None

    # Componente de filtrado
    metodos_pago = pagos_df['Metodo pago'].unique()
    filtro_metodo_pago = expander.selectbox("Por método de pago:", ["Todos"] + list(metodos_pago))

    if filtro_metodo_pago == "Todos":
        filtro_metodo_pago = None

    # Componente de filtrado por fecha
    fechas = pd.to_datetime(pagos_df['Fecha']).dt.date.unique()
    filtro_fecha = expander.selectbox("Por fecha:", ["Día", "Semana", "Mes", "Fecha específica"])

    if filtro_fecha == "Día":
        filtro_fecha = pd.Timestamp.now().date()
    elif filtro_fecha == "Semana":
        filtro_fecha = pd.Timestamp.now().date() - pd.DateOffset(weeks=1)
    elif filtro_fecha == "Mes":
        filtro_fecha = pd.Timestamp.now().date() - pd.DateOffset(months=1)
    elif filtro_fecha == "Fecha específica":
        filtro_fecha = expander.date_input('Seleccionar fecha')

    # Filtrar el dataframe por estado seleccionado, método de pago y fecha
    df_filtrado = pagos_df.copy()
    if filtro_estado:
        df_filtrado = df_filtrado[df_filtrado['Estado'] == filtro_estado]

    if filtro_metodo_pago:
        df_filtrado = df_filtrado[df_filtrado['Metodo pago'] == filtro_metodo_pago]

    if filtro_fecha:
        if filtro_fecha == "Día":
            filtro_fecha = pd.Timestamp.now().date()
        elif filtro_fecha == "Semana":
            filtro_fecha = pd.Timestamp.now().date() - pd.DateOffset(weeks=1)
        elif filtro_fecha == "Mes":
            filtro_fecha = pd.Timestamp.now().date() - pd.DateOffset(months=1)
        df_filtrado = df_filtrado[pd.to_datetime(df_filtrado['Fecha']).dt.date == pd.Timestamp(filtro_fecha).date()]

    # Mostrar el dataframe filtrado
    col2.dataframe(df_filtrado)
                
    total = df_filtrado['Monto'].sum()
    col2.metric(label="Acumulado de pagos", value=f"${total:,.2f}", delta="Total.")

    style_metric_cards(background_color="#F5F5F5", border_left_color="#35A94A")
else:
    st.write("No hay registros disponibles.")
