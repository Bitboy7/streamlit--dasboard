import streamlit as st
import pandas as pd
from fpdf import FPDF
import base64
import io
import tempfile
from controllers.querys import obtener_registros_df
from datetime import datetime
from helpers.download_files import create_pdf, create_plot

# Función para cargar los datos
def load_data():
    registros = obtener_registros_df()
    df = pd.DataFrame(registros, columns=['Fecha', 'monto', 'Categoria', 'Sucursal','Numero de cuenta', 'Banco'])
    return df
    
# Streamlit app
st.title("Reporte de Gastos")

# Cargar datos
df = load_data()

# Mostrar resumen
st.subheader("Resumen de Gastos")
st.write(f"Total de gastos: ${df['monto'].sum():.2f}")
st.write(f"Promedio de gastos: ${df['monto'].mean():.2f}")
st.write(f"Gasto máximo: ${df['monto'].max():.2f}")
st.write(f"Gasto mínimo: ${df['monto'].min():.2f}")

# Mostrar gráfico
st.subheader("Gráfico de Gastos por Categoría")
fig = create_plot(df, 'Categoria', 'monto', 'Gastos por Categoría')
st.plotly_chart(fig)

# Generar PDF
if st.button("Generar Reporte PDF"):
    pdf = create_pdf(df)
    
    # Guardar PDF en un archivo temporal
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        pdf.output(temp_file.name)
    
    # Codificar PDF para descarga
    with open(temp_file.name, "rb") as file:
        b64 = base64.b64encode(file.read()).decode()
    
    href = f'<a href="data:application/pdf;base64,{b64}" download="reporte_gastos.pdf" style="text-decoration: none; color: white; background-color: #1976d2; padding: 10px 20px; border-radius: 5px;">Descargar Reporte PDF</a>'
    st.markdown(href, unsafe_allow_html=True)
