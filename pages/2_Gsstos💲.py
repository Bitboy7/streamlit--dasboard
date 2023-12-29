import streamlit as st
import mysql.connector
import os
import time
from dotenv import load_dotenv
load_dotenv()

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
if col1.button("Insertar"):
    if id_sucursal and id_cat_gastos and monto and descripcion:
        insertar(id_sucursal, id_cat_gastos, monto, descripcion)
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
col1.subheader("Editar")
# Obtener el ID del registro a editar
id_edit = col1.number_input("ID del registro a editar:", min_value=0)
# Obtener datos
query = f"SELECT * FROM registro WHERE id = {id_edit}"
cursor.execute(query)
registros = cursor.fetchone()
if registros:
    # Mostrar formulario con los datos del cliente
    id_sucursal_edit = col1.number_input("Sucursal:", value=registros[1])
    id_cat_gastos_edit = col1.number_input("Categoria:", value=registros[2])
    monto_edit = col1.number_input("Monto:", value=registros[3])
    descripcion_edit = col1.text_area("Descripcion:", value=registros[5])

    if col1.button("Guardar cambios"):
        # Actualizar los datos del cliente en la base de datos
        sql = f"""
            UPDATE registro
            SET id_sucursal = '{id_sucursal_edit}', id_cat_gasto = '{id_cat_gastos_edit}', monto = '{monto_edit}', descripcion = '{descripcion_edit}'
            WHERE id = {id_edit}
            """
        cursor.execute(sql)
        conn.commit()
        st.toast(f"Registro {id_edit} actualizado correctamente. ", icon="🔄")
        time.sleep(.5)
        st.toast('Hecho!')
else:
    col1.warning(f"No se encontró un registro con ID {id_edit}.")

# Eiminar registros

col2.subheader("Eliminar")
# Obtener el IDa eliminar
id_delete = col2.number_input("ID del registro a eliminar:", min_value=0)

if col2.button("Eliminar."):
    eliminar(id_delete)
    st.toast(
        f"Registro con ID {id_delete} eliminado correctamente.",  icon='✅', key=None)

# Mostrar clientes

col2.subheader("Registro. 📄💹")

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
    col2.dataframe(data)
else:
    col2.warning("No hay registros añadidos.")

# Cerrar la conexión
cursor.close()
conn.close()
