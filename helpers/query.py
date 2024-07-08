from models.db import conn
import streamlit as st

# Función para eliminar un cliente por su ID
def eliminar_cliente(id):
    with conn.cursor() as cursor:
        sql = f"DELETE FROM productores WHERE id = {id}"
        cursor.execute(sql)
        conn.commit()
        
@st.cache_data
def obtener_valores_estado(cursor):
    # Obtener los valores de la columna id de la tabla estado
    query = "SELECT id FROM estado"
    cursor.execute(query)
    result = cursor.fetchall()
    # Crear un diccionario con los valores obtenidos
    valores = {i[0]: i[0] for i in result}
    return valores

