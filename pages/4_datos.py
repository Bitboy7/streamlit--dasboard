import streamlit as st
import mysql.connector
import os
import time
import datetime
from dotenv import load_dotenv
import pandas as pd
from openpyxl import Workbook
import io
import base64
from openpyxl.styles import numbers
import locale
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
load_dotenv()
import plotly.express as px
import plotly.graph_objects as go
st.set_page_config(
    page_title="Datos 📊",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

with open('./style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Configurar variables para la conexión a MySQL
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_PORT = os.getenv("MYSQL_PORT")

# Conexión a la base de datos
conn = mysql.connector.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE,
    port=MYSQL_PORT
)
cursor = conn.cursor()
# Check if connection is established
if conn.is_connected():
    st.write("Connected to database")
else:
    st.write("Not connected to database")

# Mostrar datos

st.subheader("Datos 📊")

# Realizar la consulta SQL
with conn:
    cursor.execute("""SELECT r.*, su.nombre AS sucursal, ca.nombre AS categoria
                      FROM registro r
                      LEFT JOIN sucursal su ON r.id_sucursal = su.id
                      LEFT JOIN cat_gastos ca ON r.id_cat_gasto = ca.id;""")
    registros = cursor.fetchall()

# Mostrar la tabla en Streamlit
if registros:
    # Crear una lista de diccionarios para los datos de la tabla
    data = [{"ID": registro[0], "id_sucursal": registro[1], "id_cat_gasto": registro[2],
             "monto": registro[3], "fecha registrada": registro[4], "descripcion": registro[5],
             "sucursal": registro[6], "categoria": registro[7]} for registro in registros]

    # Mostrar la tabla en Streamlit
    expander = st.expander("Filtros", expanded=False)

    # Obtener los nombres de categoría únicos
    categorias = set([registro["categoria"] for registro in data])
    filtro_categoria = expander.selectbox("Por categoria:", ["Todas"] + list(categorias))

    if filtro_categoria == "Todas":
        filtro_categoria = None

    # Componente de filtrado
    filtro_sucursal = expander.selectbox("Por sucursal:", ["Todas"] + list(
        set([registro["sucursal"] for registro in data])))

    if filtro_sucursal == "Todas":
        filtro_sucursal = None
# Filtrar el dataframe por categoría seleccionada, fecha y sucursal
df_filtrado = pd.DataFrame(data)
if filtro_categoria:
    df_filtrado = df_filtrado[df_filtrado["categoria"] == filtro_categoria]

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
        df_filtrado = df_filtrado[
            (pd.to_datetime(df_filtrado["fecha registrada"]).dt.date >= start_date) &
            (pd.to_datetime(
                df_filtrado["fecha registrada"]).dt.date <= end_date)
        ]
if filtro_sucursal:
    df_filtrado = df_filtrado[df_filtrado["sucursal"] == filtro_sucursal]

# Formatear la columna "monto" como moneda
locale.setlocale(locale.LC_ALL, '')  # Set the locale to the user's default

df_filtrado["monto"] = df_filtrado["monto"].map(
    lambda x: locale.currency(x, grouping=True))

# Mostrar el dataframe filtrado
expander.dataframe(df_filtrado)

# Obtener el tipo de estadística seleccionada por el usuario
filtro_estadistica = expander.selectbox(
    "Tipo de estadística:", ["Suma", "Promedio", "Mínimo", "Máximo"])

if filtro_estadistica:
    # Convertir la columna "monto" a números
    df_filtrado["monto"] = pd.to_numeric(
        df_filtrado["monto"].str.replace('[^\d.]', ''), errors='coerce')

    if filtro_estadistica == "Suma":
        # Calcular la suma de la columna "monto"
        suma_monto = df_filtrado["monto"].sum()
        expander.write(f"Suma de la columna 'monto': ${suma_monto} pesos")
    elif filtro_estadistica == "Promedio":
        # Calcular el promedio de la columna "monto"
        promedio_monto = df_filtrado["monto"].mean()
        expander.write(f"Promedio de la columna 'monto': {promedio_monto}")
    elif filtro_estadistica == "Mínimo":
        # Obtener el valor mínimo de la columna "monto"
        minimo_monto = df_filtrado["monto"].min()
        expander.markdown(
            f"Valor mínimo de la columna 'monto': {minimo_monto}")
    elif filtro_estadistica == "Máximo":
        # Obtener el valor máximo de la columna "monto"
        maximo_monto = df_filtrado["monto"].max()
        expander.markdown(
            f"Valor máximo de la columna 'monto': {maximo_monto}")

# Generar el archivo Excel a partir del dataframe filtrado
def generate_excel(df_filtrado):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(['ID', 'id_sucursal', 'id_cat_gasto', 'monto',
                     'fecha registrada', 'descripcion', 'sucursal', 'categoria'])
    for _, row in df_filtrado.iterrows():
        worksheet.append(list(row))

    # Add totals row with sum formula in 'monto' column
    last_row = worksheet.max_row
    totals_row = [f"=SUM(D2:D{last_row})"] + [""] * (worksheet.max_column - 1)
    worksheet.append(totals_row)

    # Apply formatting to totals row
    totals_row_number = last_row + 1
    for column in range(1, worksheet.max_column + 1):
        cell = worksheet.cell(row=totals_row_number, column=column)
        cell.alignment = Alignment(horizontal='right')

    # Create table and apply style to the table
    table_range = f"A1:{get_column_letter(worksheet.max_column)}{totals_row_number}"
    table = Table(displayName="Table1", ref=table_range)
    style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    table.tableStyleInfo = style
    worksheet.add_table(table)
    # Format column 'monto' as currency
    currency_format = numbers.FORMAT_CURRENCY_USD_SIMPLE
    worksheet.column_dimensions['D'].number_format = currency_format
    return workbook

# Devuelve el contenido del archivo Excel como una cadena binaria


def get_binary_content(workbook):
    binary_content = io.BytesIO()
    workbook.save(binary_content)
    return binary_content.getvalue()


if expander.button("Generar Excel"):
    # Generar el archivo Excel a partir del dataframe filtrado
    workbook = generate_excel(df_filtrado)

    # Obtener el contenido binario del archivo Excel
    excel_content = get_binary_content(workbook)

    # Codificar el contenido binario en base64
    excel_base64 = base64.b64encode(excel_content).decode('utf-8')

    # Generar el enlace de descarga del archivo Excel
    href = f'<a href="data:application/octet-stream;base64,{excel_base64}" download="datos.xlsx" style="color: white; text-decoration: none; font-weight: bold; background-color: green; padding: 0.5rem 1rem; text-decoration: none;transition: all 0.3s ease-out;border-radius: 1rem; margin: 8px;">Descargar Excel</a>'
    expander.markdown(href, unsafe_allow_html=True)
    notificacion = st.spinner("Generando archivo...")
    time.sleep(2.5)
    st.toast(f"Archivo Excel generado con éxito")
    
# Crear gráfico interactivo con Plotly
fig = px.bar(df_filtrado, x='categoria', y='monto',
             hover_data=['sucursal', 'monto'], color='sucursal',
             labels={'pop':'population of Canada'}, height=400)

# Añadir título al gráfico
fig.update_layout(title="Gráfico de Montos por Categoría.")

# Añadir estilo al gráfico
fig.update_traces(marker_line_color='rgb(8,48,107)', marker_line_width=1.5, opacity=0.6)

# Configurar cada barra con un color distinto
fig.update_traces(marker=dict(color=px.colors.qualitative.Plotly))
# Crear gráfico interactivo con Plotly
fig2 = px.bar(df_filtrado, x='sucursal', y='monto',
             hover_data=['categoria', 'monto'], color='categoria',
             labels={'pop':'population of Canada'}, height=400)

# Añadir título al gráfico
fig2.update_layout(title="Gráfico de Montos por Sucursal.")

# Añadir estilo al gráfico
fig2.update_traces(marker_line_color='rgb(8,48,107)', marker_line_width=1.5, opacity=0.6)

# Configurar cada barra con un color distinto
fig2.update_traces(marker=dict(color=px.colors.qualitative.Plotly))

with st.expander("Gráfico"):
    # Mostrar gráfico en Streamlit
    st.plotly_chart(fig)
    # Mostrar gráfico en Streamlit
    st.plotly_chart(fig2)    
