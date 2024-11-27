import requests
from bs4 import BeautifulSoup
import json
from config import location_template

def fetch_static_content():
    url = 'https://n-l-e.ru/shops/'
    response = requests.get(url)
    return response.content

def fetch_additional_content():
    ajax_url = 'https://n-l-e.ru/bitrix/services/main/ajax.php?mode=class&c=nle%3Ashops.list&action=getShopsList'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0'
    }
    payload = {
        'offset': 10,
        'limit': 'Infinity'
    }
    response = requests.post(ajax_url, headers=headers, data=payload)
    return response.text

def extract_info_from_content(content):
    soup = BeautifulSoup(content, 'html.parser')
    locations = []

    shop_items = soup.find_all('div', class_='shops__list_item')
    for item in shop_items:
        location = location_template.copy()

        title = item.find('p', class_='shops_block__city_title')
        location['name'] = title.text.strip() if title else 'Не указано'

        address = item.find('span', class_='icon icon_map_point')
        location['address'] = address.text.strip() if address else 'Не указано'

        coordinates = item.find('a', class_='icon icon_map')
        if coordinates:
            href = coordinates.get('href')
            if href and "text=" in href:
                coords = href.split("text=")[1].split("&")[0]
                coords = coords.replace("%2C", ",")
                latlon = list(map(float, coords.split(',')))
                location['latlon'] = latlon
            else:
                location['latlon'] = [0.0, 0.0]
        else:
            location['latlon'] = [0.0, 0.0]

        phones = []
        phone_spans = item.find_all('span', class_='icon icon_phone')
        for span in phone_spans:
            a_tags = span.find_all('a')
            for a_tag in a_tags:
                phones.append(a_tag.text.strip())
        location['phones'] = phones if phones else ['Не указано']

        work_hours = item.find('span', class_='icon icon_clock')
        location['working_hours'] = [work_hours.text.strip()] if work_hours else ['Пн-Пт 09:00-17:00, Сб-Вс 10:00-15:00']

        locations.append(location)

    return locations

def extract_info_from_ajax_response(response_text):
    response_json = json.loads(response_text)
    if response_json.get("status") == "success":
        html_content = response_json["data"]["html"]
        return extract_info_from_content(html_content)
    else:
        print("Ошибка в ответе AJAX-запроса")
        return []

def save_to_json(data, filename='files_json/site1.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    static_content = fetch_static_content()
    static_info = extract_info_from_content(static_content)

    additional_content = fetch_additional_content()
    if additional_content:
        dynamic_info = extract_info_from_ajax_response(additional_content)

        combined_info = static_info + dynamic_info

        save_to_json(combined_info)
    else:
        print("Не удалось получить дополнительные данные")

if __name__ == "__main__":
    main()
