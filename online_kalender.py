import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
st.title("⚡ Landsdækkende Årsplanlægger")

# 1. Sikker data-indlæsning
@st.cache_data
def load_data():
    if os.path.exists('kundeliste.xlsx'):
        df = pd.read_excel('kundeliste.xlsx', skiprows=2)
        df.columns = df.columns.astype(str).str.strip()
        return df
    return None

# Initialiser session_state hvis den mangler
if 'df_plan' not in st.session_state:
    st.session_state['df_plan'] = None

df_kunder = load_data()

# 2. Knap-logik
if st.button("Generer plan"):
    if df_kunder is not None:
        # Her vil din beregningslogik ligge
        # Eksempel: Vi tager rådata og gemmer dem som 'df_plan'
        st.session_state['df_plan'] = df_kunder 
        st.success("Plan genereret!")
    else:
        st.error("Kunne ikke finde 'kundeliste.xlsx'.")

# 3. Visning af tabel (kun hvis data findes)
if st.session_state['df_plan'] is not None:
    df = st.session_state['df_plan']
    
    # Konsulent-filter
    if 'Konsulent' in df.columns:
        valgt_konsulent = st.selectbox("Vælg konsulent:", df['Konsulent'].unique())
        df_filt = df[df['Konsulent'] == valgt_konsulent]
        
        st.header(f"📋 Rute for {valgt_konsulent}")
        st.dataframe(df_filt, use_container_width=True)
    else:
        st.warning("Kolonnen 'Konsulent' blev ikke fundet i Excel-filen.")
