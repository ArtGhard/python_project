import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

current_dir = os.getcwd()
img_dir = os.path.join(current_dir, 'python_project/analysis', 'analysis_img')
os.makedirs(img_dir, exist_ok=True)

plt.style.use('default')
np.random.seed(42)

minecraft_data = pd.DataFrame({
    'Year': [2018, 2019, 2020, 2021, 2022, 2023, 2024],
    'Active_Players_Millions': [91, 112, 131, 141, 173, 182, 195],
    'Searches_Millions': [45, 52, 68, 73, 81, 79, 85]
})

calculator_usage = pd.DataFrame({
    'Calculator_Type': ['Крафт предметов', 'Постройки', 'Ресурсы',
                        'Фермы', 'Рецепты'],
    'Daily_Users': [12500, 8900, 15600, 6700, 21300]
})

months = pd.date_range('2023-01', '2024-01', freq='M')
revenue_data = pd.DataFrame({
    'Month': months,
    'Ad_Revenue': np.random.normal(1500, 300, len(months)).cumsum() + 1000,
    'Premium_Users': np.random.randint(50, 200, len(months)).cumsum(),
    'Traffic': np.random.normal(10000, 2000, len(months)).cumsum()
})

user_demographics = pd.DataFrame({
    'Age_Group': ['13-17', '18-24', '25-34', '35-44', '45+'],
    'Percentage': [35, 28, 20, 12, 5],
    'Avg_Session_Minutes': [45, 38, 25, 18, 12]
})

colors = ['#2E86AB', '#A8DADC', '#F24236', '#F7EF81', '#1B998B']

plt.figure(figsize=(12, 8))
plt.plot(minecraft_data['Year'], minecraft_data['Active_Players_Millions'],
         marker='o', linewidth=3, markersize=8,
         color=colors[0], label='Активные игроки')
plt.plot(minecraft_data['Year'], minecraft_data['Searches_Millions'],
         marker='s', linewidth=3, markersize=8,
         color=colors[1], label='Поисковые запросы')
plt.title('Динамика популярности Minecraft', fontsize=16,
          fontweight='bold', pad=20)
plt.xlabel('Год', fontsize=12)
plt.ylabel('Млн пользователей', fontsize=12)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.xticks(minecraft_data['Year'])
all_data = zip(minecraft_data['Year'],
               minecraft_data['Active_Players_Millions'],
               minecraft_data['Searches_Millions'])
for i, (year, players, searches) in enumerate(all_data):
    plt.annotate(f'{players}M', (year, players), textcoords="offset points",
                 xytext=(0, 10), ha='center', fontsize=9)
    plt.annotate(f'{searches}M', (year, searches), textcoords="offset points",
                 xytext=(0, -15), ha='center', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(img_dir, 'Популярность Майнкрафта.png'), dpi=300,
            bbox_inches='tight')
plt.close()

plt.figure(figsize=(12, 8))
bars = plt.bar(calculator_usage['Calculator_Type'],
               calculator_usage['Daily_Users'],
               color=colors, alpha=0.85, edgecolor='black', linewidth=0.5)
plt.title('Востребованность типов калькуляторов', fontsize=16,
          fontweight='bold', pad=20)
plt.xlabel('Тип калькулятора', fontsize=12)
plt.ylabel('Пользователей в день', fontsize=12)
plt.xticks(rotation=15, ha='right')
plt.grid(True, alpha=0.3, axis='y')
for bar, users in zip(bars, calculator_usage['Daily_Users']):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 200,
             f'{users:,}', ha='center', va='bottom', fontweight='bold',
             fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(img_dir, 'Использование калькулятора.png'), dpi=300,
            bbox_inches='tight')
plt.close()

plt.figure(figsize=(10, 8))
wedges, texts, autotexts = plt.pie(user_demographics['Percentage'],
                                   labels=user_demographics['Age_Group'],
                                   autopct='%1.1f%%', startangle=90,
                                   colors=colors,
                                   textprops={'fontsize': 11})
plt.title('Возрастная структура аудитории', fontsize=16, fontweight='bold',
          pad=20)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(10)
plt.tight_layout()
plt.savefig(os.path.join(img_dir, 'Возрастная структура.png'), dpi=300,
            bbox_inches='tight')
plt.close()

plt.figure(figsize=(12, 8))
plt.plot(revenue_data['Month'], revenue_data['Ad_Revenue'],
         marker='o', linewidth=2.5, markersize=6, color=colors[3],
         label='Доход от рекламы')
plt.plot(revenue_data['Month'], revenue_data['Premium_Users'],
         marker='s', linewidth=2.5, markersize=6, color=colors[4],
         label='Premium пользователи')
plt.title('Динамика доходов и пользователей',
          fontsize=16,
          fontweight='bold',
          pad=20)
plt.xlabel('Месяц', fontsize=12)
plt.ylabel('Доход ($) / Пользователи', fontsize=12)
plt.legend(fontsize=11)
plt.grid(True, alpha=0.3)
plt.xticks(rotation=45)
ax2 = plt.gca().twinx()
ax2.plot(revenue_data['Month'], revenue_data['Traffic'],
         marker='^', linewidth=2.5, markersize=6, color=colors[2],
         linestyle='--', label='Трафик')
ax2.set_ylabel('Трафик (посещений)', fontsize=12)
ax2.legend(loc='upper right', fontsize=11)
plt.tight_layout()
plt.savefig(os.path.join(img_dir, 'Трафик дохода.png'), dpi=300,
            bbox_inches='tight')
plt.close()

plt.figure(figsize=(10, 6))
months_projected = ['2026', '2027', '2028']
users_projected = [50000, 75000, 100000]
plt.plot(months_projected, users_projected, linewidth=3, marker='o',
         markersize=8, color="#1F6D8F")
plt.title('Прогноз роста пользователей', fontsize=14, fontweight='bold')
plt.ylabel('Пользователей в день', fontsize=12)
plt.grid(True, alpha=0.3)
for i, (month, users) in enumerate(zip(months_projected, users_projected)):
    plt.annotate(f'{users:,}', (month, users), textcoords="offset points",
                 xytext=(0, 10), ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(img_dir, 'Прогноз роста пользователей.png'),
            dpi=300, bbox_inches='tight')
plt.close()

plt.figure(figsize=(10, 6))
projects = ['Minecraft Calc', 'Сайт-визитка', 'Магазин', 'Приложение']
roi_values = [247, 45, 89, 156]
bars = plt.bar(projects, roi_values, color=['#2E86AB', '#A8DADC',
                                            '#A8DADC', '#A8DADC'],
               alpha=0.8, edgecolor='black', linewidth=0.5)
plt.title('Сравнение ROI', fontsize=14, fontweight='bold')
plt.ylabel('ROI (%)', fontsize=12)
for bar, roi in zip(bars, roi_values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
             f'{roi}%', ha='center', va='bottom', fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(img_dir, 'Сравнение ROI.png'), dpi=300,
            bbox_inches='tight')
plt.close()
