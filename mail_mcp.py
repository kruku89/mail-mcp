import os
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, ".env"))

IMAP_SERVER = os.getenv("IMAP_SERVER", "mail.centrumautomatyki.eu")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
SMTP_SERVER = os.getenv("SMTP_SERVER", "mail.centrumautomatyki.eu")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
EMAIL_USER = os.getenv("EMAIL_USER", "lukasz@centrumautomatyki.eu")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

app = FastAPI(title="Roundcube Mail MCP API")

def decode_header_str(header_value: str) -> str:
    if not header_value:
        return ""
    decoded_list = decode_header(header_value)
    result = ""
    for decoded_string, charset in decoded_list:
        if isinstance(decoded_string, bytes):
            result += decoded_string.decode(charset or "utf-8", errors="ignore")
        else:
            result += str(decoded_string)
    return result

@app.get("/")
def health_check():
    return {"status": "online", "service": "Roundcube-Mail-MCP"}

@app.get("/tools/list_recent_emails")
def api_list_recent_emails(count: int = 10, folder: str = "INBOX"):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select(folder)
        status, messages = mail.search(None, "ALL")
        if status != "OK" or not messages[0]:
            mail.logout()
            return {"result": f"Brak wiadomości w folderze {folder}."}
        mail_ids = messages[0].split()
        recent_ids = mail_ids[-count:]
        recent_ids.reverse()
        results = []
        for mail_id in recent_ids:
            _, msg_data = mail.fetch(mail_id, "(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = decode_header_str(msg.get("Subject", ""))
                    from_str = decode_header_str(msg.get("From", ""))
                    date_str = msg.get("Date", "")
                    results.append(f"ID: {mail_id.decode()}\nOd: {from_str}\nTemat: {subject}\nData: {date_str}\n---")
        mail.logout()
        return {"result": "\n".join(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SearchRequest(BaseModel):
    query: str
    folder: str = "INBOX"
    limit: int = 10

@app.post("/tools/search_emails")
def api_search_emails(req: SearchRequest):
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select(req.folder)
        status, messages = mail.search(None, f'(OR SUBJECT "{req.query}" FROM "{req.query}")')
        if status != "OK" or not messages[0]:
            mail.logout()
            return {"result": f"Nie znaleziono wiadomości pasujących do: '{req.query}'"}
        mail_ids = messages[0].split()[-req.limit:]
        mail_ids.reverse()
        results = []
        for mail_id in mail_ids:
            _, msg_data = mail.fetch(mail_id, "(BODY[HEADER.FIELDS (FROM SUBJECT DATE)])")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = decode_header_str(msg.get("Subject", ""))
                    from_str = decode_header_str(msg.get("From", ""))
                    date_str = msg.get("Date", "")
                    results.append(f"ID: {mail_id.decode()}\nOd: {from_str}\nTemat: {subject}\nData: {date_str}\n---")
        mail.logout()
        return {"result": "\n".join(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
