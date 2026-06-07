import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(page_title="Ruteplanlægger", layout="wide")
st.title("⚡ Ultra-Hurtig Landsdækkende Årsplanlægger")

# --- 1. DATO-BEREGNER ---
def get_date_from_week(year, week_str, day_str):
    """Omregner 'Uge X' og 'Dag' til en dato i 2026."""
    try:
        # Uddrag tal fra "Uge 1" -> 1
        week_num = int(''.join(filter(str.isdigit, str(week_str))))
        
        # Mapping af ugedage
        days = {"mandag": 0, "tirsdag": 1, "onsdag": 2, "torsdag": 3, "fredag": 4}
        day_idx = days.get(str(day_str).lower(), 0)
        
        # Beregn dato fra årets første mandag
        jan1 = datetime(year, 1, 1)
        first_monday = jan1 + timedelta(days=(7-jan1.weekday()) % 7)
        target_date = first_monday + timedelta(weeks=week_num-1, days=day_idx)
        return target_date
    except:
        return datetime(year, 1, 5) # Fallback dato

# --- 2. DATA LOADING ---
@st.cache_data
def load_data():
    if os.path.exists('kundeliste.xlsx'):
        df = pd.read_excel('kundeliste.xlsx', skiprows=2)
        df.columns = df.columns.astype(str).str.strip()
        return df
    return None

df_kunder = load_data()

if df_kunder is not None:
    # --- 3. BEREGNING AF RUTER ---
    plan_data = []
    for _, row in df_kunder.iterrows():
        # Beregn unik dato pr. række
        date_obj = get_date_from_week(2026, row.get('Uge', 'Uge 1'), row.get('Dag', 'Mandag'))
        
        plan_data.append({
            "title": str(row.get("Kundenavn", "Ukendt")),
            "start": date_obj.strftime('%Y-%m-%d'),
            "end": date_obj.strftime('%Y-%m-%d'),
            "Konsulent": str(row.get("Konsulent", "Ukendt"))
        })
    
    df_plan = pd.DataFrame(plan_data)

    # --- 4. VISNING ---
    konsulenter = sorted(df_plan['Konsulent'].unique())
    valgt = st.selectbox("Vælg konsulent:", konsulenter)

    # Filtrer data
    df_visning = df_plan[df_plan['Konsulent'] == valgt]
    
    st.header(f"📅 Rute for {valgt}")
    
    # Vis kalender
    calendar(events=df_visning.to_dict('records'), options={"initialView": "dayGridMonth"})
    
    # Vis tabel
    st.dataframe(df_visning)
else:
    st.error("Kunne ikke finde 'kundeliste.xlsx'. Tjek filnavnet.")
