import requests
from bs4 import BeautifulSoup
import os
import time
from datetime import datetime

FIXR_URL = "https://fixr.co/organiser/timepiece"
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
TARGETS = ["Wednesday", "Friday", "Saturday"]

def scan():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        res = requests.get(FIXR_URL, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            txt = link.get_text().strip()
            if any(day in txt for day in TARGETS):
                if "Coming Soon" not in txt and "Sold Out" not in txt:
                    url = link['href']
                    full_url = url if url.startswith('http') else f"https://fixr.co{url}"
                    requests.post(WEBHOOK, json={"content": f"🚨 **DROP!** {txt}\n{full_url}\n@everyone"})
                    return True
        return False
    except:
        return False

if __name__ == "__main__":
    # Check 5 times with 60s gaps. Total run time = ~4 minutes.
    for i in range(5):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Scan {i+1}/5...")
        if scan():
            break # Stop if found
        if i < 4:
            time.sleep(60)
