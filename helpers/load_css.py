import streamlit as st
from streamlit_extras import stylable_container

@st.cache_data
def load_css_style():
    with open('style.css') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)   

def remote_js(url):
    st.markdown(f'<script src="{url}"></script>', unsafe_allow_html=True)

def iconMetricContainer(key,iconUnicode,color='grey'):
    """Function that returns a CSS styled container for adding a Material Icon to a Streamlit st.metric value

    Args:
        key (str): Unique key for the component
        iconUnicode (str): Code point for a Material Icon, you can find them here https://fonts.google.com/icons. Sample \e8b6 
        color (str, optional): HTML Hex color value for the icon. Defaults to 'grey'.

    Returns:
        DeltaGenerator: A container object. Elements can be added to this container using either the 'with'
        notation or by calling methods directly on the returned object.
    """
    css_style=f'''                 
                    div[data-testid="stMetricValue"]>div::before
                    {{                            
                        font-family: "Material Icons";
                        content: "{iconUnicode}";
                        vertical-align: -20%;
                        color: {color};
                    }}                    
                    '''
    iconMetric=stylable_container(
                key=key,
                css_styles=css_style
            )
    return iconMetric

    
    