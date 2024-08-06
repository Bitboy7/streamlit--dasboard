import streamlit as st
import time
import pandas as pd
from helpers.load_css import load_css_style, remote_css, remote_js, iconMetricContainer
from models.db import create_connection
from controllers.querys import execute_query, fetch_all, fetch_one, obtener_sucursales, obtener_categorias_gastos, obtener_categorias_ordenadas, obtener_registros_df, insertar, actualizar, eliminar, obtener_cuenta

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
)

from st_pages import show_pages_from_config, add_page_title
show_pages_from_config()

# Cargar el estilo CSS
load_css_style()
st.write("""
            <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap')
            </style>
        """, unsafe_allow_html=True)

remote_css(
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css")

remote_css(
            "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")

remote_css("https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap")

remote_js(
            "https://code.jquery.com/jquery-3.6.0.min.js")
    
# Crear la conexión a la base de datos
conn = create_connection()
cursor = conn.cursor()

# Verificar si la conexión fue exitosa
if conn.is_connected():
    st.write("Connected to database")
else:
    st.write("Not connected to database")

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

    cuenta = obtener_cuenta()
    v3 = {i[0]: i[1] for i in cuenta}
    cuenta = expand_insert.selectbox("Cuenta:", options=list(v3))
    nombre_cuenta = v3.get(cuenta, "")

    expand_insert.write(f"<p style= font-size: 24px; font-weight: bold;color: #26472A;'>Numero de cuenta: {nombre_cuenta}</p>", unsafe_allow_html=True)

    fecha = expand_insert.date_input("Fecha:")

    if expand_insert.button("Insertar", type="primary"):
        if id_sucursal and id_cat_gastos and monto and descripcion:
            insertar(id_sucursal, id_cat_gastos, monto, descripcion, cuenta, fecha)
            with st.spinner('Wait for it...'):
                time.sleep(3)
            st.success('Done!')
            st.toast(f"Operacion por la contidad de ${monto} pesos.", icon="💰")

            id_sucursal = ""
            id_cat_gastos = ""
            monto = ""
            descripcion = ""
            cuenta = ""
            fecha = ""
        else:
            st.error("Por favor, completa todos los campos requeridos antes de insertar.")

# Editar registros
expe = col1.expander("Editar. ✏️", expanded=False)

with expe.subheader("Selecciona el ID a editar."):
    id_edit = expe.number_input("ID del registro a editar:", min_value=0)
    query = "SELECT * FROM gastos WHERE id = %s"
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

# Mostrar categorias
df_categorias = pd.DataFrame(categorias, columns=["ID", "Categorías"])
expc = col2.expander("Categorias.")
expc.dataframe(df_categorias)

# Mostrar registros
col2.subheader("Registro. 📄💹")

registros = obtener_registros_df()

if registros:
    data = [{"ID": registro[0], "id_sucursal": registro[1], "id_cat_gasto": registro[2],
             "monto": "${:,.2f}".format(registro[3]), "fecha registrada": registro[4], "descripcion": registro[5], "id_cuenta_banco": registro[6], "fecha": registro[7],"sucursal": registro[8], "categoria": registro[9], "estado": registro[10]} for registro in registros]

    col2.dataframe(data)
else:
    col2.warning("No hay registros añadidos.")
