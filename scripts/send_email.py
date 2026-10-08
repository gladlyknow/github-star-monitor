import os
import smtplib
from email.message import EmailMessage
from pathlib import Path

def main():
    keys = ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "REPORT_EMAIL_TO")
    if any(not os.getenv(k) for k in keys):
        print("Email skipped: configure SMTP_HOST, SMTP_USER, SMTP_PASSWORD, REPORT_EMAIL_TO")
        return
    reports = sorted(Path("reports").glob("*.md"))
    if not reports:
        raise RuntimeError("No Markdown report")
    report = reports[-1]
    message = EmailMessage()
    message["From"] = os.environ["SMTP_USER"]
    message["To"] = os.environ["REPORT_EMAIL_TO"]
    message["Subject"] = "GitHub SaaS intelligence - " + report.stem
    message.set_content(report.read_text(encoding="utf-8"))
    message.add_attachment(report.read_bytes(), maintype="text", subtype="markdown", filename=report.name)
    with smtplib.SMTP_SSL(os.environ["SMTP_HOST"], int(os.getenv("SMTP_PORT", "465")), timeout=30) as client:
        client.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        client.send_message(message)
    print("SMTP accepted report")

if __name__ == "__main__":
    main()
