from flask import Flask, render_template, request, url_for, session, jsonify
from flask import redirect
from auth import init_db, register_user, login_user, get_user_by_id
from pathlib import Path
import json
import math
import statistics

# ПРОЧИТАЙТЕ README! (ПРО РАЗРАБОТКУ ПРОЕКТА В САМОМ НИЗУ)

app = Flask(__name__)
app.secret_key = 'add_you_super_mega_ultra_secret_key'

init_db()


# ЗАГРУЗКА ДАННЫХ ДЛЯ ПОДСЧЁТА
def load_counting_data():
    basedir = Path(__file__).resolve().parent
    filepath = basedir / 'data' / 'items.json'
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


# ЗАГРУЗКА ДАННЫХ ДЛЯ ПЕРЕВОДА МОБОВ
def load_mob_data():
    basedir = Path(__file__).resolve().parent
    filepath = basedir / 'data' / 'mobs.json'
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


# ЗАГРУЗКА ДАННЫХ ДЛЯ ПЕРЕВОДА ПРЕДМЕТОВ
def load_items_data():
    basedir = Path(__file__).resolve().parent
    filepath = basedir / 'data' / 'items_and_names.json'
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


# ЗАГРУЗКА ДАННЫХ ДЛЯ ПЕРЕВОДА СТРУКТУР
def load_dungeons_data():
    basedir = Path(__file__).resolve().parent
    filepath = basedir / 'data' / 'chest_dungeons.json'
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


recipes = load_counting_data()
mob_names = load_mob_data()
item_names = load_items_data()
dungeon_names = load_dungeons_data()


METHOD_LABELS = {
    'mining': 'Добыча',
    'crafting': 'Крафт',
    'smelting': 'Переплавка',
    'stripping': 'Обтёсывание',
    'naturally': 'Натуральное выпадение',
    'from_mobs': 'С мобов',
    'from_chest': 'Из сундуков'
}


# СОЗДАНИЕ ОСНОВНОЙ СТРАНИЦЫ
@app.route('/', methods=['GET', 'POST'])
def index():
    user = None
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
    result_data = None
    user_item = ""
    user_value = ""

    if request.method == 'POST':
        try:
            item = request.form['item']
            value = int(request.form['value'])
            user_item = item
            user_value = value

            full_item = find_item_by_name(item)
            if not full_item:
                result_data = {"html": f"Предмет '{item}' не найден.",
                               "methods": []}
            else:
                selected_method = request.form.get('selected_method')
                if not selected_method:
                    selected_method = full_item['obtainable']['primary_method']

                calc_result = calculate_method_by_name(full_item,
                                                       selected_method, value)
                html_result = format_method_result(selected_method,
                                                   calc_result)

                result_data = {
                    "item_obj": full_item,
                    "value": value,
                    "methods": get_all_method_names(full_item),
                    "selected_method": selected_method,
                    "html": html_result
                }

        except ValueError:
            result_data = {"html": "Ошибка: введите корректное число.",
                           "methods": []}
        except Exception as e:
            result_data = {"html": f"Ошибка: {e}", "methods": []}

    return render_template(
        'index.html',
        result_data=result_data,
        user_item=user_item,
        user_value=user_value,
        user=user,
        METHOD_LABELS=METHOD_LABELS
    )


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    nickname = request.form['nickname']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    avatar = request.form.get('avatar', 'default.png')  # по умолчанию

    if password != confirm_password:
        return jsonify({"success": False, "message": "Пароли не совпадают"})

    if len(password) < 8:
        return jsonify({"success": False, "message": "Пароль должен быть\
                         не менее 8 символов"})

    if register_user(username, nickname, password, avatar):
        return jsonify({"success": True, "message": "Регистрация успешна"})
    else:
        return jsonify({"success": False, "message": "Пользователь уже\
                         существует"})


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user_id = login_user(username, password)
    if user_id:
        session['user_id'] = user_id
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message":
                        "Неверный логин или пароль"})


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


