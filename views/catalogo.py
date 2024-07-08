import streamlit as st
import os
from dotenv import load_dotenv
import time
from streamlit_modal import Modal

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

# Función para insertar clientes
def insertar_cliente(nombre, telefono, correo, estado):
    query = """
    INSERT INTO productores (fullname, phone, email, id_estado)
    VALUES (%s, %s, %s, %s)
    """
    params = (nombre, telefono, correo, estado)
    execute_query(query, params)

# Función para eliminar un cliente
def eliminar_cliente(id_cliente):
    query = "DELETE FROM productores WHERE id = %s"
    params = (id_cliente,)
    execute_query(query, params)

# Función para obtener todos los clientes
def obtener_clientes():
    query = "SELECT * FROM productores"
    return fetch_all(query)

# Función para obtener todos los estados
@st.cache_data
def obtener_estados():
    query = "SELECT * FROM estado"
    return fetch_all(query)

# Función para obtener el nombre de un estado por su ID
def obtener_nombre_estado(id_estado):
    query = "SELECT id, nombre FROM estado WHERE id = %s"
    params = (id_estado,)
    result = fetch_one(query, params)
    if result:
        return result[0]
    else:
        return "Estado no encontrado"

# Crear dos columnas
col1, col2 = st.columns([100, 135])

#################### Insertar registros

#Ventana Expander
with col1.expander("Registrar nuevo cliente. 📝"):
    # Formulario para insertar clientes
    nombre = st.text_input("Nombre:", placeholder="Ingrese el nombre")
    telefono = st.text_input("Teléfono:", placeholder="Ingrese el teléfono")
    correo = st.text_input("Correo:", placeholder="Ingrese el correo")

    # Mostrar el selectbox en el formulario
    estados = obtener_estados()
    estado_options = [obtener_nombre_estado(estado[0]) for estado in estados]
    estado = st.selectbox(label="Selecciona un estado:", options=estado_options)
    
    if st.button("Insertar", key="insertar", type="primary"):
        if nombre and telefono and correo and estado:
            insertar_cliente(nombre, telefono, correo, estado)
            with st.spinner('Wait for it...'):
                time.sleep(2)
                # Reiniciar los campos de entrada
                nombre = ""
                telefono = ""
                correo = ""
                estado = ""
                st.success(f"Cliente {nombre} insertado correctamente.")
                time.sleep(.5)
                st.toast('Hecho!', icon='🎉')

        else:
            st.error("Por favor, completa todos los campos requeridos antes de insertar.")

################### Editar registros

col1.subheader("Editar")

# Obtener el ID del cliente a editar
id_edit = col1.number_input("ID del cliente a editar:", min_value=0)

# Obtener los datos del cliente a editar
query = "SELECT * FROM productores WHERE id = %s"
params = (id_edit,)
cliente = fetch_one(query, params)

if cliente:
    # Mostrar formulario con los datos del cliente
    nombre_edit = col1.text_input("Nombre:", value=cliente[1])
    telefono_edit = col1.text_input("Teléfono:", value=cliente[2])
    correo_edit = col1.text_input("Correo:", value=cliente[3])
    estado_edit = col1.text_input("ID Estado:", value=cliente[4])

    if col1.button("Guardar cambios"):
        # Actualizar los datos del cliente en la base de datos
        query = """
        UPDATE productores
        SET fullname = %s, phone = %s, email = %s, id_estado = %s
        WHERE id = %s
        """
        params = (nombre_edit, telefono_edit, correo_edit, estado_edit, id_edit)
        execute_query(query, params)
        st.toast(f"Cliente {nombre_edit} actualizado correctamente.", icon="✅")
else:
    col1.warning(f"No se encontró un cliente con ID {id_edit}.")

################### Eliminar registros
with col1.expander("Eliminar", expanded=False):
    col1.subheader("Eliminar")
    # Obtener el ID del cliente a eliminar
    id_delete = col1.number_input("ID del cliente a eliminar:", min_value=0)
if col1.button("Eliminar."):
    eliminar_cliente(id_delete)
    with st.spinner('Eliminando cliente...'):
        time.sleep(2.5)
    st.toast(f"Cliente con ID {id_delete} eliminado correctamente.")

################## Mostrar clientes

col2.subheader("Catálogo. 📖")

# Mostrar la tabla en Streamlit
def mostrar_clientes():
    clientes = obtener_clientes()
    if clientes:
        # Crear una lista de diccionarios para los datos de la tabla
        data = [{"ID": cliente[0], "Nombre": cliente[1], "Telefono": cliente[2],
                 "Correo": cliente[3], "id_estado": cliente[4]} for cliente in clientes]

        # Mostrar la tabla en Streamlit
        col2.dataframe(data)
    else:
        col2.warning("No hay clientes registrados.")

mostrar_clientes()

# Cerrar la conexión
cursor.close()
conn.close()
