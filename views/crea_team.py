import streamlit as st
import pandas as pd
from sqlalchemy import text

def show():
    st.title("➕ Crea team")

    with st.form(key = "from_crea_team", border = True, clear_on_submit = True):
        input_nome_team = st.text_input("Nome del team", max_chars = 100)

        query = '''SELECT Nome, Cognome, CF, TU.Username AS Username
                   FROM TBL_ANAGRAFICHE TA, TBL_UTENTI TU, TBL_RUOLI TR
                   WHERE TA.CF = TU.CF_socio AND
                        TU.Username = TR.Username AND
                        Ruolo = 'Utente standard'
                '''
        
        utenti_df = pd.read_sql(query, st.session_state.engine)

        utenti_df['Nome Cognome'] = utenti_df['Nome'].astype(str) + ' ' + utenti_df['Cognome'].astype(str) + ' - ' + utenti_df['CF'].astype(str) + ' - ' + utenti_df['Username'].astype(str)

        utenti_df = utenti_df['Nome Cognome'].tolist()
        utenti_df = [''] + utenti_df

        input_gestore = st.selectbox("Gestore del team", options = utenti_df)

        input_descrizione = st.text_area("Descrizione del team")

        submitted = st.form_submit_button("Submit", use_container_width = True)

        if submitted:
            err = []

            query = '''SELECT Nome
                       FROM TBL_TEAM
                    '''
            
            team_df = pd.read_sql(query, st.session_state.engine)

            for _, t in team_df.iterrows():
                if t['Nome'] == input_nome_team:
                    err.append('Esiste già un team con questo nome.')
                    break

            if input_nome_team == '':
                err.append('Il campo team non può essere lasciato vuoto.')

            if input_gestore == '':
                err.append('Il campo Gestore non può essere lasciato vuoto.')

            if input_descrizione == '':
                err.append('Il campo descrizione non può essere lasciato vuoto.')

            if err:
                for e in err:
                    st.error(e, icon = '🚨')
            else:
                username_gestore = input_gestore.split()[-1]
                CF_gestore = input_gestore.split()[-3]

                query = text('''UPDATE TBL_RUOLI
                                SET Ruolo = 'Gestore di un team'
                                WHERE Username = :username
                            ''')
            
                with st.session_state.engine.connect() as conn:
                    conn.execute(query, {
                        'username': username_gestore
                    })

                    conn.commit()

                query = text('''INSERT INTO TBL_TEAM (Nome, Gestore, Descrizione)
                                VALUES (:nome, :gestore, :descrizione)
                            ''')
                
                with st.session_state.engine.connect() as conn:
                    conn.execute(query, {
                        'nome': input_nome_team,
                        'gestore': CF_gestore,
                        'descrizione': input_descrizione
                    })

                    conn.commit()

                st.success('Team creato con successo', icon = '✅')
