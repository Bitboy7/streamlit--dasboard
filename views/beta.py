import streamlit as st
import pandas as pd
from models.db import * 
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.subplots as sp

# Establecer la página
st.set_page_config(page_title="Panel de análisis", page_icon="🌎", layout="wide")  
st.subheader("📈 Panel de análisis de negocios")
st.write("Este es un panel de análisis simple para negocios")

#get data from mysql
result = view_all_data()

df = pd.DataFrame(result,columns=[	
'ID', 'ID_sucursal', 'ID_categoria', 'Monto','Fecha registrada', 'Descripcion', 'Sucursal', 'Categoria', 'Estado'
])
#switcher
st.sidebar.header("Please filter")
Sucursal=st.sidebar.multiselect(
    "Fltrar por sucursall",
     options=df["Sucursal"].unique(),
     default=df["Sucursal"].unique(),
)
Categoria=st.sidebar.multiselect(
    "Filter ID_categoria",
     options=df["Categoria"].unique(),
     default=df["Categoria"].unique(),
)

df_selection=df.query(
    "Sucursal==@Sucursal & Categoria==@Categoria"
)

#top analytics
def metrics():
 col1, col2, col3 = st.columns(3)

 col1.metric(label="Total Customers", value=df_selection['ID'].count(), delta="All customers")

 col2.metric(label="Total Monto", value= f"{df_selection['Monto'].sum():,.0f}",delta=df['Monto'].median())

 col3.metric(label="Monto", value= f"{ df_selection['Monto'].max()-df['Monto'].min():,.0f}",delta="Monto Range")

 style_metric_cards(background_color="#FFFFFF",border_left_color="#1f66bd")

#create divs
div1, div2=st.columns(2)

#pie chart
def pie():
 with div1:
  theme_plotly = None # None or streamlit
  fig = px.pie(df_selection, values='Monto', names='ID_sucursal', title='Monto by ID_sucursal')
  fig.update_layout(legend_title="ID_sucursal", legend_y=0.9)
  fig.update_traces(textinfo='percent+label', textposition='inside')
  st.plotly_chart(fig, use_container_width=True, theme=theme_plotly)

#bar chart
def barchart():
  theme_plotly = None # None or streamlit
  with div2:
    fig = px.bar(df_selection, y='Monto', x='ID_categoria', text_auto='.2s',title="Controlled text sizes, positions and angles")
    fig.update_traces(textfont_size=18, textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")

#mysql table
def table():
  with st.expander("Tabular"):
  #st.dataframe(df_selection,use_container_width=True)
   shwdata = st.multiselect('Filter :', df.columns, default=["ID","ID_sucursal","ID_categoria","Monto","Fecha registrada","Descripcion","Sucursal","Categoria","Estado"])
   st.dataframe(df_selection[shwdata],use_container_width=True)


#option menu
with st.sidebar:
        selected=option_menu(
        menu_title="Main Menu",
         #menu_title=None,
        options=["Home","Table"],
        icons=["house","book"],
        menu_icon="cast", #option
        default_index=0, #option
        orientation="vertical",

        )
 
if selected=="Home":
    
    pie()
    barchart()
    metrics()

if selected=="Table":
   metrics()
   table()
   df_selection.describe().T
