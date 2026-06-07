import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(page_title="Ruteplanlægger", layout="wide")
st.title("⚡ Ultra-Hurtig Landsdækkende Årsplanlægger")

# --- 1. HJÆLPEFUNKTIONER ---
def get_date_from_week(year, week, day_of_week):
    """Konverterer ugenummer og dag (0-4) til en dato-streng."""
    # Starter på første mandag i året
    first_day = datetime(year, 1, 1)
    first_monday = first_day + timedelta(days=(7-first_day.weekday()) % 7)
    target_date = first_monday + timedelta(weeks=week-1, days=day_of_week)
    return target_date.strftime('%Y-%m-%d')

@st.cache_data
def load_data():
    if os.path.exists('kundeliste.xlsx'):
        df = pd.read_excel('kundeliste.xlsx', skiprows=2)
        df.columns = df.columns.astype(str).str.strip()
        return df
    return None

# --- 2. BEREGNINGSLOGIK ---
def generate_calendar_data(df):
    plan_data = []
    # HER ER DIT FOR-LOOP (Tilpasset til dato-beregning)
    for _, row in df.iterrows():
        # Sørg for at din data har 'Uge' (f.eks. 1) og 'Dag' (0=Man, 4=Fre)
        # Hvis du ikke har dem endnu, skal de beregnes her
        uge = int(row.get('Uge', 1)) 
        dag = 0 # Default mandag, eller hent fra din data
        
        calc_date = get_date_from_week(2026, uge, dag)
        
        plan_data.append({
            "title": str(row.get("Navn", "Ukunde")),
            "start": calc_date,
            "end": calc_date,
            "Konsulent": str(row.get("Konsulent", "Ukendt"))
        })
    return pd.DataFrame(plan_data)

# --- 3. HOVEDPROGRAM ---
df_kunder = load_data()

if df_kunder is not None:
    # Beregn data
    if 'df_plan' not in st.session_state:
        st.session_state['df_plan'] = generate_calendar_data(df_kunder)
    
    df_plan = st.session_state['df_plan']

    # Konsulent-valg
    konsulenter = df_plan['Konsulent'].unique()
    valgt = st.selectbox("Vælg konsulent:", konsulenter)

    # Filtrering
    df_visning = df_plan[df_plan['Konsulent'] == valgt]
    
    st.header(f"📅 Rute for {valgt}")
    
    # Vis kalender
    calendar_events = df_visning.to_dict('records')
    calendar(events=calendar_events, options={"initialView": "dayGridMonth"})
    
    st.subheader("📋 Detaljer")
    st.dataframe(df_visning)
else:
    st.error("Kunne ikke finde 'kundeliste.xlsx'. Tjek GitHub-mappen.")
