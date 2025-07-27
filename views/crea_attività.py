import streamlit as st
import datetime
from sqlalchemy import text

def show():
    st.title("➕ Crea attività")

    with st.form(key = "form_crea_attività", clear_on_submit = True, border = True):
        input_denominazione_CA = st.text_input("Denominazione", max_chars = 100)
        input_data_CA = st.date_input("Data", min_value = datetime.date(1000, 1, 1), max_value = datetime.date(3000, 1, 1), format = 'DD/MM/YYYY')

        c1, c2 = st.columns(2)

        with c1:
            input_oraInizio_CA = st.time_input("Ora di inizio")

        with c2:
            input_oraFine_CA = st.time_input("Ora di fine")

        input_max_partecipanti_CA = st.number_input("Numero massimo di partecipanti", value = 0, min_value = 0, step = 1)
        st.write(":gray[Lasciare 0 se non c'è limite di partecipanti]")

        input_descrizione_CA = st.text_area("Descrizione")

        submitted = st.form_submit_button("Submit", use_container_width = True)

        if submitted:
            err = []

            if input_denominazione_CA == "":
                err.append("Il campo 'Denominazione' non può essere lasciato vuoto.")

            if input_data_CA < datetime.date.today():
                err.append("La data inserita è precedente alla data odierna.")

            if input_oraInizio_CA > input_oraFine_CA:
                err.append("L'ora d'inizio è maggiore dell'ora di fine.")

            if input_descrizione_CA == "":
                err.append("Il campo 'Descrizione' non può essere lasciato vuoto.")

            if input_max_partecipanti_CA == 0:
                input_max_partecipanti_CA = None

            if err:
                for e in err:
                    st.error(e, icon = "🚨")
            else:
                query = text('''INSERT INTO TBL_ATTIVITA (Denominazione, Data, Ora_inizio, Ora_fine, Max_partecipanti, Descrizione)
                                VALUES (:denominazione, :data, :ora_inizio, :ora_fine, :max_partecipanti, :descrizione)   
                                ''')
                
                with st.session_state.engine.connect() as conn:
                    conn.execute(query, {
                        'denominazione': input_denominazione_CA,
                        'data': input_data_CA,
                        'ora_inizio': input_oraInizio_CA,
                        'ora_fine': input_oraFine_CA,
                        'max_partecipanti': input_max_partecipanti_CA,
                        'descrizione': input_descrizione_CA
                    })

                    conn.commit()

                st.success("L'attività è stata creata con successo.", icon = '✅')

                query = text('''INSERT INTO TBL_COMUNICAZIONI (Titolo, Testo, Categoria, Data_scadenza, Autore, Destinatario)
                                VALUES (:titolo, :testo, 'Evento', :data_scadenza, :autore, :destinatario)
                                ''')

                with st.session_state.engine.begin() as conn:
                    for _, u in st.session_state.users.iterrows():
                        conn.execute(query, {
                            'titolo': input_denominazione_CA,
                            'testo': f"Ciao {u['Username']}! <br> È stata programmata una nuova attività che potrebbe interessarti: <br> <br> 📅 Data: {input_data_CA} <br> 🕒 Ora di inizio: {input_oraInizio_CA} <br> 🕒 Ora fine: {input_oraFine_CA} <br> <br> Se vuoi saperne di più o partecipare, trovi tutti i dettagli sul gestionale. <br> A presto! <br> Il team di SPIKKIO",
                            'data_scadenza': datetime.datetime.combine(input_data_CA, input_oraFine_CA),
                            'autore': st.session_state.user,
                            'destinatario': u['Username']
                        })

                st.success("Le comunicazioni sono state inserite con successo.", icon = '✅')