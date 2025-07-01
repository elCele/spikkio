import streamlit as st
from sqlalchemy import create_engine
import bcrypt
from sqlalchemy import text
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ------------------------ Inizializzazione variabili di stato ------------------------

db_username = st.secrets["DB_USERNAME"]

ss_variables = {
    "engine": create_engine(f"mysql+mysqlconnector://{db_username}:@localhost/SPIKKIO"),
    "current_page": "Log in",
    "logged": False,
    "user": "",
    "role": []
}

def initialize_var():
    for var in ss_variables:
        if var not in st.session_state:
            st.session_state[var] = ss_variables[var]

# ------------------------ Log out ------------------------

def log_out():
    st.session_state.logged = False
    st.session_state.user = ""
    st.session_state.role = []
    st.session_state.current_page = "Log in"

# ------------------------ Gestione della navigazione ------------------------
    # Ogni "pagina" avrà questa configurazione nella sidebar per la navigazione tra pagine

def config_sidebar():
    st.sidebar.image(image = "./img/SPIKKIO_gestionale.png")

    st.sidebar.write("")    # spacing

    if st.session_state.logged:

        st.sidebar.subheader(f":red[User:] {st.session_state.user}")
        st.sidebar.subheader(f":red[Qualifica:] ")
        st.sidebar.subheader(f":red[Ruolo:] {', '.join(st.session_state.role)}", divider = "red")

        st.sidebar.button(label = "Homepage", use_container_width = True, icon = "🏠", on_click = lambda: st.session_state.update(current_page = "Homepage"))

        with st.sidebar.expander(label = "Anagrafiche", icon = "👥"):
            st.button(label = "Inserisci anagrafica", use_container_width = True, icon = "➕", on_click = lambda: st.session_state.update(current_page = "Inserisci anagrafica"))
            st.button(label = "Visualizza soci", use_container_width = True, icon = "🔍", on_click = lambda: st.session_state.update(current_page = "Visualizza soci"))
            st.button(label = "Tesseramento", use_container_width = True, icon = "🪪", on_click = lambda: st.session_state.update(current_page = "Tesseramento"))
            st.button(label = "Visualizza tesserati", use_container_width = True, icon = "🔍")

        with st.sidebar.expander(label = "Tessere", icon = "🪪"):
            st.button(label = "Inserisci tipo tessera", use_container_width = True, icon = "➕")
            st.button(label = "Inserisci tipo qualifica", use_container_width = True, icon = "➕")
            st.button(label = "Visualizza qualifiche", use_container_width = True, icon = "🔍")

        with st.sidebar.expander(label = "Direttivo", icon = "📄"):
            st.button(label = "Programma riunione direttivo", use_container_width = True, icon = "➕")
            st.button(label = "Visualizza riunioni direttivo", use_container_width = True, icon = "🔍")
            st.button(label = "Inserisci presenze direttivo", use_container_width = True, icon = "📝")

        with st.sidebar.expander(label = "Assemblea", icon = "📣"):
            st.button(label = "Programma riunione assemblea", use_container_width = True, icon = "➕")
            st.button(label = "Visualizza riunioni assemblea", use_container_width = True, icon = "🔍")
            st.button(label = "Inserisci presenze assemblea", use_container_width = True, icon = "📝")

        with st.sidebar.expander(label = "Enti", icon = "🏢"):
            st.button(label = "Inserisci ente", use_container_width = True, icon = "➕")
            st.button(label = "Visualizza enti", use_container_width = True, icon = "🔍")
            st.button(label = "Inserisci affiliazione", use_container_width = True, icon = "➕")
            st.button(label = "Visualizza affiliazioni", use_container_width = True, icon = "🔍")

        with st.sidebar.expander(label = "Attività", icon = "⚡"):
            st.button(label = "Programma attività", use_container_width = True, icon = "➕")
            st.button(label = "Visualizza attività", use_container_width = True, icon = "🔍")
            st.button(label = "Gestisci prenotazioni attività", use_container_width = True, icon = "📝")

        with st.sidebar.expander(label = "Profilo", icon = "👤"):
            st.button(label = "Cambia credenziali", use_container_width = True, icon = "🔄️", on_click = lambda: st.session_state.update(current_page = "Cambia credenziali"))

        st.sidebar.button(label = "Log out", use_container_width = True, on_click = log_out, type = "primary")

    else:
        if st.session_state.current_page == "Log in":
            st.sidebar.button(label = "Login", use_container_width = True, icon = "🔑")
        elif st.session_state.current_page == "Cambia credenziali":
            st.sidebar.button(label = "Cambia credenziali", use_container_width = True, icon = "🔄️")

# ------------------------ Crittazione delle password ------------------------

def hash_password(password):
    # Genera un salt (valore casuale che rende ogni hash unico)
    salt = bcrypt.gensalt()
    # Calcola l'hash
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Ritorna l'hash come stringa decodificata
    return hashed.decode('utf-8')

# ------------------------ Update dello username ------------------------

def update_username(old_username, new_username):
    query = text("UPDATE TBL_UTENTI SET Username = :new_username WHERE Username = :old_username")
    with st.session_state.engine.connect() as conn:
        conn.execute(query, {"new_username": new_username, "old_username": old_username})
        conn.commit()

# ------------------------ Update della password ------------------------

def update_password(username, plain_password):
    hashed = hash_password(plain_password)
    query = text("UPDATE TBL_UTENTI SET Password = :hashed WHERE Username = :username")
    with st.session_state.engine.connect() as conn:
        conn.execute(query, {"hashed": hashed, "username": username})
        conn.commit()

# ------------------------ Invio email ------------------------

def send_email(subject, body, to_email, from_email, from_password, smtp_server = 'smtp.gmail.com', smtp_port = 587):
    try:
        # Crea il messaggio
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attacca il corpo del messaggio
        msg.attach(MIMEText(body, 'plain'))

        # Connessione al server SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Abilita la crittografia

        # Login
        server.login(from_email, from_password)

        # Invia la mail
        server.send_message(msg)

        # Chiude la connessione
        server.quit()

        print(f"Email inviata correttamente a {to_email}")
    except Exception as e:
        print(f"Errore durante l'invio dell'email: {e}")
