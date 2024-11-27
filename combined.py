import json

def read_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

site1_data = read_json('files_json/site1.json')
site2_data = read_json('files_json/site2.json')
site3_data = read_json('files_json/site3.json')

combined_data = site1_data + site2_data + site3_data

def save_to_json(data, filename='files_json/combined.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

save_to_json(combined_data)

