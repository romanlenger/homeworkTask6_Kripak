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
    prev_char_is_underscore = False
    for char in string:
        if char.lower() in translit_mapping:
            translit_string += translit_mapping[char.lower()]
            prev_char_is_underscore = False
        elif re.match(r'[a-zA-Z0-9]', char):
            translit_string += char.lower()
            prev_char_is_underscore = False
        else:
            if not prev_char_is_underscore:
                translit_string += '_'
                prev_char_is_underscore = True

    return translit_string.strip('_')


def process_archive(file_path, sorting_folder):
    archive_name, file_extension = os.path.splitext(os.path.basename(file_path))
    normalized_archive_name = normalize(archive_name)
    
    archive_folder = os.path.join(sorting_folder, normalized_archive_name)

    try:
        os.makedirs(archive_folder)
    except FileExistsError:
        pass

    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(archive_folder)
    except zipfile.BadZipFile:
        pass

    category = os.path.relpath(archive_folder, sorting_folder)
    new_archive_path = os.path.join(sorting_folder, "archives", normalized_archive_name)

    shutil.move(archive_folder, new_archive_path)

    return new_archive_path


def process_file(folder_path, file_path):
    _, file_extension = os.path.splitext(file_path)

    category = None
    if file_extension[1:].lower() in ('jpeg', 'png', 'jpg', 'svg'):
        category = 'images'
    elif file_extension[1:].lower() in ('avi', 'mp4', 'mov', 'mkv'):
        category = 'video'
    elif file_extension[1:].lower() in ('doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx', 'docV'):
        category = 'documents'
    elif file_extension[1:].lower() in ('mp3', 'ogg', 'wav', 'amr'):
        category = 'audio'
    elif file_extension[1:].lower() in ('zip', 'gz', 'tar'):
        category = 'archives'
        archive_folder = process_archive(file_path, folder_path)
        category = os.path.relpath(archive_folder, folder_path)
    else:
        category = 'others'

    if os.path.exists(file_path) and category is not None:
        category_folder = os.path.join(folder_path, category)
        file_name_without_extension, _ = os.path.splitext(os.path.basename(file_path))

        new_file_path = os.path.join(category_folder, f"{normalize(file_name_without_extension)}{file_extension}")
        os.makedirs(category_folder, exist_ok=True)
        shutil.move(file_path, new_file_path)

    print(f"File: {normalize(file_name_without_extension)} | Category: {category}")
    

def process_folder(folder_path):
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for file in files:
            file_path = os.path.join(root, file)
            process_file(folder_path, file_path)

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
