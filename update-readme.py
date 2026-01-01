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

<<<<<<< Updated upstream
=======
def wrap_text(text, width=60):
    if not text:
        return ""
    text = " ".join(text.split()) 
    return textwrap.fill(text, width=width, break_long_words=False, break_on_hyphens=False)

def generate_svg(quote_en, author_en, quote_ru, author_ru, date_str):
    line1 = f"«{quote_en}» — {author_en}"
    line2 = f"«{quote_ru}» — {author_ru}" if quote_ru else ""

    line1_wrapped = wrap_text(line1, 65)
    line2_wrapped = wrap_text(line2, 50) if line2 else ""

    line1_lines = line1_wrapped.count('\n') + 1
    line2_lines = line2_wrapped.count('\n') + 1 if line2 else 0

    line_height = 24

    total_height = 40 + 10 + (line1_lines * line_height) + (8 if line2 else 0) + (line2_lines * line_height) + 20
    total_height = max(160, total_height)

    def escape_xml(text):
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def make_tspans(text, start_y, lh):
        lines = text.split('\n')
        tspans = []
        for i, line in enumerate(lines):
            y = start_y + i * lh
            tspans.append(f'    <tspan x="30" y="{y}">{escape_xml(line)}</tspan>')
        return "\n".join(tspans)

    bg_color = "#141321"
    text_color = "#58a6ff"
    translation_color = "#8b949e"

    svg_content = f'''<svg width="800" height="{total_height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .title {{ font: bold 18px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: {text_color}; }}
    .quote {{ font: italic 16px Georgia, 'Times New Roman', serif; fill: {text_color}; }}
    .translation {{ font: 14px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: {translation_color}; }}
  </style>
  <rect width="800" height="{total_height}" fill="{bg_color}" rx="12" ry="12"/>
  <text class="title">
    <tspan x="30" y="40">Quote of the day ({date_str})</tspan>
  </text>
  <text class="quote">
{make_tspans(line1_wrapped, 70, line_height)}
  </text>'''

    if line2:
        y_start = 70 + line1_lines * line_height + 8
        svg_content += f'''
  <text class="translation">
{make_tspans(line2_wrapped, y_start, line_height)}
  </text>'''

    svg_content += "\n</svg>"
    return svg_content

>>>>>>> Stashed changes
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