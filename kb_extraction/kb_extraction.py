import re
import requests
import wikitextparser as wtp

import re
import requests
import wikitextparser as wtp

import re
import requests
import wikitextparser as wtp

def get_clean_terraria_wiki(page_title):
    # 1. Fetch RAW Wikitext
    URL = "https://terraria.wiki.gg/api.php"
    params = {"action": "parse", "page": page_title, "prop": "wikitext", "format": "json"}
    response = requests.get(URL, params=params).json()
    raw_content = response['parse']['wikitext']['*']

    # 2. Remove HTML comments
    raw_content = re.sub(r'<!--.*?-->', '', raw_content, flags=re.DOTALL)

    # 3. Extract item names (tightened)
    raw_content = re.sub(
        r'\{\{item\|([^\|\}\n]+)[^\}]*?\}\}',
        r'\1',
        raw_content,
        flags=re.IGNORECASE | re.DOTALL
    )

    # 3b. Clean any leftover |note=...|image=...png}} tails
    raw_content = re.sub(
        r'\|[^\n\{\}]*?\.(?:png|jpg|jpeg|gif|svg)[^\n\{\}]*?\}\}',
        '',
        raw_content,
        flags=re.IGNORECASE
    )

    # 3c. Clean bare filename fragments (Word.png or Word.png/Word2.png)
    raw_content = re.sub(
        r'\b[\w\s]+\.(?:png|jpg|jpeg|gif|svg)(?:/[\w\s]+\.(?:png|jpg|jpeg|gif|svg))*',
        '',
        raw_content,
        flags=re.IGNORECASE
    )


    # 4. Extract infocard section names as plain headers
    #    {{infocard/start|type=Gearing Up|name=Melee|theme=melee}} -> "[Melee]"
    raw_content = re.sub(
        r'\{\{infocard/start[^\}]*\|name=([^\|\}]+)[^\}]*\}\}',
        r'\n[\1]\n',
        raw_content,
        flags=re.IGNORECASE
    )

    # 5. Extract infocard/box titles as sub-headers
    #    {{infocard/box/start|title=Weapons}} -> "Weapons:"
    raw_content = re.sub(
        r'\{\{infocard/box/start\|title=([^\|\}]+)\}\}',
        r'\1:\n',
        raw_content,
        flags=re.IGNORECASE
    )

    # 6. NOW safely remove all remaining structural templates (single-line only)
    #    Using re.MULTILINE but NOT re.DOTALL to avoid cross-line greediness
    raw_content = re.sub(r'\{\{[^\{\}]*\}\}', '', raw_content)

    # 7. Repeat pass for any nested templates that became exposed
    #    (run 2-3 times to handle nesting)
    for _ in range(3):
        raw_content = re.sub(r'\{\{[^\{\}]*\}\}', '', raw_content)

    # 8. Parse remaining wikitext with wikitextparser
    parsed = wtp.parse(raw_content)

    # Remove File/Image wikilinks
    for link in parsed.wikilinks:
        if link._match is None:
            continue
        try:
            title = link.title.strip().lower()
            if title.startswith(('file:', 'image:')):
                del link[:]
        except (AttributeError, TypeError):
            continue

    clean_text = parsed.plain_text()

    # 9. Final cleanup
    # After step 3 (item extraction), add this:

    clean_text = re.sub(r'File:.*?\.(png|jpg|jpeg|gif|svg)\|?', '', clean_text, flags=re.IGNORECASE)

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

    # Collapse excessive blank lines
    clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)

    return clean_text.strip()

# def get_clean_terraria_wiki(page_title):
#     # 1. Fetch RAW Wikitext
#     URL = "https://terraria.wiki.gg/api.php"
#     params = {"action": "parse", "page": page_title, "prop": "wikitext", "format": "json"}
#     response = requests.get(URL, params=params).json()
#     raw_content = response['parse']['wikitext']['*']
    
#     # --- NEW PRE-PARSER STEP ---
#     # This turns {{Console}} -> Console so wikitextparser doesn't delete it
#     raw_content = re.sub(r'\{\{([a-zA-Z0-9\s]+)\}\}', r'\1', raw_content)
#     # ---------------------------

#     # 2. Parse with wikitextparser
#     parsed = wtp.parse(raw_content)
    
#     for link in parsed.wikilinks:
#         if link._match is None: continue
#         try:
#             title = link.title.strip().lower()
#             if title.startswith(('file:', 'image:')):
#                 del link[:] 
#         except (AttributeError, TypeError): continue

#     # 3. Get plain text (Now 'Console' and 'Mobile' are safe!)
#     clean_text = parsed.plain_text()

#     # 4. Final Polish: Template Flattening
    
#     # FIRST: Extract the item name from {{item|Name|...}}
#     # This regex looks for 'item|', captures the name until the next '|' or '}'
#     clean_text = re.sub(r'\{\{item\|([^\|\}]+).*?\}\}', r'\1', clean_text, flags=re.IGNORECASE)

#     # SECOND: Unpack simple single-word templates like {{Console}}
#     clean_text = re.sub(r'\{\{([a-zA-Z0-9\s]+)\}\}', r'\1', clean_text)

#     # THIRD: Now it's safe to remove the structural UI templates (the containers)
#     # We use DOTALL because Infocards span many lines
#     clean_text = re.sub(r'\{\{.*?\}\}', '', clean_text, flags=re.DOTALL)

#     # FOURTH: Cleanup leftovers
#     clean_text = re.sub(r'File:.*?\.(png|jpg|jpeg|gif|svg)\|?', '', clean_text, flags=re.IGNORECASE)
    
#     # Remove HTML comments left by the wiki editors (e.g. )
#     clean_text = re.sub(r'', '', clean_text, flags=re.DOTALL)

#     # 5. UI Cleanup: Remove known Wiki navigation artifacts
#     artifacts = [
#         r'legacy nav tab', 
#         r'navigation menu', 
#         r'jump to navigation', 
#         r'jump to search',
#         r'tocright',
#         r'tocleft',
#     ]
#     for artifact in artifacts:
#         clean_text = re.sub(artifact, '', clean_text, flags=re.IGNORECASE)
    
#     # Remove excessive newlines caused by deleted templates
#     clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text)

#     return clean_text.strip()

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
