from config import Config
from sendgrid import SendGridAPIClient
from flask import render_template
from sendgrid.helpers.mail import (
    Mail,
    From,
    To,
    Bcc,
    Subject,
    Content,
    MimeType,
    ReplyTo,
)


def sendEmail(
    subject,
    content,
    to_emails,
    reply_to="shyamalruparel1991@gmail.com",
    from_email="shy@ti4.nyc",
):
    message = Mail()
    message.to = [
        To("shyamalruparel1991@gmail.com", "Shy", p=0),
        To("wsireland@gmail.com", "Sean", p=0),
    ]
    bcc = []
    for email in to_emails:
        if (
            email[0] == "shyamalruparel1991@gmail.com"
            or email[0] == "wsireland@gmail.com"
        ):
            continue
        bcc.append(Bcc(email[0], email[1], p=0))
    message.bcc = bcc
    message.subject = Subject(subject, p=0)
    message.content = Content(MimeType.text, content)
    message.reply_to = ReplyTo(reply_to, reply_to.split("@")[0])
    message.from_email = From(from_email, from_email.split("@")[0])

    try:
        sendgrid_client = SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)
        response = sendgrid_client.send(message)
    except Exception as e:
        print(e.body)
    return response.status_code


def sendPasswordResetEmail(user):
    token = user.get_reset_password_token()
    message = Mail()
    message.to = [
        To(user.email, user.username, p=0),
    ]
    message.subject = Subject("[TI4.NYC] Reset your password]", p=0)
    message.from_email = From("noreply@ti4.nyc", "noreply")
    message.content = Content(
        MimeType.text,
        render_template("email/reset_password.txt", user=user, token=token),
    )
    message.content = Content(
        MimeType.html,
        render_template("email/reset_password.html", user=user, token=token),
    )
    try:
        sendgrid_client = SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)
        response = sendgrid_client.send(message)
    except Exception as e:
        print(e.body)
    return response.status_code
