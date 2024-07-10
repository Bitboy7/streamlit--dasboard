import streamlit as st
from datetime import datetime
import mysql.connector
from decimal import Decimal
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
import pandas as pd

conn = create_connection()
cursor = conn.cursor()

# Check if connection is established
if conn.is_connected():
    st.write("Connected to database")
else:
    st.write("Not connected to database")

# Funciones para interactuar con la base de datos
def insertar_estado(nombre):
    conn = create_connection()
    cursor = conn.cursor()
    query = "INSERT INTO estado (id, nombre) VALUES (%s, %s)"
    cursor.execute(query, (nombre[:25], nombre))
    conn.commit()
    conn.close()

def insertar_sucursal(nombre, direccion, telefono, id_estado):
    conn = create_connection()
    cursor = conn.cursor()
    query = "INSERT INTO sucursal (nombre, direccion, telefono, id_estado) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (nombre, direccion, telefono, id_estado))
    conn.commit()
    conn.close()


# Clases para representar las entidades
class CuentaBanco:
    def __init__(self, id, numero_cuenta, saldo, fecha_creacion, id_sucursal, id_banco):
        self.id = id
        self.numero_cuenta = numero_cuenta
        self.saldo = Decimal(str(saldo))  # Convertimos a Decimal
        self.fecha_creacion = fecha_creacion
        self.id_sucursal = id_sucursal
        self.id_banco = id_banco

    def registrar_gasto(self, monto, descripcion):
        monto_decimal = Decimal(str(monto))  # Convertimos el monto a Decimal
        if self.saldo >= monto_decimal:
            self.saldo -= monto_decimal
            actualizar_saldo(self.id, self.saldo)
            registrar_movimiento(self.id, -monto_decimal, descripcion)
            return True
        return False

    def registrar_venta(self, monto, descripcion):
        monto_decimal = Decimal(str(monto))  # Convertimos el monto a Decimal
        self.saldo += monto_decimal
        actualizar_saldo(self.id, self.saldo)
        registrar_movimiento(self.id, monto_decimal, descripcion)

    def obtener_movimientos(self):
        query = "SELECT * FROM movimientos_cuenta WHERE id_cuenta = %s ORDER BY fecha DESC"
        return obtener_datos(query, (self.id,))

# Funciones para interactuar con la base de datos
def ejecutar_query(query, params=None):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def obtener_datos(query, params=None):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

# Funciones específicas para la gestión de cuentas
def crear_cuenta(numero_cuenta, saldo_inicial, id_sucursal, id_banco):
    saldo_decimal = Decimal(str(saldo_inicial))  # Convertimos el saldo inicial a Decimal
    query = "INSERT INTO cuenta_banco (numero_cuenta, saldo, id_sucursal, id_banco) VALUES (%s, %s, %s, %s)"
    return ejecutar_query(query, (numero_cuenta, saldo_decimal, id_sucursal, id_banco))

def actualizar_saldo(id_cuenta, nuevo_saldo):
    query = "UPDATE cuenta_banco SET saldo = %s WHERE id = %s"
    ejecutar_query(query, (nuevo_saldo, id_cuenta))

def registrar_movimiento(id_cuenta, monto, descripcion):
    query = "INSERT INTO movimientos_cuenta (id_cuenta, monto, descripcion, fecha) VALUES (%s, %s, %s, NOW())"
    ejecutar_query(query, (id_cuenta, monto, descripcion))

def obtener_cuenta(id_cuenta):
    query = "SELECT * FROM cuenta_banco WHERE id = %s"
    resultado = obtener_datos(query, (id_cuenta,))
    if resultado:
        return CuentaBanco(**resultado[0])
    return None

def obtener_movimientos(id_cuenta):
    query = "SELECT * FROM movimientos_cuenta WHERE id_cuenta = %s ORDER BY fecha DESC"
    return obtener_datos(query, (id_cuenta,))

# Interfaz de Streamlit para la gestión de cuentas
def gestion_cuentas():
    st.title("Gestión de Cuentas Bancarias")
    
    menu_cuentas = ["Crear Cuenta", "Ver Saldo", "Realizar Depósito", "Realizar Retiro", "Ver Movimientos"]
    opcion_cuenta = st.sidebar.selectbox("Selecciona una opción", menu_cuentas)

    if opcion_cuenta == "Crear Cuenta":
        crear_nueva_cuenta()
    elif opcion_cuenta == "Ver Saldo":
        ver_saldo_cuenta()
    elif opcion_cuenta == "Realizar Depósito":
        realizar_deposito()
    elif opcion_cuenta == "Realizar Retiro":
        realizar_retiro()
    elif opcion_cuenta == "Ver Movimientos":
        ver_movimientos_cuenta()

