import streamlit as st
import pandas as pd
import os
from streamlit_calendar import calendar

st.set_page_config(layout="wide")

# 1. Definer en standardværdi for df_plan i session_state
if 'df_plan' not in st.session_state:
    st.session_state['df_plan'] = None

# 2. Funktion til at indlæse data
def load_data():
    if os.path.exists('kundeliste.xlsx'):
        return pd.read_excel('kundeliste.xlsx', skiprows=2)
    return None

df_kunder = load_data()

# 3. Beregnings-logik (kun hvis filen findes og knappen trykkes)
if df_kunder is not None:
    if st.button("Lyn-generer 52-Ugers Plan"):
        # HER skal dit for-loop ligge, som genererer din plan
        # Eksempel:
        # data = []
        # for ... :
        #     data.append(...)
        
        # Når dit loop er færdigt, opretter du df_plan:
        df_plan = pd.DataFrame(data) 
        
        # Gem den i session_state
        st.session_state['df_plan'] = df_plan
        st.success("Plan genereret!")

# 4. Visning (tjekker om df_plan eksisterer, før den bruges)
if st.session_state['df_plan'] is not None:
    st.header("📅 Online Ruteskema")
    # Her kalder du din kalender med st.session_state['df_plan']
else:
    st.info("Upload 'kundeliste.xlsx' og tryk på knappen for at starte.")
