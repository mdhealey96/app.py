import streamlit as st
import pandas as pd
import requests
from urllib.parse import urljoin
import time
import sys
import subprocess

# Ensure dependencies are installed
try:
    import bs4
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "beautifulsoup4"], check=True)
    import bs4

from bs4 import BeautifulSoup
from requests_html import HTMLSession

def get_events_from_website(website_url):
    """Scrapes the given website for event listings."""
    try:
        session = HTMLSession()
        response = session.get(website_url)
        response.html.render(timeout=20)  # Render JavaScript if needed
        
        soup = BeautifulSoup(response.html.html, 'html.parser')
        events = []
        
        for event_section in soup.find_all(['article', 'div'], class_=lambda x: x and 'event' in x.lower()):
            event_name = event_section.find(['h2', 'h3', 'h4'])
            date = event_section.find('time')
            link = event_section.find('a', href=True)
            
            events.append({
                'Event Name': event_name.text.strip() if event_name else 'N/A',
                'Start Date': date.text.strip() if date else 'N/A',
                'Time': 'N/A',
                'End Date': 'N/A',
                'Link': urljoin(website_url, link['href']) if link else website_url
            })
        
        return events
    except Exception as e:
        return [{'Event Name': 'Error fetching events', 'Start Date': str(e), 'Time': 'N/A', 'End Date': 'N/A', 'Link': website_url}]

# Streamlit UI
st.title("NYC Events Web Scraper")
uploaded_file = st.file_uploader("Upload CSV with Organization Websites", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if df.shape[1] < 2:
        st.error("CSV format should have Organization Name and Website URL")
    else:
        df.columns = ['Organization', 'Website']
        results = []
        
        for _, row in df.iterrows():
            st.write(f"Scraping: {row['Website']}")
            events = get_events_from_website(row['Website'])
            for event in events:
                event['Organization'] = row['Organization']
                results.append(event)
            time.sleep(2)  # Avoid overloading servers
        
        results_df = pd.DataFrame(results)
        st.write(results_df)
        st.download_button("Download Events CSV", results_df.to_csv(index=False), file_name="nyc_events.csv")