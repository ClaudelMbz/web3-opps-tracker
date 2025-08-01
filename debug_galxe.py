#!/usr/bin/env python3
"""
Debug script to understand why Galxe scraper is returning 0 quests
"""

import requests
from bs4 import BeautifulSoup
import re
import sys
import os

# Add path for galxe_requests import
sys.path.insert(0, os.path.abspath('.'))
from galxe_requests import ScraperAPIBalancer

def debug_galxe_structure():
    """Debug the actual HTML structure returned by Galxe"""
    
    # Initialize balancer to get API key
    balancer = ScraperAPIBalancer()
    account_key = balancer.get_accounts_batch(batch_size=1, url="https://galxe.com/explore?page=1")[0]
    
    print(f"🔍 Debugging Galxe HTML structure with account: {account_key[:8]}...")
    
    # Make request to Galxe
    params = {
        "api_key": account_key,
        "url": "https://galxe.com/explore?page=1",
        "render": "true",
        "timeout": 60000,
        "country_code": "us"
    }
    
    response = requests.get("http://api.scraperapi.com", params=params, timeout=65)
    
    if response.status_code != 200:
        print(f"❌ Request failed: {response.status_code}")
        return
    
    html = response.text
    print(f"✅ Got HTML response: {len(html)} characters")
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Look for the old selectors that are expected
    print("\n=== CHECKING OLD SELECTORS ===")
    old_campaign_items = soup.select("div.campaign-item")
    print(f"div.campaign-item found: {len(old_campaign_items)}")
    
    old_card_titles = soup.select("h5.card-title a")
    print(f"h5.card-title a found: {len(old_card_titles)}")
    
    # Analyze the actual HTML structure
    print("\n=== ANALYZING HTML STRUCTURE ===")
    
    # Look for patterns that might indicate campaigns/projects
    patterns_to_check = [
        'campaign', 'project', 'quest', 'card', 'item', 'opportunity',
        'space', 'community', 'task', 'activity'
    ]
    
    for pattern in patterns_to_check:
        # Check class names
        class_matches = soup.find_all(attrs={"class": re.compile(pattern, re.I)})
        if class_matches:
            print(f"📋 Pattern '{pattern}' in classes: {len(class_matches)} elements")
            # Show first few class names
            classes = [elem.get('class') for elem in class_matches[:3]]
            print(f"   Sample classes: {classes}")
    
    # Look for links that might be campaigns
    print("\n=== LOOKING FOR CAMPAIGN LINKS ===")
    all_links = soup.find_all('a', href=True)
    campaign_links = [link for link in all_links if '/space/' in link['href'] or '/quest/' in link['href'] or '/campaign/' in link['href']]
    print(f"Found {len(campaign_links)} potential campaign links")
    
    if campaign_links:
        print("Sample campaign links:")
        for i, link in enumerate(campaign_links[:5]):
            print(f"  {i+1}. {link['href']} - Text: '{link.get_text().strip()[:50]}...'")
    
    # Look for any structured data
    print("\n=== LOOKING FOR STRUCTURED DATA ===")
    scripts = soup.find_all('script')
    json_scripts = []
    for script in scripts:
        if script.string and ('campaigns' in script.string.lower() or 'projects' in script.string.lower()):
            json_scripts.append(script.string[:200] + "...")
    
    if json_scripts:
        print(f"Found {len(json_scripts)} scripts with campaign data")
        for i, script in enumerate(json_scripts[:2]):
            print(f"Script {i+1}: {script}")
    
    # Save a sample of the HTML for manual inspection
    with open('galxe_debug_sample.html', 'w', encoding='utf-8') as f:
        f.write(html[:10000])  # First 10k characters
    print(f"\n💾 Saved first 10k characters to 'galxe_debug_sample.html'")
    
    # Try to find the actual structure being used
    print("\n=== LOOKING FOR CURRENT STRUCTURE ===")
    
    # Modern web apps often use specific patterns
    possible_selectors = [
        "div[data-testid*='campaign']",
        "div[data-testid*='project']", 
        "div[class*='Campaign']",
        "div[class*='Project']",
        "div[class*='Card']",
        ".space-card",
        ".project-card", 
        ".campaign-card",
        "[data-cy*='campaign']",
        "[data-cy*='project']"
    ]
    
    for selector in possible_selectors:
        try:
            elements = soup.select(selector)
            if elements:
                print(f"✅ Found {len(elements)} elements with selector: {selector}")
                # Show sample element
                if elements[0]:
                    sample_classes = elements[0].get('class', [])
                    sample_attrs = {k: v for k, v in elements[0].attrs.items() if k in ['class', 'data-testid', 'data-cy']}
                    print(f"   Sample element attributes: {sample_attrs}")
        except Exception as e:
            continue

if __name__ == "__main__":
    debug_galxe_structure()
