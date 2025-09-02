import os, email
from bs4 import BeautifulSoup
import pandas as pd

# folder where you saved .eml attachments
EML_FOLDER = "mails"

data = []

for filename in os.listdir(EML_FOLDER):
    if filename.endswith(".eml"):
        filepath = os.path.join(EML_FOLDER, filename)
        with open(filepath, "rb") as f:
            raw_msg = email.message_from_binary_file(f)

        subject = raw_msg.get("subject", "")
        sender = raw_msg.get("from", "")
        date = raw_msg.get("date", "")

        body = ""

        if raw_msg.is_multipart():
            parts = []
            for part in raw_msg.walk():
                ctype = part.get_content_type()
                disp = str(part.get("Content-Disposition"))

                # skip attachments
                if "attachment" in disp:
                    continue

                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        text = payload.decode(errors="ignore")
                        if ctype == "text/plain":
                            parts.append(text)
                        elif ctype == "text/html" and not parts:  # fallback
                            soup = BeautifulSoup(text, "html.parser")
                            parts.append(soup.get_text())
                except:
                    continue
            body = "\n".join(parts).strip()
        else:
            # single-part email
            payload = raw_msg.get_payload(decode=True)
            if payload:
                text = payload.decode(errors="ignore")
                if raw_msg.get_content_type() == "text/html":
                    soup = BeautifulSoup(text, "html.parser")
                    body = soup.get_text()
                else:
                    body = text

        data.append({
            "Subject": subject,
            "Sender": sender,
            "Date": date,
            "Body": body.strip()
        })

df = pd.DataFrame(data)
df.to_csv("2024_full_mails.csv", index=False, encoding="utf-8")

print(f"✅ Extracted {len(df)} mails from .eml files → saved to clubs_emails_from_eml.csv")
print(df.iloc[0]["Body"])