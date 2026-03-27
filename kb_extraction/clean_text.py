import re


def clean_text(text):
    # Remove just the image filenames, not the whole line
    text = re.sub(r"\S+\.(png|jpg|gif)", "", text, flags=re.IGNORECASE)

    # Remove "Music:" lines
    text = re.sub(r"Music:.*\n", "", text)

    # Remove "Summoned with..." lines (optional, remove if you want to keep them)
    text = re.sub(r"Summoned.*\n", "", text)

    # Remove "For elaborate strategies..." lines
    text = re.sub(r"For elaborate strategies.*\n", "", text)

    # Remove table of contents section
    text = re.sub(r"Contents.*?Pre-Hardmode bosses", "Pre-Hardmode bosses", text, flags=re.DOTALL)

    # Remove version/platform header
    text = re.sub(r"Desktop version.*?\n", "", text)

    # Remove short junk lines (like single words or duplicates)
    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        line = line.strip()

        # Skip empty or very short junk lines
        if len(line) < 3:
            continue

        # Remove duplicate-like lines (e.g., "King Slime" repeated)
        if cleaned_lines and line == cleaned_lines[-1]:
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # Fix excessive spacing
    text = re.sub(r"\n{2,}", "\n\n", text)

    return text.strip()


# Read file
with open("getting_started.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

# Clean it
cleaned = clean_text(raw_text)

# Save output
with open("cleaned_getting_started.txt", "w", encoding="utf-8") as f:
    f.write(cleaned)

print("Cleaned text saved to cleaned_getting_started.txt")