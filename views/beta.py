import streamlit as st
import pandas as pd
import plotly.express as px
# Importar las funciones de ayuda
from helpers.load_css import load_css_style

# Configuración de la página
st.set_page_config(page_title="Dashboard de Gastos", layout="wide")
st.title("Dashboard de Gastos")

# Cargar el estilo CSS
load_css_style()

# Importar conexion
from models.db import create_connection

# Función para cargar los datos
@st.cache_data
def load_data():
    conn = create_connection()
    query = """
    SELECT gg.fecha, gg.monto, cg.nombre as categoria, s.nombre as sucursal, c.numero_cuenta, b.nombre as banco
    FROM gastos_gastos gg
    JOIN gastos_catgastos cg ON gg.id_cat_gastos_id = cg.id
    JOIN catalogo_sucursal s ON gg.id_sucursal_id = s.id
    JOIN gastos_cuenta c ON gg.id_cuenta_banco_id = c.id
    JOIN gastos_banco b ON c.id_banco_id = b.id;
    """
    df = pd.read_sql(query, conn)
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

# Función para calcular las sumas por período
def calculate_sums(df, period):
  if period == 'Día':
    return df.groupby([df['fecha'].dt.date, 'categoria', 'sucursal', 'banco'])['monto'].sum().reset_index()
  elif period == 'Semana':
    return df.groupby([df['fecha'].dt.to_period('W').astype(str), 'categoria', 'sucursal', 'banco'])['monto'].sum().reset_index()
  elif period == 'Mes':
    return df.groupby([df['fecha'].dt.to_period('M').astype(str), 'categoria', 'sucursal', 'banco'])['monto'].sum().reset_index()

# Carga de datos
df = load_data()

# Selectores
col1, col2, col3, col4 = st.columns(4)
with col1:
    period = st.selectbox("Seleccione el período", ['Día', 'Semana', 'Mes'])
with col2:
    categoria = st.multiselect("Seleccione categorías", options=df['categoria'].unique())
with col3:
    sucursal = st.multiselect("Seleccione sucursales", options=df['sucursal'].unique())
with col4:
    banco = st.multiselect("Seleccione bancos", options=df['banco'].unique())

# Filtrar datos
filtered_df = df
if categoria:
    filtered_df = filtered_df[filtered_df['categoria'].isin(categoria)]
if sucursal:
    filtered_df = filtered_df[filtered_df['sucursal'].isin(sucursal)]
if banco:
    filtered_df = filtered_df[filtered_df['banco'].isin(banco)]

# Cálculo de sumas
sums_df = calculate_sums(filtered_df, period)

# Visualización de datos
st.subheader(f"Suma de gastos por {period}")
fig = px.line(sums_df, x='fecha', y='monto', color='categoria', 
              title=f'Gastos por {period}', 
              labels={'monto': 'Monto total', 'fecha': 'Fecha'})
st.plotly_chart(fig, use_container_width=True)

# Tabla de datos
st.subheader("Tabla de datos")
st.dataframe(sums_df)

# Estadísticas básicas
st.subheader("Estadísticas básicas")
st.write(sums_df['monto'].describe())

# Gráfico de barras por categoría
st.subheader("Gastos por categoría")
cat_sums = sums_df.groupby('categoria')['monto'].sum().sort_values(ascending=False)
fig_cat = px.bar(cat_sums, x=cat_sums.index, y='monto', title='Total de gastos por categoría')
st.plotly_chart(fig_cat, use_container_width=True)

# Gráfico de pastel por sucursal
st.subheader("Distribución de gastos por sucursal")
suc_sums = sums_df.groupby('sucursal')['monto'].sum()
fig_suc = px.pie(suc_sums, values='monto', names=suc_sums.index, title='Distribución de gastos por sucursal')
st.plotly_chart(fig_suc, use_container_width=True)