import json
import os

current_dir = os.getcwd()
print(f"Текущая директория: {current_dir}")

possible_paths = [
    'items.json',
    './items.json',
    'python_project/items.json',
    './python_project/items.json',
    '../items.json'
]

json_data = None
file_path = None

for path in possible_paths:
    if os.path.exists(path):
        file_path = path
        break

if file_path:
    print(f"Найден файл: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
else:
    print("Файл items.json не найден! Проверьте расположение файла.")
    exit()

items_dict = {}
for item in json_data['all_items']:
    items_dict[item['name']] = item

item_name = input("Введите название предмета: ")
count = int(input("Введите количество: "))

if item_name not in items_dict:
    print("Предмет не найден!")
else:
    item = items_dict[item_name]

    if 'crafting' in item['obtainable']['methods']:
        crafting_data = item['obtainable']['methods']['crafting']['type']
        recipe = crafting_data['crafting_table']['ingredient_options'][0]
        result_count = recipe['result_count']
        recipes_needed = (count + result_count - 1) // result_count

        print(f"\nДля {count} {item_name} нужно:")

        for ingredient in recipe['ingredients']:
            total_needed = ingredient['count'] * recipes_needed
            ing_name = ingredient['id']
            for search_item in json_data['all_items']:
                if search_item['id'] == ingredient['id']:
                    ing_name = search_item['name']
                    break

            print(f"- {ing_name}: {total_needed}")

    elif 'mining' in item['obtainable']['methods']:
        mining_data = item['obtainable']['methods']['mining']
        print(f"\nВремя добычи {count} {item_name}:")
        print("Время приблизительно и расчитано при идеальных,",
              "условиях, когда блоки стоят друг за другом")

        for tool, speed_data in mining_data['mining_methods'].items():
            if count == 1:
                total_time = (speed_data['speed'] * count)
            else:
                total_time = 2 * (speed_data['speed'] * count)
            print(f"{tool}: {total_time:.2f} сек")

    elif 'smelting' in item['obtainable']['methods']:
        smelting_data = item['obtainable']['methods']['smelting']['type']
        recipe = smelting_data['furnace']['ingredient_options'][0]
        result_id = recipe['ingredients'][0]['id']
        for search_item in json_data['all_items']:
            if search_item['id'] == result_id:
                ing_name = search_item['name']
                break
        print(f"\n Нужно будет переплавить {count} {ing_name}")
