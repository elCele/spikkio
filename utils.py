import streamlit as st
import streamlit_extras as ste

def config_sidebar():
    st.sidebar.image(image = "./img/SPIKKIO_gestionale.png")

    st.sidebar.write("")    # spacing
    st.sidebar.write("")
    st.sidebar.write("")

    if st.session_state.logged:

        st.sidebar.button(label = "Homepage", use_container_width = True, icon = "🏠", on_click = lambda: st.session_state.update(current_page = "Homepage"))

        with st.sidebar.expander(label = "Anagrafiche", icon = "👥"):
            st.button(label = "Inserisci anagrafica", use_container_width = True, icon = "➕", on_click = lambda: st.session_state.update(current_page = "Inserisci anagrafica"))
            st.button(label = "Visualizza soci", use_container_width = True, icon = "🔍")

        with st.sidebar.expander(label = "Tessere", icon = "🪪"):
            st.button(label = "Visualizza tessere", use_container_width = True, icon = "🔍")
            st.button(label = "Inserisci tipo tessera", use_container_width = True, icon = "➕")
            st.write("")    # spacing
            st.button(label = "Visualizza qualifiche", use_container_width = True, icon = "🔍")
            st.button(label = "Inserisci tipo qualifica", use_container_width = True, icon = "➕")

        with st.sidebar.expander(label = "Direttivo", icon = "📄"):
            st.button(label = "Visualizza riunioni direttivo", use_container_width = True, icon = "🔍")
            st.button(label = "Inserisci presenze direttivo", use_container_width = True, icon = "📝")
            st.button(label = "Programma riunione direttivo", use_container_width = True, icon = "➕")

        with st.sidebar.expander(label = "Assemblea", icon = "📣"):
            st.button(label = "Visualizza riunioni assemblea", use_container_width = True, icon = "🔍")
            st.button(label = "Inserisci presenze assemblea", use_container_width = True, icon = "📝")
            st.button(label = "Programma riunione assemblea", use_container_width = True, icon = "➕")

        with st.sidebar.expander(label = "Enti", icon = "🏢"):
            st.button(label = "Inserisci ente", use_container_width = True, icon = "➕")
            st.button(label = "Visualizza enti", use_container_width = True, icon = "🔍")
            st.write("")
            st.button(label = "Inserisci affiliazione", use_container_width = True, icon = "➕")
            st.button(label = "Visualizza affiliazioni", use_container_width = True, icon = "🔍")

        with st.sidebar.expander(label = "Attività", icon = "⚡"):
            st.button(label = "Programma attività", use_container_width = True, icon = "➕")
            st.button(label = "Visualizza attività", use_container_width = True, icon = "🔍")
            st.button(label = "Gestisci prenotazioni attività", use_container_width = True, icon = "📝")

    else:
        st.sidebar.button(label = "Login", use_container_width = True, icon = "🔑")

province_sigle = [
    "AG", "AL", "AN", "AO", "AR", "AP", "AT", "AV", "BA", "BT", "BL", "BN",
    "BG", "BI", "BO", "BZ", "BS", "BR", "CA", "CL", "CB", "CI", "CE", "CT",
    "CZ", "CH", "CO", "CS", "CR", "KR", "CN", "EN", "FM", "FE", "FI", "FG",
    "FC", "FR", "GE", "GO", "GR", "IM", "IS", "SP", "AQ", "LT", "LE", "LC",
    "LI", "LO", "LU", "MC", "MN", "MS", "MT", "VS", "ME", "MI", "MO", "MB",
    "NA", "NO", "NU", "OG", "OT", "OR", "PD", "PA", "PR", "PV", "PG", "PU",
    "PE", "PC", "PI", "PT", "PN", "PZ", "PO", "RG", "RA", "RC", "RE", "RI",
    "RN", "RM", "RO", "SA", "SS", "SV", "SI", "SR", "SO", "TA", "TE", "TR",
    "TO", "TP", "TN", "TV", "TS", "UD", "VA", "VE", "VB", "VC", "VR", "VV",
    "VI", "VT"
]

    