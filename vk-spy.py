import json
import requests
import time
import functools
import urllib.request, urllib.error
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
VERSION = '5.68'
TOKEN = '5dfd6b0dee902310df772082421968f4c06443abecbc082a8440cb18910a56daca73ac8d04b25154a1128' # необходимо добавить токен
VICTIM = ['eshmargunov', '5030613']
N = 2 # не более, чем N друзей в группе, цифра от 1


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
                print('Ошибка ReadTimeout, ожидание восстанавления соединение')
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
                    print('Ошибка ReadTimeout, ожидание восстанавления соединение')
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
            print('Ошибка ReadTimeout, ожидание восстанавления соединение')
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
            print('Ошибка ReadTimeout, ожидание восстанавления соединение')
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
    temp = get_groups(VICTIM[1])
    if temp == 'privacy_error':
        print('Данные о группах заданного Вами пользователя закрыты')
        if N > 1:
            print('Будем искать только не более заданного N друзей жертвы')
            groups_of_victim = {}
        else:
            return 'privacy_error'
    else:
        groups_of_victim = {}.fromkeys(temp, 0)
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
    return list_of_groups_of_victims


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
            print(friends_of_victim)
        else:
            groups_of_victim = get_spy_groups(friends_of_victim)
            if groups_of_victim != 'privacy_error':
                if groups_of_victim:
                    json_dump = divide_result_request(groups_of_victim)
                    json_dump = delete_extra_info(json_dump)
                    with open('groups.json', 'w') as f:
                        json.dump(json_dump, f, ensure_ascii=False)
                else:
                    print('Для указанного пользователя по заданным параметрам результатов не получено')
            else:
                print('У жертвы закрыты группы, попробуйте задать N и найти '
                      'группы, в которых есть общие друзья, но не более, чем N человек')
    else:
        print('У заданного Вами пользователя нет друзей')
    print('Программа завершила свою работу')


