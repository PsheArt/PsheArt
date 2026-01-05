import urllib.request
import json
import re
import os
from datetime import datetime

GIST_URL = os.getenv("GIST_URL", "https://gist.githubusercontent.com/.../raw/...")

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
    """Проверяет, обновлялся ли термин в этой неделе, по содержимому README.md"""
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
        print("Week unchanged. Skipping term update.")
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