import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import utils.consts as c
import bcrypt
from sqlalchemy import text
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
import io
import pytz
from icalendar import Calendar, Event
import datetime

# ------------------------ Inizializzazione variabili di stato ------------------------

db_username = st.secrets["DB_USERNAME"]

ss_variables_b1 = {
    "engine": create_engine(f"mysql+mysqlconnector://{db_username}:@localhost/SPIKKIO"),
    "current_page": "Log in",
    "logged": False,
    "user": "",
    "role": "",
    "CF_socio": "",
    "inTeam": False
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
    st.sidebar.image(image = "./img/SPIKKIO_logo_b.png")

    st.sidebar.write("")    # spacing

    if st.session_state.logged:

        st.markdown(c.custom_css, unsafe_allow_html = True)
        with st.sidebar.container(key = 'user_info_container'):
            st.subheader(f"👤 :primary[User:] {st.session_state.user}")
            st.subheader(f"⚙️ :primary[Ruolo:] {st.session_state.role}")

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

# ------------------------ Creazione tessera virtuale ------------------------

def build_tessera(nome_titolare, cognome_titolare, cf_titolare, data_scadenza, cod_tessera):
    sfondo_tessera_path = 'img/card_back.png'
    logo_limone_path = 'img/SPIKKIO_logo.png'

    try:
        sfondo = Image.open(sfondo_tessera_path).convert("RGBA")
        width, height = sfondo.size

        logo = Image.open(logo_limone_path).convert("RGBA")
        logo_height = int(height * 1.2)
        logo = logo.resize((int(logo.width * (logo_height / logo.height)), logo_height), Image.Resampling.LANCZOS)
        logo_x = int(width / 2 - 150)
        logo_y = 30
        sfondo.paste(logo, (logo_x, logo_y), logo)

        buffer_barcode = io.BytesIO()
        Code128 = barcode.get_barcode_class('code128')
        code128_instance = Code128(cod_tessera, writer = ImageWriter())
        code128_instance.write(buffer_barcode)
        buffer_barcode.seek(0)

        barcode_img = Image.open(buffer_barcode).convert("RGBA")

        barcode_target_width = int(width * 0.4)
        barcode_target_height = int(barcode_img.height * (barcode_target_width / barcode_img.width))
        barcode_img = barcode_img.resize((barcode_target_width, barcode_target_height), Image.Resampling.LANCZOS)

        barcode_img = barcode_img.rotate(90, expand = True)

        barcode_x = width - barcode_img.width - 20
        barcode_y = 100
        sfondo.paste(barcode_img, (barcode_x, barcode_y), barcode_img)

        draw = ImageDraw.Draw(sfondo)

        rect_x1, rect_y1 = 10, int(height - 105)
        rect_x2, rect_y2 = int(width / 2 + 20), int(height - 10)
        radius = 15

        fill_color = (256, 256, 256, 200)

        overlay = Image.new('RGBA', sfondo.size, (0,0,0,0))

        draw_overlay = ImageDraw.Draw(overlay)
        draw_overlay.rounded_rectangle((rect_x1, rect_y1, rect_x2, rect_y2), radius = radius, fill = fill_color)

        sfondo.paste(overlay, (0, 0), overlay)

        try:
            font_dati = ImageFont.truetype("fonts/Montserrat-Bold.ttf", 15)
        except IOError:
            font_dati = ImageFont.load_default()

        text_color = (0, 0, 0, 255)

        draw.text((20, height - 95), f"{nome_titolare} {cognome_titolare}", font = font_dati, fill = text_color)
        draw.text((20, height - 65), f"{cf_titolare}", font = font_dati, fill = text_color)
        draw.text((20, height - 35), f"Data scadenza:  {data_scadenza}", font = font_dati, fill = text_color)

        img_buffer = io.BytesIO()
        sfondo.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        return img_buffer

    except FileNotFoundError as e:
        return None
    except Exception as e:
        return None

# ------------------------ Creazione file .ics per inserire evento nel calendario ------------------------

def genera_ics(nome_evento, descrizione, data_evento, ora_inizio, ora_fine, luogo="Luogo da definire"):
    tz = pytz.timezone('Europe/Rome')
    inizio = datetime.datetime.combine(data_evento, (datetime.datetime.min + ora_inizio).time())
    fine = datetime.datetime.combine(data_evento, (datetime.datetime.min + ora_fine).time())

    inizio = tz.localize(inizio)
    fine = tz.localize(fine)

    cal = Calendar()
    event = Event()
    event.add('summary', nome_evento)
    event.add('description', descrizione)
    event.add('dtstart', inizio)
    event.add('dtend', fine)
    event.add('location', luogo)
    event.add('dtstamp', datetime.datetime.now(tz=tz))
    cal.add_component(event)

    return cal.to_ical()
