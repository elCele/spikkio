import streamlit as st
import pandas as pd

def show():
    st.title("👥 Visualizza team")

    query = f'''SELECT *
                FROM TBL_TEAM TT, TBL_PARTECIPAZIONI_TEAM TPT
                WHERE CF_socio = '{st.session_state.CF_socio}' AND
                    TT.Nome = TPT.Team
                '''
    
    df_teams = pd.read_sql(query, st.session_state.engine)

    for _, t in df_teams.iterrows():
        with st.container(border = True):
            st.subheader(t['Nome'])

            st.markdown(f"> {t['Descrizione']}")

            st.write(f":gray[Data creazione: {t['Data_creazione'].strftime('%d-%m-%Y')}]")
