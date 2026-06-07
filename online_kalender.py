import streamlit as st
import pandas as pd
import os
from streamlit_calendar import calendar

st.set_page_config(page_title="Ruteplanlægger", layout="wide")
st.title("⚡ Ultra-Hurtig Landsdækkende Årsplanlægger")

# --- 1. DATA LOADING ---
if os.path.exists('kundeliste.xlsx'):
    df_kunder = pd.read_excel('kundeliste.xlsx', skiprows=2)
    df_kunder.columns = df_kunder.columns.astype(str).str.strip()

    # --- 2. DIN BEREGNINGSLOGIK ---
    # Her skal dit for-loop være, der bygger 'endelig_52_plan'
    # For nu bruger jeg en simpel model, så vi kan se kalenderen:
    endelig_52_plan = []
    for _, row in df_kunder.iterrows():
        endelig_52_plan.append({
            "title": row.get("Navn", "Ukendt Kunde"),
            "start": "2026-06-08", # Sæt din beregnede dato her
            "end": "2026-06-08"
        })
    
    df_plan = pd.DataFrame(endelig_52_plan)
    
    # --- 3. KALENDER VISNING ---
    st.header("📅 Online Ruteskema")
    
    # Her er den vigtigste linje: Du SKAL kalde calendar() funktionen
    calendar_options = {
        "initialView": "dayGridMonth",
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listWeek"},
    }
    
    # Dette tegner selve kalenderen på skærmen
    calendar(events=endelig_52_plan, options=calendar_options)

    # --- 4. TABEL VISNING ---
    st.subheader("📋 Samlet tabel")
    st.dataframe(df_plan)

else:
    st.error("Filen 'kundeliste.xlsx' blev ikke fundet.")