def crear_nueva_cuenta():
    st.subheader("Crear Nueva Cuenta Bancaria")
    numero_cuenta = st.text_input("Número de Cuenta")
    saldo_inicial = st.number_input("Saldo Inicial", min_value=0.0, step=0.01)
    
    # Obtener sucursales y bancos para los selectbox
    sucursales = obtener_datos("SELECT id, nombre FROM sucursal")
    bancos = obtener_datos("SELECT id, nombre FROM bancos")
    
    id_sucursal = st.selectbox("Sucursal", options=[s['id'] for s in sucursales], format_func=lambda x: next(s['nombre'] for s in sucursales if s['id'] == x))
    id_banco = st.selectbox("Banco", options=[b['id'] for b in bancos], format_func=lambda x: next(b['nombre'] for b in bancos if b['id'] == x))
    
    if st.button("Crear Cuenta"):
        id_cuenta = crear_cuenta(numero_cuenta, saldo_inicial, id_sucursal, id_banco)
        if id_cuenta:
            st.success(f"Cuenta creada con éxito. ID de cuenta: {id_cuenta}")
        else:
            st.error("Error al crear la cuenta.")

def ver_saldo_cuenta():
    st.subheader("Ver Saldo de Cuenta")
    id_cuenta = st.number_input("ID de la Cuenta", min_value=1, step=1)
    if st.button("Ver Saldo"):
        cuenta = obtener_cuenta(id_cuenta)
        if cuenta:
            st.write(f"Número de cuenta: {cuenta.numero_cuenta}")
            st.write(f"Saldo actual: ${cuenta.saldo:.2f}")
        else:
            st.error("Cuenta no encontrada.")

def realizar_deposito():
    st.subheader("Realizar Depósito")
    id_cuenta = st.number_input("ID de la Cuenta", min_value=1, step=1)
    monto = st.number_input("Monto a Depositar", min_value=0.01, step=0.01)
    descripcion = st.text_input("Descripción del Depósito")
    
    if st.button("Realizar Depósito"):
        cuenta = obtener_cuenta(id_cuenta)
        if cuenta:
            cuenta.registrar_venta(monto, descripcion)
            st.success(f"Depósito de ${monto:.2f} realizado con éxito.")
        else:
            st.error("Cuenta no encontrada.")

def realizar_retiro():
    st.subheader("Realizar Retiro")
    id_cuenta = st.number_input("ID de la Cuenta", min_value=1, step=1)
    monto = st.number_input("Monto a Retirar", min_value=0.01, step=0.01)
    descripcion = st.text_input("Descripción del Retiro")
    
    if st.button("Realizar Retiro"):
        cuenta = obtener_cuenta(id_cuenta)
        if cuenta:
            if cuenta.registrar_gasto(monto, descripcion):
                st.success(f"Retiro de ${monto:.2f} realizado con éxito.")
            else:
                st.error("Saldo insuficiente para realizar el retiro.")
        else:
            st.error("Cuenta no encontrada.")

def ver_movimientos_cuenta():
    st.subheader("Ver Movimientos de Cuenta")
    id_cuenta = st.number_input("ID de la Cuenta", min_value=1, step=1)
    if st.button("Ver Movimientos"):
        movimientos = obtener_movimientos(id_cuenta)
        if movimientos:
            df_movimientos = pd.DataFrame(movimientos)
            st.dataframe(df_movimientos)
        else:
            st.info("No se encontraron movimientos para esta cuenta.")

# ... (funciones similares para otras tablas)

# Interfaz de Streamlit
def main():
    st.title("Sistema de Gestión Bancaria")

    menu = ["Estados", "Sucursales", "Productores", "Bancos", "Cuentas", "Gastos", "Ventas"]
    choice = st.sidebar.selectbox("Selecciona una opción", menu)

    if choice == "Estados":
        st.subheader("Registro de Estados")
        nombre_estado = st.text_input("Nombre del Estado")
        if st.button("Registrar Estado"):
            insertar_estado(nombre_estado)
            st.success(f"Estado {nombre_estado} registrado con éxito")

    elif choice == "Sucursales":
        st.subheader("Registro de Sucursales")
        nombre_sucursal = st.text_input("Nombre de la Sucursal")
        direccion = st.text_input("Dirección")
        telefono = st.text_input("Teléfono")
        id_estado = st.text_input("ID del Estado")
        if st.button("Registrar Sucursal"):
            insertar_sucursal(nombre_sucursal, direccion, telefono, id_estado)
            st.success(f"Sucursal {nombre_sucursal} registrada con éxito")

    elif choice == "Cuentas":
     gestion_cuentas()      


if __name__ == "__main__":
    main()