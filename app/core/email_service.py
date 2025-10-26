from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List
from app.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME
)

fm = FastMail(conf)

async def send_password_reset_email(email_to: EmailStr, token: str, username: str):

    reset_url = f"{settings.FRONTEND_RESET_PASSWORD_URL}?token={token}"

    #cuerpo correo
    html_template = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Arial', sans-serif; line-height: 1.6; }}
            .container {{ width: 90%; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            .button {{ background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            p {{ margin-bottom: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h3>Hola, {username}</h3>
            <p>Recibimos una solicitud para restablecer tu contraseña en ZooConnect.</p>
            <p>Si no hiciste esta solicitud, puedes ignorar este correo de forma segura.</p>
            <p>
                Haz clic en el siguiente botón para establecer una nueva contraseña. 
                Este enlace expirará en <strong>{settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES} minutos</strong>.
            </p>
            <p>
                <a href="{reset_url}" class="button">Restablecer Contraseña</a>
            </sppan>
            <p style="margin-top: 30px; font-size: 0.9em; color: #555;">
                Si el botón no funciona, copia y pega esta URL en tu navegador:
                <br>
                <a href="{reset_url}">{reset_url}</a>
            </p>
        </div>
    </body>
    </html>
    """
    message = MessageSchema(
        subject="Restablece tu contraseña de ZooConnect",
        recipients=[email_to],
        body=html_template,
        subtype=MessageType.html
    )

    try:
        await fm.send_message(message)
        print(f"Correo de reseteo enviado a {email_to}")
    except Exception as e:
        print(f"Error al enviar correo: {e}")