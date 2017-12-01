import json
import requests
from pprint import pprint
import time
import functools
import urllib.request, urllib.error
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
VERSION = '5.68'
TOKEN = '' # необходимо добавить токен
VICTIM = ['tim_leary', '8822']
N = 2 # количество друзей в группе


def data_return(data):
    try:
        if data['error']['error_code'] == 6:
            return 'wait'
        elif data['error']['error_code'] == 7:
            return 'permission'
        elif data['error']['error_code'] == 18:
            return 'Такого пользователя не существует'
        elif data['error']['error_code'] == 113:
            return 'Неверный id или имя пользователя'
        elif data['error']['error_code'] == 260:
            return 'privacy_error'
        else:
            print('Неизвестная ошибка:', data)
    except:
        return data['response']['items']


def get_friends(user):
    connect = 1
    while connect:
        if user.isdigit():
            params = {
                'v': VERSION,
                'access_token': TOKEN,
                'user_id': user
            }
            try:
                response = requests.get('https://api.vk.com/method/friends.get', params, timeout=(1))
                data = response.json()
                connect = 0
                return data_return(data)
            except requests.exceptions.ReadTimeout:
                print('Ошбика ReadTimeout, ожидание восстанавления соединение')
            except requests.exceptions.ConnectTimeout:
                print('Ошибка ConnectionTimeout, ожидание восстановления соединения')
        else:
            try:
                urllib.request.urlopen('https://vk.com/' + user)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    print('Введено неверное имя пользователя')
            else:
                params = {
                    'v': VERSION,
                    'access_token': TOKEN,
                    'code': 'return API.friends.get({"user_id": API.users.get({"user_ids":"' + user + '"})@.id});'
                }
                try:
                    response = requests.get('https://api.vk.com/method/execute', params, timeout=(1))
                    data = response.json()
                    connect = 0
                    return data_return(data)
                except requests.exceptions.ReadTimeout:
                    print('Ошбика ReadTimeout, ожидание восстанавления соединение')
                except requests.exceptions.ConnectTimeout:
                    print('Ошибка ConnectionTimeout, ожидание восстановления соединения')


def get_groups(user):
    connect = 1
    while connect:
        params = {
            'v': VERSION,
            'access_token': TOKEN,
            'user_id': user,
            'filter': 'groups',
        }
        try:
            response = requests.get('https://api.vk.com/method/groups.get', params, timeout=(1))
            data = response.json()
            connect = 0
            return data_return(data)
        except requests.exceptions.ReadTimeout:
            print('Ошбика ReadTimeout, ожидание восстанавления соединение')
        except requests.exceptions.ConnectTimeout:
            print('Ошибка ConnectionTimeout, ожидание восстановления соединения')


def get_data_of_groups(groups):
    connect = 1
    while connect:
        params = {
            'v': VERSION,
            'access_token': TOKEN,
            'group_ids': groups,
            'fields': 'members_count'
        }
        try:
            response = requests.get('https://api.vk.com/method/groups.getById', params, timeout=(1))
            data = response.json()
            connect = 0
            try:
                if data['error']['error_code'] == 6:
                    return 'wait'
                else:
                    print('Неизвестная ошибка:', data['error'])
            except:
                return data['response']
        except requests.exceptions.ReadTimeout:
            print('Ошбика ReadTimeout, ожидание восстанавления соединение')
        except requests.exceptions.ConnectTimeout:
            print('Ошибка ConnectionTimeout, ожидание восстановления соединения')


def update_spy_groups(groups, dict):
    for val in groups:
        try:
            if list(dict.keys()).index(val) + 1:
                dict[val] += 1
        except:
            dict[val] = 1
    return dict


def get_spy_groups(friends_of_victim):
    groups_of_victim = {}.fromkeys(get_groups(VICTIM[1]), 0)
    for i, friend in enumerate(friends_of_victim):
        temp = get_groups(friend)
        while temp == 'wait':
            print('Много запросов. Подождем')
            time.sleep(1)
            temp = get_groups(friend)
        if temp == 'privacy_error':
            print('Ошибка приватности. Обработано {:.4}%'.format(i / len(friends_of_victim) * 100))
            continue
        elif temp == 'Такого пользователя не существует':
            print('Ошибка удаленного пользователя. Обработано {:.4}%'.format(i / len(friends_of_victim) * 100))
            continue
        elif temp == 'permission':
            print('Ошибка доступа. Обработано {:.4}%'.format(i / len(friends_of_victim) * 100))
            continue
        else:
            groups_of_victim = update_spy_groups(temp, groups_of_victim)
        print('Обработано {:.4}%'.format(i / len(friends_of_victim) * 100))
    list_of_groups_of_victims = []
    for i, item in groups_of_victim.items():
        if item < N:
            list_of_groups_of_victims.append(i)
    print(list_of_groups_of_victims)
    return list_of_groups_of_victims


def get_data_of_groups_with_friends(users, group):
    connect = 1
    while connect:
        params = {
            'v': VERSION,
            'access_token': TOKEN,
            'group_id': group,
            'user_ids': str(users)[1:-1]
        }
        try:
            response = requests.get('https://api.vk.com/method/groups.isMember', params, timeout=(1))
            data = response.json()
            connect = 0
            try:
                if data['error']['error_code'] == 6:
                    return 'wait'
                else:
                    print('Неизвестная ошибка:', data['error'])
            except:
                return data['response']
        except requests.exceptions.ReadTimeout:
            print('Ошбика ReadTimeout, ожидание восстанавления соединение')
        except requests.exceptions.ConnectTimeout:
            print('Ошибка ConnectionTimeout, ожидание восстановления соединения')


def divide_result_request(groups_of_victim):
    blocks = 0
    json_dump = []
    # магическое число около 3251 - максимальное число знаков в uri запросе
    if len(groups_of_victim) > 300:
        blocks = len(groups_of_victim) // 300
    for block in range(blocks + 1):
        temp = groups_of_victim[300 * block: 300 * (block + 1)]
        if get_data_of_groups(str(temp)[1:-1]) == 'wait':
            print('Много запросов. Подождем')
            time.sleep(1)
            json_dump.extend(get_data_of_groups(str(temp)[1:-1]))
        else:
            json_dump.extend(get_data_of_groups(str(temp)[1:-1]))
    return json_dump


def delete_extra_info(json_dump):
    items = ['is_closed', 'photo_100', 'photo_200', 'photo_50', 'screen_name', 'type', 'deactivated']
    for data in json_dump:
        list(map(lambda x: functools.partial(data.pop, x, None)(), items))
    return json_dump


if __name__ == '__main__':
    friends_of_victim = get_friends(VICTIM[1])
    if friends_of_victim:
        if friends_of_victim == 'Такого пользователя не существует':
            print('Такого пользователя не существует')
        else:
            groups_of_victim = get_spy_groups(friends_of_victim)
            json_dump = divide_result_request(groups_of_victim)
            json_dump = delete_extra_info(json_dump)
            json.dump(json_dump, open('groups.json', 'w'))
    else:
        print('У заданного Вами пользователя нет друзей')
    print('Программа завершила свою работу')

# Проверка
# pprint(json.load(open('groups.json', 'r')))

#'''

