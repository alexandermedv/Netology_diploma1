import requests
import os
import json


class VkUser:
    """Работа с vk.com"""
    url = 'https://api.vk.com/method'

    def __init__(self, token, version, owner_id):
        self.params = {
            'access_token': token,
            'v': version
        }
        self.owner_id = owner_id

    def get_photos(self, q, directory, kol):
        print('Сохранение фотографий с vk.com во временную локальную папку.')
        photos_get_url = self.url + '/photos.get'
        photos_get_params = {
            'owner_id': '552934290',
            'album_id': 'profile',
            'extended': '1'
        }
        req = requests.get(photos_get_url, params={**self.params, **photos_get_params}).json()

        photos_dict = {}
        result = []

        for photo in req['response']['items']:
            if photo['likes']['count'] not in photos_dict:
                photos_dict[photo['likes']['count']] = photo
                p = {}
                p['file_name'] = str(photo['likes']['count']) + ".jpg"
                max_photo = photo['sizes'][0]
                for item in photo['sizes']:
                    if item['height'] > max_photo['height']:
                        max_photo = item
                p['size'] = max_photo['height']
                img_data = requests.get(max_photo['url']).content
                with open(directory + p['file_name'], 'wb') as handler:
                    handler.write(img_data)
                result.append(p)
            else:
                key = str(photo['likes']['count']) + '_' + str(photo['date'])
                photos_dict[key] = photo
                p = {}
                p['file_name'] = str(photo['likes']['count']) + '_' + str(photo['date']) + ".jpg"
                max_photo = photo['sizes'][0]
                for item in photo['sizes']:
                    if item['height'] > max_photo['height']:
                        max_photo = item
                p['size'] = max_photo['height']
                img_data = requests.get(max_photo['url']).content
                with open(directory + p['file_name'], 'wb') as handler:
                    handler.write(img_data)
                result.append(p)

        def myFunc(e):
            return e['size']
        result.sort(reverse=True, key=myFunc)
        result = result[:kol]
        with open(directory + 'file_list.json', 'w') as f:
            json.dump(result, f)
        print('Фотографии сохранены на локальном диске.')

        return result

    def delete_temporary(self, directory):
        """Удаление временных файлов и папок"""

        print('Удаление временных файлов и папки.')
        for file_path in os.listdir(directory):
            os.remove(directory + file_path)
        os.rmdir(directory)
        print('Все временные файлы и папки удалены')

        return 'Удаление временных файлов и папок выполнено'


class YaUploader:
    """Работа с яндекс.диск"""
    def __init__(self, token, directory, file_list):
        self.token = token
        self.directory = directory
        self.file_list = file_list

    def upload(self):
        """Загрузка всех файлов из папки directory на яндекс диск"""

        # Создание папки
        print('Создание папки на яндекс диске.')
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        resp = requests.put(url, headers={"Authorization": self.token}, params={"path": self.directory})

        # Сохранение файлов в папку
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {"Authorization": self.token}

        names = []
        for file in self.file_list:
            names.append(file['file_name'])

        for file_path in os.listdir(self.directory):
            if file_path in names:
                params = {"path": self.directory + file_path}
                resp = requests.get(url, headers=headers, params=params)

                with open(self.directory + file_path, 'rb') as f:
                    print('Загрузка файла:', file_path)
                    response = requests.post(resp.json()['href'], files={"file": f})
                    if str(response) == '<Response [201]>':
                        print('Файл успешно загружен.')
                    else:
                        return 'Файл не загружен.'

        print('Загрузка файла json с названиями и размерами файлов')
        params = {"path": self.directory + 'file_list.json'}
        resp = requests.get(url, headers=headers, params=params)

        with open(self.directory + 'file_list.json', 'rb') as f:
            response = requests.post(resp.json()['href'], files={"file": f})
            if str(response) == '<Response [201]>':
                print('Файл успешно загружен.')
            else:
                return 'Файл не загружен.'

        return 'Загрузка выполнена.'


# Ввод данных
# ID пользователя, у которого треуется выгрузить фотографии
owner_id = '552934290'
token_vk = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
# Папка, в которую будут сохраняться файлы
directory = 'photos_from_vk/'
# Количество сохраняемых фотографий
kol = 5
# Вставьте свой токен для яндекс.диска:
token_ya = ''

vk_client = VkUser(token_vk, '5.131', owner_id)

print('Создание временной папки на локальном диске.')
os.mkdir(directory)

print('Сохранение фотографий во временную папку.')
file_list = vk_client.get_photos(requests, directory, kol)

try:
    uploader = YaUploader(token_ya, directory, file_list)
    result = uploader.upload()
    print(result)
finally:
    vk_client.delete_temporary(directory)

print('Все необходимые действия выполнены. Резервное копирование фотографий завершено.')
