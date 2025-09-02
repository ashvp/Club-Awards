import requests
import urllib.parse
from bs4 import BeautifulSoup

# target url via scrape.do
targetUrl = urllib.parse.quote("https://www.snuchennai.edu.in/clubs/")
url = "http://api.scrape.do/?url={}&token=73f7c02b36694c8795b7ff0aea5d40b5919ed68fb46".format(targetUrl)

response = requests.get(url)

# parse HTML
soup = BeautifulSoup(response.text, "html.parser")

# extract all <p> tags
paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]

# save to text file
with open("clubs_paragraphs.txt", "w", encoding="utf-8") as f:
    for para in paragraphs:
        if para == "Will Be Updated Soon…":
            continue
        else:
            f.write(para + "\n")

print(f"✅ Extracted {len(paragraphs)} paragraphs → saved to clubs_paragraphs.txt")


