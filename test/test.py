import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

SUBJECT = "Email Data"

msg = MIMEMultipart()
msg['Subject'] = SUBJECT
msg['From'] = self.EMAIL_FROM
msg['To'] = ', '.join(self.EMAIL_TO)

part = MIMEBase('application', "octet-stream")
part.set_payload(open("text.txt", "rb").read())
encoders.encode_base64(part)

part.add_header('Content-Disposition', 'attachment; filename="text.txt"')

msg.attach(part)