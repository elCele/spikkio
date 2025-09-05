import streamlit as st
import pandas as pd
from sqlalchemy import text

def show():
    st.title("👥 Il mio team")

    query = f'''SELECT *
                FROM TBL_TEAM TT
                WHERE Gestore = '{st.session_state.CF_socio}'
                '''
    
    df_team = pd.read_sql(query, st.session_state.engine)

    with st.container(border = True):
        st.subheader(df_team['Nome'][0])

        st.markdown(f"> {df_team['Descrizione'][0]}")

        st.write(f":gray[Data creazione: {df_team['Data_creazione'][0].strftime('%d-%m-%Y')}]")

    query = f'''SELECT *
                FROM TBL_PROGETTI_TEAMS TPT
                WHERE Team = '{df_team['Nome'][0]}'
                '''
    
    df_progetti = pd.read_sql(query, st.session_state.engine)

    query = f'''SELECT *
                FROM TBL_PARTECIPAZIONI_TEAM TPT, TBL_ANAGRAFICHE TA
                WHERE Team = '{df_team['Nome'][0]}' AND
                    TPT.CF_socio = TA.CF
                '''
    
    df_membri = pd.read_sql(query, st.session_state.engine)

    query = f'''SELECT *
                FROM TBL_ANAGRAFICHE TA
                WHERE TA.CF NOT IN (
                    SELECT TPT.CF_socio
                    FROM TBL_PARTECIPAZIONI_TEAM TPT
                    WHERE TPT.Team = '{df_team['Nome'][0]}'
                )
                '''
    
    df_non_membri = pd.read_sql(query, st.session_state.engine)

    non_membri = ['']
    non_membri = non_membri + (df_non_membri["CF"] + "  - " + df_non_membri["Nome"] + " " + df_non_membri["Cognome"]).tolist()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Progetti")
        i_col1, i_col2 = st.columns(2)
        cols = [i_col1, i_col2]
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

            if i == 1:
                i = 0
            else:
                i += 1

    with col2:
        st.subheader("Membri")

        i_col1, i_col2 = st.columns([0.7, 0.3], vertical_alignment = 'bottom')

        with i_col1:
            utente = st.selectbox("Utenti non iscritti", options = non_membri, )

        with i_col2:
            btn_aggiungi_utente = st.button("Aggiungi", icon = '➕', use_container_width = True)

            if btn_aggiungi_utente:
                if utente != '':
                    CF = utente.split()[0]

                    query = text('''INSERT INTO TBL_PARTECIPAZIONI_TEAM (Team, CF_socio)
                                    VALUES (:team, :cf);
                                    ''')
                
                    with st.session_state.engine.connect() as conn:
                        conn.execute(query, {
                            'team': df_team['Nome'][0],
                            'cf': CF
                        })

                        conn.commit()

                    st.rerun()
        with st.container(border = True):
            for _, m in df_membri.iterrows():
                with st.container(border = True):
                    i_col1, i_col2, i_col3 = st.columns([0.1, 0.6, 0.3], vertical_alignment = 'center')

                    with i_col2:
                        st.write(f"👤 {m['Nome']} {m['Cognome']}")  

                    with i_col3:
                        btn_elimina_membro = st.button("Elimina", key = f"{m['CF']} - elimina", icon = '➖', use_container_width = True)

                        if btn_elimina_membro:
                            query = text('''DELETE FROM TBL_PARTECIPAZIONI_TEAM
                                            WHERE CF_socio = :cf;
                                            ''')
                            
                            with st.session_state.engine.connect() as conn:
                                conn.execute(query, {
                                    'cf': m['CF']
                                })

                                conn.commit()

                            st.rerun()