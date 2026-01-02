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

def wrap_text(text, width=90):
    if not text:
        return ""
    text = " ".join(text.split()) 
    return textwrap.fill(text, width=width, break_long_words=False, break_on_hyphens=False)

def generate_svg(quote_en, author_en, quote_ru, author_ru, date_str):
    svg_width = 650
    padding_percent = 0.1
    text_x = svg_width * padding_percent 

    line1 = f"«{quote_en}» — {author_en}"
    line2 = f"«{quote_ru}» — {author_ru}" if quote_ru else ""

    line1_wrapped = wrap_text(line1, 60)
    line2_wrapped = wrap_text(line2, 70) if line2 else ""

    line1_lines = line1_wrapped.count('\n') + 1
    line2_lines = line2_wrapped.count('\n') + 1 if line2 else 0

    line_height = 24
    top_padding = 45          
    gap_between = 8 if line2 else 0
    bottom_padding = 15       

    total_height = top_padding + (line1_lines * line_height) + gap_between + (line2_lines * line_height) + bottom_padding
    total_height = max(80, total_height)

    def escape_xml(text):
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def make_tspans(text, start_y, lh, x_pos):
        lines = text.split('\n')
        tspans = []
        for i, line in enumerate(lines):
            y = start_y + i * lh
            tspans.append(f'    <tspan x="{x_pos}" y="{y}">{escape_xml(line)}</tspan>')
        return "\n".join(tspans)

    bg_color = "#141321"
    text_color = "#58a6ff"
    translation_color = "#8b949e"

    svg_content = f'''<svg width="{svg_width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .quote {{ font: italic 17px Georgia, 'Times New Roman', serif; fill: {text_color}; }}
    .translation {{ font: 15px -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; fill: {translation_color}; }}
  </style>
  <rect width="100%" height="{total_height}" fill="{bg_color}" rx="12" ry="12"/>
  <text class="quote">
{make_tspans(line1_wrapped, top_padding, line_height, text_x)}
  </text>'''

    if line2:
        y_start = top_padding + line1_lines * line_height + gap_between
        svg_content += f'''
  <text class="translation">
{make_tspans(line2_wrapped, y_start, line_height, text_x)}
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

    quote_image_block = '''
    <div align="center">
    <img src="quote.svg" alt="Quote of the day">
    </div>'''

    full_block = f'''<!-- DAILY_QUOTE_START -->
    {quote_image_block}
    <!-- DAILY_QUOTE_END -->'''

    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = full_block + "\n"

    pattern = r'<!-- DAILY_QUOTE_START -->\s*.*?\s*<!-- DAILY_QUOTE_END -->'
    match = re.search(pattern, content, flags=re.DOTALL)

    if match:
        content = re.sub(pattern, full_block, content, flags=re.DOTALL)
    else:
        content = full_block + "\n\n" + content.strip()

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    main()
