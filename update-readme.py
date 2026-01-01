import urllib.request
import json
import re
import datetime
import ssl
import textwrap

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
                return item.get("q", "").strip(), item.get("a", "Unknown").strip()
    except Exception:
        pass
    return (
        "The only way to do great work is to love what you do.",
        "Steve Jobs"
    )

def translate(text, source='en', target='ru'):
    if not TRANSLATOR_AVAILABLE or not text:
        return ""
    try:
        return GoogleTranslator(source=source, target=target).translate(text)
    except Exception:
        return ""

def wrap_text(text, width=60):
    return textwrap.fill(text, width=width)

def generate_svg(quote_en, author_en, quote_ru, author_ru, date_str):
    line1 = f"«{quote_en}» — {author_en}"
    line2 = f"«{quote_ru}» — {author_ru}" if quote_ru else ""

    line1_wrapped = wrap_text(line1, 60)
    line2_wrapped = wrap_text(line2, 60) if line2 else ""

    lines_count = 2 + line1_wrapped.count('\n') + (1 if line2 else 0) + line2_wrapped.count('\n')
    height = max(160, 60 + lines_count * 24)

    def escape_xml(text):
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    line1_xml = escape_xml(line1_wrapped).replace("\n", "\n    ")
    line2_xml = escape_xml(line2_wrapped).replace("\n", "\n    ") if line2 else ""

    bg_color = "#141321"
    text_color = "#58a6ff"
    translation_color = "#8b949e"

    svg_content = f'''<svg width="600" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .container {{ fill: {bg_color}; rx: 12; ry: 12; }}
    .title {{ font: bold 18px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: {text_color}; }}
    .quote {{ font: italic 16px Georgia, 'Times New Roman', serif; fill: {text_color}; }}
    .translation {{ font: 14px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: {translation_color}; }}
  </style>
  <rect class="container" x="0" y="0" width="600" height="{height}"/>
  <text x="30" y="40" class="title">📅 Quote of the day ({date_str})</text>
  <text x="30" y="70" class="quote">
    {line1_xml}
  </text>'''

    if line2:
        y_pos = 70 + (line1_wrapped.count('\n') + 1) * 24
        svg_content += f'''
  <text x="30" y="{y_pos}" class="translation">
    {line2_xml}
  </text>'''

    svg_content += "\n</svg>"
    return svg_content

def main():
    quote_en, author_en = get_quote()
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    if TRANSLATOR_AVAILABLE and quote_en:
        quote_ru = translate(quote_en)
        author_ru = translate(author_en) if author_en != "Unknown" else author_en
    else:
        quote_ru, author_ru = "", ""

    svg_data = generate_svg(quote_en, author_en, quote_ru, author_ru, today)
    with open("quote.svg", "w", encoding="utf-8") as f:
        f.write(svg_data)

    quote_image_block = '''<div align="center">
  <img src="quote.svg" alt="Quote of the day">
</div>

'''
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = ""
    pattern = r'<div align="center">\s*<img src="quote\.svg"[^>]*>.*?</div>\s*\n?'
    content = re.sub(pattern, "", content, flags=re.DOTALL)

    new_content = quote_image_block + content.lstrip()

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)

if __name__ == "__main__":
    main()