import os
import requests
import vk_api
import random
from io import BytesIO

token = os.environ.get('VK_TOKEN')
group_id = os.environ.get('GROUP_ID')

def post_with_photo():
    # 1. Читаем правила
    if not os.path.exists('rules.txt'):
        print("Файл rules.txt не найден")
        return

    with open('rules.txt', 'r', encoding='utf-8') as f:
        all_rules = [line.strip() for line in f if '|' in line]
    
    # 2. Читаем историю использованных
    used_rules = []
    if os.path.exists('used_rules.txt'):
        with open('used_rules.txt', 'r', encoding='utf-8') as f:
            used_rules = [line.strip() for line in f if line.strip()]

    remaining_rules = [r for r in all_rules if r not in used_rules]

    if not remaining_rules:
        remaining_rules = all_rules
        open('used_rules.txt', 'w', encoding='utf-8').close()

    # 3. Выбор правила
    chosen_line = random.choice(remaining_rules)
    text_part, photo_url = chosen_line.split('|')

    # 4. Авторизация
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    upload = vk_api.VkUpload(vk_session)

    # 5. Загрузка фото (ФИНАЛЬНЫЙ ФИКС)
    attachments = []
    try:
        response = requests.get(photo_url.strip(), timeout=20)
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            image_data.name = 'image.jpg' # Принудительно задаем имя файла для ВК
            
            # Загружаем на сервер ВК
            photo = upload.photo_wall(image_data, group_id=int(group_id))[0]
            attachments.append(f"photo{photo['owner_id']}_{photo['id']}")
            print(f"Фото подготовлено: {attachments[0]}")
    except Exception as e:
        print(f"Ошибка загрузки фото: {e}")

    # 6. Публикация
    vk.wall.post(
        owner_id=-int(group_id),
        message=text_part.strip(),
        attachments=",".join(attachments) if attachments else None,
        from_group=1
    )

    # 7. Запись истории
    with open('used_rules.txt', 'a', encoding='utf-8') as f:
        f.write(chosen_line + '\n')

if __name__ == "__main__":
    post_with_photo()