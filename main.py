import json
from config import access_token
import requests
from tqdm import tqdm
from datetime import datetime


class VK:
    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return f'{response.json()["response"][0]["first_name"]} {response.json()["response"][0]["last_name"]}'

    def get_max_size_photos(self, items):
        photo = {}
        for item in items:
            if str(item['likes']['count']) in photo:
                photo[
                    (f"{str(item['likes']['count'])}__"
                     f"{datetime.strftime(datetime.fromtimestamp(item['date']), '%d_%m_%Y')}")] = \
                    item['sizes'][-1]['url'], item['sizes'][-1]['type']
            else:
                photo[str(item['likes']['count'])] = item['sizes'][-1]['url'], item['sizes'][-1]['type']
        return photo

    def save_photo_info(self, profile_photos):
        info_photo = []
        for file_name, photo_info in profile_photos.items():
            info_photo_tmp = {'file_name': f'{file_name}.jpg', 'size': photo_info[1]}
            info_photo.append(info_photo_tmp)
        self.write_json(info_photo)

    def write_json(self, data):
        with open('response.json', 'a') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def get_profile_photos(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': self.id, 'album_id': 'profile', 'extended': True, 'count': 5}
        response = requests.get(url, params={**self.params, **params})
        items = response.json()['response']["items"]
        profile_photos = self.get_max_size_photos(items)
        self.save_photo_info(profile_photos)
        return profile_photos


class YdConnector:
    def __init__(self, token):
        self.token = token
        self.headers = {'Authorization': f'OAuth {token}'}

    def create_folder(self, folder_name):
        self.folder_name = folder_name
        url_create_folder = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {
            'path': self.folder_name

        }
        response = requests.put(url_create_folder, headers=self.headers, params=params)
        return response.status_code

    def save_photo(self, profile_photos):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        for file_name, url_photo in tqdm(profile_photos.items()):
            response = requests.get(url, params={'path': f'{self.folder_name}/{file_name}', 'overwrite': 'true'},
                                    headers=self.headers)
            url_upload = response.json().get('href')
            r = requests.get(url_photo[0])
            requests.put(url_upload, data=r)


user_id = str(input('Введите id пользователя VK: '))
vk = VK(access_token, user_id)

yd_token = str(input('Введите ваш токен ЯндексДиск: '))
yd_1 = YdConnector(yd_token)
yd_1.create_folder(vk.users_info())
yd_1.save_photo(vk.get_profile_photos())
