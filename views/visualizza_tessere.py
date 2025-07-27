import streamlit as st
import pandas as pd
from utils import functions as f

def show():
    st.title('🪪 Visualizza tessere')
    
    query = '''SELECT *
               FROM TBL_TESSERE TT, TBL_ANAGRAFICHE TA
               WHERE TT.CF_socio = TA.CF
               '''
    
    df_tessere = pd.read_sql(query, st.session_state.engine)

    nTessere = 0

    for _, t in df_tessere.iterrows():
        if t['CF_socio'] == st.session_state.CF_socio:
            nTessere += 1

            with st.container(border = True):
                c1, c2 = st.columns([0.4, 0.6], vertical_alignment = 'center')

                with c1:
                    st.image(f.build_tessera(t['Nome'], t['Cognome'], t['CF_socio'], t['Data_scadenza'].date(), t['Codice_tessera']))

                with c2:
                    st.subheader(f"{t['Codice_tessera']}")
                    st.write(f"🪪 Tipologia tessera: :gray[{t['Tipo']}]")
                    st.write(f"🔑 Qualifica: :gray[{t['Qualifica']}]")
                    st.write(f"📆 Data di tesseramento: :gray[{t['Data_tesseramento'].date().strftime('%d/%m/%Y')}]")
                    st.write(f"📆 Data di scadenza: :red[{t['Data_scadenza'].date().strftime('%d/%m/%Y')}]")

    if nTessere == 0:
        with st.container(height = 100, border = True):
            st.markdown(
                """
                <style>
                .centered-text {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100%; /* Occupa l'altezza del container */
                    font-size: 20px;
                    color: gray;
                    padding-top: 20px;
                }
                </style>
                <div class="centered-text">
                    Nessuna tessera trovata
                </div>
                """,
                unsafe_allow_html=True
            )