def process_input(item, value):
    full_item = find_item_by_name(item)
    if not full_item:
        return {
            "error": f"Предмет '{item}' не найден.",
            "methods": [],
            "selected_method": None,
            "html": f"Предмет '{item}' не найден."
        }

    all_methods = get_all_method_names(full_item)
    primary = full_item['obtainable']['primary_method']

    primary_result = calculate_method_by_name(full_item, primary, value)
    primary_html = format_method_result(primary, primary_result)

    return {
        "item_obj": full_item,
        "value": value,
        "methods": all_methods,
        "selected_method": primary,
        "html": primary_html
    }


# ПОИСК ПРЕДМЕТА ПО ВВЕДННОМУ В ПОЛЕ НАЗВАНИЮ
def find_item_by_name(name):
    for item in recipes['all_items']:
        if item['name'] == name:
            return item
    return None


# ПОИСК АЛЬТЕРНАТИВНЫХ МЕТОДОВ СОЗДАНИЯ ПРЕДМЕТА
def get_all_method_names(item):
    methods = item.get('obtainable', {}).get('methods', {})
    return list(methods.keys())


# РАСЧЁТ ДЛЯ ВСЕХ ВОЗМОЖНЫХ МЕТОДОВ
def calculate_method_by_name(item, method_name, value):
    if method_name == 'mining':
        return mining(item, value)
    elif method_name == 'crafting':
        return crafting(item, value)
    elif method_name == 'stripping':
        return stripping(item, value)
    elif method_name == 'naturally':
        return naturally(item, value)
    elif method_name == 'from_mobs':
        return from_mobs(item, value)
    elif method_name == 'from_chest':
        return from_chest(item, value)
    elif method_name == 'smelting':
        return smelting(item, value)
    else:
        return {"error": f"Метод '{method_name}' не поддерживается."}


# ОПРДЕЛЕНИЕ МЕТОДА ПОЛУЧЕНИЯ ПРЕДМЕТА ДЛЯ ВЫВОДА И ФОРМАТИРОВАНИЯ
def format_method_result(method_name, result_data):
    if method_name == 'mining':
        return mining_format(result_data)
    elif method_name == 'crafting':
        return crafting_format(result_data)
    elif method_name == 'stripping':
        return stripping_format(result_data)
    elif method_name == 'from_mobs':
        return from_mobs_format(result_data)
    elif method_name == 'naturally':
        return naturally_format(result_data)
    elif method_name == 'smelting':
        return smelting_format(result_data)
    elif method_name == 'from_chest':
        return from_chest_format(result_data)
    else:
        return f"<p>Неизвестный метод: {method_name}</p>"


# ФОРМАТИРОВАНИЕ
# ########################################################################### #
def mining_format(result_data):
    img_list = []
    for key in result_data['all_methods']:
        key_img2 = 'minecraft_' + key.replace(':', '_')
        i_url2 = f'<img src="static/calc_img_items/{key_img2}.png"\
                   width="40" height="40">'
        img_list.append(i_url2)

    key_img = result_data['minimal_tool']
    key_img = 'minecraft_' + key_img.replace(':', '_')
    i_url = f'<img src="static/calc_img_items/{key_img}.png"\
             width="40" height="40">'

    key_img3 = result_data['source_blocks']
    key_img3 = key_img3.replace(':', '_')
    i_url3 = f'<img src="static/calc_img_items/{key_img3}.png"\
              width="40" height="40">'

    for key in item_names:
        if result_data['source_blocks'] == key:
            result_data['source_blocks'] = item_names[key]
        if result_data['minimal_tool'] == key:
            result_data['minimal_tool'] = item_names[key]

    new_result = {}
    for key_2, value in result_data['all_methods'].items():
        key_2 = item_names.get(key_2, key_2)
        new_result[key_2] = value
    result_data['all_methods'] = new_result

    return f"""
        <h3>Добыча</h3>
        <p>  </p>
        <p>Минимальный инструмент: {result_data['minimal_tool']} {i_url}</p>
        <p>Нужно сломать блоков: {result_data['blocks_needed']}</p>
        <p>Добывается из: {result_data['source_blocks']} {i_url3}</p>
        <h4>Время добычи для каждого инструмента:</h4>
        <ul>
        {''.join([f'<li>{tool}: {time:.2f} секунд {img}</li>'
                  for (tool, time), img in
                  zip(result_data['all_methods'].items(), img_list)])}
        </ul>
        """


