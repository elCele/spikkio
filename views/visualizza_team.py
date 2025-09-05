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

    teams = []

    st.subheader("I miei team")
    with st.container(border = False):
        for _, t in df_teams.iterrows():
            teams.append(t['Nome'])

            with st.container(border = True):
                st.subheader(t['Nome'])

                st.markdown(f"> {t['Descrizione']}")

                st.write(f":gray[Data creazione: {t['Data_creazione'].strftime('%d-%m-%Y')}]")

    teams = "', '".join(teams)
    teams = "('" + teams + "')"

    query = f'''SELECT *
                FROM TBL_PROGETTI_TEAMS TPT
                WHERE Team IN {teams}
                '''
    
    df_progetti = pd.read_sql(query, st.session_state.engine)

    st.subheader("Progetti")
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    i = 0

    for _, p in df_progetti.iterrows():
        with cols[i]:
            with st.container(border = True):
                st.subheader(f"📂 {p['Nome']}")
                st.write(p['Descrizione'])
                if pd.isna(p['Data_fine']) and pd.isna(p['Deadline']):
                    st.write(f":gray[{p['Data_inizio'].strftime('%d-%m-%Y')} - ...]")
                elif pd.isna(p['Data_fine']) and not pd.isna(p['Deadline']):
                    st.write(f":gray[{p['Data_inizio'].strftime('%d-%m-%Y')} -] :red[{p['Deadline'].strftime('%d-%m-%Y')}]")
                else:
                    st.write(f":gray[{p['Data_inizio'].strftime('%d-%m-%Y')} - {p['Data_fine'].strftime('%d-%m-%Y')}]")

        if i == 2:
            i = 0
        else:
            i += 1
                