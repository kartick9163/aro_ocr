import smtplib, socket, base64, requests, datetime, string, random, re, os, json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def ip4():
    ip_address = socket.gethostbyname(socket.gethostname())
    return(ip_address)


def text_to_base64(text):
    text_bytes = text.encode('utf-8')
    base64_bytes = base64.b64encode(text_bytes)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string

def base64_to_text(base64_string):
    base64_bytes = base64_string.encode('utf-8')
    text_bytes = base64.b64decode(base64_bytes)
    text = text_bytes.decode('utf-8')
    return text


def send_email(sender_email, receiver_email, subject, name):
    try:
        bs64 = text_to_base64(receiver_email)        
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        body = f"""
                  <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Confirm Your Account</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f9f9f9;
                    margin: 0;
                    padding: 0;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 20px auto;
                    background-color: #ffffff;
                    padding: 20px;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    text-align: center;
                }}
                .header img {{
                    width: 150px;
                    margin-bottom: 20px;
                }}
                .content {{
                    text-align: left;
                    margin: 0 20px;
                }}
                .content p {{
                    font-size: 16px;
                    line-height: 1.5;
                    color: #333;
                }}
                .button-container {{
                    margin: 20px 0;
                }}
                .activate-button {{
                    background-color: #24c9d4;
                    color: #ffffff;
                    text-decoration: none;
                    padding: 12px 20px;
                    border-radius: 5px;
                    font-size: 16px;
                    display: inline-block;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    color: #666;
                }}
                .footer a {{
                    color: #0066cc;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                
                <h1>Please confirm your account</h1>
                <div class="content">
                    <p>Hello, <strong>{name}</strong>,</p>
                    <p>Activate your account by following the link below to confirm your email address.</p>
                </div>
                <div class="button-container">
                    <a href="http://{ip4()}:8000/api/email_vrfy?uid={bs64}" class="activate-button" target="_blank">
                        Activate my account
                    </a>
                </div>
                <div class="content">
                    
                </div>
                
            </div>
        </body>
        </html>
        """
        # app_pwd = 'bkaz vfrf pelh rraf'  #for kartickdutta.files@gmail.com
        app_pwd = 'xmpi bwfo kvce awhw'  # for kartickdutta2153@gmail.com        
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)  
        server.starttls()  
        server.login(sender_email, app_pwd)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
    

def generate_api_key():
    characters = string.ascii_letters + string.digits  
    length  = 33
    random_text = ''.join(random.choice(characters) for _ in range(length))
    return random_text

