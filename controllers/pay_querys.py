import pandas as pd
from models.db import create_connection
import streamlit as st

conn = create_connection()
cursor = conn.cursor()

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

def get_productor_options():
    p_query = "SELECT fullname, id_estado FROM productores"
    p_data = pd.DataFrame(fetch_all(p_query))
    p_options = p_data[0].tolist()
    p_id_estado = p_data[1].tolist()
    return p_options, p_id_estado

@st.cache_data
def get_estado_options():
    estado_query = "SELECT id FROM estado"
    estado_data = pd.DataFrame(fetch_all(estado_query))
    estado_options = estado_data[0].tolist()
    return estado_options

def get_pagos_data():
    pagos_query = "SELECT * FROM pagos"
    pagos_data = pd.DataFrame(fetch_all(pagos_query))
    return pagos_data
