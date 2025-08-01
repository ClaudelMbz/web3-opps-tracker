#!/usr/bin/env python3
"""
Simple debug script to check Galxe HTML structure
"""

import requests
from bs4 import BeautifulSoup
import re

def debug_galxe_simple():
    """Debug Galxe structure using direct request (for testing purposes)"""
    
    print("🔍 Fetching Galxe page to analyze structure...")
    
    # Simple direct request to see what we get
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get("https://galxe.com/explore", headers=headers, timeout=30)
        print(f"✅ Got response: {response.status_code}, {len(response.text)} characters")
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        # Save the HTML for inspection
        with open('galxe_simple_debug.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("💾 Saved full HTML to 'galxe_simple_debug.html'")
        
        # Check old selectors
        print("\n=== CHECKING OLD SELECTORS ===")
        old_campaign_items = soup.select("div.campaign-item")
        print(f"div.campaign-item found: {len(old_campaign_items)}")
        
        # Look for modern patterns
        print("\n=== MODERN PATTERNS ===")
        
        # Check for any divs with interesting classes
        all_divs = soup.find_all('div', class_=True)
        interesting_classes = []
        
        for div in all_divs[:100]:  # Check first 100 divs
            classes = div.get('class', [])
            class_str = ' '.join(classes)
            if any(keyword in class_str.lower() for keyword in ['card', 'item', 'project', 'space', 'campaign']):
                interesting_classes.append(class_str)
        
        if interesting_classes:
            print("Found interesting div classes:")
            for cls in set(interesting_classes[:10]):
                print(f"  - {cls}")
        
        # Look for links to spaces/projects
        print("\n=== LOOKING FOR PROJECT LINKS ===")
        all_links = soup.find_all('a', href=True)
        project_links = []
        
        for link in all_links:
            href = link.get('href', '')
            if '/space/' in href:
                text = link.get_text().strip()
                if text:
                    project_links.append((href, text[:50]))
        
        if project_links:
            print(f"Found {len(project_links)} project links:")
            for href, text in project_links[:5]:
                print(f"  - {href} | {text}")
        else:
            print("No /space/ links found")
        
        # Check for Next.js or React data
        print("\n=== LOOKING FOR APP DATA ===")
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('__NEXT_DATA__' in script.string or 'window.__INITIAL_STATE__' in script.string):
                print("Found app data script (first 200 chars):")
                print(script.string[:200] + "...")
                break
        
        # Look for any data attributes
        print("\n=== DATA ATTRIBUTES ===")
        elements_with_data = soup.find_all(attrs=lambda x: x and any(k.startswith('data-') for k in x.keys()))
        if elements_with_data:
            print(f"Found {len(elements_with_data)} elements with data attributes")
            for elem in elements_with_data[:5]:
                data_attrs = {k: v for k, v in elem.attrs.items() if k.startswith('data-')}
                if data_attrs:
                    print(f"  - {elem.name}: {data_attrs}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_galxe_simple()
