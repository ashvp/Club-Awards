import re
import pandas as pd
import numpy as np
from datetime import datetime
from math import log2
import os
import glob

# Define the different WhatsApp chat export formats.
# Each format has a regex pattern, a date parser, and group indices for user/message.
CHAT_FORMATS = [
    {
        # Format 1: [DD/MM/YYYY, HH:MM:SS AM/PM] User: Message
        "pattern": re.compile(r"^\[(\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}:\d{2} (?:AM|PM|am|pm))\] ([^:]+): (.*)$"),
        "date_parser": lambda m: datetime.strptime(m.group(1), "%d/%m/%Y, %I:%M:%S %p"),
        "user_group": 2, "msg_group": 3,
        "pre_process": lambda line: line.replace('\u202f', ' ')
    },
    {
        # Format 2: DD/MM/YY, HH:MM - User: Message (24h format)
        "pattern": re.compile(r"^(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}) - ([^:]+): (.*)$"),
        "date_parser": lambda m: datetime.strptime(f"{m.group(1)}, {m.group(2)}", "%d/%m/%y, %H:%M"),
        "user_group": 3, "msg_group": 4,
        "pre_process": None
    },
    {
        # Format 3: DD/MM/YY, HH:MM AM/PM - User: Message
        "pattern": re.compile(r"^(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2} (?:am|pm|AM|PM)) - ([^:]+): (.*)$"),
        "date_parser": lambda m: datetime.strptime(f"{m.group(1)}, {m.group(2)}", "%d/%m/%y, %I:%M %p"),
        "user_group": 3, "msg_group": 4,
        "pre_process": None
    }
]

def analyze_chat(chat_file_path):
    """
    Analyzes a single WhatsApp chat file to calculate engagement metrics.
    It automatically detects the chat format for each line.
    """
    rows = []
    try:
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
                            break  # Move to next line once format is matched
                        except (ValueError, IndexError):
                            # This format's pattern matched, but parsing failed. Try next format.
                            continue
    except FileNotFoundError:
        print(f"Error: File not found at {chat_file_path}")
        return None

    if not rows:
        return None

    df = pd.DataFrame(rows, columns=["Datetime", "User", "Message"])
    df["Date"] = df["Datetime"].dt.date

    # 1. Activity: Average number of messages per day.
    activity = df.groupby("Date").size().mean() if not df.empty else 0

    # 2. Participation: Entropy of messages per user, normalized.
    user_counts = df["User"].value_counts()
    if not user_counts.empty:
        total_msgs = user_counts.sum()
        probs = user_counts / total_msgs
        entropy = -(probs * np.log2(probs)).sum()
        max_entropy = log2(len(user_counts)) if len(user_counts) > 1 else 1
        participation = entropy / max_entropy if max_entropy > 0 else 0
    else:
        participation = 0

    # 3. Responsiveness: Inverse of the average reply delay in minutes.
    df_sorted = df.sort_values("Datetime").reset_index(drop=True)
    delays = []
    for i in range(1, len(df_sorted)):
        if df_sorted.loc[i, "User"] != df_sorted.loc[i-1, "User"]:
            delta = (df_sorted.loc[i, "Datetime"] - df_sorted.loc[i-1, "Datetime"]).total_seconds() / 60
            if 0 < delta < 180:  # Only consider replies within 3 hours
                delays.append(delta)
    responsiveness = 1 / (1 + np.mean(delays)) if delays else 0.5

    # 4. Sustainability: Consistency of weekly activity.
    if not df.empty:
        weekly = df.groupby(pd.Grouper(key="Datetime", freq="W")).size()
        sustainability = 1 / (1 + weekly.std()) if len(weekly) > 1 else 1
    else:
        sustainability = 0

    # Club Engagement Index (CEI): Weighted average of the metrics.
    cei = (0.4 * activity + 0.3 * participation + 0.2 * responsiveness + 0.1 * sustainability)

    # Normalize CEI to a 5-star rating
    if cei > 100: rating = "⭐⭐⭐⭐⭐"
    elif cei > 50: rating = "⭐⭐⭐⭐"
    elif cei > 20: rating = "⭐⭐⭐"
    elif cei > 10: rating = "⭐⭐"
    else: rating = "⭐"

    club_name = os.path.basename(chat_file_path).replace(".txt", "")
    
    return {
        "Club": club_name,
        "Activity (msgs/day)": activity,
        "Participation": participation,
        "Responsiveness": responsiveness,
        "Sustainability": sustainability,
        "CEI": cei,
        "Rating": rating
    }

def main():
    """
    Main function to find all chat files, analyze them, and save the
    results to a CSV file.
    """
    script_dir = os.path.dirname(__file__)
    whatsapp_dir = os.path.abspath(os.path.join(script_dir, "..", "whatsapp"))
    output_csv_path = os.path.abspath(os.path.join(script_dir, "..", "club_engagement_analysis.csv"))
    
    chat_files = glob.glob(os.path.join(whatsapp_dir, "*.txt"))
    
    all_metrics = []
    for chat_file in chat_files:
        print(f"Analyzing {os.path.basename(chat_file)}...")
        metrics = analyze_chat(chat_file)
        if metrics:
            all_metrics.append(metrics)

    if not all_metrics:
        print("No chat files found or processed. Exiting.")
        return

    df_all = pd.DataFrame(all_metrics)
    df_all = df_all.sort_values("CEI", ascending=False).reset_index(drop=True)
    
    df_all.to_csv(output_csv_path, index=False)
    
    print("\n📊 Club Engagement Report")
    print(df_all.to_string())
    print(f"\n✅ Saved detailed analysis to {output_csv_path}")

if __name__ == "__main__":
    main()