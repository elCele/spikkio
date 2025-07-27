import streamlit as st
from sqlalchemy import text

def show():
    st.title("📢 Effettua segnalazioni")

    with st.form("form_effettua_segnalazioni", clear_on_submit = True):
        input_titolo_ES = st.text_input("Titolo", max_chars = 200)
        input_testo_ES = st.text_area("Segnalazione", height = 200, placeholder = 'Descrivere il problema in maniera breve ma dettagliata')

        submitted = st.form_submit_button("Submit", use_container_width = True, type = 'primary')

        if submitted:
            err = []

            if input_titolo_ES == '':
                err.append("Il campo Titolo non può essere vuoto.")

            if input_testo_ES == '':
                err.append('Il campo Segnalazione non può essere vuoto.')

            if err:
                for e in err:
                    st.error(e, icon = "🚨")
            else:
                query = text('''INSERT INTO TBL_SEGNALAZIONI (Titolo, Testo, Creato_da)
                                VALUES (:titolo, :testo, :creato_da)
                                ''')
                
                with st.session_state.engine.connect() as conn:
                    conn.execute(query, {
                        'titolo': input_titolo_ES,
                        'testo': input_testo_ES,
                        'creato_da': st.session_state.user
                    })

                    conn.commit()

            st.success("La segnalazione è stata inviata correttamente", icon = "✅")