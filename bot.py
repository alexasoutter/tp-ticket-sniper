import requests
from bs4 import BeautifulSoup
import os

# CONFIG
FIXR_URL = "https://fixr.co/organiser/timepiece"
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
TARGETS = ["Wednesday", "Friday", "Saturday"]

def check():
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(FIXR_URL, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    # Logic: Look for any link that isn't 'Coming Soon'
    links = soup.find_all('a', href=True)
    for link in links:
        txt = link.get_text().strip()
        if any(day in txt for day in TARGETS):
            # If it has a link but doesn't say "Coming Soon" or "Sold Out"
            if "Coming Soon" not in txt and "Sold Out" not in txt:
                url = link['href']
                full_url = url if url.startswith('http') else f"https://fixr.co{url}"
                requests.post(WEBHOOK, json={"content": f"🚨 **DROP DETECTED!**\n{txt}\n{full_url}\n@everyone"})
                print(f"Found: {txt}")

if __name__ == "__main__":
    check()
