import requests
import json
import time
import random
from config import location_template, user_agents

url = 'https://lukoil.bg/api/cartography/GetCountryDependentSearchObjectData'
params = {
    'form': 'gasStation',
}


def fetch_data(url, params):
    headers = {'User-Agent': random.choice(user_agents)}
    response = requests.get(url, headers=headers, params=params)
    print(f"Запрос: {response.url}")
    print(f"Статус: {response.status_code}")
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            print("Ошибка JSON")
            print(response.text)
            return None
    else:
        print(f"Ошибка при запросе данных: {response.status_code}")
        print(response.text)
        return None


def format_working_hours(business_hours):
    if not business_hours:
        return ["mon - sun 00:00 - 24:00"]
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    formatted_hours = [f"{days[i]} {day['StartTime']} - {day['EndTime']}" for i, day in enumerate(business_hours) if
                       day]
    return [", ".join(formatted_hours)]


def process_data(data):
    station_ids = [f'gasStation{station["GasStationId"]}' for station in data['GasStations']]  # Все ID АЗС

    # Чанки id
    id_chunks = [station_ids[i:i + 50] for i in range(0, len(station_ids), 50)]

    all_stations_info = []

    for chunk in id_chunks:
        time.sleep(random.randint(1, 5))

        ids_param = '&'.join([f'ids={station_id}' for station_id in chunk])
        api_url = f'https://lukoil.bg/api/cartography/GetObjects?{ids_param}&lng=EN'

        response = fetch_data(api_url, None)

        if response:
            for station in response:
                gas_station = station.get('GasStation', {})
                business_hours = gas_station.get('StationBusinessHours')
                if business_hours:
                    business_hours = business_hours.get('Days', [])
                else:
                    business_hours = []
                working_hours = format_working_hours(business_hours)

                location = location_template.copy()
                location.update({
                    'name': gas_station.get('DisplayName', 'Не указано'),
                    'address': f"{gas_station.get('City', 'Не указано')}, {gas_station.get('Street', 'Не указано')}, {gas_station.get('Address', 'Не указано')}",
                    'latlon': [gas_station.get('Latitude', 0), gas_station.get('Longitude', 0)],
                    'phones': [gas_station.get('Phone', 'Не указано'), gas_station.get('Fax', 'Не указано')],
                    'working_hours': working_hours
                })
                all_stations_info.append(location)
        else:
            print("Не удалось получить данные для АЗС из текущего chunk.")

    return all_stations_info


def save_to_json(data, filename='files_json/site3.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    data = fetch_data(url, params)

    if data:
        all_stations_info = process_data(data)
        save_to_json(all_stations_info)
    else:
        print("Не удалось получить ID АЗС.")


if __name__ == "__main__":
    main()
