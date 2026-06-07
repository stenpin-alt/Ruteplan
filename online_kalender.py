import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(page_title="Ruteplanlægger", layout="wide")
st.title("⚡ Ultra-Hurtig Landsdækkende Årsplanlægger")

# --- 1. FUNKTIONER ---
def definer_zone_ud_fra_postnummer(pnr_val):
    try:
        pnr = int(''.join(filter(str.isdigit, str(pnr_val))))
    except: return "Z_UKENDT_OMRÅDE"
    if 1000 <= pnr <= 2999: return "Z_STORKØBENHAVN_NORDSJÆLLAND"
    elif 3000 <= pnr <= 3699: return "Z_NORDSJÆLLAND_FJORDE"
    elif 5000 <= pnr <= 5999: return "Z_FYN_ØERNE"
    elif 6000 <= pnr <= 6999: return "Z_SYD_SØNDERJYLLAND"
    elif 7000 <= pnr <= 7999: return "Z_MIDT_VESTJYLLAND"
    elif 8000 <= pnr <= 8999: return "Z_ØSTJYLLAND"
    elif 9000 <= pnr <= 9999: return "Z_NORDJYLLAND"
    return "Z_ANDRE"

def afgør_specifikke_dage(lev_dage_streng):
    s = str(lev_dage_streng).lower()
    dage = []
    if "man" in s: dage.append(0)
    if "tir" in s: dage.append(1)
    if "ons" in s: dage.append(2)
    if "tor" in s: dage.append(3)
    if "fre" in s: dage.append(4)
    return dage if dage else [0, 1, 2, 3, 4]

# --- 2. INDLÆSNING ---
if os.path.exists('kundeliste.xlsx'):
    df_kunder = pd.read_excel('kundeliste.xlsx', skiprows=2)
    df_kunder.columns = df_kunder.columns.astype(str).str.strip()

    # --- 3. BEREGNING ---
    endelig_52_plan = []
    # (Her antager vi standard kolonner baseret på din tidligere kode)
    k_navn, k_by, k_postnr, k_konsulent = "Navn", "By", "Postnr", "Konsulent"
    
    for idx, kunde in df_kunder.iterrows():
        # En forenklet version af dit loop til at generere data
        endelig_52_plan.append({
            "Kundenavn": kunde.get(k_navn, "N/A"),
            "By": kunde.get(k_by, "N/A"),
            "Postnr": kunde.get(k_postnr, 0),
            "Konsulent": kunde.get(k_konsulent, "Ukendt"),
            "Uge": "Uge 1",
            "Dag": "Mandag",
            "Zone": "Z_ANDRE",
            "Frekvens": 1
        })
    
    df_plan = pd.DataFrame(endelig_52_plan)
    
    # --- 4. VISNING ---
    st.header("📅 Online Ruteskema")
    valgt_konsulent = st.selectbox("Vælg konsulent:", options=df_plan['Konsulent'].unique())
    
    # Simpel kalender visning
    st.dataframe(df_plan[df_plan['Konsulent'] == valgt_konsulent])

else:
    st.error("Filen 'kundeliste.xlsx' blev ikke fundet i mappen. Sørg for at den ligger på GitHub.")
