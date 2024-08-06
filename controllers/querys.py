import pandas as pd
from models.db import create_connection
import streamlit as st

conn = create_connection()
cursor = conn.cursor()

# Funciones para las consultas a la base de datos
def execute_query(query, params=None):
    """
    Ejecuta la consulta SQL dada y realiza los cambios en la base de datos.

    Args:
        query (str): La consulta SQL a ejecutar.
        params (tuple, opcional): Los parámetros para pasar a la consulta (por defecto: None).

    Returns:
        None
    """
    cursor.execute(query, params)
    conn.commit()

def fetch_all(query, params=None):
    """
    Obtiene todas las filas de la base de datos según la consulta y los parámetros dados.

    Args:
        query (str): La consulta SQL a ejecutar.
        params (tuple, opcional): Los parámetros para pasar a la consulta. Por defecto, None.

    Returns:
        list: Una lista de tuplas que representan las filas obtenidas.
    """
    cursor.execute(query, params)
    return cursor.fetchall()

def fetch_one(query, params=None):
    """
    Obtiene una fila de la base de datos según la consulta y los parámetros dados.

    Args:
        query (str): La consulta SQL a ejecutar.
        params (tuple, opcional): Los parámetros para pasar a la consulta. Por defecto, None.

    Returns:
        tuple: Una tupla que representa la fila obtenida.
    """
    cursor.execute(query, params)
    return cursor.fetchone()

# ---------------------PRODUCTORES------------------------------------    
@st.cache_data(ttl=600)
def get_productor_options():
    p_query = "SELECT fullname, id_estado FROM productores"
    p_data = pd.DataFrame(fetch_all(p_query))
    p_options = p_data[0].tolist()
    p_id_estado = p_data[1].tolist()
    return p_options, p_id_estado

def get_pagos_data():
    pagos_query = "SELECT * FROM pagos"
    pagos_data = pd.DataFrame(fetch_all(pagos_query))
    return pagos_data

# Función para eliminar un cliente por su ID
def eliminar_cliente(id):
    with conn.cursor() as cursor:
        sql = f"DELETE FROM productores WHERE id = {id}"
        cursor.execute(sql)
        conn.commit()

# ----------------------GASTOS-------------------------------------
# Función para insertar registros
def insertar(id_sucursal, id_cat_gasto, monto, descripcion, cuenta, fecha):
    sql = """
    INSERT INTO gastos (id_sucursal_id, id_cat_gastos_id, monto, descripcion, id_cuenta_banco_id, fecha)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (id_sucursal, id_cat_gasto, monto, descripcion, cuenta, fecha)
    execute_query(sql, params)

# Función para actualizar registros
def actualizar(id_edit, id_sucursal_edit, id_cat_gastos_edit, monto_edit, descripcion_edit):
    sql = """
        UPDATE gastos_gastos
        SET id_sucursal_id = %s, id_cat_gastos_id = %s, monto = %s, descripcion = %s
        WHERE id = %s
    """
    params = (id_edit, id_sucursal_edit, id_cat_gastos_edit, monto_edit, descripcion_edit)
    execute_query(sql, params)

# Función para eliminar registros
def eliminar(id):
    sql_select = "SELECT id FROM gastos_gastos WHERE id = %s"
    result = fetch_one(sql_select, (id,))
    if result is None:
        st.error("El ID no existe en la base de datos")
        return
    sql_delete = "DELETE FROM gastos_gastos WHERE id = %s"
    execute_query(sql_delete, (id,))

# ----------------------SUCURSALES-------------------------------------
# Obtener los valores de la columna id de la tabla sucursal
def obtener_sucursales():
    query = "SELECT id, nombre FROM catalogo_sucursal"
    return fetch_all(query)

# ----------------------CATEGORIAS GASTOS-------------------------------------
# Obtener los valores de la columna id y nombre de la tabla cat gastos
def obtener_categorias_gastos():
    query = "SELECT id, nombre FROM gastos_catgastos"
    return fetch_all(query)

# Obtener los nombres de las categorias ordenadas
@st.cache_data(ttl=600)
def obtener_categorias_ordenadas():
    query = "SELECT * FROM gastos_catgastos ORDER BY ID ASC"
    result = fetch_all(query)
    return [(row[0], row[1]) for row in result]

# ----------------------ESTADOS-------------------------------------        
@st.cache_data
def obtener_valores_estado(cursor):
    # Obtener los valores de la columna id de la tabla estado
    query = "SELECT nombre FROM catalogo_estado"
    cursor.execute(query)
    result = cursor.fetchall()
    # Crear un diccionario con los valores obtenidos
    valores = {i[0]: i[0] for i in result}
    return valores

@st.cache_data
def get_estado_options():
    estado_query = "SELECT id FROM catalogo_estado"
    estado_data = pd.DataFrame(fetch_all(estado_query))
    estado_options = estado_data[0].tolist()
    return estado_options

# ----------------------REGISTROS-------------------------------------
# Obtener registros para mostar en la tabla
def obtener_registros_df():
    query = """
    SELECT gg.fecha, gg.monto, cg.nombre as categoria, s.nombre as sucursal, c.numero_cuenta, b.nombre as banco
    FROM gastos_gastos gg
    JOIN gastos_catgastos cg ON gg.id_cat_gastos_id = cg.id
    JOIN catalogo_sucursal s ON gg.id_sucursal_id = s.id
    JOIN gastos_cuenta c ON gg.id_cuenta_banco_id = c.id
    JOIN gastos_banco b ON c.id_banco_id = b.id;
    """
    return fetch_all(query)

# ----------------------BANCOS-------------------------------------
# Obtener los valores de la columna id de la tabla banco
def obtener_cuenta():
    query = "SELECT id, numero_cuenta, id_banco_id, rfc FROM gastos_cuenta"
    return fetch_all(query)
