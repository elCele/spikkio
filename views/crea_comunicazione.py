import streamlit as st
import pandas as pd
import datetime
from sqlalchemy import text

def show():
    st.title("📝 Crea comunicazione")

    with st.container(border = True):
        input_titolo_CC = st.text_input('Titolo della comunicazione')
        input_testo_CC = st.text_area('Testo della comunicazione')

        input_categoria_CC = st.selectbox('Categoria', ['Avviso', 'Evento', 'Convocazione'])

        c1, c2, c3 = st.columns([1.5, 4.25, 4.25], vertical_alignment = 'bottom')

        with c1:
            input_dataScadenzaEnable_CC = st.toggle('Inserisci scadenza')

        with c2:
            if input_dataScadenzaEnable_CC:
                input_dataScadenza_CC = st.date_input('Data di scadenza', min_value = "today")
            else:
                input_dataScadenza_CC = st.date_input('Data di scadenza', min_value = "today", disabled = True)

        with c3:
            if input_dataScadenzaEnable_CC:
                input_oraScadenza_CC = st.time_input('Ora di scadenza')
            else:
                input_oraScadenza_CC = st.time_input('Ora di scadenza', disabled = True)

        c1, c2 = st.columns([0.2, 0.8])

        with c1:
            input_tipoUtenti_CC = st.selectbox("Seleziona utenti", ['Utenti singoli', 'Ruoli'])

        with c2:
            query = '''SELECT CF, Nome, Cognome, TU.Username, Ruolo
                        FROM TBL_ANAGRAFICHE TA, TBL_UTENTI TU, TBL_RUOLI TR
                        WHERE TA.CF = TU.CF_socio AND
                            TU.Username = TR.Username;
                        '''
            
            df_utenti = pd.read_sql(query, st.session_state.engine)

            option_array = []

            if input_tipoUtenti_CC == 'Ruoli':
                for _, u in df_utenti.iterrows():
                    option_array.append(u['Ruolo'])

                option_array = list(dict.fromkeys(option_array))

            if input_tipoUtenti_CC == 'Utenti singoli':
                for _, u in df_utenti.iterrows():
                    option_array.append(f"{u['Nome']} {u['Cognome']} - {u['CF']}")

            input_destinatari_CC = st.multiselect("Destinatari", option_array)

        c1, c2 = st.columns([2, 1], vertical_alignment = 'center')

        with c1:
            input_allegato_CC = st.file_uploader('Allegato', accept_multiple_files = False)

        with c2:
            if input_allegato_CC == None:
                input_estensioneFile_CC = st.text_input('Estensione del file', placeholder = "Scrivere solo l'estensione, senza il punto", max_chars = 20, disabled = True)
            else:
                input_estensioneFile_CC = st.text_input('Estensione del file', placeholder = "Scrivere solo l'estensione, senza il punto", max_chars = 20)

        submitted = st.button('Submit', use_container_width = True)

        if submitted:
            err = []

            if input_titolo_CC == '':
                err.append('Il campo titolo non può rimanere vuoto.')

            if input_testo_CC == '':
                err.append('Il campo testo non può rimanere vuoto.')

            if input_dataScadenzaEnable_CC and input_oraScadenza_CC < datetime.datetime.now().time():
                err.append("L'orario scelto non è valido.")
            elif input_dataScadenzaEnable_CC:
                input_dataScadenza_CC = datetime.datetime.combine(input_dataScadenza_CC, input_oraScadenza_CC)
            else:
                input_dataScadenza_CC = None

            if not input_destinatari_CC:
                err.append('La lista dei destinatari non può essere vuota.')
            
            if input_allegato_CC == None:
                input_estensioneFile_CC = None

            if err:
                for e in err:
                    st.error(e, icon = '🚨')
            else:
                if input_tipoUtenti_CC == 'Utenti singoli':
                    CF_dest = []
                    
                    for d in input_destinatari_CC:
                        d = d.split()
                        CF_dest.append(d[-1])

                    CF_dest = '(' + ', '.join([f"'{cf}'" for cf in CF_dest]) + ')'

                    query = f'''SELECT Username
                                FROM TBL_UTENTI
                                WHERE CF_socio IN {CF_dest}
                             '''
                    
                    df_destinatari = pd.read_sql(query, st.session_state.engine)

                    for _, d in df_destinatari.iterrows():
                        query = text('''INSERT INTO TBL_COMUNICAZIONI (Titolo, Testo, Categoria, Data_scadenza, Autore, Destinatario, Allegato, Estensione_allegato)
                                        VALUES (:titolo, :testo, :categoria, :data_scadenza, :autore, :destinatario, :allegato, :estensione)
                                        ''')
                        
                        with st.session_state.engine.connect() as conn:
                            conn.execute(query, {
                                'titolo': input_titolo_CC,
                                'testo': input_testo_CC,
                                'categoria': input_categoria_CC,
                                'data_scadenza': input_dataScadenza_CC,
                                'autore': st.session_state.user,
                                'destinatario': d['Username'],
                                'allegato': input_allegato_CC,
                                'estensione': input_estensioneFile_CC
                            })

                            conn.commit()

                    st.success('Comunicazioni inserite con successo.', icon = '✅')