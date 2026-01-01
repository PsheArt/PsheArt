# update-readme.py
import urllib.request
import json
import re
import datetime
import ssl

try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False

def get_quote():
    try:
        context = ssl.create_default_context()
        with urllib.request.urlopen("https://zenquotes.io/api/random", context=context, timeout=10) as response:
            data = json.loads(response.read().decode())
            if data and isinstance(data, list):
                item = data[0]
                quote_en = item.get("q", "").strip()
                author = item.get("a", "Unknown").strip()
                return quote_en, author
    except Exception:
        pass
    return (
        "The only way to do great work is to love what you do.",
        "Steve Jobs"
    )

def translate(text, source='en', target='ru'):
    if not TRANSLATOR_AVAILABLE:
        return ""
    try:
        return GoogleTranslator(source=source, target=target).translate(text)
    except Exception:
        return ""

def main():
    quote_en, author_en = get_quote()
    quote_ru = translate(quote_en) if TRANSLATOR_AVAILABLE else ""
    author_ru = translate(author_en) if TRANSLATOR_AVAILABLE and author_en != "Unknown" else author_en
    if quote_ru:
        translation_line = f"(Цитата дня: «{quote_ru}» — {author_ru})"
    else:
        translation_line = ""

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    original_line = f"> «{quote_en}» — {author_en}"

    if translation_line:
        quote_block = f"{original_line}\n{translation_line}"
    else:
        quote_block = original_line

    new_content = f"## 📅 Quote of the day ({today})\n\n{quote_block}\n"

    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = "# My Repository\n\n"

    # Замена существующего блока
    pattern = r"(## 📅 Quote of the day \(.*?\)\n\n> .*?)(?=\n## |\Z)"
    if re.search(pattern, content, re.DOTALL):
        updated = re.sub(pattern, new_content, content, count=1, flags=re.DOTALL)
    else:
        lines = content.splitlines(keepends=True)
        if len(lines) > 1:
            lines.insert(1, "\n" + new_content + "\n")
        else:
            lines.append("\n" + new_content + "\n")
        updated = "".join(lines)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(updated)

if __name__ == "__main__":
    main()