# ########################################################################### #
def crafting_format(result_data):
    img_list = []
    for key in result_data['needed_ingredients']:
        key_img = key.replace(':', '_')
        i_url = f'<img src="static/calc_img_items/{key_img}.png"\
                 width="40" height="40">'
        img_list.append(i_url)
    print(result_data)
    print(img_list)
    new_ing_list = {}
    for name_ru, value in result_data['needed_ingredients'].items():
        name_ru = item_names.get(name_ru, name_ru)
        new_ing_list[name_ru] = value
    result_data['needed_ingredients'] = new_ing_list

    return f"""
        <h3>Крафт</h3>
        <p>  </p>
        <p>Станок: {result_data['craft_station']}</p>
        <h4>Ингредиенты:</h4>
        <ul>{''.join([f"<li>{name}: {count} {img}<li>"
                     for (name, count), img in
                     zip(result_data['needed_ingredients'].items(),
                     img_list)])}</p>
        </ul>
        """


# ########################################################################### #
def stripping_format(result_data):
    key_img = result_data['stripping_block']
    key_img = key_img.replace(':', '_')
    i_url = f'<img src=static/calc_img_items/{key_img}.png\
             width="40" height="40">'
    for key_strip in item_names:
        if result_data['stripping_block'] == key_strip:
            result_data['stripping_block'] = item_names[key_strip]
            break
        else:
            pass
    for key_strip_mb in mob_names:
        if result_data['stripping_block'] == key_strip_mb:
            result_data['stripping_block'] = mob_names[key_strip_mb]
            break
        else:
            pass
    return f"""
        <h3>Обтёсывание</h3>
        <p>  </p>
        <p>Нужно обтесать: {result_data['strip_block_count']}</p>
        <p>Из чего(кого) добывается:
        {result_data['stripping_block']} {i_url}</p>
        <p>Инструмент: {result_data['required_tool']}</p>
        """


# ########################################################################### #
def naturally_format(result_data):
    return f"""
        <h3>Натуральное выпадение</h3>
        <p>  </p>
        <p><strong>Нужное количесво ({result_data['result_count']}) выпадет
        из</strong>: {result_data['conditions']} естественным образом</p>
        <p> <strong>Времени потребуется</strong>: {result_data['total_time']}
        секунд</p>
    """


# ########################################################################### #
def from_mobs_format(result_data):
    options_list = []
    translated_data = []
    spec = None
    for num in result_data['mob_variations']:
        key_in = num['mob']
        for key_out in mob_names:
            if key_in == key_out:
                num['mob'] = mob_names[key_out]
                translated_data.append(num)
                break
            else:
                pass
    for opt in translated_data:
        if 'special_condition' in opt:
            spec = opt['special_condition']['description']
        else:
            spec = 'Нет'
        desc = f"""
        <li>
            <strong>Моб:</strong> {opt['mob']}<br>
            <strong>Нужно в среднем убить мобов:</strong>\
            {opt['kills_needed']}<br>
            <strong>Специальное условие:</strong> {spec}<br>
            <p>  </p>
        </li>
        """
        options_list.append(desc)
        options_html = '<ul>' + ''.join(options_list) + '</ul>'

    return f"""
        <h3>Выпадение с мобов</h3>
        <p>  </p>
        {options_html}
        """


