import json
import os

def save_to_manifest(page_title, clean_content, source_url, game_state):
    # Create the structured object
    manifest_entry = {
        "metadata": {
            "title": page_title,
            "source": source_url,
            "game_state": game_state, # e.g., "Pre-Hardmode"
            "last_updated": "2026-03-20",
            "version": "1.4.4"
        },
        "content": clean_content
    }

    # Ensure directory exists
    output_dir = "knowledge_base/processed"
    os.makedirs(output_dir, exist_ok=True)

    # Create a safe filename (replace colons/spaces)
    safe_name = page_title.lower().replace(":", "_").replace(" ", "_")
    file_path = f"{output_dir}/{safe_name}.json"

    # Save as JSON
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(manifest_entry, f, indent=4, ensure_ascii=False)
    
    print(f"Successfully saved manifest to: {file_path}")

# Example Usage:
# save_to_manifest("Guide:Getting started", content, "https://...", "Pre-Hardmode")