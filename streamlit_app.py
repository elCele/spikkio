import streamlit as st
from utils import functions as f, consts as c

from views import (
    page_404,
    login,
    cambia_credenziali,
    bacheca,
    inserisci_anagrafica,
    team,
    visualizza_anagrafiche,
    visualizza_tessere,
    crea_attività,
    effettua_segnalazioni,
    gestisci_segnalazioni,
    crea_comunicazione,
    visualizza_attività,
    crea_team,
    gestisci_utenze,
    visualizza_team
)

f.initialize_var_batch_1()
f.initialize_var_batch_2()

f.config_sidebar()

st.set_page_config(
        page_title = f"SPIKKIO - {st.session_state.current_page}",
        page_icon = "🍋",
        layout = "wide",
        initial_sidebar_state = "auto"
    )

PAGE_FUNCTIONS = {
    "Log in": login,
    "Cambia credenziali": cambia_credenziali,
    "Bacheca": bacheca,
    "Inserisci anagrafica": inserisci_anagrafica,
    "Visualizza anagrafiche": visualizza_anagrafiche,
    "Visualizza tessere": visualizza_tessere,
    "Crea attività": crea_attività,
    "Effettua segnalazioni": effettua_segnalazioni,
    "Gestisci segnalazioni": gestisci_segnalazioni,
    "Crea comunicazione": crea_comunicazione,
    "Visualizza attività": visualizza_attività,
    "Crea team": crea_team,
    "Gestisci utenze": gestisci_utenze,
    "Visualizza team": visualizza_team,
    "Il mio team": team
}

if PAGE_FUNCTIONS.get(st.session_state.current_page):
    PAGE_FUNCTIONS.get(st.session_state.current_page).show()
else:
    page_404.show()
