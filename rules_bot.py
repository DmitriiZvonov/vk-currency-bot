import os
import requests
import vk_api
import random
from io import BytesIO  # Добавили этот импорт, чтобы фото читалось корректно

token = os.environ.get('VK_TOKEN')
group_id = os.environ.get('GROUP_ID')

def post_with_photo():
    # 1. Загружаем все правила
    with open('rules.txt', 'r', encoding='utf-8') as f:
        all_rules = [line.strip() for line in f.readlines() if line.strip()]
    
    # 2. Загружаем уже использованные правила
    if os.path.exists('used_rules.txt'):
        with open('used_rules.txt', 'r', encoding='utf-8') as f:
            used_rules = [line.strip() for line in f.readlines() if line.strip()]
    else:
        used_rules = []

    # 3. Находим те, которые еще не постили
    remaining_rules = [r for r in all_rules if r not in used_rules]

    # Если правила закончились, начинаем круг заново
    if not remaining_rules:
        remaining_rules = all_rules
        with open('used_rules.txt', 'w', encoding='utf-8') as f:
            f.write("")

    # 4. Выбираем случайное правило
    chosen_line = random.choice(remaining_rules)
    if '|' not in chosen_line:
        print(f"Ошибка в строке: {chosen_line}. Нет разделителя |")
        return

    text_part, photo_url = chosen_line.split('|')

    # 5. Авторизация в ВК
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    upload = vk_api.VkUpload(vk_session)

    # 6. Загрузка фото
    attachments = None
    try:
        response = requests.get(photo_url.strip(), stream=True, timeout=10)
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            # Загружаем на сервер ВК
            photo_upload = upload.photo_wall(photos=image_data, group_id=int(group_id))[0]
            attachments = f"photo{photo_upload['owner_id']}_{photo_upload['id']}"
            print("Фото успешно загружено на сервер ВК")
    except Exception as e:
        print(f"Не удалось загрузить фото: {e}")

    # 7. Публикация поста
    vk.wall.post(
        owner_id=-int(group_id),
        message=text_part.strip(),
        attachments=attachments,
        from_group=1
    )

    # 8. Записываем, что это правило использовано
    with open('used_rules.txt', 'a', encoding='utf-8') as f:
        f.write(chosen_line + '\n')

if __name__ == "__main__":
    try:
        post_with_photo()
        print("Пост с фото опубликован!")
    except Exception as e:
        print(f"Ошибка при выполнении: {e}")