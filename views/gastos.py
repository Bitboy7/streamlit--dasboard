import streamlit as st
import time
import pandas as pd

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

conn = create_connection()
cursor = conn.cursor()

# Check if connection is established
if conn.is_connected():
    st.write("Connected to database")
else:
    st.write("Not connected to database")

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

# Función para insertar registros
def insertar(id_sucursal, id_cat_gasto, monto, descripcion):
    sql = """
    INSERT INTO registro (id_sucursal, id_cat_gasto, monto, descripcion)
    VALUES (%s, %s, %s, %s)
    """
    params = (id_sucursal, id_cat_gasto, monto, descripcion)
    execute_query(sql, params)

# Función para actualizar registros
def actualizar(id_edit, id_sucursal_edit, id_cat_gastos_edit, monto_edit, descripcion_edit):
    sql = """
        UPDATE registro
        SET id_sucursal = %s, id_cat_gasto = %s, monto = %s, descripcion = %s
        WHERE id = %s
    """
    params = (id_sucursal_edit, id_cat_gastos_edit, monto_edit, descripcion_edit, id_edit)
    execute_query(sql, params)

# Función para eliminar registros
def eliminar(id):
    sql_select = "SELECT id FROM registro WHERE id = %s"
    result = fetch_one(sql_select, (id,))
    if result is None:
        st.error("El ID no existe en la base de datos")
        return
    sql_delete = "DELETE FROM registro WHERE id = %s"
    execute_query(sql_delete, (id,))

# Obtener los valores de la columna id de la tabla sucursal
def obtener_sucursales():
    query = "SELECT id, nombre FROM sucursal"
    return fetch_all(query)

# Obtener los valores de la columna id y nombre de la tabla cat gastos
def obtener_categorias_gastos():
    query = "SELECT id, nombre FROM cat_gastos"
    return fetch_all(query)

# Obtener los nombres de las categorias ordenadas
def obtener_categorias_ordenadas():
    query = "SELECT * FROM cat_gastos ORDER BY ID ASC"
    result = fetch_all(query)
    return [(row[0], row[1]) for row in result]

# Obtener registros
def obtener_registros():
    query = """
        SELECT r.*, su.nombre AS Sucursal, ca.nombre AS Categoria, es.nombre AS Estado
        FROM registro r, sucursal su, cat_gastos ca, estado es
        WHERE r.id_sucursal = su.id
        AND r.id_cat_gasto = ca.id
        AND su.id_estado = es.id
        ORDER BY r.id DESC
        LIMIT 50;
    """
    return fetch_all(query)

# Crear dos columnas
col1, col2 = st.columns({90, 135})

# Editar registros
expand_insert = col1.expander("Añadir.. ✏️", expanded=False)

with expand_insert.subheader("Insertar registros. 📝"):
    sucursales = obtener_sucursales()
    v = {i[0]: i[1] for i in sucursales}
    id_sucursal = expand_insert.selectbox(label="Selecciona una sucursal:", options=list(v))
    nombre_sucursal = v.get(id_sucursal, "")
    expand_insert.write(f"{nombre_sucursal}")

    categorias_gastos = obtener_categorias_gastos()
    v2 = {i[0]: i[1] for i in categorias_gastos}
    id_cat_gastos = expand_insert.selectbox(label="Selecciona una categoria:", options=list(v2))
    nombre_cat_gastos = v2.get(id_cat_gastos, "")
    expand_insert.write(f"{nombre_cat_gastos}")

    monto = expand_insert.number_input("Monto:", step=0.01, format="%.2f")
    descripcion = expand_insert.text_area("Descripcion:")
    if expand_insert.button("Insertar", type="primary"):
        if id_sucursal and id_cat_gastos and monto and descripcion:
            insertar(id_sucursal, id_cat_gastos, monto, descripcion)
            st.spinner('Procesando...')
            time.sleep(1)
            st.toast(f"Operacion por la contidad de ${monto} pesos.", icon="💰")
            time.sleep(.5)
            st.toast('Hecho!', icon='🎉')

            id_sucursal = ""
            id_cat_gastos = ""
            monto = ""
            descripcion = ""
        else:
            st.error("Por favor, completa todos los campos requeridos antes de insertar.")

# Editar registros
expe = col1.expander("Editar. ✏️", expanded=False)

with expe.subheader("Selecciona el ID a editar."):
    id_edit = expe.number_input("ID del registro a editar:", min_value=0)
    query = "SELECT * FROM registro WHERE id = %s"
    registros = fetch_one(query, (id_edit,))

if registros:
    id_sucursal_edit = expe.number_input("Sucursal:", value=registros[1])
    id_cat_gastos_edit = expe.number_input("Categoria:", value=registros[2])
    monto_edit = expe.number_input("Monto:", value=registros[3])
    descripcion_edit = expe.text_area("Descripcion:", value=registros[5])

    if expe.button("Guardar cambios"):
        actualizar(id_edit, id_sucursal_edit, id_cat_gastos_edit, monto_edit, descripcion_edit)
        st.spinner('Actualizando datos...')
        st.toast(f"Registro {id_edit} actualizado correctamente. ", icon="🔄")
        time.sleep(.5)
        st.toast('Hecho!')
else:
    expe.warning(f"No se encontró un registro con ID {id_edit}.")

# Eliminar registros
expander = col1.expander("Eliminar. ❌", expanded=False)

with expander.subheader("Selecciona el ID a eliminar."):
    id_delete = expander.number_input("ID del registro a eliminar:", min_value=0)

if expander.button("Eliminar registro."):
    eliminar(id_delete)

# Obtener las categorias ordenadas
categorias = obtener_categorias_ordenadas()
df_categorias = pd.DataFrame(categorias, columns=["ID", "Categorías"])
expc = col2.expander("Categorias.")
expc.dataframe(df_categorias)

# Mostrar registros
col2.subheader("Registro. 📄💹")

registros = obtener_registros()

if registros:
    data = [{"ID": registro[0], "id_sucursal": registro[1], "id_cat_gasto": registro[2],
             "monto": "${:,.2f}".format(registro[3]), "fecha registrada": registro[4], "descripcion": registro[5],
             "sucursal": registro[6], "categoria": registro[7], "estado": registro[8]} for registro in registros]

    col2.dataframe(data)
else:
    col2.warning("No hay registros añadidos.")
