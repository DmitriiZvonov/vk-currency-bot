import os
import requests
import vk_api
from datetime import datetime

# Получаем секретные данные
token = os.environ.get('VK_TOKEN')
group_id = os.environ.get('GROUP_ID')

def get_currency_rate():
    url = "https://www.cbr-xml-daily.ru/daily_json.js"
    response = requests.get(url)
    data = response.json()
    
    # Данные по дирхаму
    rate = data['Valute']['AED']['Value']
    nominal = data['Valute']['AED']['Nominal']
    prev_rate = data['Valute']['AED']['Previous']
    
    final_rate = round(rate / nominal, 2)
    final_prev = round(prev_rate / nominal, 2)
    
    # Считаем разницу
    diff = round(final_rate - final_prev, 2)
    if diff > 0:
        trend = f"📈 +{diff} руб."
    elif diff < 0:
        trend = f"📉 {diff} руб."
    else:
        trend = "平 Без изменений"
        
    return final_rate, trend

def post_to_vk(message):
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    vk.wall.post(owner_id=-int(group_id), message=message)

if __name__ == "__main__":
    try:
        current_rate, trend = get_currency_rate()
        date_today = datetime.now().strftime("%d.%m.%Y")
        
        # Красивый информативный текст
        text = (
            f"🇦🇪 Актуальный курс дирхама к рублю\n"
            f"📅 На сегодня, {date_today}:\n\n"
            f"💵 1 AED = {current_rate} RUB\n"
            f"📊 Изменение за сутки: {trend}\n\n"
            f"Курс обновлен автоматически на основе данных ЦБ РФ. Сохраняйте себе, чтобы быть в курсе! 📍\n\n"
            f"#ДубайНаЛадони #дубай #оаэ #дирхам #валюта"
        )
        
        post_to_vk(text)
        print("Пост с новыми хештегами опубликован!")
    except Exception as e:
        print(f"Ошибка: {e}")