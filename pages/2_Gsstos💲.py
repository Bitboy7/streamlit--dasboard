import streamlit as st
import mysql.connector
import os
import time
from dotenv import load_dotenv
import pandas as pd
load_dotenv()

st.set_page_config(
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
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

# Funciones
# Función para insertar registros
def insertar(id_sucursal, id_cat_gasto, monto, descripcion):
    sql = f"""
    INSERT INTO registro (id_sucursal, id_cat_gasto, monto, descripcion)
    VALUES ('{id_sucursal}', '{id_cat_gasto}', '{monto}', '{descripcion}')
"""
    val = {"id_sucursal": id_sucursal, "id_cat_gasto": id_cat_gasto,
           "monto": monto, "estado": descripcion}
    cursor.execute(sql, val)
    conn.commit()

# Función para eliminar un cliente por su ID
def eliminar(id):
    sql = f"DELETE FROM registro WHERE id = {id}"
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()


# Crear dos columnas
col1, col2 = st.columns({90, 135})
# Insertar registros
col1.subheader("Añadir.")

# Obtener los valores de la columna id de la tabla sucursal
query = "SELECT id FROM sucursal"
cursor.execute(query)
result = cursor.fetchall()
# Crear un diccionario con los valores obtenidos
v = {i[0]: i[0] for i in result}

# Formulario para insertar gastos
id_sucursal = col1.selectbox(label="Selecciona una sucursal:", options=list(v))

# Obtener los valores de la columna id de la tabla cat gastos
cursor2 = conn.cursor()
query2 = "SELECT id FROM cat_gastos"
cursor2.execute(query2)
result2 = cursor2.fetchall()
# Crear un diccionario con los valores obtenidos
v2 = {i[0]: i[0] for i in result2}


id_cat_gastos = col1.selectbox(
    label="Selecciona una categoria:", options=list(v2))
monto = col1.number_input("Monto:", step=0.01)
# Mostrar el selectbox en el formulario
descripcion = col1.text_area("Descripcion:")
if col1.button("Insertar", type="primary"):
    if id_sucursal and id_cat_gastos and monto and descripcion:
        insertar(id_sucursal, id_cat_gastos, monto, descripcion)
        st.spinner('Procesando...')
        time.sleep(1)
        st.toast(f"Operacion por la contidad de ${monto} pesos.", icon="💰")
        time.sleep(.5)
        st.toast('Hecho!', icon='🎉')

        # Reiniciar los campos de entrada
        id_sucursal = ""
        id_cat_gastos = ""
        monto = ""
        descripcion = ""
    else:
        st.error("Por favor, completa todos los campos requeridos antes de insertar.")

# Editar registros
expe = col1.expander("Editar registros. ✏️", expanded=False)

with expe.subheader("Selecciona el ID a editar."):
    # Obtener el ID del registro a editar
    id_edit = expe.number_input("ID del registro a editar:", min_value=0)
    # Obtener datos
    query = f"SELECT * FROM registro WHERE id = {id_edit}"
    cursor.execute(query)
    registros = cursor.fetchone()
if registros:
    # Mostrar formulario con los datos del cliente
    id_sucursal_edit = expe.number_input("Sucursal:", value=registros[1])
    id_cat_gastos_edit = expe.number_input("Categoria:", value=registros[2])
    monto_edit = expe.number_input("Monto:", value=registros[3])
    descripcion_edit = expe.text_area("Descripcion:", value=registros[5])

    if expe.button("Guardar cambios"):
        # Actualizar los datos del cliente en la base de datos
        sql = f"""
            UPDATE registro
            SET id_sucursal = '{id_sucursal_edit}', id_cat_gasto = '{id_cat_gastos_edit}', monto = '{monto_edit}', descripcion = '{descripcion_edit}'
            WHERE id = {id_edit}
            """
        cursor.execute(sql)
        conn.commit()
        st.spinner('Actualizando datos...')
        st.toast(f"Registro {id_edit} actualizado correctamente. ", icon="🔄")
        time.sleep(.5)
        st.toast('Hecho!')
else:
    expe.warning(f"No se encontró un registro con ID {id_edit}.")

# Eiminar registros
expander = col1.expander("Eiminar registros. ❌", expanded=False)

with expander.subheader("Selecciona el ID a eliminar."):
    # Obtener el IDa eliminar
    id_delete = expander.number_input(
        "ID del registro a eliminar:", min_value=0)
if expander.button("Eliminar registro."):
    eliminar(id_delete)
    with st.spinner('Eliminando...'):
        time.sleep(2.5)
    st.toast(
        f"Registro con ID {id_delete} eliminado correctamente.",  icon='✅')

# Obtener los nombres de las categorias ordenadas
query = "SELECT * FROM cat_gastos ORDER BY ID ASC "
cursor.execute(query)
result = cursor.fetchall()
categorias = [(row[0], row[1]) for row in result]

# Crear un dataframe con los nombres de las categorias
df_categorias = pd.DataFrame(categorias, columns=["ID", "Categorías"])
expc = col2.expander("Categorias.")
# Mostrar el dataframe dentro de un expander
expc.dataframe(df_categorias)

# Mostrar registros

col2.subheader("Registro. 📄💹")

# Realizar la consulta SQL
with conn:
    cursor.execute("""SELECT r.*, su.nombre AS Sucursal, ca.nombre AS Categoria, es.nombre AS Estado
                      FROM registro r, sucursal su, cat_gastos ca, estado es
                      WHERE r.id_sucursal = su.id
                      AND r.id_cat_gasto = ca.id
                      AND su.id_estado = es.id;""")
    registros = cursor.fetchall()

# Mostrar la tabla en Streamlit
if registros:
    # Crear una lista de diccionarios para los datos de la tabla
    data = [{"ID": registro[0], "id_sucursal": registro[1], "id_cat_gasto": registro[2],
             "monto": "${:,.2f}".format(registro[3]), "fecha registrada": registro[4], "descripcion": registro[5],
             "sucursal": registro[6], "categoria": registro[7], "estado": registro[8]} for registro in registros]

    # Mostrar la tabla en Streamlit
    col2.dataframe(data)

else:
    col2.warning("No hay registros añadidos.")

# Cerrar la conexión
cursor.close()
conn.close()
