import os
import requests
import vk_api
import random
from io import BytesIO

token = os.environ.get('VK_TOKEN')
group_id = os.environ.get('GROUP_ID')

def post_with_photo():
    # 1. Читаем правила и фильтруем пустые строки
    with open('rules.txt', 'r', encoding='utf-8') as f:
        all_rules = [line.strip() for line in f if '|' in line]
    
    if os.path.exists('used_rules.txt'):
        with open('used_rules.txt', 'r', encoding='utf-8') as f:
            used_rules = [line.strip() for line in f if line.strip()]
    else:
        used_rules = []

    remaining_rules = [r for r in all_rules if r not in used_rules]

    if not remaining_rules:
        remaining_rules = all_rules
        open('used_rules.txt', 'w', encoding='utf-8').close()

    chosen_line = random.choice(remaining_rules)
    text_part, photo_url = chosen_line.split('|')

    # 2. Авторизация
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    upload = vk_api.VkUpload(vk_session)

    # 3. Загрузка фото
    attachments = []
    try:
        response = requests.get(photo_url.strip(), timeout=15)
        if response.status_code == 200:
            image = BytesIO(response.content)
            photo = upload.photo_wall(image, group_id=int(group_id))[0]
            attachments.append(f"photo{photo['owner_id']}_{photo['id']}")
            print(f"Фото загружено: {attachments[0]}")
    except Exception as e:
        print(f"Ошибка загрузки фото: {e}")

    # 4. Публикация
    vk.wall.post(
        owner_id=-int(group_id),
        message=text_part.strip(),
        attachments=",".join(attachments) if attachments else None,
        from_group=1
    )

    # 5. Сохранение
    with open('used_rules.txt', 'a', encoding='utf-8') as f:
        f.write(chosen_line + '\n')

if __name__ == "__main__":
    try:
        post_with_photo()
        print("Готово!")
    except Exception as e:
        print(f"Ошибка: {e}")