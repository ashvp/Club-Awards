import os
import email
import subprocess
import glob
import json
import re
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup
import numpy as np

# --- Email Scraping Service ---

def scrape_emails():
    """
    Reads .eml files from the 'mails' directory, parses them, and saves the content to a CSV file.
    Returns the path to the output CSV.
    """
    print("Starting email scraping service...")
    # Assuming the server is run from the 'backend' directory
    eml_folder = "mails"
    output_csv = "2024_full_mails.csv"

    if not os.path.isdir(eml_folder):
        raise FileNotFoundError(f"The directory '{eml_folder}' was not found.")

    data = []
    for filename in os.listdir(eml_folder):
        if filename.endswith(".eml"):
            filepath = os.path.join(eml_folder, filename)
            with open(filepath, "rb") as f:
                raw_msg = email.message_from_binary_file(f)

            subject = raw_msg.get("subject", "")
            sender = raw_msg.get("from", "")
            date = raw_msg.get("date", "")
            body = ""

            if raw_msg.is_multipart():
                for part in raw_msg.walk():
                    if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                        body = part.get_payload(decode=True).decode(errors="ignore").strip()
                        break # Take the first plain text part
            else:
                payload = raw_msg.get_payload(decode=True)
                if payload:
                    body = payload.decode(errors="ignore").strip()
            
            # Basic HTML cleanup if body is still HTML
            if "<html" in body.lower():
                body = BeautifulSoup(body, "html.parser").get_text()

            data.append({"Subject": subject, "Sender": sender, "Date": date, "Body": body})

    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"Email scraping complete. Saved {len(df)} emails to {output_csv}")
    return os.path.abspath(output_csv)

# --- Instagram Scraping Service ---

def scrape_instagram_profile(username: str):
    """
    Runs the instaScrapper.py script as a subprocess for the given username.
    Returns the content of the generated JSON file.
    """
    print(f"Starting Instagram scraping service for {username}...")
    script_path = os.path.join("utils", "instaScrapper.py")
    
    # Run the script from the 'backend' directory context
    process = subprocess.run(
        ["python", script_path, username],
        capture_output=True, text=True, check=False, cwd=os.getcwd()
    )

    if process.returncode != 0:
        print("Instagram scraper script failed.")
        raise Exception(f"InstaScrapper Error: {process.stderr}")

    print("Instagram scraper script finished.")
    # Find the output file created by the script
    search_pattern = f"{username}_insta_data_*.json"
    list_of_files = glob.glob(search_pattern)
    if not list_of_files:
        raise FileNotFoundError("Scraper output file not found.")

    latest_file = max(list_of_files, key=os.path.getctime)
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- WhatsApp Analysis Service ---
# Note: This is the logic from whatsappAnalyser.py, adapted for service use.

CHAT_FORMATS = [
    { "pattern": re.compile(r"^\[(\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}:\d{2} (?:AM|PM|am|pm))\] ([^:]+): (.*)$" ), "date_parser": lambda m: datetime.strptime(m.group(1), "%d/%m/%Y, %I:%M:%S %p"), "user_group": 2, "msg_group": 3, "pre_process": lambda line: line.replace('\u202f', ' ')},
    { "pattern": re.compile(r"^(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}) - ([^:]+): (.*)$" ), "date_parser": lambda m: datetime.strptime(f"{m.group(1)}, {m.group(2)}", "%d/%m/%y, %H:%M"), "user_group": 3, "msg_group": 4, "pre_process": None},
    { "pattern": re.compile(r"^(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2} (?:am|pm|AM|PM)) - ([^:]+): (.*)$" ), "date_parser": lambda m: datetime.strptime(f"{m.group(1)}, {m.group(2)}", "%d/%m/%y, %I:%M %p"), "user_group": 3, "msg_group": 4, "pre_process": None}
]

def _analyze_chat_file(chat_file_path):
    rows = []
    with open(chat_file_path, "r", encoding="utf-8") as f:
        for line in f:
            for fmt in CHAT_FORMATS:
                processed_line = fmt["pre_process"](line) if fmt["pre_process"] else line
                match = fmt["pattern"].match(processed_line.strip())
                if match:
                    try:
                        dt = fmt["date_parser"](match)
                        user = match.group(fmt["user_group"])
                        msg = match.group(fmt["msg_group"])
                        rows.append([dt, user, msg])
                        break
                    except (ValueError, IndexError):
                        continue
    if not rows:
        return None

    df = pd.DataFrame(rows, columns=["Datetime", "User", "Message"])
    df["Date"] = df["Datetime"].dt.date
    activity = df.groupby("Date").size().mean() if not df.empty else 0
    user_counts = df["User"].value_counts()
    if not user_counts.empty:
        total_msgs = user_counts.sum()
        probs = user_counts / total_msgs
        entropy = -(probs * np.log2(probs)).sum()
        max_entropy = np.log2(len(user_counts)) if len(user_counts) > 1 else 1
        participation = entropy / max_entropy if max_entropy > 0 else 0
    else:
        participation = 0
    df_sorted = df.sort_values("Datetime").reset_index(drop=True)
    delays = []
    for i in range(1, len(df_sorted)):
        if df_sorted.loc[i, "User"] != df_sorted.loc[i-1, "User"]:
            delta = (df_sorted.loc[i, "Datetime"] - df_sorted.loc[i-1, "Datetime"]).total_seconds() / 60
            if 0 < delta < 180:
                delays.append(delta)
    responsiveness = 1 / (1 + np.mean(delays)) if delays else 0.5
    if not df.empty:
        weekly = df.groupby(pd.Grouper(key="Datetime", freq="W")).size()
        sustainability = 1 / (1 + weekly.std()) if len(weekly) > 1 else 1
    else:
        sustainability = 0
    cei = (0.4 * activity + 0.3 * participation + 0.2 * responsiveness + 0.1 * sustainability)
    if cei > 100: rating = "⭐⭐⭐⭐⭐"
    elif cei > 50: rating = "⭐⭐⭐⭐"
    elif cei > 20: rating = "⭐⭐⭐"
    elif cei > 10: rating = "⭐⭐"
    else: rating = "⭐"
    return {"Club": os.path.basename(chat_file_path).replace(".txt", ""), "Activity (msgs/day)": activity, "Participation": participation, "Responsiveness": responsiveness, "Sustainability": sustainability, "CEI": cei, "Rating": rating}

def analyze_whatsapp_chats():
    """
    Finds all chat files in the 'whatsapp' directory, analyzes them, and saves to a CSV.
    Returns the content of the CSV as a JSON array.
    """
    print("Starting WhatsApp analysis service...")
    whatsapp_dir = "whatsapp"
    output_csv = "club_engagement_analysis.csv"

    if not os.path.isdir(whatsapp_dir):
        raise FileNotFoundError(f"The directory '{whatsapp_dir}' was not found.")

    chat_files = glob.glob(os.path.join(whatsapp_dir, "*.txt"))
    all_metrics = []
    for chat_file in chat_files:
        metrics = _analyze_chat_file(chat_file)
        if metrics:
            all_metrics.append(metrics)

    if not all_metrics:
        return []

    df_all = pd.DataFrame(all_metrics).sort_values("CEI", ascending=False).reset_index(drop=True)
    df_all.to_csv(output_csv, index=False)
    print(f"WhatsApp analysis complete. Saved results to {output_csv}")
    return df_all.to_dict(orient='records')
