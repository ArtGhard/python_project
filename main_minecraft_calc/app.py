from flask import Flask, render_template, request
from pathlib import Path
import json
import math

# ПРОЧИТАЙТЕ README! (ПРО РАЗРАБОТКУ ПРОЕКТА В САМОМ НИЗУ)

app = Flask(__name__)


def load_counting_data():
    basedir = Path(__file__).resolve().parent
    filepath = basedir / 'data' / 'items.json'
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_mob_data():
    basedir = Path(__file__).resolve().parent
    filepath = basedir / 'data' / 'mobs.json'
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_items_data():
    basedir = Path(__file__).resolve().parent
    filepath = basedir / 'data' / 'items_and_names.json'
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


recipes = load_counting_data()
mob_names = load_mob_data()
item_names = load_items_data()


@app.route('/', methods=['GET', 'POST'])
def index():
    result_input = None
    if request.method == 'POST':
        try:
            item = request.form['item']
            value = int(request.form['value'])
            result_input = process_input(item, value)
        except ValueError:
            result_input = "Ошибка: введите корректное число."
        except Exception as e:
            result_input = f"Ошибка: {e}"

    return render_template('index.html', result_input=result_input)


def process_input(item, value):
    return calculate_resources(item, value)


def calculate_resources(item_name, value):
    item = find_item_by_name(item_name)
    if not item:
        return f"Предмет '{item_name}' не найден."

    result = define_primary_method(item, value)
    result['method'] = item['obtainable']['primary_method']
    return method_format_main(result)


def find_item_by_name(name):
    for item in recipes['all_items']:
        if item['name'] == name:
            return item
    return None


def define_primary_method(item, value):
    method = item.get('obtainable', {}).get('primary_method')
    if method == 'mining':
        return mining(item, value,)
    elif method == 'crafting':
        return crafting(item, value)
    elif method == 'stripping':
        return stripping(item, value)
    elif method == 'naturally':
        return naturally(item, value)
    elif method == 'from_mobs':
        return from_mobs(item, value)
    elif method == 'from_chest':
        return from_chest(item, value)
    elif method == 'smelting':
        return smelting(item, value)


def method_format_main(result_data):
    method = result_data.get('method')
    if method == 'mining':
        return mining_format(result_data)
    elif method == 'crafting':
        return crafting_format(result_data)
    elif method == 'stripping':
        return stripping_format(result_data)
    elif method == 'from_mobs':
        return from_mobs_format(result_data)
    elif method == 'naturally':
        return naturally_format(result_data)
    elif method == 'smelting':
        return smelting_format(result_data)


def mining_format(result_data):
    for key in item_names:
        if result_data['source_blocks'] == key:
            result_data['source_blocks'] = item_names[key]
        if result_data['minimal_tool'] == key:
            result_data['minimal_tool'] = item_names[key]
        else:
            pass
    new_result = {}
    for key_2, value in result_data['all_methods'].items():
        key_2 = item_names.get(key_2, key_2)
        new_result[key_2] = value
    result_data['all_methods'] = new_result
    print(result_data)
    return f"""
        <h3>Добыча</h3>
        <p>Минимальный инструмент: {result_data['minimal_tool']}</p>
        <p>Нужно сломать блоков: {result_data['blocks_needed']}</p>
        <p>Добывается из: {result_data['source_blocks']}</p>
        <h4>Время добычи для каждого инструмента:</h4>
        <ul>
        {''.join([f'<li>{tool}: {time:.2f} секунд</li>' for tool,
                 time in result_data['all_methods'].items()])}
        </ul>
        """


def crafting_format(result_data):
    new_ing_list = {}
    for name_ru, value in result_data['needed_ingredients'].items():
        name_ru = item_names.get(name_ru, name_ru)
        new_ing_list[name_ru] = value
    result_data['needed_ingredients'] = new_ing_list
    ingredients_list = '<br>'.join([f"{name}: {count}" for name, count in
                                   result_data['needed_ingredients'].items()])
    return f"""
        <h3>Крафт</h3>
        <p>Станок: {result_data['craft_station']}</p>
        <h4>Ингредиенты:</h4>
        <p>{ingredients_list}</p>
        """


def stripping_format(result_data):
    for key_strip in item_names:
        if result_data['stripping_block'] == key_strip:
            result_data['stripping_block'] = item_names[key_strip]
        else:
            pass
    for key_strip_mb in mob_names:
        if result_data['stripping_block'] == key_strip_mb:
            result_data['stripping_block'] = mob_names[key_strip_mb]
        else:
            pass
    print(result_data['stripping_block'])
    return f"""
        <h3>Обтёсывание</h3>
        <p>Нужно обтесать: {result_data['strip_block_count']}</p>
        <p>Из чего(кого) добывается: {result_data['stripping_block']}</p>
        <p>Инструмент: {result_data['required_tool']}</p>
        """


def naturally_format(result_data):
    return f"""
        <h3>Натуральное выпадение<h3>
        <p>Нужное количесво ({result_data['result_count']}) выпадет
        из: {result_data['conditions']} естественным образом</p>
        <p> Времени поребуется: {result_data['total_time']} секунд</p>
    """


