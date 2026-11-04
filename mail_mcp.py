import os
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, ".env"))

IMAP_SERVER = os.getenv("IMAP_SERVER", "mail.centrumautomatyki.eu")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
SMTP_SERVER = os.getenv("SMTP_SERVER", "mail.centrumautomatyki.eu")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
EMAIL_USER = os.getenv("EMAIL_USER", "lukasz@centrumautomatyki.eu")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

mcp = FastMCP("Roundcube-Mail-MCP")

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

@mcp.tool()
def list_recent_emails(count: int = 10, folder: str = "INBOX") -> str:
    """Pobiera listę najnowszych wiadomości z wybranego folderu (np. INBOX, Sent, Spam)."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select(folder)
        status, messages = mail.search(None, "ALL")
        if status != "OK" or not messages[0]:
            mail.logout()
            return f"Brak wiadomości w folderze {folder}."
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
        return "\n".join(results)
    except Exception as e:
        return f"Błąd pobierania wiadomości: {str(e)}"

@mcp.tool()
def read_email(email_id: str, folder: str = "INBOX") -> str:
    """Odczytuje pełną treść konkretnej wiadomości na podstawie ID."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select(folder)
        status, msg_data = mail.fetch(email_id.encode(), "(RFC822)")
        if status != "OK":
            mail.logout()
            return f"Nie znaleziono wiadomości o ID: {email_id}"
        body = ""
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = decode_header_str(msg.get("Subject", ""))
                from_str = decode_header_str(msg.get("From", ""))
                date_str = msg.get("Date", "")
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                            payload = part.get_payload(decode=True)
                            if payload:
                                body += payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body += payload.decode(msg.get_content_charset() or "utf-8", errors="ignore")
                mail.logout()
                return f"Od: {from_str}\nTemat: {subject}\nData: {date_str}\n\nTreść:\n{body.strip()}"
        mail.logout()
        return "Błąd odczytu treści."
    except Exception as e:
        return f"Błąd odczytu emaila: {str(e)}"

@mcp.tool()
def search_emails(query: str, folder: str = "INBOX", limit: int = 10) -> str:
    """Wyszukuje wiadomości e-mail zawierające podaną frazę (np. nazwę firmy lub nazwisko)."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select(folder)
        status, messages = mail.search(None, f'(OR SUBJECT "{query}" FROM "{query}")')
        if status != "OK" or not messages[0]:
            mail.logout()
            return f"Nie znaleziono wiadomości pasujących do: '{query}'"
        import os
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Ładowanie .env z lokalnej ścieżki (dla uruchomień lokalnych)
script_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(script_dir, ".env"))

IMAP_SERVER = os.getenv("IMAP_SERVER", "mail.centrumautomatyki.eu")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
SMTP_SERVER = os.getenv("SMTP_SERVER", "mail.centrumautomatyki.eu")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
EMAIL_USER = os.getenv("EMAIL_USER", "lukasz@centrumautomatyki.eu")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

mcp = FastMCP("Roundcube-Mail-MCP")

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

@mcp.tool()
def list_recent_emails(count: int = 10, folder: str = "INBOX") -> str:
    """Pobiera listę najnowszych wiadomości z wybranego folderu (np. INBOX, Sent, Spam)."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select(folder)
        status, messages = mail.search(None, "ALL")
        if status != "OK" or not messages[0]:
            mail.logout()
            return f"Brak wiadomości w folderze {folder}."
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
        return "\n".join(results)
    except Exception as e:
        return f"Błąd pobierania wiadomości: {str(e)}"

@mcp.tool()
def read_email(email_id: str, folder: str = "INBOX") -> str:
    """Odczytuje pełną treść konkretnej wiadomości na podstawie ID."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select(folder)
        status, msg_data = mail.fetch(email_id.encode(), "(RFC822)")
        if status != "OK":
            mail.logout()
            return f"Nie znaleziono wiadomości o ID: {email_id}"
        body = ""
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject = decode_header_str(msg.get("Subject", ""))
                from_str = decode_header_str(msg.get("From", ""))
                date_str = msg.get("Date", "")
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                            payload = part.get_payload(decode=True)
                            if payload:
                                body += payload.decode(part.get_content_charset() or "utf-8", errors="ignore")
                else:
                    payload = msg.get_payload(decode=True)
                    if payload:
                        body += payload.decode(msg.get_content_charset() or "utf-8", errors="ignore")
                mail.logout()
                return f"Od: {from_str}\nTemat: {subject}\nData: {date_str}\n\nTreść:\n{body.strip()}"
        mail.logout()
        return "Błąd odczytu treści."
    except Exception as e:
        return f"Błąd odczytu emaila: {str(e)}"

@mcp.tool()
def search_emails(query: str, folder: str = "INBOX", limit: int = 10) -> str:
    """Wyszukuje wiadomości e-mail zawierające podaną frazę."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASSWORD)
        mail.select(folder)
        status, messages = mail.search(None, f'(OR SUBJECT "{query}" FROM "{query}")')
        if status != "OK" or not messages[0]:
            mail.logout()
            return f"Nie znaleziono wiadomości pasujących do: '{query}'"
        mail_ids = messages[0].split()[-limit:]
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
        return "\n".join(results)
    except Exception as e:
        return f"Błąd wyszukiwania: {str(e)}"

@mcp.tool()
def send_email(to_address: str, subject: str, body: str) -> str:
    """Wysyła nową wiadomość e-mail z adresu firmy."""
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = to_address
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        return f"Wiadomość została wysłana do {to_address}."
    except Exception as e:
        return f"Błąd wysyłania emaila: {str(e)}"

if __name__ == "__main__":
    if "PORT" in os.environ:
        # Tryb Railway (Cloud MCP przez SSE dla Gemini)
        port = int(os.environ["PORT"])
        mcp.run(transport="sse", host="0.0.0.0", port=port)
    else:
        # Tryb lokalny macOS (stdio dla Claude Desktop)
        mcp.run()  
