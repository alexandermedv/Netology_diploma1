import requests
import os
import json
import time


def delete_temporary(directory):
    """Удаление временных файлов и папок"""

    print('Удаление временных файлов и папки.')
    for file_path in os.listdir(directory):
        os.remove(directory + file_path)
    os.rmdir(directory)
    print('Все временные файлы и папки удалены')

    return


class VkUser:
    """Работа с vk.com"""
    url = 'https://api.vk.com/method'

    def __init__(self, token, version, owner_id):
        self.params = {
            'access_token': token,
            'v': version
        }
        self.owner_id = owner_id

    def get_photos(self, q, directory):
        print('Сохранение фотографий с vk.com во временную локальную папку.')
        photos_get_url = self.url + '/photos.get'
        photos_get_params = {
            'owner_id': self.owner_id,
            'album_id': 'profile',
            'extended': '1'
        }
        req = requests.get(photos_get_url, params={**self.params, **photos_get_params}).json()

        photos_dict = []
        for photo in req['response']['items']:
            p = {}
            if photo['likes']['count'] not in photos_dict:
                p['file_name'] = str(photo['likes']['count']) + ".jpg"
            else:
                p['file_name'] = str(photo['likes']['count']) + '_' + str(photo['date']) + ".jpg"
            photos_dict.append(photo['likes']['count'])

            max_photo = photo['sizes'][-1]
            p['size'] = max_photo['height']
            img_data = requests.get(max_photo['url']).content
            with open(directory + p['file_name'], 'wb') as handler:
                handler.write(img_data)

        print('Фотографии сохранены на локальном диске.')

        return


class YaUploader:
    """Работа с яндекс.диск"""

    def __init__(self, token, directory):
        self.token = token
        self.directory = directory
        self.apibaseurl = 'https://cloud-api.yandex.net/v1/disk/resources'

    def create_folder(self):
        """"Проверка наличия папки и создание, если требуется"""
        # Проверка наличия папки на яндекс диске
        resp = requests.get(self.apibaseurl, headers={"Authorization": self.token}, params={"path": self.directory})
        if resp.status_code == 200:
            # Удаление папки, если она уже существует
            resp = requests.delete(self.apibaseurl, headers={"Authorization": self.token}, params={"path": self.directory})
            time.sleep(2)
            print('Удалена папка на яндекс диске:', directory)

        # Создание папки
        print('Создание папки на яндекс диске.')
        resp = requests.put(self.apibaseurl, headers={"Authorization": self.token}, params={"path": self.directory})

    def upload(self, kol):
        """Загрузка файлов из папки directory на яндекс диск"""
        # Сохранение файлов в папку
        headers = {"Authorization": self.token}
        # file_list = []
        for file_path in os.listdir(self.directory):
            if file_path.endswith(".jpg"):
                d = {}
                d['file_name'] = file_path
                d['size'] = int(os.path.getsize(self.directory + file_path))
                # file_list.append(d)

                def myfunc(file):
                    return int(os.path.getsize(self.directory + file))
                if d['file_name'] in sorted(os.listdir(self.directory), key=myfunc, reverse=True)[:kol]:
                    params = {"path": self.directory + file_path}
                    resp = requests.get(self.apibaseurl + '/upload', headers=headers, params=params)

                    with open(self.directory + file_path, 'rb') as f:
                        print('Загрузка файла:', file_path)
                        response = requests.post(resp.json()['href'], files={"file": f})
                        if response.status_code == 201:
                            print('Файл успешно загружен.')
                        else:
                            print('Файл не загружен.')

                    with open(directory + 'file_list.json', 'a') as f:
                        json.dump(d, f)

        print('Загрузка файла json с названиями и размерами файлов')
        params = {"path": self.directory + 'file_list.json'}
        resp = requests.get(self.apibaseurl + '/upload', headers=headers, params=params)

        with open(self.directory + 'file_list.json', 'rb') as f:
            response = requests.post(resp.json()['href'], files={"file": f})
            if response.status_code == 201:
                print('Файл успешно загружен.')
            else:
                print('Файл не загружен.')

        print('Загрузка выполнена.')


if __name__ == "__main__":
    # Ввод данных
    # ID пользователя, у которого треуется выгрузить фотографии
    # owner_id = '552934290'
    token_vk = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
    owner_id = str(input('Введите аккаунт:\n'))
    # Папка, в которую будут сохраняться файлы
    directory = 'photos_from_vk/'
    # Количество сохраняемых фотографий
    # kol = 5
    kol = int(input('Введите количество фотографий:\n'))

    token_ya = str(input('Введите яндекс токен:\n'))

    vk_client = VkUser(token_vk, '5.131', owner_id)

    print('Создание временной папки на локальном диске.')
    os.mkdir(directory)

    uploader = YaUploader(token_ya, directory)
    try:
        vk_client.get_photos(requests, directory)
        uploader.create_folder()
        uploader.upload(kol)
    finally:
        delete_temporary(directory)

    print('Все необходимые действия выполнены. Резервное копирование фотографий завершено.')
