import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import utils.consts as c
import bcrypt
from sqlalchemy import text
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ------------------------ Inizializzazione variabili di stato ------------------------

db_username = st.secrets["DB_USERNAME"]
db_password = st.secrets["DB_PASSWORD"]

ss_variables_b1 = {
    "engine": create_engine(f"mysql+mysqlconnector://{db_username}:{db_password}@100.64.25.18/SPIKKIO"),
    "current_page": "Log in",
    "logged": False,
    "user": "",
    "role": "",
    "CF_socio": "",
}

def initialize_var_batch_1():
    for var, value in ss_variables_b1.items():
        if var not in st.session_state:
            st.session_state[var] = value

def initialize_var_batch_2():
    if "users" not in st.session_state:
        st.session_state["users"] = pd.read_sql("SELECT * FROM TBL_UTENTI", st.session_state.engine)

# ------------------------ Log out ------------------------

def log_out():
    for var in ss_variables_b1:
        st.session_state[var] = ss_variables_b1[var]

    st.session_state["users"] = pd.read_sql("SELECT * FROM TBL_UTENTI", st.session_state.engine)

# ------------------------ Gestione della navigazione ------------------------
    # Ogni "pagina" avrà questa configurazione nella sidebar per la navigazione tra pagine

def config_sidebar():
    st.sidebar.image(image = "./img/SPIKKIO_gestionale.png")

    st.sidebar.write("")    # spacing

    if st.session_state.logged:

        st.sidebar.subheader(f":red[User:] {st.session_state.user}")
        st.sidebar.subheader(f":red[Qualifica:] ")
        st.sidebar.subheader(f":red[Ruolo:] {st.session_state.role}", divider = "red")

        if st.session_state.role in c.users:
            pagine_per_utente = c.users[st.session_state.role]
        else:
            pagine_per_utente = []

        for voce in pagine_per_utente:
            voce.build()

        st.sidebar.button(label = "Log out", use_container_width = True, on_click = log_out, type = "primary")

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
