#!/usr/bin/env python3
"""
Test the new parsing logic
"""

from bs4 import BeautifulSoup

def test_parse_quests(html):
    """Test the new parsing logic"""
    if not html:
        return []
    soup = BeautifulSoup(html, 'html.parser')
    quests = []
    
    # Debug: Print some HTML to understand the structure
    print(f"🔍 Analyzing HTML structure...")
    
    # Look for the main grid container
    grid_container = soup.select_one("div.GridFlowContainer_grid-flow__m_iqK")
    if grid_container:
        print(f"✅ Found grid container with {len(grid_container.find_all())} child elements")
    else:
        print("❌ Grid container not found")
    
    # Try multiple possible selectors for quest cards
    selectors_to_try = [
        # Grid items
        "div.GridFlowContainer_grid-flow__m_iqK > div",
        "div.GridFlowContainer_grid-flow__m_iqK > *",
        # Card-like elements
        "div[class*='card']",
        "div[class*='Card']", 
        "div[class*='item']",
        "div[class*='Item']",
        # Links to spaces/campaigns
        "a[href*='/space/']",
        "a[href*='/quest/']",
        "a[href*='/campaign/']",
        # Look for any links in the main content area
        "main a[href]"
    ]
    
    found_items = []
    for selector in selectors_to_try:
        items = soup.select(selector)
        if items:
            print(f"✅ Found {len(items)} items with selector: {selector}")
            found_items.extend(items)
            break  # Use the first working selector
    
    if not found_items:
        print("❌ No quest items found with any selector")
        return []
    
    print(f"📊 {len(found_items)} items found to process")
    return found_items

if __name__ == "__main__":
    # Read the HTML we saved earlier
    try:
        with open('galxe_simple_debug.html', 'r', encoding='utf-8') as f:
            html = f.read()
        print(f"📄 Loaded HTML file: {len(html)} characters")
        items = test_parse_quests(html)
        print(f"🎯 Final result: {len(items)} items found")
    except FileNotFoundError:
        print("❌ HTML file not found. Run simple_debug.py first.")
