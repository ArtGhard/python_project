import json
import os

# Получаем текущую директорию и ищем файл
current_dir = os.getcwd()
print(f"Текущая директория: {current_dir}")

# Пробуем разные возможные пути
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

# Создаем словарь для поиска
items_dict = {}
for item in json_data['all_items']:
    items_dict[item['name']] = item

# Ввод данных
item_name = input("Введите название предмета: ")
count = int(input("Введите количество: "))

# Поиск и расчет
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
            # Ищем имя ингредиента
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
