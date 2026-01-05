import urllib.request
import json
import re
import os
import textwrap
from datetime import datetime

GIST_URL = os.getenv("GIST_URL", "https://gist.githubusercontent.com/.../raw/...")
def wrap_text(text, width=70):
    if not text:
        return ""
    text = " ".join(text.split())
    return textwrap.fill(text, width=width, break_long_words=False, break_on_hyphens=False)

def generate_term_svg(term_data):
    term_line = f"Term: {term_data['termin']}"
    desc_line = f"Description: {term_data['description']}"
    trans_line = f"Перевод: {term_data['translate_ru']}" if term_data['translate_ru'] else ""
    ref_line = f"Link: {term_data['reference']}" if term_data['reference'] else ""

    term_wrapped = wrap_text(term_line, 70)
    desc_wrapped = wrap_text(desc_line, 70)
    trans_wrapped = wrap_text(trans_line, 70) if trans_line else ""
    ref_wrapped = wrap_text(ref_line, 70) if ref_line else ""

    term_lines = term_wrapped.count('\n') + 1
    desc_lines = desc_wrapped.count('\n') + 1
    trans_lines = trans_wrapped.count('\n') + 1 if trans_wrapped else 0
    ref_lines = ref_wrapped.count('\n') + 1 if ref_wrapped else 0

    line_height = 20
    top_padding = 20
    gap = 8

    total_height = top_padding + (term_lines * line_height) + gap + (desc_lines * line_height)
    if trans_wrapped:
        total_height += gap + (trans_lines * line_height)
    if ref_wrapped:
        total_height += gap + (ref_lines * line_height)
    total_height += 20 

    total_height = max(120, total_height)

    def escape_xml(text):
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def make_tspans(text, start_y, lh, x_pos):
        lines = text.split('\n')
        tspans = []
        for i, line in enumerate(lines):
            y = start_y + i * lh
            tspans.append(f'    <tspan x="{x_pos}" y="{y}">{escape_xml(line)}</tspan>')
        return "\n".join(tspans)

    svg_width = 650
    padding_percent = 0.05
    text_x = svg_width * padding_percent

    bg_color = "#141321"
    text_color = "#58a6ff"
    translation_color = "#8b949e"
    link_color = "#7ee787"

    svg_content = f'''<svg width="{svg_width}" height="{total_height}" xmlns="http://www.w3.org/2000/svg">
  <style>
    .term {{ font: bold 16px sans-serif; fill: {text_color}; }}
    .desc {{ font: 15px sans-serif; fill: {text_color}; }}
    .trans {{ font: italic 14px sans-serif; fill: {translation_color}; }}
    .ref {{ font: 13px sans-serif; fill: {link_color}; }}
  </style>
  <rect width="100%" height="{total_height}" fill="{bg_color}" rx="12" ry="12"/>
  <text class="term">
{make_tspans(term_wrapped, top_padding, line_height, text_x)}
  </text>
  <text class="desc">
{make_tspans(desc_wrapped, top_padding + term_lines * line_height + gap, line_height, text_x)}
  </text>'''

    current_y = top_padding + (term_lines + desc_lines) * line_height + gap * 2
    if trans_wrapped:
        svg_content += f'''
  <text class="trans">
{make_tspans(trans_wrapped, current_y, line_height, text_x)}
  </text>'''
        current_y += trans_lines * line_height + gap

    if ref_wrapped:
        svg_content += f'''
  <text class="ref">
{make_tspans(ref_wrapped, current_y, line_height, text_x)}
  </text>'''

    svg_content += "\n</svg>"
    return svg_content

def fetch_terms_from_gist(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())
        return data
    except Exception as e:
        print(f"Error fetching Gist: {e}")
        return []

def get_current_week():
    return datetime.now().strftime("%Y-%U")

def should_update_term(readme_content):
    pattern = r'<!-- WEEKLY_TERM_START -->.*?<!-- Updated: ([\d-]+) -->.*?<!-- WEEKLY_TERM_END -->'
    match = re.search(pattern, readme_content, re.DOTALL)
    if match:
        last_update_date_str = match.group(1)
        last_week = datetime.strptime(last_update_date_str, "%Y-%m-%d").strftime("%Y-%U")
        current_week = get_current_week()
        return last_week != current_week
    return True 

def get_weekly_term():
    terms = fetch_terms_from_gist(GIST_URL)
    if not terms:
        return {
            "termin": "Error",
            "description": "Could not load terms from Gist.",
            "translate_ru": "Не удалось загрузить термины из Gist.",
            "reference": "",
            "example": ""
        }

    try:
        year = datetime.now().strftime("%Y")
        week = int(datetime.now().strftime("%U"))
        index = (int(year) * 53 + week) % len(terms)
        item = terms[index]

        return {
            "termin": item.get("termin", "—"),
            "description": item.get("description", ""),
            "translate_ru": item.get("translate_ru", ""),
            "reference": item.get("reference", ""),
            "example": item.get("example", "")
        }
    except Exception as e:
        return {
            "termin": "Error",
            "description": f"Failed to load term: {str(e)}",
            "translate_ru": f"Ошибка: {str(e)}",
            "reference": "",
            "example": ""
        }

def main():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        content = ""

    if not should_update_term(content):
        return
    
    term_data = get_weekly_term()

    today_str = datetime.now().strftime("%Y-%m-%d")
    lines = []
    lines.append(f'<strong>Term: {term_data["termin"]}</strong>')
    if term_data["description"]:
        lines.append(f'<br><small><strong>Description:</strong> {term_data["description"]}</small>')
    if term_data["translate_ru"]:
        lines.append(f'<br><small><strong>Перевод:</strong> {term_data["translate_ru"]}</small>')
    if term_data["reference"]:
        lines.append(f'<br><small><strong>Ссылка:</strong> <a href="{term_data["reference"]}" target="_blank">📖 Learn more</a></small>')
    if term_data["example"]:
        example_safe = (
            term_data["example"]
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        lines.append(f'<br><pre><code>{example_safe}</code></pre>')

    term_html = "\n".join(lines) + f'\n<!-- Updated: {today_str} -->'
    term_block = f'''<!-- WEEKLY_TERM_START -->
<div align="center">
  <blockquote>
    {term_html}
  </blockquote>
</div>
<!-- WEEKLY_TERM_END -->'''
    term_pattern = r'<!-- WEEKLY_TERM_START -->.*?<!-- WEEKLY_TERM_END -->'
    if re.search(term_pattern, content, re.DOTALL):
        content = re.sub(term_pattern, term_block, content, flags=re.DOTALL)
    else:
    
        if '<!-- DAILY_QUOTE_END -->' in content:
            content = content.replace('<!-- DAILY_QUOTE_END -->', '<!-- DAILY_QUOTE_END -->\n\n' + term_block)
        else:
            content = content.rstrip() + "\n\n" + term_block

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    main()