import requests
from bs4 import BeautifulSoup
import json
import re
from config import location_template

def fetch_static_content():
    url = 'https://ufahimchistka.ru/reception/'
    response = requests.get(url)
    return response.content

def extract_info_from_content(content):
    soup = BeautifulSoup(content, 'html.parser')
    locations = []

    cards = soup.find_all('div', class_='card')
    for card in cards:
        location = location_template.copy()

        card_text = card.find('p', class_='card-text')
        if card_text:
            lines = card_text.decode_contents().split('<br/>')
            if len(lines) >= 4:
                location['name'] = lines[0].strip()
                location['phones'] = [lines[1].strip()]
                location['working_hours'] = [lines[2].strip(), lines[3].strip()]

        address = card.find('div', class_='card-header')
        location['address'] = address.text.strip() if address else 'Не указано'

        # координаты из скрипта js
        scripts = soup.find_all('script', type='text/javascript')
        for script in scripts:
            script_content = script.string
            if script_content:
                coords = re.findall(r'\d+\.\d+,\d+\.\d+', script_content)
                if coords:
                    lat, lon = map(float, coords[0].split(','))
                    location['latlon'] = [lat, lon]
                    break

        locations.append(location)

    return locations

def save_to_json(data, filename='files_json/site2.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    static_content = fetch_static_content()
    locations = extract_info_from_content(static_content)

    save_to_json(locations)

if __name__ == "__main__":
    main()
