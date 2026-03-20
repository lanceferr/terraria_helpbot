import re
import requests
import wikitextparser as wtp

def get_clean_terraria_wiki(page_title):
    # 1. Fetch the RAW Wikitext from the API (not the HTML)
    URL = "https://terraria.wiki.gg/api.php"
    params = {
        "action": "parse",
        "page": page_title,
        "prop": "wikitext", # This ensures we get the 'source' code
        "format": "json"
    }
    
    response = requests.get(URL, params=params).json()
    raw_content = response['parse']['wikitext']['*']
    
    # 2. Parse with wikitextparser
    parsed = wtp.parse(raw_content)
    # Use a list to avoid mutation issues while deleting
    for link in parsed.wikilinks:
        # 1. ADD THIS CHECK: Ensure the link is valid and has a match object
        if link._match is None:
            continue
            
        # 2. Safely access the title
        try:
            title = link.title
            if title and title.strip().lower().startswith(('file:', 'image:')):
                del link[:] 
        except (AttributeError, TypeError):
            # Skip links that cause internal library errors
            continue

    # 3. Get plain text (converts [[Wood|Logs]] -> Logs)
    clean_text = parsed.plain_text()
    
    # 4. Final Polish: Remove leftover Wiki-specific artifacts (like {{...}} templates)
    clean_text = re.sub(r'File:.*?\.(png|jpg|jpeg|gif|svg)\|?', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'\{\{.*?\}\}', '', clean_text) # Removes templates
    clean_text = re.sub(r'\[\[File:.*?\]\]', '', clean_text) # Removes image embeds
    
    return clean_text.strip()