# ########################################################################### #
def smelting_format(result_data):
    key_img = result_data['smelt_ingredient']
    key_img = key_img.replace(':', '_')
    i_url = f'<img src=static/calc_img_items/{key_img}.png\
             width="40" height="40">'
    for key_smelt in item_names:
        if result_data['smelt_ingredient'] == key_smelt:
            result_data['smelt_ingredient'] = item_names[key_smelt]
            break
        else:
            pass
    return f"""
        <h3>Переплавка</h3>
        <p>  </p>
        <p><strong>Станок:</strong> {result_data['table']}<p>
        <p><strong>Ингредиент для
        переплавки:</strong> {result_data['smelt_ingredient']} {i_url}<p>
        <p><strong>Нужное количество:</strong> {result_data['need_count']}<p>
        """


# ########################################################################### #
def from_chest_format(result_data):
    options_list = []
    translated_data = []
    for num in result_data['chest_variations']:
        key_in = num['dungeon']
        for key_out in dungeon_names:
            if key_in == key_out:
                num['dungeon'] = dungeon_names[key_out]
                translated_data.append(num)
                break
            else:
                pass
    for opt in translated_data:
        desc = f"""
        <li>
            <strong>Структура с сундуком:</strong> {opt['dungeon']}<br>
            <strong>Нужно в среднем залутать сундуков:</strong>\
            {opt['result']}<br>
            <p>  </p>
        </li>
        """
        options_list.append(desc)
        options_html = '<ul>' + ''.join(options_list) + '</ul>'

    return f"""
        <h3>Появление в сундуках</h3>
        <p>  </p>
        {options_html}
        """


# РАСЧЁТ
# ########################################################################### #
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
        mining_block = item['id']
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
    return final_result


# ########################################################################### #
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
    return final_result


# ########################################################################### #
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
    return final_result


# ########################################################################### #
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
    return final_result


# ########################################################################### #
def from_mobs(item, value):
    drop_options2 = item['obtainable']['methods']['from_mobs']['type']
    drop_options = drop_options2['mob_drops']['drop_options']
    mob_variations = []
    for option in drop_options:
        mob = {}
        mob['mob'] = option['mob']
        chance = option['chance']
        result_raw = option['result_count']
        if not isinstance(result_raw, list):
            avg_count = result_raw
        else:
            avg_count = statistics.mean(result_raw)
        expected_per_kill = chance * avg_count
        spawn_chance = 1.0
        special_condition = option.get('special_condition')
        if special_condition and 'spawn_chance' in special_condition:
            spawn_chance = special_condition['spawn_chance']
            mob['special_condition'] = special_condition
        total_expected = spawn_chance * expected_per_kill
        if total_expected <= 0:
            kills = float('inf')
        else:
            kills = value / total_expected
        mob['kills_needed'] = math.ceil(kills)
        mob_variations.append(mob)
    final_result = {
        "mob_variations": mob_variations
    }
    return final_result


# ########################################################################### #
def smelting(item, value):
    smelting_data = item['obtainable']['methods']['smelting']['type']
    smelt = smelting_data['furnace']['ingredient_options'][0]
    smelt_ingredient = smelt['ingredients'][0]['id']
    need_count = round(value / smelt['ingredients'][0]['count'])
    final_result = {
        'smelt_ingredient': smelt_ingredient,
        'need_count': need_count,
        'table': "Печь"
    }
    return final_result


# ########################################################################### #
def from_chest(item, value):
    chest_data_big = item['obtainable']['methods']['from_chest']['type']
    chest_data = chest_data_big['chest_loot']['loot_options']
    chests = []
    for chest_number in chest_data:
        chest = {}
        chest['dungeon'] = chest_number['chest']
        chance = chest_number['chance']
        if not isinstance(chest_number['result_count'], list):
            result_count = value / (chest_number['result_count'] * chance)
            chest['result'] = math.ceil(result_count)
            chests.append(chest)
        else:
            result_avg = statistics.mean(chest_number['result_count'])
            result_count = value / (result_avg * chance)
            chest['result'] = math.ceil(result_count)
            chests.append(chest)
    final_result = {
        "chest_variations": chests
    }
    return final_result


# ЗАПУСК САЙТА
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