def from_mobs_format(result_data):
    if 'multiple_options' in result_data:
        options_list = []
        for opt in result_data['multiple_options']:
            desc = f"""
            <li>
                <strong>Моб:</strong> {opt['mob']}<br>
                <strong>Нужно убить (в среднем):</strong> {opt['kills_needed_avg']:.2f}<br>
                {f"<strong>Условие:</strong> {opt['special_condition']
                 ['description']}" if 'special_condition' in opt else ''}
            </li>
            """
            options_list.append(desc)
            options_html = '<ul>' + ''.join(options_list) + '</ul>'
        return f"""
            <h3>Добыча с мобов</h3>
            <h4>Выпадает из:</h4>
            {options_html}
            """
    else:
        opt = result_data
        return f"""
            <h3>Добыча с мобов</h3>
            <p><strong>Моб:</strong> {opt['mob']}</p>
            <p><strong>Нужно убить (в среднем):</strong> {opt['kills_needed_avg']:.2f}</p>
            {f"<strong>Условие:</strong> {opt['special_condition']
             ['description']}" if 'special_condition' in opt else ''}
            """


def smelting_format(result_data):
    pass


# ####################################################### 991


def mining(item, value):
    mining_data = item['obtainable']['methods']['mining']
    minimal_tool = mining_data.get('minimal_tool', 'unknown')
    mining_methods = mining_data['mining_methods']
    result_count = mining_data.get('result_count')
    source_block = mining_data.get('source_block')
    chance = mining_data.get('chance')

    if not chance:
        if not isinstance(result_count, list):
            blocks_needed = value / result_count
            blocks_needed = math.ceil(blocks_needed)
        else:
            count = round(sum(result_count) / len(result_count))
            blocks_needed = math.ceil(value / math.ceil(count))
    else:
        if not isinstance(result_count, list):
            blocks_needed = (value / result_count) / chance
            blocks_needed = math.ceil(blocks_needed)
        else:
            count = round(sum(result_count) / len(result_count)) / chance
            blocks_needed = math.ceil(value / math.ceil(count))

    if source_block:
        if not isinstance(source_block, list):
            mining_block = source_block
        else:
            mining_block = ' или '.join(source_block)
    else:
        mining_block = item['name']
    result = {}
    for tool, data in mining_methods.items():
        speed = data['speed']
        total_time = speed * blocks_needed
        result[tool] = total_time
    final_result = {
        'minimal_tool': minimal_tool,
        'all_methods': result,
        'source_blocks': mining_block,
        'blocks_needed': blocks_needed
    }
    print(final_result)  # костыль для проверки
    return final_result


def crafting(item, value):
    crafting_data = item['obtainable']['methods']['crafting']
    first_type = next(iter(crafting_data['type']))
    recipe_data = crafting_data['type'][first_type]['ingredient_options'][0]

    ingredients = recipe_data['ingredients']
    result_count = recipe_data['result_count']

    cycles = math.ceil(value / result_count)

    needed_ingredients = {}
    for i in ingredients:
        needed_ingredients[i['id']] = i['count'] * cycles

    craft_station = None
    if first_type.replace('_', '') == 'craftingtable':
        craft_station = "Верстак"
    elif first_type.replace('_', '') == 'stonecutter':
        craft_station = "Камнерез"
    elif first_type.replace('_', '') == 'smithingtable':
        craft_station = "Кузнечный стол"

    final_result = {
        'craft_station': craft_station,
        'needed_ingredients': needed_ingredients
    }
    print(final_result)  # костыль для проверки
    return final_result


def stripping(item, value):
    stripping_data = item['obtainable']['methods']['stripping']
    result_count = stripping_data.get('count')
    strip_block_count = math.ceil(value / result_count)
    stripping_block = stripping_data.get('id')
    required_tool = stripping_data.get('required_tool')
    final_result = {
        'strip_block_count': strip_block_count,
        'stripping_block': stripping_block,
        'required_tool': required_tool
    }
    print(final_result)  # костыль для проверки
    return final_result


def naturally(item, value):
    nature_data = item['obtainable']['methods']['naturally']
    conditions = nature_data.get('conditions')
    time_range = nature_data.get('time_range')
    total_time = time_range * value
    result_count = value
    final_result = {
        'result_count': result_count,
        'conditions': conditions,
        'total_time': total_time
    }
    print(final_result)  # костыль для проверки
    return final_result


def from_mobs(item, value):
    mobs_data = item['obtainable']['methods']['from_mobs']['type']['mob_drops']
    drop_options = mobs_data.get('drop_options', [])

    if not drop_options:
        return {"error": "Нет данных о добыче с мобов"}

    results = []

    for option in drop_options:
        mob_id = option['mob']
        chance = option.get('chance')
        result_count = option.get('result_count')
        special_condition = option.get('special_condition', {})

        if isinstance(result_count, list):
            avg_result = sum(result_count) / len(result_count)
            kills_needed_avg = value / (avg_result * chance)
        else:

            kills_needed_avg = value / (result_count * chance)

        kills_needed_avg = round(kills_needed_avg)

        result = {
            'mob': mob_id,
            'kills_needed_avg': kills_needed_avg,
        }

        if special_condition:
            spawn_chance = special_condition.get('spawn_chance')
            if spawn_chance:
                result['special_condition'] = special_condition
                non_done = math.ceil(kills_needed_avg / spawn_chance)
                result['kills_needed_avg'] = non_done

        results.append(result)

    if len(results) == 1:
        final_result = results[0]
    else:
        final_result = {
            'multiple_options': results
        }

    print(final_result)
    return final_result


# метод на стадии доработки (к субботе появится (наверное))
def smelting(item, value):
    pass


# метод на стадии доработки (к субботе появится (наверное))
def from_chest(item, value):
    pass


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
