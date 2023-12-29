import streamlit as st
import mysql.connector
import os, time
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

######################## Funciones

# Función para insertar clientes
def insertar_cliente(nombre, telefono, correo, estado):
    sql = f"""
    INSERT INTO productores (fullname, phone, email, id_estado)
    VALUES ('{nombre}', '{telefono}', '{correo}', '{estado}')
"""
    val = {"nombre": nombre, "telefono": telefono,
           "correo": correo, "estado": estado}
    cursor.execute(sql, val)
    conn.commit()

# Función para eliminar un cliente por su ID
def eliminar_cliente(id):
    sql = f"DELETE FROM productores WHERE id = {id}"
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()

# Crear dos columnas
col1, col2 = st.columns({100, 135})

#################### Insertar registros

col1.subheader("Registrar productor.")

# Obtener los valores de la columna id de la tabla estado
query = "SELECT id FROM estado"
cursor.execute(query)
result = cursor.fetchall()
# Crear un diccionario con los valores obtenidos
valores = {i[0]: i[0] for i in result}

# Formulario para insertar clientes
nombre = col1.text_input("Nombre:")
telefono = col1.text_input("Telefono:")
correo = col1.text_input("Correo:")
# Mostrar el selectbox en el formulario
estado = col1.selectbox(label="Selecciona un estado:", options=list(valores))

if col1.button("Insertar"):
    if nombre and telefono and correo and estado:
        insertar_cliente(nombre, telefono, correo, estado)
        st.toast(f"Cliente {nombre} insertado correctamente.")
        time.sleep(.5)
        st.toast('Hecho!', icon='🎉')

        # Reiniciar los campos de entrada
        nombre = ""
        telefono = ""
        correo = ""
        estado = ""
    else:
        st.error("Por favor, completa todos los campos requeridos antes de insertar.")

################### Editar registros

col1.subheader("Editar")

# Obtener el ID del cliente a editar
id_edit = col1.number_input("ID del cliente a editar:", min_value=0)

# Obtener los datos del cliente a editar
query = f"SELECT * FROM productores WHERE id = {id_edit}"
cursor.execute(query)
cliente = cursor.fetchone()
if cliente:
        # Mostrar formulario con los datos del cliente
        nombre_edit = col1.text_input("Nombre:", value=cliente[1])
        telefono_edit = col1.text_input("Teléfono:", value=cliente[2])
        correo_edit = col1.text_input("Correo:", value=cliente[3])
        estado_edit = col1.text_input("ID Estado:", value=cliente[4])

        if col1.button("Guardar cambios"):
            # Actualizar los datos del cliente en la base de datos
            sql = f"""
            UPDATE productores
            SET fullname = '{nombre_edit}', phone = '{telefono_edit}', email = '{correo_edit}', id_estado = '{estado_edit}'
            WHERE id = {id_edit}
            """
            cursor.execute(sql)
            conn.commit()
            st.toast(f"Cliente {nombre_edit} actualizado correctamente.", icon="✅")
else:
        col1.warning(f"No se encontró un cliente con ID {id_edit}.")

################### Eiminar registros

col2.subheader("Eliminar")
# Obtener el ID del cliente a eliminar
id_delete = col2.number_input("ID del cliente a eliminar:", min_value=0)

if col2.button("Eliminar."):
    eliminar_cliente(id_delete)
    st.success(f"Cliente con ID {id_delete} eliminado correctamente.")

################## Mostrar clientes

col2.subheader("Catálogo. 📖")

# Realizar la consulta SQL
with conn:
    cursor.execute("SELECT * FROM productores")
    clientes = cursor.fetchall()

# Mostrar la tabla en Streamlit
if clientes:
    # Crear una lista de diccionarios para los datos de la tabla
    data = [{"ID": cliente[0], "Nombre": cliente[1], "Telefono": cliente[2],
             "Correo": cliente[3], "id_estado": cliente[4]} for cliente in clientes]

    # Mostrar la tabla en Streamlit
    col2.table(data)
else:
    col2.warning("No hay clientes registrados.")

# Cerrar la conexión
cursor.close()
conn.close()




