import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#user credentials:
SENDER_EMAIL="vinayworkpvk@gmail.com"
PASSKEY="tcmb hgjv akrn jivx"

#stmp server
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

#email send function defination
def emailSend(to_email:str, subject:str, body:str):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['TO'] = to_email
        msg['Subject']=subject
        msg.attach(MIMEText(body,"plain"))

        #server connection
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls() # start server scurly
        server.login(SENDER_EMAIL, PASSKEY) #login to  server
        server.sendmail(from_addr=SENDER_EMAIL, to_addrs=to_email, msg=msg.as_string())

        server.quit()
    except Exception as e:
        return f"Something wrong in sending mail:{e}"
