from config import Config
import sendgrid
from sendgrid.helpers.mail import *

sg = sendgrid.SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)


def sendEmail(
    subject,
    content,
    reply_to="shy@shyruparel.com",
    from_email="shy@ti4.nyc",
    to_emails=["shy@shyruparel.com"],
):
    from_email = Email(from_email)
    to_list = Personalization()
    for email in to_emails:
        to_list.add_to(Email(email))
    content = Content("text/plain", content)
    mail = Mail(from_email, None, subject, content)
    mail.add_personalization(to_list)
    mail.reply_to = reply_to
    response = sg.client.mail.send.post(request_body=mail.get())
    print(type(response.status_code))
    return response.status_code
