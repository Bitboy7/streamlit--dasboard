import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px
from models.db import create_connection
import os

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

conn = create_connection()
cursor = conn.cursor()

# Check if connection is established
if conn.is_connected():
    st.write("Connected to database")
else:
    st.write("Not connected to database")

######################## Funciones para las consultas a la base de datos

def execute_query(query, params=None):
    cursor.execute(query, params)
    conn.commit()

def fetch_all(query, params=None):
    cursor.execute(query, params)
    return cursor.fetchall()

def fetch_one(query, params=None):
    cursor.execute(query, params)
    return cursor.fetchone()

# Función para ejecutar consultas SQL
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

# Cargar datos
@st.cache_data
def load_data():
  data = run_query("""    
    SELECT r.*, su.nombre AS Sucursal, ca.nombre AS Categoria, es.nombre AS Estado
    FROM registro r, sucursal su, cat_gastos ca, estado es
    WHERE r.id_sucursal = su.id
    AND r.id_cat_gasto = ca.id
    AND su.id_estado = es.id;
    """)
  columns = ['ID', 'ID_sucursal', 'ID_categoria', 'Monto', 'Fecha_registrada', 'Descripcion', 'Sucursal', 'Categoria', 'Estado']
  df = pd.DataFrame(data, columns=columns)
  df['Fecha_registrada'] = pd.to_datetime(df['Fecha_registrada'])
  df['Monto'] = df['Monto'].astype(str).str.replace('$', '').str.replace(',', '').astype(float)
  return df

df = load_data()

# Interfaz de Streamlit
st.title('Dashboard de Análisis de Transacciones')

# Sidebar para filtros
st.sidebar.header('Filtros')
sucursal = st.sidebar.multiselect('Selecciona Sucursal', options=df['Sucursal'].unique())
categoria = st.sidebar.multiselect('Selecciona Categoría', options=df['Categoria'].unique())
estado = st.sidebar.multiselect('Selecciona Estado', options=df['Estado'].unique())

# Aplicar filtros
if sucursal:
    df = df[df['Sucursal'].isin(sucursal)]
if categoria:
    df = df[df['Categoria'].isin(categoria)]
if estado:
    df = df[df['Estado'].isin(estado)]

# Métricas principales
col1, col2, col3 = st.columns(3)
col1.metric("Total Transacciones", f"{len(df)}")
col2.metric("Monto Total", f"${df['Monto'].sum():,.2f}")
col3.metric("Promedio por Transacción", f"${df['Monto'].mean():,.2f}")

# Gráficas
st.subheader('Análisis de Transacciones')
# Métricas principales
colg1, colg2 = st.columns(2)
# Gráfica de barras: Monto total por sucursal
with colg1.container():
  st.subheader('Monto Total por Sucursal')
  fig_sucursal = px.bar(df.groupby('Sucursal')['Monto'].sum().reset_index(), 
              x='Sucursal', y='Monto')
  st.plotly_chart(fig_sucursal)

# Gráfica de pastel: Distribución de categorías
with colg2.container():
  st.subheader('Distribución de Montos por Categoría')
  fig_categoria = px.pie(df, values='Monto', names='Categoria')
  st.plotly_chart(fig_categoria)

# Gráfica de línea: Tendencia de transacciones en el tiempo
with st.container():
  st.subheader('Tendencia de Transacciones en el Tiempo')
  df_time = df.groupby('Fecha_registrada')['Monto'].sum().reset_index()
  fig_time = px.line(df_time, x='Fecha_registrada', y='Monto')
  st.plotly_chart(fig_time)

# Mapa de calor: Transacciones por estado
with st.container():
  st.subheader('Transacciones por Estado')
  fig_estado = px.choropleth(df.groupby('Estado')['Monto'].sum().reset_index(),
           locations='Estado',
           locationmode='country names',
           color='Monto',
           hover_name='Estado',
           color_continuous_scale='Viridis')
  st.plotly_chart(fig_estado)


# Tabla de datos
st.subheader('Datos Detallados')
st.dataframe(df)