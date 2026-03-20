import re
import requests
import wikitextparser as wtp

def get_clean_terraria_wiki(page_title):
    # 1. Fetch RAW Wikitext
    URL = "https://terraria.wiki.gg/api.php"
    params = {"action": "parse", "page": page_title, "prop": "wikitext", "format": "json"}
    response = requests.get(URL, params=params).json()
    raw_content = response['parse']['wikitext']['*']
    
    # --- NEW PRE-PARSER STEP ---
    # This turns {{Console}} -> Console so wikitextparser doesn't delete it
    raw_content = re.sub(r'\{\{([a-zA-Z0-9\s]+)\}\}', r'\1', raw_content)
    # ---------------------------

    # 2. Parse with wikitextparser
    parsed = wtp.parse(raw_content)
    
    for link in parsed.wikilinks:
        if link._match is None: continue
        try:
            title = link.title.strip().lower()
            if title.startswith(('file:', 'image:')):
                del link[:] 
        except (AttributeError, TypeError): continue

    # 3. Get plain text (Now 'Console' and 'Mobile' are safe!)
    clean_text = parsed.plain_text()
    
    # 4. Final Cleanup (Removes the complex templates like Infoboxes)
    clean_text = re.sub(r'\{\{.*?\}\}', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'File:.*?\.(png|jpg|jpeg|gif|svg)\|?', '', clean_text, flags=re.IGNORECASE)

    # 5. UI Cleanup: Remove known Wiki navigation artifacts
    artifacts = [
        r'legacy nav tab', 
        r'navigation menu', 
        r'jump to navigation', 
        r'jump to search',
        r'tocright',
        r'tocleft',
    ]
    for artifact in artifacts:
        clean_text = re.sub(artifact, '', clean_text, flags=re.IGNORECASE)
    
    # Remove excessive newlines caused by deleted templates
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)

    return clean_text.strip()

# def get_clean_terraria_wiki(page_title):
#     # 1. Fetch the RAW Wikitext from the API (not the HTML)
#     URL = "https://terraria.wiki.gg/api.php"
#     params = {
#         "action": "parse",
#         "page": page_title,
#         "prop": "wikitext", # This ensures we get the 'source' code
#         "format": "json"
#     }
    
#     response = requests.get(URL, params=params).json()
#     raw_content = response['parse']['wikitext']['*']
    
#     # 2. Parse with wikitextparser
#     parsed = wtp.parse(raw_content)
#     # Use a list to avoid mutation issues while deleting
#     for link in parsed.wikilinks:
#         if link._match is None:
#             continue
            
#         try:
#             title = link.title.strip().lower()
#             # Case A: It's an image/file -> Delete the whole thing
#             if title.startswith(('file:', 'image:')):
#                 del link[:] 
            
#             # Case B: It's a normal link (like [[Console]])
#             # Do NOTHING here. Let wikitextparser handle it in Step 3.
                
#         except (AttributeError, TypeError):
#             continue

#     # 3. Get plain text (converts [[Wood|Logs]] -> Logs)
#     clean_text = parsed.plain_text()
    
    
#     # # 4. Final Polish (Updated for multi-line templates)
#     # # The re.DOTALL flag ensures that {{ ... }} is removed even if it spans multiple lines
#     # clean_text = re.sub(r'\{\{.*?\}\}', '', clean_text, flags=re.DOTALL)
    
#     # # This catches any loose 'File:' text that wasn't inside [[]] brackets
#     # clean_text = re.sub(r'File:.*?\.(png|jpg|jpeg|gif|svg)\|?', '', clean_text, flags=re.IGNORECASE)
#     # # clean_text = re.sub(r'File:.*?\.(png|jpg|jpeg|gif|svg)\|?', '', clean_text, flags=re.IGNORECASE)
#     # # clean_text = re.sub(r'\{\{.*?\}\}', '', clean_text) # Removes templates
#     # # clean_text = re.sub(r'\[\[File:.*?\]\]', '', clean_text) # Removes image embeds
    
#     # 4. Final Polish (Surgical Template Removal)

#     # # 4. Final Polish: Surgical Template Handling
    
#     # # FIRST: Unpack simple text templates (e.g., {{Console}} -> Console)
#     # # This uses a 'capturing group' (\1) to keep the word but drop the braces
#     # clean_text = re.sub(r'\{\{([a-zA-Z0-9\s]+)\}\}', r'\1', clean_text)

#     # # SECOND: Remove complex/noisy templates that span multiple lines
#     # # (e.g., {{Infobox|...}} or {{Guide/Tip|...}})
#     # # We use DOTALL so the .*? matches across newlines
#     # clean_text = re.sub(r'\{\{.*?\}\}', '', clean_text, flags=re.DOTALL)

#     # # THIRD: Cleanup leftover file extensions and stray image markers
#     # clean_text = re.sub(r'File:.*?\.(png|jpg|jpeg|gif|svg)\|?', '', clean_text, flags=re.IGNORECASE)

#     return clean_text.strip()
