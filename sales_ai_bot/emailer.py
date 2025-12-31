import smtplib
from email.message import EmailMessage
import os

def send_report(pdf_path, to_emails, subject="AI Sales Strategy Report", body=None):
    EMAIL = os.getenv("SMTP_EMAIL")
    PASSWORD = os.getenv("SMTP_PASSWORD")
    if not EMAIL or not PASSWORD:
        raise RuntimeError("SMTP_EMAIL or SMTP_PASSWORD not set in environment")

    msg = EmailMessage()
    msg["From"] = EMAIL
    msg["To"] = ", ".join(to_emails)
    msg["Subject"] = subject

    body = body or (
        "Hello,\n\nPlease find attached your AI Sales Strategy Report.\n\n"
        "This report includes:\n"
        "- Executive KPIs\n- Product & Customer analysis\n- Sales trends & forecast\n- Actionable recommendations\n\n"
        "Regards,\nAI Sales Analytics Team\n"
    )
    msg.set_content(body)

    with open(pdf_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="application",
            subtype="pdf",
            filename=os.path.basename(pdf_path),
        )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)

    return True
