import os
import re
import zipfile
import shutil
import sys


def normalize(string):
    translit_mapping = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'ґ': 'g', 'д': 'd', 'е': 'e',
        'є': 'ie', 'ж': 'zh', 'з': 'z', 'и': 'y', 'і': 'i', 'ї': 'i', 'й': 'i',
        'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
        'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch',
        'ш': 'sh', 'щ': 'shch', 'ь': '', 'ю': 'iu', 'я': 'ia'
    }

    translit_string = ''
    for char in string:
        if char.lower() in translit_mapping:
            translit_string += translit_mapping[char.lower()]
        elif re.match(r'[a-zA-Z0-9]', char):
            translit_string += char.lower()
        else:
            translit_string += '_'

    return translit_string


def process_archive(file_path, sorting_folder):
    # отримуємо ім'я архіву без розширення
    archive_name = os.path.splitext(os.path.basename(file_path))[0]

    # створюємо папку для архіву у папці, яку сортуємо
    archive_folder = os.path.join(sorting_folder, archive_name)
    os.makedirs(archive_folder)

    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(archive_folder)

    # повертаємо створену папку для архіву
    return archive_folder


def process_file(folder_path, file_path, normalized_file_name):

    _, file_extension = os.path.splitext(file_path)

    # Визначаємо категорію за розширенням
    category = None
    if file_extension[1:].lower() in ('jpeg', 'png', 'jpg', 'svg'):
        category = 'images'
    elif file_extension[1:].lower() in ('avi', 'mp4', 'mov', 'mkv'):
        category = 'video'
    elif file_extension[1:].lower() in ('doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx'):
        category = 'documents'
    elif file_extension[1:].lower() in ('mp3', 'ogg', 'wav', 'amr'):
        category = 'audio'
    elif file_extension[1:].lower() in ('zip', 'gz', 'tar'):
        category = 'archives'

        # застосовуємо функцію для розпакування архіву і отримання шляху до створеної папки
        archive_folder = process_archive(file_path, folder_path)

        # оновлюємо категорію та шлях файлу
        category = os.path.relpath(archive_folder, folder_path)

    if os.path.exists(file_path):
        # Перейменовуємо та переміщуємо файл
        new_file_path = os.path.join(folder_path, category, normalized_file_name + file_extension)
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        shutil.move(file_path, new_file_path)


def process_folder(folder_path):

    for root, dirs, files in os.walk(folder_path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            normalized_file_name = normalize(file)
            process_file(folder_path, file_path, normalized_file_name)

        # видаляємо порожні папки
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)


def main():
    if len(sys.argv) != 2:
        print("error")
    else:
        folder_path = sys.argv[1]
        process_folder(folder_path)
        print("Folder sorted successfully")


if __name__ == "__main__":
    main()
