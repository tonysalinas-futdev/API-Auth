import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

#Funcion para mandar emails
def send_email(subject:str, to:str, from_:str, text:str):
    messagge=EmailMessage()
    messagge["Subject"]=subject
    messagge["From"]=from_
    messagge["To"]=to
    messagge.set_content(text)
    host="smtp.gmail.com"
    port=587

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()  # Seguridad TLS
            
            server.login(os.getenv("USERNAME_EMAIL"),os.getenv("EMAIL_PASSWORD"))
            server.send_message(messagge)
            print("Correo enviado correctamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")