import os
import requests
import vk_api
import random

token = os.environ.get('VK_TOKEN')
group_id = os.environ.get('GROUP_ID')

def post_with_photo():
    # 1. Загружаем все правила
    with open('rules.txt', 'r', encoding='utf-8') as f:
        all_rules = f.readlines()
    
    # 2. Загружаем уже использованные правила
    if os.path.exists('used_rules.txt'):
        with open('used_rules.txt', 'r', encoding='utf-8') as f:
            used_rules = f.readlines()
    else:
        used_rules = []

    # 3. Находим те, которые еще не постили
    remaining_rules = [r for r in all_rules if r not in used_rules]

    # Если правила закончились, очищаем список использованных и начинаем круг заново
    if not remaining_rules:
        remaining_rules = all_rules
        open('used_rules.txt', 'w').close() 

    # 4. Выбираем случайное правило
    chosen_line = random.choice(remaining_rules).strip()
    text_part, photo_url = chosen_line.split('|')

    # 5. Авторизация в ВК
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    upload = vk_api.VkUpload(vk_session)

    # 6. Загрузка фото в ВК по ссылке
    image_data = requests.get(photo_url, stream=True).raw
    photo = upload.photo_wall(photos=image_data, group_id=int(group_id))[0]
    attachment = f"photo{photo['owner_id']}_{photo['id']}"

    # 7. Публикация поста
    full_text = f"💡 Полезно знать об ОАЭ\n\n{text_part}\n\n#ДубайНаЛадони #оаэ #дирхам #советы"
    vk.wall.post(owner_id=-int(group_id), message=full_text, attachments=attachment)

    # 8. Записываем, что это правило использовано
    with open('used_rules.txt', 'a', encoding='utf-8') as f:
        f.write(chosen_line + '\n')

if __name__ == "__main__":
    try:
        post_with_photo()
        print("Пост с фото опубликован!")
    except Exception as e:
        print(f"Ошибка: {e}")