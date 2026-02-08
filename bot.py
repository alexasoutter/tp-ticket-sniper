import requests
from bs4 import BeautifulSoup
import os
import time

# --- CONFIG ---
FIXR_URL = "https://fixr.co/organiser/timepiece"
WEBHOOK = os.getenv("DISCORD_WEBHOOK")
TARGETS = ["Wednesday", "Friday", "Saturday"]

def check_tickets():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(FIXR_URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # FIXR events are usually inside <a> tags that act as cards
        event_cards = soup.find_all('a', href=True)
        
        for card in event_cards:
            content = card.get_text(separator=" ").strip()
            
            # 1. Filter for your specific days
            if any(day in content for day in TARGETS):
                
                # 2. Check for "Live" indicators
                # We want events that mention a price or 'Book', but NOT 'Coming Soon'
                is_live = ("£" in content or "Book" in content or "From" in content)
                is_placeholder = "Coming Soon" in content or "Sold Out" in content
                
                if is_live and not is_placeholder:
                    event_url = card['href']
                    full_url = event_url if event_url.startswith('http') else f"https://fixr.co{event_url}"
                    
                    # Clean up the name for the alert
                    event_name = content.split('\n')[0].strip()
                    
                    # 3. Send the Alert
                    payload = {
                        "content": f"🚨 **TICKETS DETECTED!** 🚨\n**Event:** {event_name}\n**Link:** {full_url}\n@everyone",
                        "username": "Timepiece Sniper"
                    }
                    requests.post(WEBHOOK, json=payload)
                    print(f"Alert sent for: {event_name}")
                    return # Stop after finding one to avoid spamming

        print("Scan complete: No live tickets found.")
        
    except Exception as e:
        print(f"Error checking FIXR: {e}")

if __name__ == "__main__":
    check_tickets()
