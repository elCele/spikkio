import streamlit as st
import pandas as pd
from sqlalchemy import text

def show():
    st.title("📌 Bacheca")

    with st.container(border = True):
        c1, c2, c3 = st.columns([0.6, 0.2, 0.2], vertical_alignment = 'bottom')

        with c1:
            filter_titolo_B = st.text_input("Cerca comunicazioni", placeholder = "Titolo comunicazione")

        with c2:
            filter_Categoria_B = st.selectbox("Cerca categoria", ['', 'Avviso', 'Evento', 'Convocazione', 'Segnalazione', 'Altro'])

        with c3:
            ancheLette = st.toggle("Mostra comunicazioni lette")

        query = f'''SELECT *
                    FROM TBL_COMUNICAZIONI
                    WHERE Destinatario = '{st.session_state.user}' AND
                        Titolo LIKE '%{filter_titolo_B}%' AND
                        Categoria LIKE '%{filter_Categoria_B}%'
                    ORDER BY Data_pubblicazione DESC;
                '''
        
        df_comunicazioni = pd.read_sql(query, st.session_state.engine)

        st.write("")
        st.write("")

        for _, c in df_comunicazioni.iterrows():
            if not ancheLette and c['Stato'] == 'Letta':
                continue

            with st.container(border = True):
                icon = ""

                if c['Categoria'] == "Avviso":
                    icon = "🔔"
                elif c['Categoria'] == 'Evento':
                    icon = "📅"
                elif c['Categoria'] == 'Convocazione':
                    icon = "📣"
                elif c['Categoria'] == 'Segnalazione':
                    icon = "📢"
                else:
                    icon = "⭕"

                if c['Categoria'] == 'Segnalazione':
                    st.subheader(f"{icon} {c['Categoria']} - [{c['Titolo']}]", divider = "gray")
                else:
                    st.subheader(f"{icon} {c['Categoria']} - {c['Titolo']}", divider = "gray")
                
                c1, c2 = st.columns([0.75, 0.15], vertical_alignment = 'top')

                with c1:
                    st.markdown(f"{c['Testo']}", unsafe_allow_html = True)

                with c2:
                    if c['Stato'] == 'Non letta':
                        segna_come_letta = st.button("Segna come letta", use_container_width = True, key = f"{c['ID_comunicazione']} - read_toggle")

                        if segna_come_letta:
                            with st.session_state.engine.connect() as conn:
                                conn.execute(text('''UPDATE TBL_COMUNICAZIONI
                                                     SET Stato = 'Letta'
                                                     WHERE ID_comunicazione = :ID'''), {'ID': c['ID_comunicazione']})
                                conn.commit()

                            st.rerun()

                if c['Allegato'] is not None and not pd.isna(c['Allegato']) and len(c['Allegato']) > 0:
                    st.download_button(
                        label = "Scarica allegato",
                        data = c['Allegato'],
                        file_name = f"{c['ID_comunicazione']}_allegato.{c['Estensione_allegato']}",
                        mime = "application/octet-stream",
                        icon = "📁",
                        key = f"{c['ID_comunicazione']} - file_button"
                    )

                st.write(f":gray[Data pubblicazione: {c['Data_pubblicazione'].strftime('%d-%m-%Y')} - {c['Data_pubblicazione'].strftime('%H:%M:%S')}]")